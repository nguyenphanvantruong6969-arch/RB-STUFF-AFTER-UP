# -*- coding: utf-8 -*-
"""Ràng buộc ở tầng CSDL: FOREIGN KEY và CHECK trên năm bảng.

Trước đây lược đồ không có ràng buộc nào — mọi luật nằm ở mã Python, và
cửa nào quên kiểm là dữ liệu hỏng lọt vào im lặng. Tệp này canh ba điều:

1. CSDL MỚI tự từ chối dữ liệu hỏng, dù nó đến từ cửa nào.
2. CSDL CŨ SẠCH được nâng lên, có sao lưu trước, KHÔNG mất một dòng nào và
   kết quả xếp CLB y nguyên.
3. CSDL CŨ BẨN thì KHÔNG bị đụng vào: phần mềm vẫn mở, vẫn chạy như trước,
   và bảng sức khoẻ dữ liệu chỉ ra dòng nào cần sửa. Nâng cấp hỏng giữa
   chừng thì CSDL y nguyên.
"""

import glob
import io
import os
import shutil
import sqlite3

import pytest

import rbda_priority_pipeline as loi
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANG = ["students", "clubs", "club_test_selection", "club_scores",
        "preferences", "match_results", "run_meta", "run_history", "stb_lock"]

# Lược đồ của năm bảng TRƯỚC khi có ràng buộc — đúng như bản đã phát hành.
LUOC_DO_CU = {
    "clubs": """club_id TEXT PRIMARY KEY, name TEXT,
        capacity INTEGER NOT NULL, reserve_capacity INTEGER NOT NULL DEFAULT 0,
        reserve_group TEXT, buoi TEXT""",
    "club_test_selection": """student_id TEXT NOT NULL, club_id TEXT NOT NULL,
        PRIMARY KEY (student_id, club_id)""",
    "club_scores": """student_id TEXT NOT NULL, club_id TEXT NOT NULL,
        score REAL NOT NULL, PRIMARY KEY (student_id, club_id)""",
    "preferences": """student_id TEXT NOT NULL, club_id TEXT NOT NULL,
        rank INTEGER NOT NULL, PRIMARY KEY (student_id, club_id)""",
    "match_results": """student_id TEXT NOT NULL, buoi TEXT NOT NULL,
        club_id TEXT, round_num INTEGER, matched_tier TEXT,
        rank_in_student_pref INTEGER, PRIMARY KEY (student_id, buoi)""",
}


def _ma(bao_cao):
    return [w["code"] for w in bao_cao["data"]["warnings"]]


def _dem(db):
    conn = sqlite3.connect(db)
    try:
        return {b: conn.execute("SELECT COUNT(*) FROM %s" % b).fetchone()[0]
                for b in BANG}
    finally:
        conn.close()


def _co_khoa_ngoai(db):
    conn = sqlite3.connect(db)
    try:
        return bool(conn.execute("PRAGMA foreign_key_list(preferences)").fetchall())
    finally:
        conn.close()


def _ha_cap(db):
    """Biến một CSDL mới thành CSDL kiểu cũ: dựng lại năm bảng KHÔNG ràng buộc."""
    conn = sqlite3.connect(db, isolation_level=None)
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")
        for ten, than in LUOC_DO_CU.items():
            conn.execute("CREATE TABLE %s__cu (%s)" % (ten, than))
            conn.execute("INSERT INTO %s__cu SELECT * FROM %s" % (ten, ten))
            conn.execute("DROP TABLE %s" % ten)
            conn.execute("ALTER TABLE %s__cu RENAME TO %s" % (ten, ten))
        conn.execute("COMMIT")
    finally:
        conn.close()


def _nap_nhieu_buoi(api):
    for i, ten in enumerate(
            ["danh_sach_CLB", "chon_CLB_muon_thi", "xep_hang_nguyen_vong"], start=1):
        with io.open(os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi",
                                  "NHIEUBUOI_0%d_%s.csv" % (i, ten)),
                     encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]


def _ket_qua(db):
    conn = sqlite3.connect(db)
    try:
        return conn.execute(
            "SELECT * FROM match_results ORDER BY student_id, buoi").fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 1. CSDL mới tự từ chối dữ liệu hỏng
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sql", [
    "INSERT INTO preferences VALUES ('KHONG_CO', 'A', 1)",
    "INSERT INTO preferences VALUES ('s1', 'KHONG_CO', 1)",
    "INSERT INTO club_test_selection VALUES ('KHONG_CO', 'A')",
    "INSERT INTO club_scores VALUES ('s1', 'KHONG_CO', 5)",
    "INSERT INTO match_results VALUES ('KHONG_CO', 'b', NULL, 1, NULL, NULL)",
    "INSERT INTO match_results VALUES ('s1', 'b', 'KHONG_CO', 1, 'general', 1)",
    "INSERT INTO preferences VALUES ('s1', 'A', 0)",
    "INSERT INTO club_scores VALUES ('s1', 'A', -1)",
    "UPDATE clubs SET capacity = 0",
    "UPDATE clubs SET reserve_capacity = -1",
    "UPDATE clubs SET reserve_capacity = 6",
    "DELETE FROM students",
    "DELETE FROM clubs",
], ids=["nv_mo_coi_hs", "nv_mo_coi_clb", "thi_mo_coi", "diem_mo_coi",
        "kq_mo_coi_hs", "kq_mo_coi_clb", "hang_0", "diem_am", "suc_chua_0",
        "du_tru_am", "du_tru_qua_suc_chua", "xoa_hs_con_du_lieu",
        "xoa_clb_con_du_lieu"])
