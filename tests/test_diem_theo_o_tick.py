# -*- coding: utf-8 -*-
"""Điểm chỉ tồn tại — và chỉ được tính — khi ô tick "muốn thi" còn đó.

VÌ SAO CẦN: trước đây bỏ tick một CLB ở Bước 1 (hoặc bấm "Sửa lại từ đầu",
hoặc nạp lại tệp chọn CLB thi) chỉ xoá ô tick, còn điểm giáo viên đã chấm
thì nằm lại trong `club_scores`. Điểm đó:

  * biến mất khỏi màn hình chấm điểm (chỉ liệt kê em có tick), và không
    xoá được nữa (`score_not_applicant`);
  * vẫn được tính nếu em còn xếp CLB đó làm nguyện vọng — em lên Tầng 1
    bằng một bài thi em đã rút, và giành chỗ của em thi thật;
  * không có cảnh báo nào.

Đo được: CLB A một chỗ, HS1 thi 5 điểm, HS2 thi 9 điểm rồi bỏ tick. HS2
vẫn lấy chỗ của HS1.
"""

import sqlite3


def _dung_hai_em(api):
    assert api.create_or_update_club("A", "CLB A", 1, 0, "")["ok"]
    assert api.create_or_update_club("B", "CLB B", 5, 0, "")["ok"]
    for ma, ten in (("HS1", "Ngô Văn An"), ("HS2", "Lê Thị Bình")):
        assert api.create_student_if_missing(ma, ten)["ok"]
        assert api.submit_test_selection(ma, ["A"])["ok"]
        assert api.submit_preferences(ma, ["A", "B"])["ok"]
    assert api.submit_club_scores("A", [
        {"student_id": "HS1", "score": 5},
        {"student_id": "HS2", "score": 9},
    ])["data"]["n_saved"] == 2


def _clb_cua(api, ma):
    for r in api.get_match_results("")["data"]:
        if r["student_id"] == ma:
            return r["club_id"]
    return None


def _diem(api):
    conn = sqlite3.connect(api.db_path)
    try:
        return set(conn.execute(
            "SELECT student_id, club_id, score FROM club_scores").fetchall())
    finally:
        conn.close()


# ------------------------------------------------------------------ #
# Bước 1 — bỏ tick
# ------------------------------------------------------------------ #

def test_bo_tick_xoa_diem_va_bao_so_diem_da_xoa(api):
    _dung_hai_em(api)
    res = api.submit_test_selection("HS2", [])
    assert res["ok"]
    assert res["data"]["n_scores_removed"] == 1
    assert ("HS2", "A", 9.0) not in _diem(api)


def test_bo_tick_khong_con_gianh_cho_bang_bai_thi_da_rut(api):
    _dung_hai_em(api)
    assert api.run_pipeline(42)["ok"]
    assert _clb_cua(api, "HS2") == "A"      # 9 > 5, đúng

    assert api.submit_test_selection("HS2", [])["ok"]
    assert api.run_pipeline(42)["ok"]
    # HS2 vẫn xếp A nhưng không còn điểm -> Tầng 2; HS1 có điểm -> Tầng 1.
    assert _clb_cua(api, "HS1") == "A"
    assert _clb_cua(api, "HS2") == "B"


def test_bo_tick_mot_clb_giu_nguyen_diem_clb_con_tick(api):
    assert api.create_or_update_club("A", "CLB A", 3, 0, "")["ok"]
    assert api.create_or_update_club("B", "CLB B", 3, 0, "")["ok"]
    assert api.create_student_if_missing("HS1", "An")["ok"]
    assert api.submit_test_selection("HS1", ["A", "B"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "HS1", "score": 8}])["ok"]
    assert api.submit_club_scores("B", [{"student_id": "HS1", "score": 6}])["ok"]

    res = api.submit_test_selection("HS1", ["A"])
    assert res["data"]["n_scores_removed"] == 1
    assert _diem(api) == {("HS1", "A", 8.0)}


def test_luu_lai_khong_doi_gi_thi_khong_xoa_diem_nao(api):
    _dung_hai_em(api)
    res = api.submit_test_selection("HS1", ["A"])
    assert res["data"]["n_scores_removed"] == 0
    assert ("HS1", "A", 5.0) in _diem(api)


