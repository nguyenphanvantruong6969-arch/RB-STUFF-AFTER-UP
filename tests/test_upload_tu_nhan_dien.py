"""Nhận diện loại file CSV tự động, và nhập danh sách CLB bằng CSV.

VÌ SAO CẦN: giao diện cũ có HAI ô nạp file — "Bước 1: chọn club muốn
thi" và "Bước 2: xếp hạng nguyện vọng" — và người dùng phải tự chọn
đúng ô. Kéo nhầm ô KHÔNG báo lỗi: file nguyện vọng dạng dài
(student_id, name, club_id, rank) nạp vào ô "chọn club thi" vẫn khớp
đủ cột, nên nó ghi thẳng vào bảng club_test_selection và báo "thành
công 5 học sinh". Nguyện vọng thật thì mất sạch, mà không một cảnh báo
nào. Với phần mềm phân bổ học sinh, đó là lỗi làm sai kết quả cả trường
mà không ai biết.

Cách chữa vừa an toàn vừa tiện hơn: người dùng KHÔNG phải chọn ô nữa —
hệ thống tự đọc dòng tiêu đề để biết đây là file gì. Khi tiêu đề KHÔNG
đủ để kết luận, hệ thống nói thẳng là chưa chắc và hỏi lại, tuyệt đối
không đoán.
"""

import pytest


def doc_mau(ten):
    import os
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mau_csv", ten
    )
    with open(p, encoding="utf-8-sig") as f:
        return f.read()


# ------------------------------------------------------------------ #
# NHẬN DIỆN CHẮC CHẮN
# ------------------------------------------------------------------ #


def test_nhan_ra_nguyen_vong_dang_rong_qua_cot_pref(api):
    d = api.detect_csv_kind("student_id,name,pref_1,pref_2\nHS001,A,x,y\n")["data"]
    assert d["kind"] == "preferences"
    assert d["format"] == "wide"
    assert d["confident"] is True


def test_nhan_ra_chon_club_thi_dang_rong_qua_cot_test_club(api):
    d = api.detect_csv_kind("student_id,name,test_club_1\nHS001,A,x\n")["data"]
    assert d["kind"] == "test_selection"
    assert d["format"] == "wide"
    assert d["confident"] is True


def test_cot_rank_la_dau_hieu_chac_chan_cua_nguyen_vong_dang_dai(api):
    """rank chỉ có nghĩa với nguyện vọng — chọn club thi không xếp hạng."""
    d = api.detect_csv_kind("student_id,name,club_id,rank\nHS001,A,x,1\n")["data"]
    assert d["kind"] == "preferences"
    assert d["format"] == "long"
    assert d["confident"] is True


def test_nhan_ra_file_danh_sach_club_qua_cot_capacity(api):
    d = api.detect_csv_kind("club_id,name,capacity\nclb_a,CLB A,20\n")["data"]
    assert d["kind"] == "clubs"
    assert d["confident"] is True


# ------------------------------------------------------------------ #
# KHÔNG CHẮC THÌ PHẢI NÓI LÀ KHÔNG CHẮC
# ------------------------------------------------------------------ #


def test_student_id_va_club_id_khong_kem_rank_la_MO_HO(api):
    """Đúng cái bẫy cũ: cùng bộ cột này có thể là chọn club thi dạng
    dài, mà cũng có thể là nguyện vọng dạng dài thiếu cột rank. Không
    được đoán — đoán sai là dữ liệu vào nhầm bảng."""
    d = api.detect_csv_kind("student_id,name,club_id\nHS001,A,x\n")["data"]
    assert d["confident"] is False
    assert set(d["candidates"]) == {"test_selection", "preferences"}


def test_file_khong_hieu_duoc_thi_bao_khong_hieu(api):
    d = api.detect_csv_kind("cot_la,cot_khac\n1,2\n")["data"]
    assert d["kind"] == "unknown"
    assert d["confident"] is False


def test_file_rong_bao_loi_ro_rang(api):
    res = api.detect_csv_kind("")
    assert res["ok"] is False


