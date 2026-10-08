# -*- coding: utf-8 -*-
"""Tệp "thay đổi so với lần chạy trước" và cờ "kết quả có thể đã cũ".

Hai câu người vận hành sẽ hỏi sau khi sửa điểm rồi chạy lại:
  * "Ai đổi CLB?" -> `get_thay_doi_ket_qua` / `export_thay_doi_ket_qua`.
  * "Kết quả đang xem có còn đúng không?" -> `get_trang_thai_ket_qua`.
"""

import csv
import sqlite3

import pytest


@pytest.fixture
def hai_em(api):
    """CLB A một chỗ. HS1 5 điểm, HS2 9 điểm -> HS2 vào A, HS1 sang B."""
    assert api.create_or_update_club("A", "CLB A", 1, 0, "")["ok"]
    assert api.create_or_update_club("B", "CLB B", 5, 0, "")["ok"]
    for ma in ("HS1", "HS2"):
        assert api.create_student_if_missing(ma, "Em " + ma)["ok"]
        assert api.submit_test_selection(ma, ["A"])["ok"]
        assert api.submit_preferences(ma, ["A", "B"])["ok"]
    assert api.submit_club_scores("A", [
        {"student_id": "HS1", "score": 5}, {"student_id": "HS2", "score": 9}])["ok"]
    return api


def cu(api):
    return api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"]


def doc(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


# ------------------------------------------------------------------ #
# Thay đổi so với lần chạy trước
# ------------------------------------------------------------------ #

def test_lan_chay_dau_chua_co_gi_de_so(hai_em):
    assert hai_em.run_pipeline(42)["ok"]
    d = hai_em.get_thay_doi_ket_qua()["data"]
    assert d["co_lan_truoc"] is False
    r = hai_em.export_thay_doi_ket_qua()
    assert not r["ok"] and r["errors"][0]["code"] == "chua_co_lan_chay_truoc"


def test_chay_lai_khong_sua_gi_thi_khong_co_thay_doi(hai_em):
    assert hai_em.run_pipeline(42)["ok"]
    assert hai_em.run_pipeline(42)["ok"]
    d = hai_em.get_thay_doi_ket_qua()["data"]
    assert d["co_lan_truoc"] is True and d["dong"] == []


def test_doi_diem_roi_chay_lai_liet_ke_dung_hai_em_doi_clb(hai_em):
    api = hai_em
    assert api.run_pipeline(42)["ok"]
    assert api.submit_club_scores("A", [
        {"student_id": "HS1", "score": 10}])["ok"]
    assert api.run_pipeline(42)["ok"]
    d = api.get_thay_doi_ket_qua()["data"]
    doi = {(x["student_id"], x["club_cu"], x["club_moi"], x["loai"]) for x in d["dong"]}
    assert doi == {("HS1", "B", "A", "doi_clb"), ("HS2", "A", "B", "doi_clb")}
    assert d["dem"]["doi_clb"] == 2

    r = api.export_thay_doi_ket_qua()
    assert r["ok"] and r["data"]["n_thay_doi"] == 2
    dong = doc(r["data"]["path"])
    assert dong[0][0] == "So sánh kết quả lúc"
    tieu_de = dong[2]
    assert tieu_de == ["Mã học sinh", "Họ tên", "CLB cũ", "Diện cũ",
                       "CLB mới", "Diện mới", "Loại thay đổi"]
    assert {(x[0], x[2], x[4], x[6]) for x in dong[3:]} == {
        ("HS1", "CLB B", "CLB A", "Đổi CLB"), ("HS2", "CLB A", "CLB B", "Đổi CLB")}


def test_em_moi_va_mat_cho(hai_em):
    api = hai_em
    assert api.run_pipeline(42)["ok"]
    # Thêm em mới giành A bằng điểm cao nhất -> HS2 mất A (sang B).
    assert api.create_student_if_missing("HS3", "Em HS3")["ok"]
    assert api.submit_test_selection("HS3", ["A"])["ok"]
    assert api.submit_preferences("HS3", ["A"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "HS3", "score": 10}])["ok"]
    assert api.run_pipeline(42)["ok"]
    loai = {x["student_id"]: x["loai"] for x in api.get_thay_doi_ket_qua()["data"]["dong"]}
    assert loai == {"HS3": "hoc_sinh_moi", "HS2": "doi_clb"}


def test_chay_hong_giu_nguyen_ban_chup_cu(hai_em, monkeypatch):
    api = hai_em
    assert api.run_pipeline(42)["ok"]
    assert api.run_pipeline(42)["ok"]
    import api as mod
    def hong(*a, **k):
        raise RuntimeError("gia lap hong giua chung")
    monkeypatch.setattr(mod, "cac_dong_match_results", hong)
    assert api.submit_club_scores("A", [{"student_id": "HS1", "score": 10}])["ok"]
    assert not api.run_pipeline(42)["ok"]
    # Rollback: không có thay đổi nào được ghi nhận, bảng kết quả nguyên vẹn.
    assert api.get_thay_doi_ket_qua()["data"]["dong"] == []


