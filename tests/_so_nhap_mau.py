"""Tiện ích cho test giao diện: dựng một Sổ nhập CLB nhỏ trên đĩa.

Giao diện chỉ nhận Sổ nhập CLB, nên mọi test giao diện cần nạp dữ liệu đều
thả một sổ. Dùng chung một chỗ để test không tự chép bố cục sổ.
"""

import so_nhap

# Đợi sổ đã đọc xong và sẵn sàng nhập (nút Nhập sổ hiện ra).
CHO_SAN_SANG = ("!document.getElementById('importActions').hidden"
                " && !document.getElementById('btnImportAll').hidden")


def clb(club_id, ten, chi_tieu=10, buoi="", uu_tien=0, nhom=""):
    return {"club_id": club_id, "name": ten, "capacity": chi_tieu,
            "reserve_capacity": uu_tien, "reserve_group": nhom, "buoi": buoi}


def ghi_so(thu_muc, ten, clubs, students=()):
    """Ghi sổ ra `thu_muc/ten` và trả về đường dẫn (chuỗi)."""
    p = str(thu_muc / ten)
    so_nhap.ghi_so_nhap(p, clubs, list(students))
    return p


def tha_va_nhap(page, duong_dan, timeout=20000):
    """Thả sổ, đợi đọc xong, bấm Nhập sổ, đợi xong."""
    page.locator("#fileAny").set_input_files([str(duong_dan)])
    page.wait_for_function(CHO_SAN_SANG, timeout=timeout)
    page.locator("#btnImportAll").click()
    page.wait_for_selector(".queue-row.is-done", timeout=timeout)
