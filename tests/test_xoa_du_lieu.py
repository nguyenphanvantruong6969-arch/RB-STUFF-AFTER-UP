# -*- coding: utf-8 -*-
"""Canh `reset_data()` — hàm xoá sạch dữ liệu để chạy thử lại từ đầu.

Đây là hàm nguy hiểm nhất trong `api.py`: gọi một phát là mất toàn bộ
học sinh. Nên phần lớn test ở đây không kiểm tra "xoá có chạy không" mà
kiểm tra **những trường hợp KHÔNG được xoá** — và kiểm tra rằng lúc đó
dữ liệu còn nguyên vẹn, chứ không phải chỉ trả về `ok=False` sau khi đã
xoá xong.
"""

import os
import sqlite3

import pytest


@pytest.fixture
def api_co_du_lieu(api):
    """Hai CLB, ba học sinh, có nguyện vọng, điểm và một lần chạy."""
    api.create_or_update_club("clb_a", "CLB A", 2, 1, "chinh_sach")
    api.create_or_update_club("clb_b", "CLB B", 2, 0, "")
    for sid, ten, nhom in [("HS01", "Nguyễn Văn A", "chinh_sach"),
                           ("HS02", "Trần Thị B", ""),
                           ("HS03", "Lê Văn C", "")]:
        api.create_student_if_missing(sid, ten)
        api.set_student_reserve_group(sid, nhom)
        api.submit_test_selection(sid, ["clb_a", "clb_b"])
        api.submit_preferences(sid, ["clb_a", "clb_b"])
        api.submit_club_scores("clb_a", [{"student_id": sid, "score": 8.0}])
        api.submit_club_scores("clb_b", [{"student_id": sid, "score": 7.0}])
    assert api.run_pipeline(seed=42)["ok"]
    return api


def _dem(api, bang):
    conn = sqlite3.connect(api.db_path)
    n = conn.execute("SELECT COUNT(*) FROM %s" % bang).fetchone()[0]
    conn.close()
    return n


# ------------------------------------------------------------------ #
# Những lần gọi KHÔNG được xoá gì
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("xac_nhan", ["", "xoa", "XOA ", "Xoa", "DELETE", "có"])
def test_xac_nhan_sai_thi_khong_xoa_gi(api_co_du_lieu, xac_nhan):
    """Xác nhận sai -> từ chối, và dữ liệu PHẢI còn nguyên.

    Test này quan trọng hơn mọi test còn lại: một hàm kiểm tra xác nhận
    SAU khi đã xoá vẫn trả về ok=False y hệt, mà dữ liệu thì mất rồi.
    """
    truoc = _dem(api_co_du_lieu, "students")
    res = api_co_du_lieu.reset_data("hoc_sinh", xac_nhan)
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "reset_confirmation_mismatch"
    assert _dem(api_co_du_lieu, "students") == truoc


def test_pham_vi_la_thi_khong_xoa_gi(api_co_du_lieu):
    truoc = _dem(api_co_du_lieu, "students")
    res = api_co_du_lieu.reset_data("xoa_het_di", "XOA")
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "reset_scope_unknown"
    assert _dem(api_co_du_lieu, "students") == truoc


def test_xac_nhan_sai_khong_de_lai_tep_sao_luu_rac(api_co_du_lieu):
    """Kiểm tra xác nhận phải chạy TRƯỚC khi sao lưu.

    Sao lưu trước rồi mới kiểm tra thì mỗi lần bấm nhầm lại đẻ ra một
    tệp .bak trong thư mục người dùng.
    """
    thu_muc = os.path.dirname(api_co_du_lieu.db_path)
    truoc = {f for f in os.listdir(thu_muc) if ".bak-" in f}
    api_co_du_lieu.reset_data("hoc_sinh", "sai")
    api_co_du_lieu.reset_data("khong_co", "XOA")
    assert {f for f in os.listdir(thu_muc) if ".bak-" in f} == truoc


# ------------------------------------------------------------------ #
# Xoá thật
# ------------------------------------------------------------------ #

