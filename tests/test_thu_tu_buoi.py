"""Chủ nhật phải đứng SAU thứ Bảy — ở mọi nơi phần mềm liệt kê buổi.

Lỗi thật (27/09, ảnh chụp của người dùng): bảng "Danh sách xếp CLB" ghi
chu_nhat trước thu_2, và CLB sinh hoạt Chủ nhật đứng đầu bảng lấp đầy. Thuật
toán (sap_buoi) vẫn đúng; lỗi nằm ở các câu SQL `ORDER BY buoi` — SQLite sắp
theo vần chữ cái, nên "chu_nhat" (c) < "thu_2" (t).
"""

import csv

import pytest

import rbda_priority_pipeline as rp

BUOI = ["chu_nhat", "thu_7", "thu_2", "thu_4"]          # cố ý không theo thứ tự
DUNG = ["thu_2", "thu_4", "thu_7", "chu_nhat"]


@pytest.fixture
def api_bon_buoi(api):
    for b in BUOI:
        api.create_or_update_club("clb_" + b, "CLB " + b, 5, 0, "", b)
    for i in range(1, 4):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Em " + sid)
        assert api.submit_preferences(sid, ["clb_" + b for b in BUOI])["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    return api


def _thu_tu_xuat_hien(ds):
    ra = []
    for b in ds:
        if b not in ra:
            ra.append(b)
    return ra


def test_ket_noi_nao_cung_co_quy_tac_thu_tu_buoi(tmp_path):
    conn = rp.connect_db(str(tmp_path / "x.db"))
    try:
        dong = conn.execute(
            "SELECT b FROM (SELECT 'chu_nhat' b UNION SELECT 'thu_2' UNION SELECT 'thu_7')"
            " ORDER BY b COLLATE THU_TU_BUOI").fetchall()
    finally:
        conn.close()
    assert [r[0] for r in dong] == ["thu_2", "thu_7", "chu_nhat"]


def test_danh_sach_xep_clb_chu_nhat_sau_thu_bay(api_bon_buoi):
    dong = api_bon_buoi.get_match_results("")["data"]
    mot_em = [r["buoi"] for r in dong if r["student_id"] == "HS01"]
    assert mot_em == DUNG


def test_bang_lap_day_chu_nhat_sau_thu_bay(api_bon_buoi):
    ds = [c["buoi"] for c in api_bon_buoi.get_club_fill_stats()["data"]]
    assert _thu_tu_xuat_hien(ds) == DUNG


def test_danh_sach_clb_quan_ly_chu_nhat_sau_thu_bay(api_bon_buoi):
    ds = [c["buoi"] for c in api_bon_buoi.list_clubs_admin()["data"]]
    assert _thu_tu_xuat_hien(ds) == DUNG


def test_tai_theo_buoi_chu_nhat_sau_thu_bay(api_bon_buoi):
    ds = [r["buoi"] for r in api_bon_buoi.get_tai_theo_buoi()["data"]]
    assert ds == DUNG


def test_tep_xuat_chu_nhat_sau_thu_bay(api_bon_buoi, tmp_path):
    d = api_bon_buoi.export_csv(str(tmp_path / "kq.csv"))["data"]
    with open(d["path"], encoding="utf-8-sig", newline="") as f:
        dong = list(csv.reader(f))
    cot = dong[0].index("Buổi")
    mot_em = [r[cot] for r in dong[1:] if r[0] == "HS01"]
    assert mot_em == DUNG


def test_tep_match_results_chu_nhat_sau_thu_bay(api_bon_buoi):
    import os
    duong = os.path.join(os.path.dirname(api_bon_buoi.db_path), "match_results.csv")
    with open(duong, encoding="utf-8", newline="") as f:
        dong = list(csv.reader(f))
    mot_em = [r[1] for r in dong[1:] if r[0] == "HS01"]
    assert mot_em == DUNG


def test_khong_cau_sql_nao_sap_buoi_thieu_collate():
    """Chốt: không còn câu SQL nào sắp buổi mà thiếu COLLATE."""
    import glob
    import os
    import re

    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    thieu = []
    for p in glob.glob(os.path.join(goc, "api*.py")):
        for i, dong in enumerate(open(p, encoding="utf-8"), 1):
            m = re.search(r"[\"'].*ORDER BY(.*)", dong)   # chỉ câu SQL trong chuỗi
            if m and re.search(r"\bbuoi\b", m.group(1)) and "THU_TU_BUOI" not in m.group(1):
                thieu.append("%s:%d" % (os.path.basename(p), i))
    assert thieu == [], thieu
