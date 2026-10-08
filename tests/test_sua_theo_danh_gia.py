# -*- coding: utf-8 -*-
"""Ba lỗi do lần rà mã (/code-review) tìm ra — mỗi lỗi một test tái hiện.

1. Dấu vân tay "kết quả còn khớp dữ liệu" lấy ở bước GHI, không phải lúc
   ĐỌC dữ liệu để tính. Kiosk lưu giữa chừng lần chạy -> kết quả tính từ dữ
   liệu cũ nhưng đóng dấu dữ liệu mới -> báo "còn khớp" sai.
2. `mo_thu_muc`: `os.path.commonpath` ném ValueError khi hai đường dẫn khác
   ổ đĩa (Windows) -> hỏng cả phép so, không thử gốc hợp lệ tiếp theo.
3. (trình duyệt, xem test_giao_dien_ux_xuat.py) tập học sinh đã chọn ở thẻ
   02 giữ em đã bị xoá -> xuất hồ sơ hỏng cả lô.
"""

import os
import sys

import pytest

import api as mod


# ------------------------------------------------------------------ #
# 1. Dấu vân tay phải khớp ĐÚNG dữ liệu lần chạy đã đọc
# ------------------------------------------------------------------ #

@pytest.fixture
def hai_em(api):
    api.create_or_update_club("A", "CLB A", 1, 0, "")
    api.create_or_update_club("B", "CLB B", 5, 0, "")
    for ma in ("HS1", "HS2"):
        api.create_student_if_missing(ma, ma)
        api.submit_test_selection(ma, ["A"])
        api.submit_preferences(ma, ["A", "B"])
    api.submit_club_scores("A", [{"student_id": "HS1", "score": 5},
                                 {"student_id": "HS2", "score": 9}])
    return api


def _chen_kiosk_luu_giua_chung(monkeypatch, api, hanh_dong):
    """Chạy `hanh_dong` (một lần lưu từ kiosk, qua kết nối KHÁC) ngay SAU khi
    lần chạy đã đọc xong dữ liệu — đúng khoảng hở mà lỗi 1 lọt qua."""
    goc = mod.validate_data_integrity
    da_chay = []

    def xen(*a, **k):
        if not da_chay:
            da_chay.append(1)
            khac = mod.PipelineAPI(api.db_path)
            assert hanh_dong(khac)["ok"]
        return goc(*a, **k)

    monkeypatch.setattr(mod, "validate_data_integrity", xen)
    return da_chay


def test_luu_giua_luc_dang_chay_thi_ket_qua_bao_cu(hai_em, monkeypatch):
    api = hai_em
    da_chay = _chen_kiosk_luu_giua_chung(
        monkeypatch, api,
        lambda k: k.submit_club_scores("A", [{"student_id": "HS1", "score": 10}]))
    assert api.run_pipeline(42)["ok"]
    assert da_chay, "khong chen duoc lan luu giua chung — test khong do gi"
    # Kết quả tính từ điểm cũ (HS2 9 > HS1 5 -> HS2 vào A)...
    kq = {r["student_id"]: r["club_id"] for r in api.get_match_results("")["data"]}
    assert kq["HS2"] == "A"
    # ...nên với điểm hiện tại (HS1 10) kết quả ĐÃ CŨ, và phải nói ra.
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is True


def test_khong_ai_luu_giua_chung_thi_van_khop(hai_em):
    assert hai_em.run_pipeline(42)["ok"]
    assert hai_em.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is False


def test_chay_mot_phan_so_voi_du_lieu_luc_doc(api, monkeypatch):
    """Chạy một buổi: quyết định có ghi dấu vân tay hay không cũng phải dựa
    trên dữ liệu LÚC ĐỌC, không phải lúc ghi."""
    api.create_or_update_club("A", "CLB A", 1, 0, "", "thu_2")
    api.create_or_update_club("C", "CLB C", 1, 0, "", "thu_4")
    for ma in ("HS1", "HS2"):
        api.create_student_if_missing(ma, ma)
        api.submit_preferences(ma, ["A", "C"])
    assert api.run_pipeline(42)["ok"]
    _chen_kiosk_luu_giua_chung(
        monkeypatch, api, lambda k: k.submit_preferences("HS1", ["C", "A"]))
    assert api.run_pipeline(42, chi_buoi=["thu_2"])["ok"]
    assert api.get_trang_thai_ket_qua()["data"]["ket_qua_cu"] is True