def test_xoa_hoc_sinh_giu_nguyen_club(api_co_du_lieu):
    res = api_co_du_lieu.reset_data("hoc_sinh", "XOA")
    assert res["ok"], res
    assert res["data"]["n_students"] == 3
    assert res["data"]["n_clubs_con_lai"] == 2

    for bang in ("students", "preferences", "club_test_selection",
                 "club_scores", "match_results", "run_meta"):
        assert _dem(api_co_du_lieu, bang) == 0, bang
    assert _dem(api_co_du_lieu, "clubs") == 2


def test_xoa_tat_ca_thi_club_cung_di(api_co_du_lieu):
    res = api_co_du_lieu.reset_data("tat_ca", "XOA")
    assert res["ok"], res
    assert res["data"]["n_students"] == 3
    assert res["data"]["n_clubs"] == 2
    assert res["data"]["n_clubs_con_lai"] == 0
    assert _dem(api_co_du_lieu, "clubs") == 0


@pytest.mark.parametrize("pham_vi", ["hoc_sinh", "tat_ca"])
def test_nhat_ky_chay_khong_bao_gio_bi_xoa(api_co_du_lieu, pham_vi):
    """run_history là nhật ký kiểm toán — lược đồ ghi rõ không bao giờ
    xoá. Xoá dữ liệu không được phép xoá dấu vết đã từng chạy những gì."""
    truoc = _dem(api_co_du_lieu, "run_history")
    assert truoc > 0
    assert api_co_du_lieu.reset_data(pham_vi, "XOA")["ok"]
    assert _dem(api_co_du_lieu, "run_history") == truoc
    assert api_co_du_lieu.reset_data(pham_vi, "XOA")["data"]["giu_lai_run_history"] is True


def test_co_sao_luu_va_sao_luu_con_du_lieu_cu(api_co_du_lieu):
    """Không chỉ kiểm tra tệp tồn tại — mở ra đếm xem có thật dữ liệu."""
    res = api_co_du_lieu.reset_data("tat_ca", "XOA")
    duong_dan = res["data"]["backup_path"]
    assert os.path.exists(duong_dan)
    assert res["data"]["backup_name"] == os.path.basename(duong_dan)

    conn = sqlite3.connect(duong_dan)
    assert conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 3
    assert conn.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 2
    conn.close()
    # ...trong khi CSDL thật đã trống.
    assert _dem(api_co_du_lieu, "students") == 0


def test_mo_khoa_stb_sau_khi_xoa(api_co_du_lieu):
    """Chạy pipeline xong là STB bị khoá. Không mở khoá lúc xoá thì lần
    chạy sau ghi nhật ký là 'tái sử dụng STB' cho một bộ số bốc thăm
    không còn tồn tại — sai cho phần kiểm toán."""
    assert api_co_du_lieu.get_stb_lock_status()["data"]["is_locked"] is True
    assert api_co_du_lieu.reset_data("hoc_sinh", "XOA")["ok"]
    assert api_co_du_lieu.get_stb_lock_status()["data"]["is_locked"] is False


def test_xoa_xong_van_dung_duoc_ngay(api_co_du_lieu):
    """Sau khi xoá, tạo lại dữ liệu và chạy pipeline phải trót lọt —
    không còn khoá, không còn ràng buộc mồ côi nào sót lại."""
    assert api_co_du_lieu.reset_data("hoc_sinh", "XOA")["ok"]
    api_co_du_lieu.create_student_if_missing("HS90", "Phạm Văn Mới")
    api_co_du_lieu.submit_test_selection("HS90", ["clb_a"])
    api_co_du_lieu.submit_preferences("HS90", ["clb_a"])
    api_co_du_lieu.submit_club_scores("clb_a", [{"student_id": "HS90", "score": 9.0}])
    res = api_co_du_lieu.run_pipeline(seed=42)
    assert res["ok"], res
    assert res["data"]["n_total"] == 1
    assert res["data"]["n_matched"] == 1
    # STB duoc ve lai chu khong "bo sung" tiep noi bo cu.
    assert res["data"]["stb_redrawn"] is True
