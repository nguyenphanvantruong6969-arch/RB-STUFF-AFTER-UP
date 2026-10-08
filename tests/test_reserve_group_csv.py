"""Gán nhóm dự trữ cho HỌC SINH ngay trong file CSV.

Khoảng trống cũ: học sinh tạo bằng CSV luôn có reserve_group rỗng, phải
vào màn hình 04 gán tay. Mà nhóm dự trữ CHÍNH LÀ cơ chế ưu tiên của
RB-DA — quên bước đó thì phần dự trữ vô hiệu hoàn toàn, pipeline vẫn
chạy trơn tru và KHÔNG báo lỗi gì. Với 120 học sinh, đây là khâu vừa
mất công vừa dễ quên.

Quy tắc đã chốt (ghi cả trong HUONG_DAN_CSV.md):
  - Ô có giá trị  -> GHI ĐÈ nhóm hiện có (người nhập chủ động đưa vào).
  - Ô trống       -> GIỮ NGUYÊN, không xoá (file thiếu cột không được
                     làm mất dữ liệu đã gán).
"""

import pytest


@pytest.fixture
def api_co_club(api):
    for cid, ten in [("clb_bongro", "CLB Bóng rổ"), ("clb_amnhac", "CLB Âm nhạc"),
                     ("clb_tienganh", "CLB Tiếng Anh")]:
        api.create_or_update_club(cid, ten, 20, 5, "chinh_sach")
    return api


def nhom(api, sid):
    rows = api.list_students_admin(sid)["data"]["rows"]
    return rows[0]["reserve_group"] if rows else None


def test_cot_reserve_group_trong_file_nguyen_vong_duoc_gan_luon(api_co_club):
    res = api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\n"
        "HS001,Nguyễn Văn An,chinh_sach,clb_bongro\n"
        "HS002,Trần Thị Bình,,clb_amnhac\n"
    )
    assert res["ok"] is True, res["errors"]
    assert nhom(api_co_club, "HS001") == "chinh_sach"
    assert nhom(api_co_club, "HS002") in (None, "")


def test_cot_reserve_group_trong_file_chon_club_thi_cung_duoc_gan(api_co_club):
    res = api_co_club.import_test_selection_csv(
        "student_id,name,reserve_group,test_club_1\n"
        "HS001,Nguyễn Văn An,khoi10,clb_bongro\n"
    )
    assert res["ok"] is True, res["errors"]
    assert nhom(api_co_club, "HS001") == "khoi10"


def test_dang_dai_cung_doc_duoc_cot_reserve_group(api_co_club):
    res = api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,club_id,rank\n"
        "HS001,Nguyễn Văn An,chinh_sach,clb_bongro,1\n"
        "HS001,Nguyễn Văn An,chinh_sach,clb_amnhac,2\n"
    )
    assert res["ok"] is True, res["errors"]
    assert nhom(api_co_club, "HS001") == "chinh_sach"


def test_o_trong_KHONG_xoa_nhom_da_gan_truoc_do(api_co_club):
    """File nhập lại mà thiếu giá trị không được làm mất dữ liệu cũ."""
    api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,A,chinh_sach,clb_bongro\n"
    )
    api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,A,,clb_amnhac\n"
    )
    assert nhom(api_co_club, "HS001") == "chinh_sach"


def test_file_KHONG_co_cot_reserve_group_cung_khong_xoa_nhom(api_co_club):
    api_co_club.bulk_set_reserve_group(["HS001"], "chinh_sach") if False else None
    api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,A,chinh_sach,clb_bongro\n"
    )
    api_co_club.import_preferences_csv(
        "student_id,name,pref_1\nHS001,A,clb_amnhac\n"
    )
    assert nhom(api_co_club, "HS001") == "chinh_sach"


def test_gia_tri_moi_GHI_DE_nhom_cu(api_co_club):
    api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,A,chinh_sach,clb_bongro\n"
    )
    api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\nHS001,A,khoi10,clb_amnhac\n"
    )
    assert nhom(api_co_club, "HS001") == "khoi10"


def test_co_cot_reserve_group_thi_du_tru_HOAT_DONG_that(api_co_club):
    """Phép thử cuối cùng: nhập bằng CSV rồi chạy pipeline, phải có học
    sinh vào được qua diện dự trữ mà KHÔNG cần gán tay ở màn hình 04."""
    api_co_club.create_or_update_club("clb_hep", "CLB Hẹp", 1, 1, "chinh_sach")
    api_co_club.import_preferences_csv(
        "student_id,name,reserve_group,pref_1\n"
        "HS001,Học sinh thường,,clb_hep\n"
        "HS002,Học sinh diện chính sách,chinh_sach,clb_hep\n"
    )
    ds = api_co_club.get_club_applicants_for_scoring("clb_hep")["data"]["applicants"]
    # cho HS001 điểm CAO hơn -> nếu không có dự trữ thì HS001 chiếm suất
    api_co_club.submit_club_scores("clb_hep", [
        {"student_id": u["student_id"], "score": 9.0 if u["student_id"] == "HS001" else 5.0}
        for u in ds
    ])
    assert api_co_club.run_pipeline(seed=42)["ok"] is True

    kq = {r["student_id"]: r for r in api_co_club.get_match_results()["data"]}
    assert kq["HS002"]["club_id"] == "clb_hep"
    assert kq["HS002"]["matched_tier"] == "reserve"


def test_nhan_dien_khong_nham_file_co_cot_reserve_group(api_co_club):
    """reserve_group không được làm hỏng việc nhận diện loại file."""
    d = api_co_club.detect_csv_kind(
        "student_id,name,reserve_group,pref_1\nHS001,A,chinh_sach,clb_bongro\n"
    )["data"]
    assert d["kind"] == "preferences"
    assert d["confident"] is True
