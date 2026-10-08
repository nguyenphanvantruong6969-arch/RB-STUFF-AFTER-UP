# -*- coding: utf-8 -*-
"""Ô tìm kiếm phải hiểu tiếng Việt như người gõ.

Trước đây mọi ô tìm dùng `LIKE` của SQLite: chỉ bỏ qua hoa/thường với chữ
Latin trơn, nên "BÌNH" không ra "Bình", gõ không dấu "binh" không ra gì,
và `%`, `_` là ký tự đại diện — gõ "_" liệt kê cả trường.
"""

import pytest

from rbda_priority_pipeline import chuan_hoa_tim_kiem, khop_tim

HOC_SINH = [
    ("HS01", "Lê Thị Bình"),
    ("HS02", "Phạm Văn Dũng"),
    ("HS03", "Đỗ Minh Khoa"),
    ("HS04", "Ngô Văn An"),
    ("HS_5", "Trần 50% Chi"),
]


@pytest.fixture
def api_co_hs(api):
    for ma, ten in HOC_SINH:
        assert api.create_student_if_missing(ma, ten)["ok"]
    return api


def _tim(api, q):
    return [r["student_id"] for r in api.list_students_admin(q, 1, 50)["data"]["rows"]]


@pytest.mark.parametrize("q, mong", [
    ("Bình", ["HS01"]),
    ("bình", ["HS01"]),
    ("BÌNH", ["HS01"]),
    ("binh", ["HS01"]),
    ("BINH", ["HS01"]),
    ("dung", ["HS02"]),
    ("Dũng", ["HS02"]),
    ("đỗ", ["HS03"]),
    ("do minh", ["HS03"]),
    ("hs0", ["HS01", "HS02", "HS03", "HS04"]),
])
def test_tim_khong_phan_biet_dau_va_hoa_thuong(api_co_hs, q, mong):
    assert _tim(api_co_hs, q) == mong


def test_phan_tram_va_gach_duoi_la_chu_thuong_khong_phai_ky_tu_dai_dien(api_co_hs):
    assert _tim(api_co_hs, "%") == ["HS_5"]
    assert _tim(api_co_hs, "_") == ["HS_5"]


def test_tim_rong_tra_ca_danh_sach(api_co_hs):
    assert len(_tim(api_co_hs, "")) == len(HOC_SINH)


def test_phan_trang_dem_dung_so_dong_khop(api_co_hs):
    d = api_co_hs.list_students_admin("van", 1, 1)["data"]
    assert d["total"] == 2 and d["total_pages"] == 2
    assert [r["student_id"] for r in d["rows"]] == ["HS02"]
    d2 = api_co_hs.list_students_admin("van", 2, 1)["data"]
    assert [r["student_id"] for r in d2["rows"]] == ["HS04"]


def test_search_students_cung_luat(api_co_hs):
    assert [r["student_id"] for r in api_co_hs.search_students("BINH")["data"]] == ["HS01"]


def test_tim_trong_ket_qua_cung_luat(api_co_hs):
    api = api_co_hs
    assert api.create_or_update_club("A", "CLB A", 10, 0, "")["ok"]
    for ma, _ in HOC_SINH:
        assert api.submit_preferences(ma, ["A"])["ok"]
    assert api.run_pipeline(42)["ok"]
    assert [r["student_id"] for r in api.get_match_results("BINH")["data"]] == ["HS01"]


def test_ham_chuan_hoa():
    assert chuan_hoa_tim_kiem("Đỗ Thị BÌNH") == "do thi binh"
    assert khop_tim("Lê Thị Bình", "binh") == 1
    assert khop_tim("Lê Thị Bình", "an") == 0
    assert khop_tim(None, "a") == 0