def test_man_hinh_cham_diem_khop_voi_du_lieu_sau_khi_bo_tick(api):
    _dung_hai_em(api)
    assert api.submit_test_selection("HS2", [])["ok"]
    ds = api.get_club_applicants_for_scoring("A")["data"]["applicants"]
    assert [u["student_id"] for u in ds] == ["HS1"]
    tong = {r["club_id"]: r for r in api.get_scoring_overview()["data"]}
    assert tong["A"]["n_applicants"] == 1 and tong["A"]["n_scored"] == 1

    # Tick lại: em quay về màn chấm điểm với ô TRỐNG, không phải điểm cũ.
    assert api.submit_test_selection("HS2", ["A"])["ok"]
    ds = {u["student_id"]: u["score"]
          for u in api.get_club_applicants_for_scoring("A")["data"]["applicants"]}
    assert ds == {"HS1": 5.0, "HS2": None}


# ------------------------------------------------------------------ #
# "Sửa lại từ đầu"
# ------------------------------------------------------------------ #

def test_sua_lai_tu_dau_xoa_ca_diem(api):
    _dung_hai_em(api)
    res = api.reset_student_entry("HS2")
    assert res["ok"]
    assert res["data"]["n_scores_removed"] == 1
    assert {r[0] for r in _diem(api)} == {"HS1"}

    # Nhập lại chỉ nguyện vọng: điểm cũ KHÔNG sống lại.
    assert api.submit_preferences("HS2", ["A", "B"])["ok"]
    assert api.run_pipeline(42)["ok"]
    assert _clb_cua(api, "HS1") == "A"


# ------------------------------------------------------------------ #
# Nạp lại tệp chọn CLB thi
# ------------------------------------------------------------------ #

def test_nap_lai_tep_bo_clb_thi_xoa_diem_va_canh_bao(api):
    _dung_hai_em(api)
    csv = "student_id,name,club_id\nHS2,Lê Thị Bình,B\n"
    res = api.import_test_selection_csv(csv)
    assert res["ok"], res["errors"]
    assert res["data"]["n_scores_removed"] == 1
    canh_bao = [w for w in res["data"]["warnings"]
                if isinstance(w, dict) and w.get("code") == "csv_score_removed_unselected"]
    assert canh_bao and canh_bao[0]["params"] == {"student_id": "HS2", "n": 1}
    assert ("HS2", "A", 9.0) not in _diem(api)


def test_nap_lai_tep_con_clb_thi_giu_diem(api):
    _dung_hai_em(api)
    csv = "student_id,name,club_id\nHS2,Lê Thị Bình,A\n"
    res = api.import_test_selection_csv(csv)
    assert res["data"]["n_scores_removed"] == 0
    assert ("HS2", "A", 9.0) in _diem(api)


def test_nap_tep_kem_diem_moi_van_ghi_diem_moi(api):
    _dung_hai_em(api)
    csv = "student_id,name,club_id,score\nHS2,Lê Thị Bình,B,7\n"
    res = api.import_test_selection_csv(csv)
    assert res["data"]["n_scores_removed"] == 1
    assert res["data"]["n_scores_written"] == 1
    assert {(s, c) for s, c, _ in _diem(api)} == {("HS1", "A"), ("HS2", "B")}


# ------------------------------------------------------------------ #
# CSDL đã có sẵn điểm mồ côi (dựng bằng bản cũ)
# ------------------------------------------------------------------ #

def _cay_diem_mo_coi(api):
    """Tạo lại đúng tình trạng bản cũ để lại: điểm còn, tick đã mất."""
    _dung_hai_em(api)
    conn = sqlite3.connect(api.db_path)
    conn.execute("DELETE FROM club_test_selection WHERE student_id = 'HS2'")
    conn.commit()
    conn.close()


def test_chay_sap_xep_bo_qua_diem_khong_co_tick(api):
    _cay_diem_mo_coi(api)
    assert api.run_pipeline(42)["ok"]
    assert _clb_cua(api, "HS1") == "A"
    assert _clb_cua(api, "HS2") == "B"


def test_bang_suc_khoe_bao_diem_khong_co_tick(api):
    _cay_diem_mo_coi(api)
    ws = api.get_data_health_report()["data"]["warnings"]
    w = [x for x in ws if x["code"] == "health_diem_khong_dang_ky_thi"]
    assert len(w) == 1
    assert w[0]["severity"] == "high"
    assert w[0]["params"]["n"] == 1
    assert w[0]["params"]["sample"] == "HS2→A"

    # Lưu lại Bước 1 cho em đó là dọn được, và cảnh báo biến mất.
    assert api.submit_test_selection("HS2", [])["data"]["n_scores_removed"] == 1
    ws = api.get_data_health_report()["data"]["warnings"]
    assert not [x for x in ws if x["code"] == "health_diem_khong_dang_ky_thi"]


def test_du_lieu_sach_khong_co_canh_bao_diem_khong_tick(api):
    _dung_hai_em(api)
    ws = api.get_data_health_report()["data"]["warnings"]
    assert not [x for x in ws if x["code"] == "health_diem_khong_dang_ky_thi"]