# ------------------------------------------------------------------ #
# 2. Mở thư mục khi hai gốc hợp lệ nằm khác ổ đĩa
# ------------------------------------------------------------------ #

def test_goc_khac_o_dia_khong_lam_hong_phep_so(api, monkeypatch):
    """Giả lập Windows: gốc Tải xuống ở C:, tệp xuất ở cạnh app.db trên D:.
    `commonpath` với gốc C: ném ValueError; gốc D: phải vẫn được thử."""
    goi = []
    if sys.platform == "win32":
        monkeypatch.setattr(os, "startfile", lambda p: goi.append(p), raising=False)
    else:
        import subprocess

        class Gia:
            def __init__(self, lenh, **kw):
                goi.append(lenh[-1])
        monkeypatch.setattr(subprocess, "Popen", Gia)

    goc_db = os.path.realpath(os.path.dirname(os.path.abspath(api.db_path)))
    o_c = os.path.realpath(os.environ["RBDA_THU_MUC_TAI_VE"])
    monkeypatch.setattr(api, "_goc_xuat_hop_le", lambda: [o_c, goc_db])

    that = os.path.commonpath

    def khac_o(ds):
        if o_c in ds and any(p != o_c and not p.startswith(o_c) for p in ds):
            raise ValueError("Paths don't have the same drive")
        return that(ds)
    monkeypatch.setattr(os.path, "commonpath", khac_o)

    r = api.mo_thu_muc(api.db_path)       # tệp nằm ở gốc D: (cạnh app.db)
    assert r["ok"], r["errors"]
    assert goi == [goc_db]


def test_luu_tu_kiosk_trong_luc_doc_thi_cho_roi_thanh_cong(hai_em):
    """Lần đọc nhất quán giữ khoá đọc. Một lần lưu từ kiosk chen vào lúc đó
    phải CHỜ rồi thành công (busy_timeout) — không được báo lỗi "database is
    locked", và dữ liệu đã đọc không được thấy lần lưu đó."""
    import threading
    import time

    import rbda_priority_pipeline as rp

    api = hai_em
    conn = rp._mo_doc_nhat_quan(api.db_path)
    du_lieu = rp._doc_du_lieu(conn.cursor())          # đang giữ khoá đọc
    ket_qua = {}

    def luu():
        khac = mod.PipelineAPI(api.db_path)
        ket_qua["res"] = khac.submit_club_scores(
            "A", [{"student_id": "HS1", "score": 10}])
        ket_qua["luc"] = time.monotonic()

    t = threading.Thread(target=luu)
    t.start()
    time.sleep(0.5)
    assert "res" not in ket_qua, "ben ghi khong cho — lan doc khong nhat quan"
    dvt = rp.dau_van_tay_du_lieu(conn.cursor())       # vẫn là dữ liệu cũ
    nha = time.monotonic()
    conn.rollback()
    conn.close()
    t.join(10)

    assert ket_qua["res"]["ok"] and ket_qua["res"]["data"]["n_saved"] == 1
    assert ket_qua["luc"] >= nha
    assert du_lieu[2]["A"]["HS1"] == 5.0
    assert api.get_trang_thai_ket_qua()["ok"]
    # Dấu vân tay lúc đọc khác dấu vân tay sau khi lưu.
    c2 = rp._mo_doc_nhat_quan(api.db_path)
    try:
        assert rp.dau_van_tay_du_lieu(c2.cursor()) != dvt
    finally:
        c2.rollback()
        c2.close()
