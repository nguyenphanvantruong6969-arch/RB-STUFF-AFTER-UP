"""Mỗi tài liệu có hai bản: .md (nguồn, sửa tay) và .html (bản trình bày,
có biểu đồ). Hai bản viết TAY, không sinh từ nhau.

Kiểm 27/09 tìm thấy ba chỗ bản .html bị bỏ lại sau khi .md có thêm nội dung:
cả mục "có phải cặp ghép TỐT NHẤT không" (CO_CHE_THUAT_TOAN), cả "Câu 4 — nhiều
buổi" (GIAI_DAP_BOC_THAM), và mục "Đã làm tới đâu" (KE_HOACH_NHIEU_BUOI). Người
đọc bản có biểu đồ — thường là giám khảo — đọc một câu trả lời cũ.

Test này bắt loại lệch đó qua CON SỐ: mọi số liệu then chốt trong .md (số
thập phân, tỉ số dạng a/b) phải có mặt trong .html. Thêm một kết quả đo vào .md
mà quên .html là đỏ ngay.

Bản .html được phép viết cùng con số theo CÁCH KHÁC (chính xác hơn, hoặc bằng
chữ, hoặc trong biểu đồ) — những chỗ đó liệt kê tường minh bên dưới, kèm lý do.
"""

import html
import os
import re

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VIET_KHAC = {
    "GIAI_DAP_BOC_THAM": {
        "0,051": "bản html ghi chính xác hơn: +0,0509",
        "0,073": "bản html ghi chính xác hơn: 0,0727",
        "0,71": "bản html chỉ ghi dạng phần trăm (1,44 %)",
        "6/10": "một phần của \"6/100\", đã có",
    },
    "KE_HOACH_NHIEU_BUOI": {
        "0/300": "bản html viết \"A1 0 · A2 0\" trên \"300 lượt\"",
        "113/300": "bản html viết \"A3 113 (37,7%)\" trên \"300 lượt\"",
    },
    "NGHIEN_CUU_TOI_UU": {
        "1,419": "cột trong biểu đồ TN4 (dữ liệu JS), không in thành chữ",
        "1,462": "cột trong biểu đồ TN4 (dữ liệu JS), không in thành chữ",
        "1,570": "cột trong biểu đồ TN4 (dữ liệu JS), không in thành chữ",
        "120/120": "bản html viết \"120 em\" ở tiêu đề bảng",
        "160/200": "bản html tóm tắt thành tỉ lệ phần trăm",
        "258/1400": "bản html viết \"0 / 1 400 em · Boston: 258\"",
        "8,3%": "bản html chỉ ghi số em (10), không ghi tỉ lệ",
        "0/10": "bản html viết bằng chữ",
    },
}

CAP = ["CO_CHE_THUAT_TOAN", "GIAI_DAP_BOC_THAM", "KE_HOACH_NHIEU_BUOI",
       "NGHIEN_CUU_TOI_UU", "KHAO_SAT_CAU_HOI"]


def _gon(x):
    return re.sub(r"\s+", "", x)


def _so_lieu_md(ten):
    md = open(os.path.join(GOC, "docs", ten + ".md"), encoding="utf-8").read()
    return {_gon(n) for n in re.findall(
        r"\b\d+(?:[,.]\d+)?\s?/\s?\d[\d ]*\d\b|\b\d+,\d+\s?%?", md)}


def _chu_html(ten):
    h = open(os.path.join(GOC, "docs", ten + ".html"), encoding="utf-8").read()
    chu = html.unescape(re.sub(r"<[^>]+>", " ", h))
    chu = re.sub(r"(\d)\s+trên\s+(\d)", r"\1/\2", chu)
    return _gon(chu)


@pytest.mark.parametrize("ten", CAP)
def test_moi_so_lieu_trong_md_co_mat_trong_html(ten):
    chu = _chu_html(ten)
    mien = VIET_KHAC.get(ten, {})
    thieu = sorted(n for n in _so_lieu_md(ten) if n not in chu and n not in mien)
    assert thieu == [], (
        f"{ten}.md co so lieu ma {ten}.html khong co: {thieu}. Them vao .html, "
        "hoac neu .html viet khac thi ghi vao VIET_KHAC kem ly do.")


@pytest.mark.parametrize("ten", CAP)
def test_danh_sach_mien_khong_giu_so_da_bo(ten):
    """Mục miễn trừ phải còn trong .md — số đã xoá khỏi .md thì xoá khỏi đây."""
    thua = set(VIET_KHAC.get(ten, {})) - _so_lieu_md(ten)
    assert thua == set(), thua
