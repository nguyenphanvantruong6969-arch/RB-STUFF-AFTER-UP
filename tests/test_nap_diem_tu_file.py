# -*- coding: utf-8 -*-
"""Nạp điểm chấm thẳng từ file, cùng file chọn CLB muốn thi.

VÌ SAO CẦN: không có điểm thì MỌI học sinh rơi xuống Tầng 2 và chỉ được
xếp bằng số bốc thăm — vòng thi coi như không tồn tại, kết quả in ra
không nói lên điều gì. Mà bộ 120 học sinh cần 356 ô điểm, gõ tay hết mất
khoảng 18 phút.
"""

import pytest


@pytest.fixture
def api_co_club(api):
    for cid, ten in (("clb_a", "CLB A"), ("clb_b", "CLB B"), ("clb_c", "CLB C")):
        api.create_or_update_club(cid, ten, 5, 0, "")
    return api


def diem_cua(api, club_id):
    r = api.get_club_applicants_for_scoring(club_id)
    assert r["ok"], r["errors"]
    return {u["student_id"]: u["score"] for u in r["data"]["applicants"]}


def ma_canh_bao(res):
    return [w["code"] for w in (res["data"].get("warnings") or [])]


# ------------------------------------------------------------------ #
# Đường chính
# ------------------------------------------------------------------ #
def test_dang_rong_nap_duoc_diem(api_co_club):
    res = api_co_club.import_test_selection_csv(
        "student_id,name,test_club_1,score_1,test_club_2,score_2\n"
        "HS1,An,clb_a,8.5,clb_b,9\n"
        "HS2,Bình,clb_a,7,,\n"
    )
    assert res["ok"], res["errors"]
    assert res["data"]["n_scores_written"] == 3
    assert diem_cua(api_co_club, "clb_a") == {"HS1": 8.5, "HS2": 7.0}
    assert diem_cua(api_co_club, "clb_b") == {"HS1": 9.0}


def test_dang_dai_cho_ket_qua_GIONG_HET_dang_rong(api):
    """Ràng buộc sẵn có của dự án: hai dạng của cùng một dữ liệu phải ra
    kết quả giống hệt nhau (xem test_csv_mau.py). Cột điểm không được phá
    ràng buộc đó."""
    def dung(a):
        for cid in ("clb_a", "clb_b"):
            a.create_or_update_club(cid, "CLB", 5, 0, "")

    from api import PipelineAPI
    import os
    import tempfile

    rong = PipelineAPI(os.path.join(tempfile.mkdtemp(), "app.db"))
    dai = PipelineAPI(os.path.join(tempfile.mkdtemp(), "app.db"))
    dung(rong)
    dung(dai)

    rong.import_test_selection_csv(
        "student_id,name,test_club_1,score_1,test_club_2,score_2\n"
        "HS1,An,clb_a,8.5,clb_b,6.25\n"
    )
    dai.import_test_selection_csv(
        "student_id,name,club_id,score\n"
        "HS1,An,clb_a,8.5\n"
        "HS1,An,clb_b,6.25\n"
    )
    for cid in ("clb_a", "clb_b"):
        assert diem_cua(rong, cid) == diem_cua(dai, cid)


def test_khong_co_cot_diem_thi_hanh_vi_y_nhu_cu(api_co_club):
    """Không hồi quy: file cũ không có cột điểm phải chạy y hệt trước."""
    res = api_co_club.import_test_selection_csv(
        "student_id,name,test_club_1,test_club_2\nHS1,An,clb_a,clb_b\n"
    )
    assert res["ok"], res["errors"]
    assert res["data"]["n_students_with_selection_written"] == 1
    assert res["data"]["n_scores_written"] == 0
    assert diem_cua(api_co_club, "clb_a") == {"HS1": None}


def test_o_trong_o_giua_van_ghep_dung_cap(api_co_club):
    """Ghép theo HẬU TỐ SỐ, không theo vị trí. Ghép theo vị trí thì bỏ
    trống test_club_2 sẽ làm điểm của club 3 gán nhầm cho club 1."""
    res = api_co_club.import_test_selection_csv(
        "student_id,name,test_club_1,score_1,test_club_2,score_2,test_club_3,score_3\n"
        "HS1,An,clb_a,5,,,clb_c,9\n"
    )
    assert res["ok"], res["errors"]
    assert diem_cua(api_co_club, "clb_a") == {"HS1": 5.0}
    assert diem_cua(api_co_club, "clb_c") == {"HS1": 9.0}


def test_nap_lai_thi_ghi_de_diem(api_co_club):
    t = "student_id,name,test_club_1,score_1\nHS1,An,clb_a,%s\n"
    api_co_club.import_test_selection_csv(t % "6")
    api_co_club.import_test_selection_csv(t % "9.5")
    assert diem_cua(api_co_club, "clb_a") == {"HS1": 9.5}


