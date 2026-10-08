"""Các hàm chưa có test nào trước đợt rà soát 26/09.

  - get_pipeline_run_warning: giao diện gọi trước MỖI lần bấm "Chạy".
  - init_db / write_match_results_to_sqlite: đường ghi CSDL dùng chung.
  - main.py: 0% độ phủ — trong khi đây là nơi quyết định app mở cửa sổ gốc,
    chế độ trình duyệt, hay màn hình phục hồi.
"""

import os
import sqlite3
import sys
import types

import pytest

import rbda_priority_pipeline as rp


# ------------------------------------------------------------------ #
# get_pipeline_run_warning
# ------------------------------------------------------------------ #


def test_canh_bao_truoc_khi_chay_luc_chua_chay_lan_nao(api):
    d = api.get_pipeline_run_warning()["data"]
    assert d["has_existing_results"] is False
    assert d["stb_locked"] is False
    assert d["last_run_at"] is None


def test_canh_bao_truoc_khi_chay_sau_mot_lan_chay(api):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nhs1,An,A\n")
    api.run_pipeline(seed=7)
    d = api.get_pipeline_run_warning()["data"]
    assert d["has_existing_results"] is True
    assert d["stb_locked"] is True
    assert d["last_run_seed"] == 7
    assert d["last_run_at"]


# ------------------------------------------------------------------ #
# init_db / write_match_results_to_sqlite
# ------------------------------------------------------------------ #


def test_init_db_chay_lai_khong_mat_du_lieu(tmp_path):
    db = str(tmp_path / "app.db")
    rp.init_db(db)
    with sqlite3.connect(db) as c:
        c.execute("INSERT INTO clubs (club_id, name, capacity, reserve_capacity) VALUES ('A','A',5,0)")
    rp.init_db(db)
    with sqlite3.connect(db) as c:
        assert c.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 1


def test_ghi_ket_qua_vao_sqlite_ghi_de_ket_qua_cu(tmp_path):
    db = str(tmp_path / "app.db")
    rp.init_db(db)
    # Khoá ngoại: match_results chỉ nhận học sinh và CLB đã có trong CSDL.
    with sqlite3.connect(db) as c:
        c.execute("INSERT INTO clubs (club_id, name, capacity, reserve_capacity) VALUES ('A','A',5,0)")
        c.executemany("INSERT INTO students (student_id, name) VALUES (?, ?)",
                      [("hs1", "HS 1"), ("hs2", "HS 2")])
    kq = rp.MatchResult(assignment={"hs1": "A", "hs2": None}, rounds_run=1,
                        matched_tier={"hs1": "general"},
                        rank_in_student_pref={"hs1": 1})
    rp.write_match_results_to_sqlite(db, kq)
    rp.write_match_results_to_sqlite(db, kq)
    with sqlite3.connect(db) as c:
        dong = c.execute("SELECT student_id, club_id FROM match_results ORDER BY student_id").fetchall()
    assert dong == [("hs1", "A"), ("hs2", None)]


# ------------------------------------------------------------------ #
# main.py
# ------------------------------------------------------------------ #


@pytest.fixture
def main_mod(monkeypatch, tmp_path):
    import main

    monkeypatch.setattr(main, "BASE_DIR", str(tmp_path))
    goi = {"serve": []}
    monkeypatch.setattr(main.browser_host, "serve",
                        lambda *a, **k: goi["serve"].append((a, k)))
    return main, goi


def _webview_gia(monkeypatch, hong_o="create"):
    """Dựng một mô-đun `webview` giả, hỏng ở bước chỉ định."""
    wv = types.ModuleType("webview")

    def create_window(*a, **k):
        if hong_o == "create":
            raise RuntimeError("Failed to resolve Python.Runtime.Loader.Initialize")
        return object()

    def start():
        if hong_o == "ctrl_c":
            raise KeyboardInterrupt
        if hong_o == "start":
            raise RuntimeError("khong co GUI")

    wv.create_window = create_window
    wv.start = start
    monkeypatch.setitem(sys.modules, "webview", wv)


def test_pywebview_hong_thi_chuyen_sang_trinh_duyet(main_mod, monkeypatch):
    main, goi = main_mod
    _webview_gia(monkeypatch, "create")
    main._show_ui("T", "index.html", object(), 800, 600, (1, 1))
    assert len(goi["serve"]) == 1
    # và ghi lý do vào tệp log để lần sau khỏi phải đoán
    with open(os.path.join(main.BASE_DIR, "loi_khoi_dong.txt"), encoding="utf-8") as f:
        assert "Python.Runtime.Loader" in f.read()


def test_pywebview_chay_duoc_thi_khong_mo_trinh_duyet(main_mod, monkeypatch):
    main, goi = main_mod
    _webview_gia(monkeypatch, "khong")
    main._show_ui("T", "index.html", object(), 800, 600, (1, 1))
    assert goi["serve"] == []


def test_ctrl_c_la_tat_chu_khong_mo_trinh_duyet(main_mod, monkeypatch):
    main, goi = main_mod
    _webview_gia(monkeypatch, "ctrl_c")
    with pytest.raises(KeyboardInterrupt):
        main._show_ui("T", "index.html", object(), 800, 600, (1, 1))
    assert goi["serve"] == []


def test_ban_dong_goi_khong_co_stderr_van_chuyen_duoc_sang_trinh_duyet(main_mod, monkeypatch):
    """PyInstaller console=False đặt sys.stderr = None. Ghi vào đó từng nổ
    ngay trong khối except và chặn luôn đường dự phòng."""
    main, goi = main_mod
    _webview_gia(monkeypatch, "start")
    monkeypatch.setattr(sys, "stderr", None)
    main._show_ui("T", "index.html", object(), 800, 600, (1, 1))
    assert len(goi["serve"]) == 1


def test_csdl_hong_thi_mo_man_hinh_phuc_hoi(main_mod, monkeypatch, tmp_path):
    main, _ = main_mod
    db = tmp_path / "app.db"
    db.write_bytes(b"day khong phai sqlite")
    monkeypatch.setattr(sys, "argv", ["main.py", str(db)])
    mo = []
    monkeypatch.setattr(main, "_show_ui", lambda title, page, api, **k: mo.append((page, api)))
    main.main()
    assert mo[0][0] == "recovery.html"
    assert type(mo[0][1]).__name__ == "RecoveryAPI"


def test_csdl_tot_thi_mo_man_hinh_chinh(main_mod, monkeypatch, tmp_path):
    main, _ = main_mod
    monkeypatch.setattr(sys, "argv", ["main.py", str(tmp_path / "moi.db")])
    mo = []
    monkeypatch.setattr(main, "_show_ui", lambda title, page, api, **k: mo.append(page))
    main.main()
    assert mo == ["index.html"]


def test_duong_dan_csdl_mac_dinh_nam_canh_chuong_trinh(main_mod, monkeypatch):
    main, _ = main_mod
    monkeypatch.setattr(sys, "argv", ["main.py"])
    assert main.resolve_db_path() == os.path.join(main.BASE_DIR, "app.db")
