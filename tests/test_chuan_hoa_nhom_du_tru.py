"""Chuẩn hoá nhãn nhóm dự trữ về một MÃ duy nhất.

VẤN ĐỀ: `reserve_group` là chuỗi tự do, gõ ở HAI nơi (file danh sách CLB
và file học sinh) và phải khớp nhau. Trước đây so khớp bằng chuỗi chính
xác, nên CLB khai `chinh_sach` còn giáo viên gõ `Chính sách` là hai nhóm
khác nhau: học sinh diện chính sách vào theo diện `general`, mất suất dự
trữ. Pipeline vẫn chạy hết và không báo lỗi — chỉ có hai dòng trong mục
Cảnh báo dữ liệu, rất dễ lướt qua.

CÁCH CHỮA: mọi nhãn đi qua một hàm chuẩn hoá TRƯỚC khi ghi vào DB — bỏ
dấu tiếng Việt, chữ thường, mọi thứ không phải chữ/số thành gạch dưới.
Hai bên gõ kiểu nào cũng quy về cùng một mã, nên không còn lệch được.

Chuẩn hoá lúc GHI (không phải lúc so sánh) là chủ ý: thuật toán trong
rbda_priority_pipeline.py vẫn so khớp chuỗi chính xác như cũ, không phải
sửa gì — chỗ nhạy cảm nhất của dự án không bị đụng tới.
"""

import pytest


@pytest.fixture
def api_co_club(api):
    api.create_or_update_club("clb_a", "CLB A", 10, 3, "chinh_sach")
    return api


def nhom_hs(api, sid):
    return api.list_students_admin(sid)["data"]["rows"][0]["reserve_group"]


def nhom_clb(api, cid):
    return {c["club_id"]: c for c in api.list_clubs_admin()["data"]}[cid]["reserve_group"]


# ------------------------------------------------------------------ #
# HÀM CHUẨN HOÁ
# ------------------------------------------------------------------ #


@pytest.mark.parametrize("go_vao,mong_doi", [
    ("chinh_sach", "chinh_sach"),
    ("Chính sách", "chinh_sach"),
    ("CHÍNH SÁCH", "chinh_sach"),
    ("Chính-Sách", "chinh_sach"),
    ("  chinh sach  ", "chinh_sach"),
    ("Chính   sách", "chinh_sach"),
    ("Khối 10", "khoi_10"),
    ("Đội tuyển", "doi_tuyen"),          # chữ Đ không tách được bằng NFD
    ("ĐỘI TUYỂN HSG", "doi_tuyen_hsg"),
    ("Ưu tiên vùng khó khăn", "uu_tien_vung_kho_khan"),
    ("", ""),
    ("   ", ""),
    (None, ""),
])
def test_chuan_hoa_dua_moi_cach_go_ve_mot_ma(api, go_vao, mong_doi):
    assert api.chuan_hoa_nhom_du_tru(go_vao) == mong_doi


def test_hai_nhom_that_su_khac_nhau_van_giu_nguyen_su_khac(api):
    """Chuẩn hoá không được gộp nhầm hai nhóm khác nghĩa."""
    assert api.chuan_hoa_nhom_du_tru("khoi_10") != api.chuan_hoa_nhom_du_tru("khoi_11")
    assert api.chuan_hoa_nhom_du_tru("chinh_sach") != api.chuan_hoa_nhom_du_tru("doi_tuyen")


# ------------------------------------------------------------------ #
# ÁP DỤNG Ở MỌI ĐƯỜNG GHI
# ------------------------------------------------------------------ #


def test_tao_club_qua_form_duoc_chuan_hoa(api):
    api.create_or_update_club("clb_a", "CLB A", 10, 3, "Chính sách")
    assert nhom_clb(api, "clb_a") == "chinh_sach"


def test_nhap_club_bang_csv_duoc_chuan_hoa(api):
    api.import_clubs_csv(
        "club_id,name,capacity,reserve_capacity,reserve_group\n"
        "clb_a,CLB A,10,3,Chính sách\n"
    )
    assert nhom_clb(api, "clb_a") == "chinh_sach"


def test_nhap_hoc_sinh_bang_csv_duoc_chuan_hoa(api_co_club):
    api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,An,Chính sách,clb_a\n"
    )
    assert nhom_hs(api_co_club, "HS001") == "chinh_sach"


def test_gan_tay_tung_em_duoc_chuan_hoa(api_co_club):
    api_co_club.create_student_if_missing("HS001", "An")
    api_co_club.set_student_reserve_group("HS001", "Chính sách")
    assert nhom_hs(api_co_club, "HS001") == "chinh_sach"


