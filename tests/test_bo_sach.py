# -*- coding: utf-8 -*-
"""Canh BỘ SẠCH trong `du_lieu_test/bo_sach/` luôn thật sự sạch.

Bộ này tồn tại vì đúng một lời hứa: **nạp vào không có cảnh báo nào**,
để người chạy thử biết mọi cảnh báo nhìn thấy đều là do dữ liệu của họ,
không phải do bộ mẫu. Lời hứa đó chỉ giữ được nếu có test canh — thêm
một quy tắc rà soát mới trong `get_data_health_report()` là bộ mẫu có
thể lặng lẽ bắt đầu kêu, mà không test nào đỏ.

Canh cả hai đường vào (.xlsx và .csv) vì máy thiếu openpyxl phải dùng
đường CSV, và hai đường đó phải cho ra CÙNG một kết quả xếp lớp.
"""

import base64
import io
import os

import pytest

BO_SACH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "du_lieu_test", "bo_sach",
)

TEN_FILE = [
    "SACH_01_danh_sach_CLB",
    "SACH_02_chon_CLB_muon_thi",
    "SACH_03_xep_hang_nguyen_vong",
]

SO_HOC_SINH = 140
SO_CLB = 12


def _nap(api, duoi):
    """Nạp cả ba file theo đúng thứ tự, trả về tổng số cảnh báo nhập."""
    tong = 0
    for ten in TEN_FILE:
        p = os.path.join(BO_SACH, ten + duoi)
        if duoi == ".xlsx":
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            r = api.xlsx_to_csv_text(b64, "")
            assert r["ok"], r
            d = r["data"]
            text = d["csv_text"] if isinstance(d, dict) else d
        else:
            with io.open(p, encoding="utf-8-sig") as f:
                text = f.read()
        res = api.import_csv_auto(text)
        assert res["ok"], (ten, res)
        tong += len(res["data"].get("warnings", []))
    return tong


@pytest.mark.parametrize("duoi", [".xlsx", ".csv"])
def test_ca_ba_file_ton_tai(duoi):
    for ten in TEN_FILE:
        assert os.path.exists(os.path.join(BO_SACH, ten + duoi)), ten + duoi


@pytest.mark.parametrize("duoi", [".xlsx", ".csv"])
def test_nap_khong_mot_canh_bao_nao(api, duoi):
    assert _nap(api, duoi) == 0


@pytest.mark.parametrize("duoi", [".xlsx", ".csv"])
def test_ra_soat_du_lieu_khong_canh_bao(api, duoi):
    _nap(api, duoi)
    h = api.get_data_health_report()
    assert h["ok"], h
    assert h["data"]["n_warnings"] == 0, h["data"]["warnings"]


def test_xep_duoc_toan_bo_hoc_sinh(api):
    _nap(api, ".xlsx")
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    assert r["data"]["n_total"] == SO_HOC_SINH
    # Hai nguyện vọng cuối của mỗi em rơi vào CLB còn chỗ, nên không em
    # nào được phép trượt hết. Trượt dù chỉ một em là bộ mẫu đã hỏng.
    assert r["data"]["n_matched"] == SO_HOC_SINH


def test_dung_ca_hai_tier_va_suat_du_tru(api):
    """Bộ mẫu phải cho THẤY cơ chế, không chỉ chạy trót lọt.

    Nếu mọi em đều vào bằng Tier 1 hoặc không suất dự trữ nào được dùng
    thì bảng kết quả không minh hoạ được gì — bộ mẫu mất tác dụng dù
    phần mềm vẫn đúng.
    """
    import sqlite3

    _nap(api, ".xlsx")
    assert api.run_pipeline(seed=42)["ok"]

    conn = sqlite3.connect(api.db_path)
    tiers = dict(conn.execute(
        "SELECT matched_tier, COUNT(*) FROM match_results GROUP BY matched_tier"
    ).fetchall())
    hang = dict(conn.execute(
        "SELECT rank_in_student_pref, COUNT(*) FROM match_results "
        "GROUP BY rank_in_student_pref"
    ).fetchall())
    conn.close()

    assert tiers.get("reserve", 0) > 0, tiers
    assert tiers.get("general", 0) > 0, tiers
    # Không phải ai cũng được nguyện vọng 1 — có thế mới thấy thuật toán
    # phải đẩy người xuống nguyện vọng dưới.
    assert hang.get(1, 0) < SO_HOC_SINH
    assert sum(n for h, n in hang.items() if h and h >= 3) > 0, hang


