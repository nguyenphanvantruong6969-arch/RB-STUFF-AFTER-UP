"""Phần dùng chung của các tệp api_*.py: import, hằng số và hàm tiện ích.

PipelineAPI từng là MỘT tệp hơn 4 000 dòng. Nay tách theo việc (xem api.py),
và mọi tệp con lấy chung các thứ dưới đây từ một chỗ.
"""

import copy
import csv
import functools
import datetime
import os
import sys


def _so_vn(x):
    """Số thập phân viết theo kiểu Việt Nam: `4,61` chứ không phải `4.61`.

    Tệp `.csv` này mở bằng Excel trên máy cài tiếng Việt, mà ở đó dấu CHẤM
    là dấu phân cách HÀNG NGHÌN — `2.33` đọc ra có thể thành `233`. Màn
    hình đã viết dấu phẩy ngay từ đầu, nên tệp viết dấu chấm là hai bên nói
    hai con số khác nhau về cùng một thứ.

    CHỈ dùng cho tệp `.csv`. Các trang dữ liệu trong sổ Excel giữ nguyên số
    THẬT (kiểu số, không phải chữ) — ở đó Excel tự hiển thị theo máy người
    dùng, và biến chúng thành chữ là làm hỏng việc tính toán, sắp xếp.
    """
    if isinstance(x, bool) or not isinstance(x, float):
        return x
    return ("%g" % x).replace(".", ",")


def _phan_tram_vn(tu, mau, lam_tron=1):
    """`42,9%` — cùng lý do như `_so_vn`."""
    if not mau:
        return ""
    return "%s%%" % _so_vn(round(100 * tu / mau, lam_tron))


def _now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _nho_trong_luc_xuat(ham):
    """Trong MỘT lần xuất, mỗi truy vấn báo cáo chỉ chạy một lần.

    export_csv dựng cả tệp tổng hợp lẫn tệp Excel từ cùng các bảng, và
    trước đây gọi lại từng hàm báo cáo cho mỗi nơi dùng: thống kê lấp đầy
    chạy bốn lần, mỗi lần một kết nối riêng. Chậm, và tệ hơn: dữ liệu đổi
    giữa hai lần gọi thì các tệp của CÙNG một lần xuất nói hai điều khác
    nhau. Ngoài lúc xuất (`_bo_nho_xuat` là None) hàm chạy như thường.
    Trả BẢN SAO để nơi gọi có sửa kết quả cũng không làm bẩn bộ nhớ.
    """
    @functools.wraps(ham)
    def boc(self, *args):
        bo_nho = getattr(self, "_bo_nho_xuat", None)
        if bo_nho is None:
            return ham(self, *args)
        khoa = (ham.__name__,) + args
        if khoa not in bo_nho:
            bo_nho[khoa] = ham(self, *args)
        return copy.deepcopy(bo_nho[khoa])
    return boc


def _fail_co_buoc(steps, errors):
    """Thất bại của run_pipeline: nhật ký từng bước nằm trong `data`.

    Trước đây gói cả hai vào `errors` thành một dict — trái với hợp đồng
    `errors: [...]` ở đầu tệp, và giao diện phải viết nhánh riêng để bóc.
    """
    return {"ok": False, "data": {"steps": steps}, "errors": list(errors)}


