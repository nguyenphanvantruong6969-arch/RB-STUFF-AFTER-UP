# -*- coding: utf-8 -*-
"""Khoá bộ ví dụ trong `du_lieu_test/vi_du_huong_dan/`.

`HUONG_DAN_SU_DUNG.md` in nguyên bảng kết quả của bộ này ra và bảo người
đọc: "ra khác bảng này là có gì đó đã đổi". Lời hứa đó chỉ giữ được nếu
có test canh — nếu không, một thay đổi bất kỳ sẽ âm thầm làm hướng dẫn
nói dối, mà hướng dẫn là thứ người khác đọc khi không có ai đứng cạnh.

Test khoá cả bảng xếp lớp lẫn bốn tình huống dạy học mà bộ này được dựng
ra để minh hoạ.
"""

import base64
import io
import os
import sqlite3

import pytest

VI_DU = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "du_lieu_test", "vi_du_huong_dan",
)

TEN_FILE = [
    "VIDU_01_danh_sach_CLB",
    "VIDU_02_chon_CLB_muon_thi",
    "VIDU_03_xep_hang_nguyen_vong",
]

# Bảng này in nguyên trong README của bộ ví dụ và trong hướng dẫn.
KET_QUA_DUNG = {
    "HS01": ("clb_bongro",  1, "general"),
    "HS02": ("clb_bongro",  1, "general"),
    "HS03": ("clb_nauan",   2, "general"),
    "HS04": ("clb_bongro",  1, "reserve"),
    "HS05": ("clb_tinhoc",  2, "general"),
    "HS06": ("clb_tinhoc",  1, "general"),
    "HS07": ("clb_mythuat", 1, "general"),
    "HS08": ("clb_mythuat", 1, "general"),
    "HS09": ("clb_nauan",   1, "general"),
}
CHUA_XEP = "HS10"
SUC_CHUA = {"clb_bongro": (3, 3), "clb_mythuat": (2, 2),
            "clb_nauan": (2, 3), "clb_tinhoc": (2, 2)}


def _nap(api, duoi=".xlsx"):
    """Nạp cả ba tệp theo thứ tự, trả về tổng số cảnh báo lúc nhập."""
    tong = 0
    for ten in TEN_FILE:
        p = os.path.join(VI_DU, ten + duoi)
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


def _ket_qua(api):
    """Chỉ những em ĐƯỢC XẾP.

    Em không được xếp vẫn có một dòng trong match_results, với club_id
    rỗng — đó là thiết kế đúng (giữ dấu vết là đã xét em này), nhưng gộp
    chung vào bảng đối chiếu thì lẫn hai chuyện khác nhau.
    """
    conn = sqlite3.connect(api.db_path)
    hang = {
        r[0]: (r[1], r[2], r[3])
        for r in conn.execute(
            "SELECT student_id, club_id, rank_in_student_pref, matched_tier "
            "FROM match_results WHERE club_id IS NOT NULL"
        )
    }
    conn.close()
    return hang


def _chua_xep(api):
    conn = sqlite3.connect(api.db_path)
    ds = {r[0] for r in conn.execute(
        "SELECT student_id FROM match_results WHERE club_id IS NULL")}
    conn.close()
    return ds


@pytest.mark.parametrize("duoi", [".xlsx", ".csv"])
def test_ca_ba_tep_ton_tai(duoi):
    for ten in TEN_FILE:
        assert os.path.exists(os.path.join(VI_DU, ten + duoi)), ten + duoi


@pytest.mark.parametrize("duoi", [".xlsx", ".csv"])
def test_nap_khong_canh_bao_nao(api, duoi):
    """Người mới không phân biệt được cảnh báo thật với cảnh báo do bộ mẫu."""
    assert _nap(api, duoi) == 0
    h = api.get_data_health_report()
    assert h["ok"], h
    assert h["data"]["n_warnings"] == 0, h["data"]["warnings"]


def test_bang_ket_qua_dung_nhu_huong_dan_in_ra(api):
    _nap(api)
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    assert (r["data"]["n_total"], r["data"]["n_matched"]) == (10, 9)

    assert _ket_qua(api) == KET_QUA_DUNG


def test_dung_mot_em_chua_duoc_xep(api):
    """HS10 chỉ xếp một nguyện vọng vào CLB đông nhất."""
    _nap(api)
    assert api.run_pipeline(seed=42)["ok"]
    assert CHUA_XEP not in _ket_qua(api)
    # Vẫn phải CÓ dòng cho em đó, chỉ là club_id rỗng — mất hẳn dòng thì
    # em này biến khỏi tệp _chua_duoc_xep.csv mà không ai biết.
    assert _chua_xep(api) == {CHUA_XEP}