def test_xoa_du_lieu_va_xoa_hoc_sinh_don_ban_chup(hai_em):
    api = hai_em
    assert api.run_pipeline(42)["ok"]
    assert api.run_pipeline(42)["ok"]
    conn = sqlite3.connect(api.db_path)
    assert conn.execute("SELECT COUNT(*) FROM ket_qua_truoc").fetchone()[0] == 2
    conn.close()
    assert api.reset_data("hoc_sinh", "XOA")["ok"]
    conn = sqlite3.connect(api.db_path)
    assert conn.execute("SELECT COUNT(*) FROM ket_qua_truoc").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM dau_van_tay_chay").fetchone()[0] == 0
    conn.close()


def test_xoa_hoc_sinh_bo_dong_cua_em_khoi_ban_chup(api):
    """`delete_student` bị chặn khi em còn trong kết quả, nên dòng chụp của
    một em xoá được chỉ tới từ CSDL cũ — vẫn phải dọn, nếu không tệp "thay
    đổi" liệt kê một em không còn tồn tại."""
    api.create_student_if_missing("HS9", "Nhầm")
    conn = sqlite3.connect(api.db_path)
    conn.execute("INSERT INTO ket_qua_truoc (student_id, buoi) VALUES ('HS9', 'x')")
    conn.commit()
    conn.close()
    assert api.delete_student("HS9")["ok"]
    conn = sqlite3.connect(api.db_path)
    assert conn.execute("SELECT COUNT(*) FROM ket_qua_truoc").fetchone()[0] == 0
    conn.close()


# ------------------------------------------------------------------ #
# Kết quả có thể đã cũ
# ------------------------------------------------------------------ #

def test_vua_chay_xong_la_khop(hai_em):
    assert hai_em.get_trang_thai_ket_qua()["data"]["co_ket_qua"] is False
    assert cu(hai_em) is False            # chưa có kết quả thì không "cũ"
    assert hai_em.run_pipeline(42)["ok"]
    assert cu(hai_em) is False


@pytest.mark.parametrize("sua", [
    lambda a: a.submit_club_scores("A", [{"student_id": "HS1", "score": 6}]),
    lambda a: a.submit_test_selection("HS1", []),
    lambda a: a.submit_preferences("HS1", ["B", "A"]),
    lambda a: a.create_or_update_club("A", "CLB A", 2, 0, ""),
    lambda a: a.set_student_reserve_group("HS1", "chinh_sach"),
    lambda a: a.create_student_if_missing("HS7", "Em mới"),
], ids=["diem", "tick", "nguyen_vong", "suc_chua", "nhom_du_tru", "hoc_sinh_moi"])
def test_moi_loai_sua_deu_bao_cu_va_chay_lai_thi_het(hai_em, sua):
    assert hai_em.run_pipeline(42)["ok"]
    assert sua(hai_em)["ok"]
    assert cu(hai_em) is True
    assert hai_em.run_pipeline(42)["ok"]
    assert cu(hai_em) is False


def test_doi_ten_khong_lam_ket_qua_cu(hai_em):
    assert hai_em.run_pipeline(42)["ok"]
    assert hai_em.create_or_update_club("A", "CLB A (tên mới)", 1, 0, "")["ok"]
    assert cu(hai_em) is False


def test_tong_hop_ghi_ro_ket_qua_con_khop_hay_khong(hai_em):
    api = hai_em
    assert api.run_pipeline(42)["ok"]

    def dong_khop():
        p = api.export_csv()["data"]["tong_hop_path"]
        return [r for r in doc(p) if r and r[0] == "Kết quả còn khớp dữ liệu"]

    assert dong_khop()[0][1] == "CÓ"
    assert api.submit_club_scores("A", [{"student_id": "HS1", "score": 6}])["ok"]
    assert dong_khop()[0][1].startswith("KHÔNG")


# ------------------------------------------------------------------ #
# Chạy riêng một số buổi
# ------------------------------------------------------------------ #

@pytest.fixture
def hai_buoi(api):
    api.create_or_update_club("A", "CLB A", 1, 0, "", "thu_2")
    api.create_or_update_club("C", "CLB C", 1, 0, "", "thu_4")
    for ma in ("HS1", "HS2"):
        api.create_student_if_missing(ma, ma)
        api.submit_test_selection(ma, ["A", "C"])
        api.submit_preferences(ma, ["A", "C"])
    api.submit_club_scores("A", [{"student_id": "HS1", "score": 5},
                                 {"student_id": "HS2", "score": 9}])
    api.submit_club_scores("C", [{"student_id": "HS1", "score": 5},
                                 {"student_id": "HS2", "score": 9}])
    assert api.run_pipeline(42)["ok"]
    return api


def test_chay_mot_buoi_sau_khi_sua_van_bao_cu(hai_buoi):
    api = hai_buoi
    # Sửa điểm thứ Tư, nhưng chỉ chạy lại thứ Hai -> thứ Tư vẫn là kết quả cũ.
    assert api.submit_club_scores("C", [{"student_id": "HS1", "score": 10}])["ok"]
    assert api.run_pipeline(42, chi_buoi=["thu_2"])["ok"]
    assert cu(api) is True
    assert api.run_pipeline(42)["ok"]
    assert cu(api) is False


def test_chay_mot_buoi_khong_sua_gi_van_khop(hai_buoi):
    assert hai_buoi.run_pipeline(42, chi_buoi=["thu_2"])["ok"]
    assert cu(hai_buoi) is False