def test_nhan_dien_doc_duoc_file_luu_tu_Excel_co_BOM(api):
    d = api.detect_csv_kind("﻿student_id,name,pref_1\nHS001,A,x\n")["data"]
    assert d["kind"] == "preferences"
    assert d["confident"] is True


def test_bon_file_mau_deu_duoc_nhan_dien_dung(api):
    ky_vong = {
        "01_chon_club_thi_dang_rong.csv": ("test_selection", "wide"),
        "03_nguyen_vong_dang_rong.csv": ("preferences", "wide"),
        "04_nguyen_vong_dang_dai.csv": ("preferences", "long"),
    }
    for ten, (kind, fmt) in ky_vong.items():
        d = api.detect_csv_kind(doc_mau(ten))["data"]
        assert d["confident"] is True, ten
        assert (d["kind"], d["format"]) == (kind, fmt), ten

    # Mẫu 02 cố tình là trường hợp mơ hồ -> phải hỏi lại, không đoán
    d = api.detect_csv_kind(doc_mau("02_chon_club_thi_dang_dai.csv"))["data"]
    assert d["confident"] is False


# ------------------------------------------------------------------ #
# NẠP TỰ ĐỘNG — người dùng chỉ thả file, không phải chọn ô
# ------------------------------------------------------------------ #


@pytest.fixture
def api_co_club(api):
    for cid, ten in [("clb_bongro","CLB Bóng rổ"), ("clb_tienganh","CLB Tiếng Anh"),
                     ("clb_robotics","CLB Robotics"), ("clb_amnhac","CLB Âm nhạc"),
                     ("clb_mythuat","CLB Mỹ thuật")]:
        api.create_or_update_club(cid, ten, 20, 0, "")
    return api


def test_nap_tu_dong_dua_nguyen_vong_vao_dung_bang(api_co_club):
    res = api_co_club.import_csv_auto(doc_mau("03_nguyen_vong_dang_rong.csv"))
    assert res["ok"] is True, res["errors"]
    assert res["data"]["kind"] == "preferences"
    st = api_co_club.get_student_entry_state("HS001")["data"]
    assert st["ranked_clubs"]      # vào đúng bảng nguyện vọng
    assert not st["tested_clubs"]  # KHÔNG lẫn sang bảng kia


def test_nap_tu_dong_dua_chon_club_thi_vao_dung_bang(api_co_club):
    res = api_co_club.import_csv_auto(doc_mau("01_chon_club_thi_dang_rong.csv"))
    assert res["ok"] is True, res["errors"]
    assert res["data"]["kind"] == "test_selection"
    st = api_co_club.get_student_entry_state("HS001")["data"]
    assert st["tested_clubs"]
    assert not st["ranked_clubs"]


def test_nap_tu_dong_TU_CHOI_file_mo_ho_thay_vi_doan_bua(api_co_club):
    """Đây là chỗ bug cũ nằm. Thà không nhập còn hơn nhập vào sai bảng."""
    res = api_co_club.import_csv_auto(doc_mau("02_chon_club_thi_dang_dai.csv"))
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "csv_kind_ambiguous"
    # và không được ghi bất kỳ thứ gì
    assert api_co_club.get_dashboard_status()["data"]["n_students"] == 0


def test_nguoi_dung_chi_ro_loai_thi_file_mo_ho_van_nap_duoc(api_co_club):
    """Mơ hồ thì hỏi lại — trả lời rồi là nạp bình thường."""
    res = api_co_club.import_csv_auto(
        doc_mau("02_chon_club_thi_dang_dai.csv"), kind="test_selection"
    )
    assert res["ok"] is True, res["errors"]
    st = api_co_club.get_student_entry_state("HS001")["data"]
    assert sorted(st["tested_clubs"]) == ["clb_amnhac", "clb_bongro", "clb_tienganh"]


# ------------------------------------------------------------------ #
# NHẬP DANH SÁCH CLB BẰNG CSV
#
# Nút thắt ĐẦU TIÊN người dùng gặp: mẫu CSV học sinh bắt buộc club phải
# tồn tại trước, mà club lại chỉ tạo được bằng cách gõ form từng cái —
# trường có 15-20 CLB thì gõ 15-20 lần, mỗi lần 5 trường.
# ------------------------------------------------------------------ #