def test_gan_hang_loat_duoc_chuan_hoa(api_co_club):
    api_co_club.create_student_if_missing("HS001", "An")
    api_co_club.create_student_if_missing("HS002", "Bình")
    api_co_club.bulk_set_reserve_group(["HS001", "HS002"], "CHÍNH SÁCH")
    assert nhom_hs(api_co_club, "HS001") == "chinh_sach"
    assert nhom_hs(api_co_club, "HS002") == "chinh_sach"


def test_bo_trong_van_la_bo_trong_khong_thanh_chuoi_la(api_co_club):
    api_co_club.create_student_if_missing("HS001", "An")
    api_co_club.set_student_reserve_group("HS001", "   ")
    assert nhom_hs(api_co_club, "HS001") in (None, "")


# ------------------------------------------------------------------ #
# PHÉP THỬ THẬT: hai bên gõ khác kiểu vẫn phải nhận nhau
# ------------------------------------------------------------------ #


def test_CLB_va_hoc_sinh_go_khac_kieu_van_khop_nhau(api):
    """Đây chính là ca hỏng trước đây: CLB ghi chinh_sach, giáo viên gõ
    'Chính sách' — em đó mất suất dự trữ, vào theo diện general."""
    api.create_or_update_club("clb_a", "CLB A", 1, 1, "chinh_sach")
    api.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\n"
        "HS001,Học sinh thường,,clb_a\n"
        "HS002,Diện chính sách,Chính sách,clb_a\n"
    )
    # cho HS001 điểm CAO hơn -> không có dự trữ thì HS001 chiếm mất suất
    api.submit_club_scores("clb_a", [
        {"student_id": "HS001", "score": 9.0},
        {"student_id": "HS002", "score": 5.0},
    ])
    assert api.run_pipeline(seed=42)["ok"] is True

    kq = {r["student_id"]: r for r in api.get_match_results()["data"]}
    assert kq["HS002"]["club_id"] == "clb_a"
    assert kq["HS002"]["matched_tier"] == "reserve"


def test_khong_con_canh_bao_nhom_mo_coi_khi_chi_khac_cach_go(api):
    api.create_or_update_club("clb_a", "CLB A", 10, 3, "chinh_sach")
    api.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,An,CHÍNH SÁCH,clb_a\n"
    )
    ma_canh_bao = {w["code"] for w in api.get_data_health_report()["data"]["warnings"]}
    assert "health_orphan_student_group" not in ma_canh_bao
    assert "health_club_group_no_students" not in ma_canh_bao


# ------------------------------------------------------------------ #
# GÕ SAI THẬT thì vẫn phải báo — chuẩn hoá không được che lỗi
# ------------------------------------------------------------------ #


def test_go_sai_chinh_ta_that_van_bao_nhom_mo_coi(api):
    """Chuẩn hoá chỉ gộp các cách viết CÙNG một chữ. Gõ nhầm hẳn sang
    chữ khác thì vẫn là nhóm khác và phải được cảnh báo."""
    api.create_or_update_club("clb_a", "CLB A", 10, 3, "chinh_sach")
    api.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,An,chinh_sac,clb_a\n"
    )
    ma_canh_bao = {w["code"] for w in api.get_data_health_report()["data"]["warnings"]}
    assert "health_orphan_student_group" in ma_canh_bao


def test_canh_bao_NGAY_LUC_NHAP_chu_khong_doi_vao_muc_khac(api):
    """Cảnh báo nằm ở mục Cảnh báo dữ liệu rất dễ bị lướt qua. Nhập xong
    là phải thấy ngay, kèm gợi ý nhóm gần giống đã có."""
    api.create_or_update_club("clb_a", "CLB A", 10, 3, "chinh_sach")
    res = api.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,An,chinh_sac,clb_a\n"
    )
    assert res["ok"] is True
    ma = [w["code"] for w in res["data"]["warnings"]]
    assert "csv_reserve_group_unknown" in ma
    w = next(w for w in res["data"]["warnings"] if w["code"] == "csv_reserve_group_unknown")
    # gợi ý đúng nhóm gần giống nhất
    assert "chinh_sach" in str(w["params"].get("goi_y", ""))


def test_khong_canh_bao_khi_nhom_khop_dung(api):
    api.create_or_update_club("clb_a", "CLB A", 10, 3, "chinh_sach")
    res = api.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,An,Chính sách,clb_a\n"
    )
    ma = [w["code"] for w in res["data"]["warnings"]]
    assert "csv_reserve_group_unknown" not in ma