def test_csdl_moi_tu_choi_du_lieu_hong(api, sql):
    assert api.create_or_update_club("A", "A", 5, 0, "")["ok"]
    assert api.create_student_if_missing("s1", "S")["ok"]
    assert api.submit_test_selection("s1", ["A"])["ok"]
    assert api.submit_preferences("s1", ["A"])["ok"]
    conn = loi.connect_db(api.db_path)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(sql)
    finally:
        conn.close()


def test_du_lieu_hop_le_van_ghi_binh_thuong(api):
    assert api.create_or_update_club("A", "A", 5, 5, "g")["ok"]
    assert api.create_student_if_missing("s1", "S")["ok"]
    assert api.submit_test_selection("s1", ["A"])["ok"]
    assert api.submit_preferences("s1", ["A"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "s1", "score": 0}])["ok"]
    assert api.run_pipeline(seed=1)["ok"]


def test_du_tru_am_bi_tu_choi_bang_loi_de_hieu(api):
    kq = api.create_or_update_club("A", "A", 5, -1, "")
    assert not kq["ok"]
    assert kq["errors"][0]["code"] == "reserve_capacity_negative"


def test_nap_csv_clb_du_tru_am_thi_bo_dong_do(api):
    kq = api.import_clubs_csv(
        "club_id,name,capacity,reserve_capacity\nA,A,5,-1\nB,B,5,0\n")
    assert kq["ok"]
    assert [c["club_id"] for c in api.list_clubs()["data"]] == ["B"]


def test_xoa_clb_con_dang_ky_thi_va_diem_van_xoa_duoc(api):
    """Xoá CLB phải xoá bảng con TRƯỚC — ngược lại khoá ngoại chặn — và
    một lần xoá hỏng không được để lại kết nối giữ khoá ghi."""
    assert api.create_or_update_club("A", "A", 5, 0, "")["ok"]
    assert api.create_student_if_missing("s1", "S")["ok"]
    assert api.submit_test_selection("s1", ["A"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "s1", "score": 7}])["ok"]
    assert api.delete_club("A")["ok"]
    assert api.create_or_update_club("B", "B", 5, 0, "")["ok"]


def test_xoa_hoc_sinh_va_xoa_du_lieu_van_chay(api):
    _nap_nhieu_buoi(api)
    sid = api.list_students_admin()["data"]["rows"][0]["student_id"]
    assert api.delete_student(sid)["ok"]
    assert api.run_pipeline(seed=42)["ok"]
    assert api.reset_data("hoc_sinh", "XOA")["ok"]
    assert api.reset_data("tat_ca", "XOA")["ok"]


# ---------------------------------------------------------------------------
# 2. CSDL cũ sạch: được nâng lên, không mất gì
# ---------------------------------------------------------------------------

def test_csdl_cu_sach_duoc_nang_len_khong_mat_dong_nao(api):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    _ha_cap(api.db_path)
    assert not _co_khoa_ngoai(api.db_path)
    truoc_dem, truoc_kq = _dem(api.db_path), _ket_qua(api.db_path)
    so_bak = len(glob.glob(api.db_path + ".bak-*"))

    mo_lai = PipelineAPI(api.db_path)

    assert _co_khoa_ngoai(api.db_path)
    assert _dem(api.db_path) == truoc_dem
    assert _ket_qua(api.db_path) == truoc_kq
    assert len(glob.glob(api.db_path + ".bak-*")) == so_bak + 1, \
        "phải sao lưu trước khi dựng lại bảng"
    # Chạy lại được, ra đúng kết quả cũ.
    assert mo_lai.run_pipeline(seed=42)["ok"]
    assert _ket_qua(api.db_path) == truoc_kq


def test_nang_cap_chay_lai_khong_lam_gi(api):
    _nap_nhieu_buoi(api)
    _ha_cap(api.db_path)
    PipelineAPI(api.db_path)
    so_bak = len(glob.glob(api.db_path + ".bak-*"))
    assert loi.di_tru_schema(api.db_path) == []
    assert len(glob.glob(api.db_path + ".bak-*")) == so_bak


