# -*- coding: utf-8 -*-
"""Hạt giống bốc thăm bị khoá CÙNG bộ số bốc thăm.

VẤN ĐỀ. Khoá bốc thăm (`stb_lock`) giữ nguyên `students.stb_number`, và
muốn vẽ lại thì phải xác nhận hai bước. Nhưng ở trường nhiều buổi, thứ tự
ưu tiên của TỪNG buổi được dẫn xuất từ bộ số đã khoá CỘNG với hạt giống
(`sinh_stb_theo_buoi`). Trước đây ô hạt giống sửa tự do: đổi 42 thành 43
rồi chạy lại cả tuần thì 22 trên 800 dòng kết quả của `bo_nhieu_buoi` đổi
chủ, trong khi màn hình vẫn báo "đã khoá". Hai việc cùng làm đổi kết quả đã
công bố lại được bảo vệ ở hai mức khác nhau.

LUẬT MỚI. Khoá là khoá: hạt giống được ghi vào `stb_lock` lúc khoá. Chạy
lại với hạt giống khác thì bị từ chối, trừ khi đi qua đúng đường "vẽ lại"
(`force_redraw_stb=True`) — đường đã có xác nhận hai bước.
"""

import io
import os
import sqlite3


GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _nap(api, thu_muc, mau):
    for i, ten in enumerate(
            ["danh_sach_CLB", "chon_CLB_muon_thi", "xep_hang_nguyen_vong"], start=1):
        with io.open(os.path.join(GOC, thu_muc, mau % (i, ten)),
                     encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]


def _nhieu_buoi(api):
    _nap(api, "du_lieu_test/bo_nhieu_buoi", "NHIEUBUOI_0%d_%s.csv")


def _mot_buoi(api):
    _nap(api, "du_lieu_test/vi_du_huong_dan", "VIDU_0%d_%s.csv")


def _doc(api, sql):
    conn = sqlite3.connect(api.db_path)
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def _ket_qua(api):
    return _doc(api, "SELECT * FROM match_results ORDER BY student_id, buoi")


def _so_lan_chay(api):
    return _doc(api, "SELECT COUNT(*) FROM run_history")[0][0]


def _ma_loi(res):
    return [e.get("code") for e in res["errors"] if isinstance(e, dict)]


# ---------------------------------------------------------------------------
# 1. Đổi hạt giống khi đã khoá: bị chặn, và KHÔNG ghi gì
# ---------------------------------------------------------------------------

def test_doi_hat_giong_khi_da_khoa_bi_chan_ca_tuan(api):
    _nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    truoc = _ket_qua(api)
    n_chay = _so_lan_chay(api)

    res = api.run_pipeline(seed=43)

    assert not res["ok"]
    assert "hat_giong_da_khoa" in _ma_loi(res)
    loi = next(e for e in res["errors"] if e.get("code") == "hat_giong_da_khoa")
    assert loi["params"] == {"cu": 42, "moi": 43}
    assert _ket_qua(api) == truoc, "lần chạy bị chặn không được đổi dòng nào"
    assert _so_lan_chay(api) == n_chay, "lần chạy bị chặn không được ghi nhật ký"


def test_doi_hat_giong_khi_da_khoa_bi_chan_ca_truong_mot_buoi(api):
    """Một luật cho mọi trường — không bắt người vận hành nhớ trường mình
    thuộc loại nào mới biết ô hạt giống có tác dụng hay không."""
    _mot_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    res = api.run_pipeline(seed=7)
    assert not res["ok"]
    assert "hat_giong_da_khoa" in _ma_loi(res)


def test_cung_hat_giong_thi_chay_lai_binh_thuong(api):
    _nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    truoc = _ket_qua(api)
    assert api.run_pipeline(seed=42)["ok"]
    assert _ket_qua(api) == truoc


# ---------------------------------------------------------------------------
# 2. Đường hợp lệ để đổi: vẽ lại
# ---------------------------------------------------------------------------

def test_ve_lai_thi_doi_duoc_hat_giong_va_khoa_theo_hat_moi(api):
    _nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    assert api.run_pipeline(seed=43, force_redraw_stb=True)["ok"]
    assert api.get_stb_lock_status()["data"]["seed"] == 43
    # Sau khi vẽ lại, hạt giống MỚI là hạt giống bị khoá.
    assert api.run_pipeline(seed=43)["ok"]
    assert "hat_giong_da_khoa" in _ma_loi(api.run_pipeline(seed=42))


def test_trang_thai_khoa_cho_biet_hat_giong(api):
    _mot_buoi(api)
    assert api.get_stb_lock_status()["data"]["seed"] is None
    assert api.run_pipeline(seed=42)["ok"]
    assert api.get_stb_lock_status()["data"]["seed"] == 42
    assert api.get_pipeline_run_warning()["data"]["stb_locked_seed"] == 42


def test_xoa_du_lieu_mo_khoa_thi_hat_giong_nao_cung_dung_duoc(api):
    _mot_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    assert api.reset_data("hoc_sinh", "XOA")["ok"]
    _mot_buoi(api)
    assert api.run_pipeline(seed=9)["ok"]
    assert api.get_stb_lock_status()["data"]["seed"] == 9


# ---------------------------------------------------------------------------
# 3. Thêm học sinh sau khi khoá vẫn chạy được với hạt giống đã khoá
# ---------------------------------------------------------------------------

def test_them_hoc_sinh_moi_khi_da_khoa(api):
    _mot_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    assert api.create_student_if_missing("HS_MOI", "Em Mới")["ok"]
    clb = api.list_clubs()["data"][0]["club_id"]
    assert api.submit_preferences("HS_MOI", [clb])["ok"]
    res = api.run_pipeline(seed=42)
    assert res["ok"], res.get("errors")
    so = _doc(api, "SELECT stb_number FROM students WHERE student_id='HS_MOI'")
    assert so[0][0] is not None


# ---------------------------------------------------------------------------
# 4. CSDL cũ: đã khoá từ trước khi có cột hạt giống
# ---------------------------------------------------------------------------

def test_csdl_cu_da_khoa_duoc_dien_hat_giong_tu_lan_chay_gan_nhat(api):
    from api import PipelineAPI

    _nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    # Giả lập CSDL dựng bằng bản cũ: bảng stb_lock chưa có cột seed.
    conn = sqlite3.connect(api.db_path)
    conn.execute("ALTER TABLE stb_lock DROP COLUMN seed")
    conn.commit()
    conn.close()

    mo_lai = PipelineAPI(api.db_path)
    assert mo_lai.get_stb_lock_status()["data"]["seed"] == 42
    assert "hat_giong_da_khoa" in _ma_loi(mo_lai.run_pipeline(seed=43))
    assert mo_lai.run_pipeline(seed=42)["ok"]


def test_csdl_cu_khong_co_lan_chay_nao_thi_nhan_hat_giong_dau_tien(api):
    """Đã khoá mà không có run_meta (không thể từ giao diện, nhưng có thể
    với tệp CSDL sửa tay) — lần chạy kế tiếp nhận hạt giống được gõ và ghi
    nó vào khoá, thay vì chặn vĩnh viễn."""
    _mot_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    conn = sqlite3.connect(api.db_path)
    conn.execute("UPDATE stb_lock SET seed = NULL")
    conn.execute("DELETE FROM run_meta")
    conn.commit()
    conn.close()
    assert api.run_pipeline(seed=5)["ok"]
    assert api.get_stb_lock_status()["data"]["seed"] == 5