def test_co_clb_con_cho_trong_khi_van_con_em_chua_xep(api):
    """Điểm dạy học quan trọng nhất của bộ này: thuật toán KHÔNG nhét học
    sinh vào CLB các em không chọn, kể cả khi CLB đó còn trống."""
    _nap(api)
    assert api.run_pipeline(seed=42)["ok"]
    conn = sqlite3.connect(api.db_path)
    thuc = {
        r[0]: (r[2], r[1])
        for r in conn.execute(
            "SELECT c.club_id, c.capacity, COUNT(m.student_id) "
            "FROM clubs c LEFT JOIN match_results m ON m.club_id = c.club_id "
            "GROUP BY c.club_id"
        )
    }
    conn.close()
    assert thuc == SUC_CHUA
    assert thuc["clb_nauan"][0] < thuc["clb_nauan"][1], "phai con cho trong"


def test_suat_du_tru_doi_dung_mot_cho(api, tmp_path):
    """Chạy hai lần, một lần có suất dự trữ và một lần bỏ đi.

    README in nguyên kết quả so sánh này ra để giải thích cơ chế dự trữ,
    nên phải đo lại chứ không được để nó thành câu chữ suông."""
    from api import PipelineAPI

    _nap(api)
    assert api.run_pipeline(seed=42)["ok"]
    co = {sid: v[0] for sid, v in _ket_qua(api).items()}

    api2 = PipelineAPI(str(tmp_path / "khong_du_tru.db"))
    _nap(api2)
    api2.create_or_update_club("clb_bongro", "CLB Bóng rổ", 3, 0, "")
    assert api2.run_pipeline(seed=42)["ok"]
    khong = {sid: v[0] for sid, v in _ket_qua(api2).items()}

    doi = {sid for sid in set(co) | set(khong)
           if co.get(sid) != khong.get(sid)}
    assert doi == {"HS03", "HS04"}, doi
    # HS04 (điểm 6,0, diện chinh_sach) vào được nhờ suất dự trữ...
    assert co["HS04"] == "clb_bongro"
    assert "HS04" not in khong
    # ...và chỗ đó, nếu bỏ dự trữ, thuộc về HS03 (điểm 8,0).
    assert khong["HS03"] == "clb_bongro"
    assert co["HS03"] == "clb_nauan"


def test_ket_qua_on_dinh_khong_co_cap_chan(api):
    from rbda_priority_pipeline import (default_reserve_eligible_fn,
                                        load_from_sqlite, run_rbda,
                                        verify_stability)

    _nap(api)
    assert api.run_pipeline(seed=42)["ok"]
    students, clubs, scores, applicants, prefs, stb = load_from_sqlite(api.db_path)
    fn = default_reserve_eligible_fn(students, clubs)
    kq = run_rbda(students, clubs, scores, applicants, prefs, stb,
                  is_reserve_eligible_fn=fn)
    assert verify_stability(kq, clubs, prefs, fn) == []


def test_hai_duong_vao_cho_cung_ket_qua(api, tmp_path):
    from api import PipelineAPI

    _nap(api, ".xlsx")
    assert api.run_pipeline(seed=42)["ok"]
    api2 = PipelineAPI(str(tmp_path / "tu_csv.db"))
    _nap(api2, ".csv")
    assert api2.run_pipeline(seed=42)["ok"]
    assert _ket_qua(api) == _ket_qua(api2)


def test_khong_co_tep_la_trong_thu_muc(api):
    cho_phep = {t + d for t in TEN_FILE for d in (".xlsx", ".csv")}
    cho_phep |= {"tao_vi_du.py", "README.md", "__pycache__", "SO_NHAP_VIDU.xlsx"}
    thua = set(os.listdir(VI_DU)) - cho_phep
    assert not thua, thua


def test_khong_hai_em_nao_trung_ho_ten(api):
    """Bộ 140 em có trùng tên thật (ngẫu nhiên). Bộ dạy học thì đừng —
    người đọc đang học cách đọc bảng, không cần thêm nhiễu."""
    _nap(api)
    conn = sqlite3.connect(api.db_path)
    ten = [r[0] for r in conn.execute("SELECT name FROM students")]
    conn.close()
    assert len(ten) == len(set(ten)) == 10
