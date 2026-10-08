# -*- coding: utf-8 -*-
"""Khoá kịch bản nhập tay trong `du_lieu_test/NHAP_TAY.md`.

Tài liệu đó hứa một bảng kết quả cụ thể và bảo người dùng: "ra khác bảng
này là phần mềm sai". Lời hứa đó chỉ giữ được nếu có test canh — nếu
không, một thay đổi trong thuật toán sẽ âm thầm làm tài liệu nói dối.

Kịch bản cố ý KHÔNG có hai em bằng điểm trong cùng một club, nên bước bốc
thăm (STB) không bao giờ được dùng tới và kết quả không phụ thuộc seed.
"""

import pytest

CLB = [
    ("clb_nhiepanh", "CLB Nhiếp ảnh", 3, 1, "chinh_sach"),
    ("clb_covua",    "CLB Cờ vua",    2, 0, ""),
    ("clb_nauan",    "CLB Nấu ăn",    2, 0, ""),
]

# ma, ten, nhom du tru, nguyen vong theo thu tu, diem tung club
HOC_SINH = [
    ("HS01", "Ngô Văn An",     "",           ["clb_nhiepanh", "clb_covua"], {"clb_nhiepanh": 9.5, "clb_covua": 8.0}),
    ("HS02", "Lê Thị Bình",    "",           ["clb_nhiepanh", "clb_nauan"], {"clb_nhiepanh": 9.0, "clb_nauan": 7.5}),
    ("HS03", "Trần Ngọc Chi",  "",           ["clb_nhiepanh", "clb_covua"], {"clb_nhiepanh": 8.5, "clb_covua": 9.0}),
    ("HS04", "Phạm Văn Dũng",  "",           ["clb_nhiepanh"],              {"clb_nhiepanh": 8.0}),
    ("HS05", "Vũ Thị Hà",      "chinh_sach", ["clb_nhiepanh", "clb_nauan"], {"clb_nhiepanh": 6.0, "clb_nauan": 6.5}),
    ("HS06", "Đỗ Minh Khoa",   "",           ["clb_covua", "clb_nauan"],    {"clb_covua": 7.0, "clb_nauan": 9.0}),
    ("HS07", "Bùi Thị Lan",    "",           ["clb_nauan"],                 {"clb_nauan": 8.5}),
    ("HS08", "Hoàng Văn Minh", "",           ["clb_covua"],                 {"clb_covua": 6.5}),
]

# Bang trong NHAP_TAY.md — sua o day thi phai sua ca tai lieu.
KET_QUA_HUA = {
    "HS01": ("clb_nhiepanh", 1, "general"),
    "HS02": ("clb_nhiepanh", 1, "general"),
    "HS03": ("clb_covua",    2, "general"),
    "HS04": (None,        None, None),
    "HS05": ("clb_nhiepanh", 1, "reserve"),
    "HS06": ("clb_covua",    1, "general"),
    "HS07": ("clb_nauan",    1, "general"),
    "HS08": (None,        None, None),
}
LAP_DAY_HUA = {"clb_nhiepanh": 3, "clb_covua": 2, "clb_nauan": 1}


def _dung_kich_ban(api):
    """Gọi ĐÚNG các hàm mà giao diện gọi khi người dùng gõ tay."""
    for cid, ten, cap, rcap, nhom in CLB:
        assert api.create_or_update_club(cid, ten, cap, rcap, nhom)["ok"]
    for ma, ten, nhom, nv, diem in HOC_SINH:
        assert api.create_student_if_missing(ma, ten)["ok"]
        if nhom:
            assert api.set_student_reserve_group(ma, nhom)["ok"]
        assert api.submit_test_selection(ma, sorted(diem))["ok"]
        assert api.submit_preferences(ma, nv)["ok"]
    for cid, *_ in CLB:
        ds = [{"student_id": ma, "score": diem[cid]}
              for ma, _, _, _, diem in HOC_SINH if cid in diem]
        assert api.submit_club_scores(cid, ds)["ok"]


def _bang_ket_qua(api):
    res = api.get_match_results()
    assert res["ok"], res["errors"]
    bang = {r["student_id"]: (r.get("club_id"),
                              r.get("rank_in_student_pref"),
                              r.get("matched_tier"))
            for r in res["data"]}
    # Hai em khong duoc xep van phai co mat trong bang, khong duoc bien mat.
    return bang


def test_ket_qua_dung_nhu_tai_lieu_da_hua(api):
    _dung_kich_ban(api)
    run = api.run_pipeline(seed=42)
    assert run["ok"], run["errors"]
    assert run["data"]["n_matched"] == 6
    assert run["data"]["n_total"] == 8
    assert _bang_ket_qua(api) == KET_QUA_HUA


def test_suat_du_tru_thang_ca_em_diem_cao_hon(api):
    """Điểm chính của cả thuật toán: HS05 6.0 vào được, HS03 8.5 và HS04
    8.0 thì không — vì một trong ba chỗ là suất dự trữ."""
    _dung_kich_ban(api)
    assert api.run_pipeline(seed=42)["ok"]
    bang = _bang_ket_qua(api)
    assert bang["HS05"] == ("clb_nhiepanh", 1, "reserve")
    assert bang["HS03"][0] != "clb_nhiepanh"
    assert bang["HS04"][0] is None


def test_con_cho_trong_ma_van_co_em_chua_duoc_xep(api):
    """Nấu ăn còn 1 chỗ trong khi 2 em chưa xếp — vì không em nào trong
    hai em đó ghi Nấu ăn vào nguyện vọng. KHÔNG được tự nhét vào."""
    _dung_kich_ban(api)
    assert api.run_pipeline(seed=42)["ok"]
    st = api.get_club_fill_stats()
    assert st["ok"]
    assert {r["club_id"]: r["matched"] for r in st["data"]} == LAP_DAY_HUA


@pytest.mark.parametrize("seed", [1, 7, 42, 999, 12345])
def test_khong_phu_thuoc_boc_tham(api, seed):
    """Không có hai em bằng điểm trong cùng club nên STB không được dùng
    tới — đổi seed mà kết quả đổi thì tài liệu đang nói sai."""
    _dung_kich_ban(api)
    assert api.run_pipeline(seed=seed)["ok"]
    assert _bang_ket_qua(api) == KET_QUA_HUA
