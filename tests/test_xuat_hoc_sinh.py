# -*- coding: utf-8 -*-
"""Xuất hồ sơ MỘT em hoặc NHIỀU em được chọn (`export_hoc_sinh_csv`).

Mỗi dòng một cặp (em, CLB) mà em đã tick thi, xếp nguyện vọng, hoặc được
xếp vào. Chọn em nào thì tệp phải có em đó — kể cả em chưa nhập gì.
"""

import csv
import os
import sqlite3

import pytest


def doc(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        r = list(csv.reader(f))
    return r[0], [dict(zip(r[0], d)) for d in r[1:]]


@pytest.fixture
def mot_buoi(api):
    api.create_or_update_club("A", "CLB A", 1, 0, "")
    api.create_or_update_club("B", "CLB B", 5, 0, "")
    api.create_or_update_club("C", "CLB C", 5, 0, "")
    for ma, ten in (("HS1", "Ngô Văn An"), ("HS2", "Lê Thị Bình"), ("HS3", "Chưa nhập")):
        api.create_student_if_missing(ma, ten)
    api.set_student_reserve_group("HS2", "chinh_sach")
    api.submit_test_selection("HS1", ["A", "C"])       # C: tick, không xếp
    api.submit_preferences("HS1", ["A", "B"])          # B: xếp, không tick
    api.submit_test_selection("HS2", ["A"])
    api.submit_preferences("HS2", ["A", "B"])
    api.submit_club_scores("A", [{"student_id": "HS1", "score": 9},
                                 {"student_id": "HS2", "score": 5}])
    assert api.run_pipeline(42)["ok"]
    return api


def test_mot_em_du_moi_cot_va_dung_tung_dong(mot_buoi):
    r = mot_buoi.export_hoc_sinh_csv(["HS1"])
    assert r["ok"], r["errors"]
    assert os.path.basename(r["data"]["path"]) == "hoc_sinh_HS1.csv"
    header, dong = doc(r["data"]["path"])
    assert header == ["Mã học sinh", "Họ tên", "Nhóm dự trữ", "Số bốc thăm",
                      "Mã CLB", "Tên CLB", "Đăng ký thi", "Điểm",
                      "Nguyện vọng thứ", "Kết quả", "Diện"]
    theo = {d["Mã CLB"]: d for d in dong}
    assert set(theo) == {"A", "B", "C"}
    assert (theo["A"]["Đăng ký thi"], theo["A"]["Điểm"], theo["A"]["Nguyện vọng thứ"],
            theo["A"]["Kết quả"], theo["A"]["Diện"]) == ("Có", "9", "1", "Được xếp", "Thường")
    assert (theo["B"]["Đăng ký thi"], theo["B"]["Nguyện vọng thứ"],
            theo["B"]["Kết quả"]) == ("—", "2", "—")
    assert (theo["C"]["Đăng ký thi"], theo["C"]["Điểm"],
            theo["C"]["Nguyện vọng thứ"]) == ("Có", "", "")
    # Số bốc thăm = số đã khoá của em.
    conn = sqlite3.connect(mot_buoi.db_path)
    stb = conn.execute("SELECT stb_number FROM students WHERE student_id='HS1'").fetchone()[0]
    conn.close()
    assert {d["Số bốc thăm"] for d in dong} == {str(stb)}


def test_nhieu_em_va_em_chua_nhap_gi_van_co_dong(mot_buoi):
    r = mot_buoi.export_hoc_sinh_csv(["HS2", "HS3", "HS2"])
    assert r["ok"]
    assert r["data"]["n_hoc_sinh"] == 2
    assert os.path.basename(r["data"]["path"]) == "hoc_sinh_da_chon_2_em.csv"
    _, dong = doc(r["data"]["path"])
    assert [d["Mã học sinh"] for d in dong] == ["HS2", "HS2", "HS3"]
    hs2 = {d["Mã CLB"]: d for d in dong if d["Mã học sinh"] == "HS2"}
    assert hs2["B"]["Kết quả"] == "Được xếp" and hs2["A"]["Kết quả"] == "—"
    assert hs2["A"]["Nhóm dự trữ"] == "chinh_sach"
    hs3 = [d for d in dong if d["Mã học sinh"] == "HS3"][0]
    assert hs3["Tên CLB"] == "(chưa nhập gì)"


def test_diem_khong_con_tick_khong_hien(mot_buoi):
    conn = sqlite3.connect(mot_buoi.db_path)
    conn.execute("DELETE FROM club_test_selection WHERE student_id='HS2'")
    conn.commit()
    conn.close()
    _, dong = doc(mot_buoi.export_hoc_sinh_csv(["HS2"])["data"]["path"])
    a = [d for d in dong if d["Mã CLB"] == "A"][0]
    assert (a["Đăng ký thi"], a["Điểm"]) == ("—", "")


def test_danh_sach_rong_va_ma_la_bi_tu_choi(mot_buoi):
    r = mot_buoi.export_hoc_sinh_csv([])
    assert not r["ok"] and r["errors"][0]["code"] == "chua_chon_hoc_sinh"
    r = mot_buoi.export_hoc_sinh_csv(["HS1", "KHONG_CO"])
    assert not r["ok"] and r["errors"][0]["code"] == "student_not_found"
    assert "KHONG_CO" in r["errors"][0]["params"]["student_id"]


def test_bao_ket_qua_cu(mot_buoi):
    assert mot_buoi.export_hoc_sinh_csv(["HS1"])["data"]["ket_qua_cu"] is False
    mot_buoi.submit_club_scores("A", [{"student_id": "HS2", "score": 10}])
    assert mot_buoi.export_hoc_sinh_csv(["HS1"])["data"]["ket_qua_cu"] is True


def test_nhieu_buoi_dung_so_boc_tham_tung_buoi(api):
    api.create_or_update_club("A", "CLB A", 5, 0, "", "thu_2")
    api.create_or_update_club("C", "CLB C", 5, 0, "", "thu_4")
    for i in range(1, 7):
        api.create_student_if_missing("HS%d" % i, "Em %d" % i)
        api.submit_preferences("HS%d" % i, ["C", "A"])
    assert api.run_pipeline(42)["ok"]
    header, dong = doc(api.export_hoc_sinh_csv(["HS3"])["data"]["path"])
    assert "Buổi" in header
    so = api.get_so_boc_tham_theo_buoi()["data"]["hoc_sinh"]
    ky_vong = [e["so"] for e in so if e["student_id"] == "HS3"][0]
    for d in dong:
        assert d["Số bốc thăm"] == str(ky_vong[d["Buổi"]])
    # Sắp theo buổi: thứ Hai trước thứ Tư, dù nguyện vọng xếp C trước.
    assert [d["Buổi"] for d in dong] == ["thu_2", "thu_4"]
    # Nguyện vọng thứ là thứ hạng TRONG BUỔI: C là nguyện vọng 1 của thứ Tư.
    assert {d["Mã CLB"]: d["Nguyện vọng thứ"] for d in dong} == {"A": "1", "C": "1"}
