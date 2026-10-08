"""
recovery.py
===========
js_api RIÊNG cho recovery.html — màn hình chỉ hiện khi PipelineAPI
KHÔNG khởi tạo được (app.db hỏng/mất, xem main.py). Không liên quan gì
tới PipelineAPI/nghiệp vụ pipeline: chỉ có 2 việc —
  1. Cho xem tình trạng lỗi + danh sách bản sao lưu (do PipelineAPI._backup_db
     tạo trước mỗi lần chạy pipeline, xem api.py).
  2. Thử khôi phục: ưu tiên bản sao lưu MỚI NHẤT còn đọc được nguyên vẹn
     (PRAGMA quick_check) — nếu bản đó cũng hỏng thì tự động lùi sang bản
     kế trước, không dừng lại ở bản đầu tiên gặp lỗi (xem
     kế hoạch kiểm thử mất dữ liệu — artifact, xem BAN_GIAO.md mục 8, nhóm C, dòng C2). Nếu không còn bản nào,
     hoặc người dùng chọn bỏ qua, có phương án cuối "bắt đầu mới" — đổi
     tên (KHÔNG xoá) tệp hỏng rồi tạo app.db trống.

main.py chỉ dùng lớp này khi PipelineAPI(db_path) ném exception, vào
đúng lúc đó CHƯA có webview window/API nào khác đang giữ app.db mở —
vì vậy copy/di chuyển file trực tiếp ở đây là an toàn (không rơi vào
tình huống "copy file trong khi tiến trình khác đang ghi" đã ghi nhận
là nguy hiểm với chế độ WAL trong ke hoạch).
"""

import datetime
import os
import shutil
import sqlite3

from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok


def thu_muc_ghi_duoc(thu_muc: str) -> bool:
    """Chương trình có TẠO được tệp trong `thu_muc` không?

    Thử tạo thật một tệp rồi xoá, KHÔNG dùng os.access(): trên Windows,
    "Quyền truy cập thư mục được kiểm soát" (chống mã độc tống tiền) và thư
    mục OneDrive đang khoá chặn việc ghi mà os.access vẫn báo là được. Đã gặp
    thật (27/09): giải nén vào một thư mục như vậy, app.db không tạo được, và
    màn hình này báo "cơ sở dữ liệu gặp sự cố" — sai nguyên nhân, người dùng
    không biết phải làm gì.
    """
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(dir=thu_muc or ".", prefix=".rbda_thu_ghi_"):
            pass
        return True
    except OSError:
        return False


def _quick_check_ok(path: str) -> bool:
    """True nếu path là file SQLite hợp lệ và PRAGMA quick_check trả 'ok'."""
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return False
    try:
        conn = sqlite3.connect(path)
        try:
            row = conn.execute("PRAGMA quick_check").fetchone()
            return bool(row) and row[0] == "ok"
        finally:
            conn.close()
    except sqlite3.Error:
        return False


