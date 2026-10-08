"""Gỡ khoá tệp và ghi lại VÌ SAO cửa sổ gốc không mở được.

VẤN ĐỀ ĐANG SỬA
Trên Windows, pywebview đi qua pythonnet -> .NET Framework. Mắt xích đó
hỏng trên bản đóng gói, app lặng lẽ chuyển sang mở bằng trình duyệt, và
**không ai biết vì sao**: `main.py` ghi vết lỗi ra `sys.stderr`, mà bản
build `console=False` không có stderr nào cả. Ba phiên làm việc phải
ĐOÁN nguyên nhân vì thông tin đã bị vứt đi ngay lúc nó xảy ra.

Tệp này làm hai việc:

  1. GỠ DẤU "tải từ Internet" khỏi các tệp .dll trong gói. Windows gắn
     dấu đó (luồng NTFS `Zone.Identifier`) vào mọi tệp giải nén từ một
     tệp .zip tải về. .NET Framework TỪ CHỐI nạp assembly mang dấu này —
     đúng với triệu chứng đang gặp: thông báo lỗi nêu rõ đường dẫn tới
     Python.Runtime.dll, tức tệp CÓ ở đó, .NET tìm thấy nhưng không nạp.
     Gỡ dấu không cần quyền Administrator.

  2. GHI LẠI mọi thứ vào `loi_khoi_dong.txt` cạnh app.db. Lần sau hỏng
     thì có nguyên văn lỗi để đọc, không phải đoán tiếp.

CHƯA KIỂM CHỨNG ĐƯỢC: máy phát triển chạy Linux, không có .NET
Framework lẫn luồng NTFS. Phần gỡ dấu chỉ chạy thật trên Windows. Đó
chính là lý do phải có phần ghi log — để nếu giả thuyết sai thì lần này
biết sai ở đâu.
"""

import os
import sys
import traceback
from datetime import datetime

TEN_LOG = "loi_khoi_dong.txt"
# Lỗi khi ĐANG CHẠY (nạp tệp, chạy pipeline, xuất kết quả). Tách khỏi log
# khởi động để mỗi tệp chỉ kể một chuyện. Giao diện chỉ hiện thông điệp
# ngắn; vết ngăn xếp đầy đủ nằm ở đây cho người bảo trì đọc.
TEN_LOG_UNG_DUNG = "loi_ung_dung.txt"
_LUONG_ZONE = ":Zone.Identifier"


def duong_log(base_dir: str, ten: str = TEN_LOG) -> str:
    return os.path.join(base_dir, ten)


def ghi(base_dir: str, *dong, ten: str = TEN_LOG) -> None:
    """Ghi thêm vào cuối tệp log. Không bao giờ được ném lỗi ra ngoài —
    hỏng phần ghi log mà làm chết app thì tệ hơn cả lỗi đang chẩn đoán."""
    try:
        with open(duong_log(base_dir, ten), "a", encoding="utf-8") as f:
            moc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for d in dong:
                f.write("[%s] %s\n" % (moc, d))
    except Exception:
        pass


def ghi_ngoai_le(base_dir: str, tieu_de: str, ten: str = TEN_LOG) -> None:
    ghi(base_dir, tieu_de, traceback.format_exc().rstrip(), ten=ten)


def ghi_ngoai_le_canh_db(db_path: str, tieu_de: str, ten: str = TEN_LOG_UNG_DUNG) -> None:
    """Như ghi_ngoai_le, nhưng nhận đường dẫn app.db: tệp log nằm cạnh nó.
    Mặc định ghi vào log LỖI KHI CHẠY. Chỉ gọi TRONG khối `except`."""
    ghi_ngoai_le(os.path.dirname(os.path.abspath(db_path)), tieu_de, ten=ten)


def go_dau_tai_ve(thu_muc: str, duoi=(".dll", ".exe", ".pyd")) -> dict:
    """Xoá luồng Zone.Identifier khỏi các tệp trong `thu_muc`.

    Trả về {"da_go": n, "bo_qua": n, "loi": n} để ghi vào log — biết nó
    đã gỡ được bao nhiêu tệp cũng là một dữ kiện chẩn đoán.
    """
    ket = {"da_go": 0, "bo_qua": 0, "loi": 0}
    if not sys.platform.startswith("win") or not os.path.isdir(thu_muc):
        return ket
    for goc, _, ten_tep in os.walk(thu_muc):
        for ten in ten_tep:
            if not ten.lower().endswith(duoi):
                continue
            p = os.path.join(goc, ten) + _LUONG_ZONE
            try:
                os.remove(p)
                ket["da_go"] += 1
            except FileNotFoundError:
                ket["bo_qua"] += 1      # không mang dấu — bình thường
            except OSError:
                ket["loi"] += 1         # đang bị khoá, hoặc không phải NTFS
    return ket