def test_csdl_demo_that_duoc_nang_len(tmp_path):
    ban = str(tmp_path / "app.db")
    shutil.copy(os.path.join(GOC, "du_lieu_test", "app_DEMO_da_cham_diem.db"), ban)
    truoc = _dem(ban)
    api = PipelineAPI(ban)
    assert _co_khoa_ngoai(ban)
    sau = _dem(ban)
    # stb_lock/run_meta có thể được init_db thêm dòng mặc định; năm bảng
    # dữ liệu thì phải y nguyên.
    for b in ["students", "clubs", "club_test_selection", "club_scores",
              "preferences", "match_results", "run_history"]:
        assert sau[b] == truoc[b], b
    assert not api.get_data_health_report()["data"]["n_high"]


# ---------------------------------------------------------------------------
# 3. CSDL cũ bẩn: không bị đụng vào, và được chỉ ra
# ---------------------------------------------------------------------------

def _csdl_cu_ban(api):
    _nap_nhieu_buoi(api)
    _ha_cap(api.db_path)
    conn = sqlite3.connect(api.db_path)
    conn.execute("INSERT INTO preferences VALUES ('HS_DA_XOA', 'clb_bongro', 1)")
    conn.commit()
    conn.close()


def test_csdl_cu_ban_khong_bi_dung_lai_va_van_mo_duoc(api):
    _csdl_cu_ban(api)
    truoc = _dem(api.db_path)
    mo_lai = PipelineAPI(api.db_path)
    assert not _co_khoa_ngoai(api.db_path)
    assert _dem(api.db_path) == truoc
    ma = _ma(mo_lai.get_data_health_report())
    assert "health_vi_pham_mo_coi_hoc_sinh" in ma


def test_sua_xong_mo_lai_thi_duoc_nang_len(api):
    _csdl_cu_ban(api)
    mo_lai = PipelineAPI(api.db_path)
    assert mo_lai.create_student_if_missing("HS_DA_XOA", "Em trở lại")["ok"]
    assert "health_vi_pham_mo_coi_hoc_sinh" not in _ma(mo_lai.get_data_health_report())
    PipelineAPI(api.db_path)
    assert _co_khoa_ngoai(api.db_path)


def test_canh_bao_chi_ro_tung_loai_vi_pham(api):
    _nap_nhieu_buoi(api)
    _ha_cap(api.db_path)
    conn = sqlite3.connect(api.db_path)
    conn.execute("UPDATE clubs SET capacity = 0 WHERE club_id = 'clb_bongro'")
    conn.execute("UPDATE club_scores SET score = -3 WHERE rowid = "
                 "(SELECT MIN(rowid) FROM club_scores)")
    conn.execute("INSERT INTO club_test_selection VALUES ('HS001', 'CLB_DA_XOA')")
    conn.commit()
    conn.close()
    ma = _ma(PipelineAPI(api.db_path).get_data_health_report())
    for can in ("health_vi_pham_clb_suc_chua_sai", "health_vi_pham_diem_am",
                "health_vi_pham_mo_coi_clb"):
        assert can in ma


def test_nang_cap_hong_giua_chung_thi_csdl_y_nguyen(api, monkeypatch):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    _ha_cap(api.db_path)
    truoc_dem, truoc_kq = _dem(api.db_path), _ket_qua(api.db_path)
    # Bảng CUỐI hỏng định nghĩa: bốn bảng trước đã dựng lại xong trong
    # giao dịch thì lỗi mới nổ — đúng chỗ khó nhất để rollback.
    hong = dict(loi._BANG_RANG_BUOC)
    hong["match_results"] = "cot_hong KIEU_HONG ((("
    monkeypatch.setattr(loi, "_BANG_RANG_BUOC", hong)

    mo_lai = PipelineAPI(api.db_path)   # không được ném lỗi ra ngoài

    assert not _co_khoa_ngoai(api.db_path)
    assert _dem(api.db_path) == truoc_dem
    assert _ket_qua(api.db_path) == truoc_kq
    conn = sqlite3.connect(api.db_path)
    try:
        con_sot = conn.execute(
            "SELECT name FROM sqlite_master WHERE name LIKE '%__moi'").fetchall()
    finally:
        conn.close()
    assert con_sot == []
    assert mo_lai.run_pipeline(seed=42)["ok"]


def test_seed_sample_data_chay_lai_tren_cung_csdl(tmp_path):
    """seed_sample_data xoá dữ liệu cũ trước khi dựng — phải xoá bảng con
    TRƯỚC bảng cha, nếu không khoá ngoại chặn ngay lần chạy thứ hai."""
    db = str(tmp_path / "mau.db")
    loi.seed_sample_data(db, n_students=20, seed=1)
    loi.seed_sample_data(db, n_students=20, seed=2)
    assert _dem(db)["students"] == 20