def test_nhap_danh_sach_club_bang_csv(api):
    res = api.import_clubs_csv(doc_mau("05_danh_sach_club.csv"))
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_clubs_created"] == 5
    clubs = {c["club_id"]: c for c in api.list_clubs_admin()["data"]}
    assert clubs["clb_tienganh"]["name"] == "CLB Tiếng Anh"
    assert clubs["clb_tienganh"]["capacity"] == 25
    assert clubs["clb_tienganh"]["reserve_capacity"] == 5
    assert clubs["clb_tienganh"]["reserve_group"] == "chinh_sach"


def test_club_csv_thieu_cot_du_tru_van_nhap_duoc(api):
    """Trường không dùng dự trữ thì không phải điền cột nào cả."""
    res = api.import_clubs_csv("club_id,name,capacity\nclb_a,CLB A,20\n")
    assert res["ok"] is True, res["errors"]
    c = api.list_clubs_admin()["data"][0]
    assert c["reserve_capacity"] == 0
    assert c["reserve_group"] in (None, "")


def test_club_csv_nhap_lai_thi_CAP_NHAT_chu_khong_tao_trung(api):
    api.import_clubs_csv("club_id,name,capacity\nclb_a,CLB A,20\n")
    res = api.import_clubs_csv("club_id,name,capacity\nclb_a,CLB A đổi tên,30\n")
    assert res["ok"] is True
    assert res["data"]["n_clubs_updated"] == 1
    assert len(api.list_clubs_admin()["data"]) == 1
    assert api.list_clubs_admin()["data"][0]["capacity"] == 30


def test_club_csv_chi_tieu_sai_thi_BO_QUA_dong_do_va_bao_ro(api):
    """Chỉ tiêu 0 hoặc dự trữ lớn hơn tổng chỉ tiêu là sai logic —
    không được im lặng nhận vào."""
    res = api.import_clubs_csv(
        "club_id,name,capacity,reserve_capacity\n"
        "clb_ok,CLB OK,20,5\n"
        "clb_am,CLB Am,0,0\n"
        "clb_qua,CLB Qua,10,50\n"
    )
    assert res["ok"] is True
    assert res["data"]["n_clubs_created"] == 1
    assert res["data"]["n_rows_skipped"] == 2
    assert len(res["data"]["warnings"]) == 2


def test_nap_tu_dong_nhan_ra_va_nhap_luon_file_club(api):
    res = api.import_csv_auto(doc_mau("05_danh_sach_club.csv"))
    assert res["ok"] is True, res["errors"]
    assert res["data"]["kind"] == "clubs"
    assert len(api.list_clubs_admin()["data"]) == 5


def test_man_hinh_quan_ly_club_phai_hien_dung_nhom_du_tru(api):
    """list_clubs_admin chỉ `return self.list_clubs()`, mà list_clubs
    KHÔNG chọn cột reserve_group — nên js/*.js:877 luôn hiện "—" ở cột
    nhóm dự trữ, kể cả club CÓ nhóm. Giáo viên nhìn màn hình 04 sẽ tưởng
    chưa club nào được gán dự trữ, trong khi DB có đủ. Nhóm dự trữ là
    cơ chế cốt lõi của RB-DA nên hiển thị sai ở đây rất dễ dẫn tới cấu
    hình lại nhầm."""
    api.create_or_update_club("clb_tienganh", "CLB Tiếng Anh", 25, 5, "chinh_sach")
    c = api.list_clubs_admin()["data"][0]
    assert c["reserve_group"] == "chinh_sach"


def test_club_nhap_bang_csv_cung_hien_dung_nhom_du_tru(api):
    api.import_clubs_csv(doc_mau("05_danh_sach_club.csv"))
    clubs = {c["club_id"]: c for c in api.list_clubs_admin()["data"]}
    assert clubs["clb_tienganh"]["reserve_group"] == "chinh_sach"
    assert clubs["clb_bongro"]["reserve_group"] in (None, "")