class RecoveryAPI:
    def __init__(self, db_path: str, init_error: str):
        self.db_path = db_path
        self.init_error = init_error

    def _backup_dir(self) -> str:
        return os.path.dirname(self.db_path) or "."

    def _backup_prefix(self) -> str:
        return f"{os.path.basename(self.db_path)}.bak-"

    def _list_backups(self):
        backup_dir = self._backup_dir()
        prefix = self._backup_prefix()
        if not os.path.isdir(backup_dir):
            return []
        names = sorted(
            (f for f in os.listdir(backup_dir) if f.startswith(prefix)),
            reverse=True,  # ten co timestamp dang so, sort nguoc = moi nhat truoc
        )
        out = []
        for name in names:
            full = os.path.join(backup_dir, name)
            try:
                stat = os.stat(full)
            except OSError:
                continue
            out.append({
                "name": name,
                "size_bytes": stat.st_size,
                "modified_at": datetime.datetime.fromtimestamp(
                    stat.st_mtime
                ).isoformat(timespec="seconds"),
            })
        return out

    def get_status(self):
        thu_muc = os.path.dirname(os.path.abspath(self.db_path))
        return _ok({
            "db_path": self.db_path,
            "init_error": self.init_error,
            "backups": self._list_backups(),
            # Không ghi được vào thư mục thì CSDL không hỏng gì cả — cần một
            # lời khuyên khác hẳn (dời thư mục), và hai nút khôi phục/bắt đầu
            # lại đều vô ích. Giao diện đổi hẳn nội dung khi thấy cờ này.
            "thu_muc": thu_muc,
            "ghi_duoc": thu_muc_ghi_duoc(thu_muc),
        })

    # Tệp phụ SQLite đi kèm app.db. `-journal` là cái có thật ở đây (chế
    # độ DELETE); `-wal`/`-shm` phòng khi tệp đến từ máy bật WAL. Để sót
    # tệp phụ lại thì SQLite coi nó là của app.db MỚI chép vào và "phục
    # hồi" nó vào bản sao lưu — làm hỏng chính bản vừa khôi phục.
    _DUOI_TEP_PHU = ("-journal", "-wal", "-shm")

    def _move_corrupt_db_aside(self):
        """Đổi tên (KHÔNG xoá) app.db hiện tại cùng tệp phụ của nó.

        Trả về đường dẫn mới, hoặc None nếu không có app.db. Đổi tên THẤT
        BẠI (tệp bị khoá trên Windows...) thì NÉM OSError — trước đây hàm
        nuốt lỗi và trả None, và start_fresh cứ thế tạo CSDL mới đè lên
        chính tệp chưa dời đi được.
        """
        if not os.path.exists(self.db_path):
            return None
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        aside = f"{self.db_path}.corrupt-{ts}"
        shutil.move(self.db_path, aside)
        for duoi in self._DUOI_TEP_PHU:
            if os.path.exists(self.db_path + duoi):
                shutil.move(self.db_path + duoi, aside + duoi)
        return aside

    def _db_hien_tai_con_tot(self) -> bool:
        """app.db hiện tại vẫn đọc được bình thường?

        Màn hình này mở cho MỌI lỗi khởi động, không riêng CSDL hỏng — cài
        vào thư mục không có quyền ghi, tệp đang bị chương trình khác khoá
        cũng dẫn tới đây. Khi đó "khôi phục" hay "bắt đầu lại" sẽ dời một
        CSDL còn nguyên vẹn đi chỗ khác. Chặn lại và nói rõ.
        """
        return _quick_check_ok(self.db_path)

    def restore_from_backup(self):
        """Thử bản sao lưu MỚI NHẤT trước; nếu hỏng, tự động lùi sang bản
        kế trước cho tới khi tìm được bản đọc được hoặc hết bản để thử."""
        if self._db_hien_tai_con_tot():
            return _fail(err("recovery_db_is_healthy"))
        backups = self._list_backups()
        if not backups:
            return _fail(err("recovery_no_backups"))

        backup_dir = self._backup_dir()
        tried = []
        for b in backups:
            full = os.path.join(backup_dir, b["name"])
            tried.append(b["name"])
            if not _quick_check_ok(full):
                continue

            try:
                corrupt_aside = self._move_corrupt_db_aside()
            except OSError as e:
                return _fail(err("recovery_restore_failed", detail=str(e)))
            try:
                shutil.copy2(full, self.db_path)
            except OSError as e:
                # Khoi phuc that bai o buoc copy — tra tep hong ve cho neu
                # da di doi, tranh mat luon ca ban hong (co the con cuu
                # duoc thu cong sau nay).
                if corrupt_aside and os.path.exists(corrupt_aside):
                    try:
                        shutil.move(corrupt_aside, self.db_path)
                    except OSError:
                        pass
                return _fail(err("recovery_restore_failed", detail=str(e)))

            return _ok({
                "restored_from": b["name"],
                "skipped": tried[:-1],
                "detail": err(
                    "recovery_restored_from",
                    backup_name=b["name"],
                    n_skipped=len(tried) - 1,
                ),
            })

        return _fail(err("recovery_all_backups_corrupt", n_tried=len(tried)))

    def start_fresh(self):
        """Phương án cuối, MANG TÍNH PHÁ HUỶ ở mức nhẹ: đổi tên file hỏng
        sang <db>.corrupt-<timestamp> (không xoá) rồi tạo app.db mới
        hoàn toàn trống."""
        from rbda_priority_pipeline import init_db

        if self._db_hien_tai_con_tot():
            return _fail(err("recovery_db_is_healthy"))
        try:
            self._move_corrupt_db_aside()
            init_db(self.db_path)
        except Exception as e:
            return _fail(err("recovery_restore_failed", detail=str(e)))
        return _ok({
            "db_path": self.db_path,
            "detail": err("recovery_fresh_created"),
        })