def thu_muc_tai_ve() -> str:
    r"""Thư mục Tải xuống của người dùng — nơi tệp kết quả nên rơi vào.

    VÌ SAO CẦN: trước đây tệp kết quả được đặt CẠNH `app.db`, tức bên
    trong thư mục cài đặt phần mềm. Người dùng bấm "Xuất kết quả" rồi
    không biết tìm ở đâu, và đó cũng là chỗ `.exe` cùng dữ liệu nằm —
    không phải chỗ để tệp cho người ta mang đi.

    Windows: hỏi thẳng hệ điều hành bằng SHGetKnownFolderPath. KHÔNG
    ghép `%USERPROFILE%\Downloads` làm cách chính, vì người dùng dời được
    thư mục này, và OneDrive thường chuyển hướng nó. Ghép tay là đoán.

    Máy khác: đọc XDG_DOWNLOAD_DIR do môi trường bàn làm việc đặt ra,
    không có thì `~/Downloads`.

    Không bao giờ ném lỗi — trả về "" nếu không tìm được chỗ nào ghi
    được, để bên gọi tự lùi về phương án cũ.
    """
    ung_vien: list[str] = []

    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class GUID(ctypes.Structure):
                _fields_ = [("d1", wintypes.DWORD), ("d2", wintypes.WORD),
                            ("d3", wintypes.WORD), ("d4", ctypes.c_byte * 8)]

            # FOLDERID_Downloads {374DE290-123F-4565-9164-39C4925E467B}
            folderid = GUID(0x374DE290, 0x123F, 0x4565,
                            (ctypes.c_byte * 8)(0x91, 0x64, 0x39, 0xC4,
                                                0x92, 0x5E, 0x46, 0x7B))
            con_tro = ctypes.c_wchar_p()
            if ctypes.windll.shell32.SHGetKnownFolderPath(
                    ctypes.byref(folderid), 0, None, ctypes.byref(con_tro)) == 0:
                ung_vien.append(con_tro.value)
                ctypes.windll.ole32.CoTaskMemFree(con_tro)
        except Exception:
            pass                                  # lùi xuống các phương án dưới
        ung_vien.append(os.path.join(
            os.environ.get("USERPROFILE", os.path.expanduser("~")), "Downloads"))
    else:
        try:
            cau_hinh = os.path.expanduser("~/.config/user-dirs.dirs")
            if os.path.isfile(cau_hinh):
                with open(cau_hinh, encoding="utf-8") as f:
                    for dong in f:
                        if dong.startswith("XDG_DOWNLOAD_DIR"):
                            gia_tri = dong.split("=", 1)[1].strip().strip('"')
                            ung_vien.append(os.path.expandvars(
                                gia_tri.replace("$HOME", os.path.expanduser("~"))))
                            break
        except Exception:
            pass
        ung_vien.append(os.path.expanduser("~/Downloads"))

    for duong in ung_vien:
        if duong and os.path.isdir(duong) and os.access(duong, os.W_OK):
            return duong
    return ""


def duong_dan_khong_de(duong_dan: str, kem_duoi: tuple = ()) -> str:
    """Kiểu trình duyệt: đã có `x.csv` thì dùng `x (2).csv`, `x (3).csv`…

    Thư mục Tải xuống là thư mục của NGƯỜI DÙNG. Ghi đè im lặng ở đó là
    xoá mất tệp họ có thể đang cần — khác hẳn khi ghi trong thư mục do
    phần mềm tự quản.

    `kem_duoi`: các đuôi khác sẽ ghi CÙNG tên gốc (vd `.csv` đi kèm
    `.xlsx`) — tên chỉ coi là trống khi trống cho mọi đuôi.
    """
    goc, duoi = os.path.splitext(duong_dan)

    def da_co(g):
        return any(os.path.exists(g + d) for d in (duoi, *kem_duoi))

    if not da_co(goc):
        return duong_dan
    n = 2
    while da_co(f"{goc} ({n})") and n < 1000:
        n += 1
    return f"{goc} ({n}){duoi}"
def _an_toan_cho_excel(o):
    """Chan Excel hieu noi dung o thanh CONG THUC.

    Excel tinh moi o bat dau bang = + - @ nhu cong thuc. Mot hoc sinh ten
    "=1+1" se hien ra la 2, va giao vien khong the biet ten that la gi. Them
    dau nhay don o dau la cach chuan de Excel hieu "day la chu, dung tinh".

    Dung CHUNG cho moi tep xuat ra — mot tep quen goi la mot cua mo.
    """
    # Tab va xuong dong o dau o cung bi Excel/LibreOffice bo qua roi doc
    # tiep phan sau nhu cong thuc (OWASP CSV injection) — chan ca hai.
    if isinstance(o, str) and o[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + o
    return o
def _ghi_csv(path: str, header, cac_dong) -> None:
    """Ghi mot tep CSV cho nguoi dung mo bang Excel.

    encoding="utf-8-sig" = UTF-8 CÓ BOM. Không có BOM thì Excel đọc tên
    tiếng Việt thành "Nguyá»…n VÄƒn An". `header` rỗng thì không ghi dòng
    tiêu đề (tệp tự chia phần, như tệp tổng hợp).
    """
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if header:
            w.writerow(header)
        w.writerows([_an_toan_cho_excel(o) for o in d] for d in cac_dong)