def test_dau_phay_thap_phan_van_doc_duoc(api_co_club):
    """Excel bản tiếng Việt lưu 8,5 chứ không phải 8.5."""
    res = api_co_club.import_test_selection_csv(
        'student_id,name,test_club_1,score_1\nHS1,An,clb_a,"8,5"\n'
    )
    assert res["ok"], res["errors"]
    assert diem_cua(api_co_club, "clb_a") == {"HS1": 8.5}


# ------------------------------------------------------------------ #
# Ô điểm hỏng — chỉ bỏ ô đó, không bỏ cả học sinh
# ------------------------------------------------------------------ #
def test_diem_ghi_chu_thi_canh_bao_nhung_giu_lua_chon_thi(api_co_club):
    res = api_co_club.import_test_selection_csv(
        "student_id,name,test_club_1,score_1\nHS1,An,clb_a,tám phẩy năm\n"
    )
    assert res["ok"], res["errors"]
    assert "csv_score_not_a_number" in ma_canh_bao(res)
    assert res["data"]["n_students_with_selection_written"] == 1, "không được bỏ cả học sinh"
    assert diem_cua(api_co_club, "clb_a") == {"HS1": None}


def test_diem_am_bi_chan(api_co_club):
    res = api_co_club.import_test_selection_csv(
        "student_id,name,test_club_1,score_1\nHS1,An,clb_a,-8\n"
    )
    assert "csv_score_negative" in ma_canh_bao(res)
    assert diem_cua(api_co_club, "clb_a") == {"HS1": None}


def test_diem_ma_khong_co_ma_club(api_co_club):
    """Gõ lệch cột: có điểm mà ô club cùng số thứ tự bỏ trống."""
    res = api_co_club.import_test_selection_csv(
        "student_id,name,test_club_1,score_1,test_club_2,score_2\nHS1,An,clb_a,8,,9\n"
    )
    assert "csv_score_without_club" in ma_canh_bao(res)
    assert diem_cua(api_co_club, "clb_a") == {"HS1": 8.0}


def test_diem_cho_club_khong_dang_ky_thi(api_co_club):
    """Dạng dài mới gặp được ca này: điểm cho club không nằm trong danh
    sách thi của em đó."""
    res = api_co_club.import_test_selection_csv(
        "student_id,name,club_id,score\nHS1,An,clb_a,8\n"
    )
    assert res["ok"], res["errors"]
    assert diem_cua(api_co_club, "clb_a") == {"HS1": 8.0}
    assert "clb_b" not in [w.get("params", {}).get("club_id") for w in res["data"]["warnings"]]


def test_ma_club_lech_hoa_thuong_van_ghi_dung_diem(api_co_club):
    """Điểm phải ghi bằng club_id ĐÃ KHỚP, không phải chuỗi thô — ghi thô
    tạo ra một dòng điểm mồ côi không màn hình nào đọc tới."""
    res = api_co_club.import_test_selection_csv(
        "student_id,name,test_club_1,score_1\nHS1,An,CLB_A,8.5\n"
    )
    assert res["ok"], res["errors"]
    assert diem_cua(api_co_club, "clb_a") == {"HS1": 8.5}


# ------------------------------------------------------------------ #
# Cột điểm đặt nhầm file
# ------------------------------------------------------------------ #
def test_cot_diem_trong_file_nguyen_vong_phai_bao(api_co_club):
    """Im lặng bỏ qua thì người nhập tưởng đã nạp điểm rồi."""
    res = api_co_club.import_preferences_csv(
        "student_id,name,pref_1,score_1\nHS1,An,clb_a,8.5\n"
    )
    assert res["ok"], res["errors"]
    assert "csv_scores_ignored_here" in ma_canh_bao(res)


# ------------------------------------------------------------------ #
# Kết quả cuối: nạp file xong là chạy được ngay, không phải chấm tay
# ------------------------------------------------------------------ #
def test_nap_file_co_diem_xong_la_khong_con_canh_bao_chua_cham(api_co_club):
    api_co_club.import_test_selection_csv(
        "student_id,name,test_club_1,score_1,test_club_2,score_2\n"
        "HS1,An,clb_a,8.5,clb_b,7\n"
        "HS2,Bình,clb_a,9,clb_b,6\n"
    )
    api_co_club.import_preferences_csv(
        "student_id,name,pref_1,pref_2\nHS1,An,clb_a,clb_b\nHS2,Bình,clb_a,clb_b\n"
    )
    ma = [w["code"] for w in api_co_club.get_data_health_report()["data"]["warnings"]]
    assert "health_scoring_none" not in ma
    assert "health_scoring_partial" not in ma
    assert api_co_club.run_pipeline(seed=42)["ok"]