def test_hai_duong_vao_cho_cung_ket_qua(api, tmp_path):
    """Đường .xlsx và đường .csv phải xếp lớp giống hệt nhau."""
    import sqlite3

    from api import PipelineAPI

    _nap(api, ".xlsx")
    assert api.run_pipeline(seed=42)["ok"]
    conn = sqlite3.connect(api.db_path)
    tu_xlsx = dict(conn.execute(
        "SELECT student_id, club_id FROM match_results").fetchall())
    conn.close()

    api2 = PipelineAPI(str(tmp_path / "app2.db"))
    _nap(api2, ".csv")
    assert api2.run_pipeline(seed=42)["ok"]
    conn = sqlite3.connect(api2.db_path)
    tu_csv = dict(conn.execute(
        "SELECT student_id, club_id FROM match_results").fetchall())
    conn.close()

    assert tu_xlsx == tu_csv


def test_khong_co_file_loi_lan_trong_thu_muc(api):
    """Thư mục này KHÔNG được chứa file dữ liệu nào ngoài ba bộ trên.

    Cả vấn đề ban đầu là người dùng thả nhầm file lỗi cố ý cùng lúc với
    bộ sạch rồi tưởng phần mềm hỏng. Thư mục sạch phải thả được TOÀN BỘ
    mà vẫn im lặng.
    """
    cho_phep = {t + d for t in TEN_FILE for d in (".xlsx", ".csv")}
    cho_phep |= {"tao_bo_sach.py", "README.md", "__pycache__", "SO_NHAP_SACH.xlsx"}
    thua = set(os.listdir(BO_SACH)) - cho_phep
    assert not thua, thua


def test_xuat_ket_qua_doc_duoc_bang_excel(api, tmp_path):
    """File xuất phải có BOM utf-8-sig, nếu không Excel vỡ dấu tiếng Việt."""
    _nap(api, ".xlsx")
    assert api.run_pipeline(seed=42)["ok"]
    dich = str(tmp_path / "ket_qua.csv")
    e = api.export_csv(dich)
    assert e["ok"], e
    with open(dich, "rb") as f:
        assert f.read(3) == b"\xef\xbb\xbf"
    with io.open(dich, encoding="utf-8-sig") as f:
        dong = f.readlines()
    assert len(dong) == SO_HOC_SINH + 1
    assert "Mã học sinh" in dong[0]


# ------------------------------------------------------------------ #
# Kịch bản THẬT đã làm hỏng việc: nạp chồng lên dữ liệu cũ
# ------------------------------------------------------------------ #

TEST_DIR = os.path.dirname(BO_SACH)

BO_TEST = [
    "TEST_01_danh_sach_CLB.xlsx",
    "TEST_02_chon_CLB_muon_thi.xlsx",
    "TEST_03_xep_hang_nguyen_vong.xlsx",
    "TEST_04_CO_LOI_CO_Y.xlsx",      # cố ý sai
]


def _nap_bo_test(api):
    for ten in BO_TEST:
        with open(os.path.join(TEST_DIR, ten), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        r = api.xlsx_to_csv_text(b64, "")
        assert r["ok"], r
        d = r["data"]
        api.import_csv_auto(d["csv_text"] if isinstance(d, dict) else d)


def test_nap_chong_len_du_lieu_cu_van_con_canh_bao(api):
    """Khẳng định lỗi CÓ THẬT trước khi khẳng định bản vá chữa được nó.

    Nạp file chỉ cộng thêm học sinh. HS204 của TEST_04 mang nhãn sai
    `chinh_sac` vẫn nằm nguyên, nên bộ sạch nạp đè lên vẫn kêu — và số
    học sinh vượt quá 140, làm lệch kết quả phân bổ.
    """
    _nap_bo_test(api)
    _nap(api, ".xlsx")

    h = api.get_data_health_report()["data"]
    nhan_la = [w for w in h["warnings"]
               if w["code"] == "health_orphan_student_group"]
    assert nhan_la, h["warnings"]
    assert nhan_la[0]["params"]["reserve_group"] == "chinh_sac"
    # Và cảnh báo phải chỉ đích danh em nào — đó là nửa còn lại của bản vá.
    assert "HS204" in nhan_la[0]["params"]["sample"]

    r = api.run_pipeline(seed=42)
    assert r["data"]["n_total"] > SO_HOC_SINH


def test_xoa_du_lieu_roi_nap_lai_thi_sach_han(api):
    """Bản vá phải đưa được đúng tình huống trên về 0 cảnh báo, 140/140."""
    _nap_bo_test(api)
    _nap(api, ".xlsx")
    assert api.run_pipeline(seed=42)["ok"]

    xoa = api.reset_data("hoc_sinh", "XOA")
    assert xoa["ok"], xoa
    # Giữ CLB nên không phải nạp lại file danh sách CLB.
    assert xoa["data"]["n_clubs_con_lai"] > 0

    assert _nap(api, ".xlsx") == 0
    h = api.get_data_health_report()["data"]
    assert h["n_warnings"] == 0, h["warnings"]

    r = api.run_pipeline(seed=42)
    assert r["data"]["n_total"] == SO_HOC_SINH
    assert r["data"]["n_matched"] == SO_HOC_SINH
