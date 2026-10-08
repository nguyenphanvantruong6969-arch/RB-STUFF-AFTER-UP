# -*- coding: utf-8 -*-
"""Chốt chặn cho điểm: số âm bị từ chối, số lệch hẳn thì cảnh báo.

Điểm chỉ có ý nghĩa **so sánh trong cùng một CLB**. Nên một con số lệch
hẳn không dừng lại ở em bị gõ nhầm: em đó nhảy lên đầu bảng, đẩy em khác
xuống, em đó lại đẩy em khác nữa. Đo trên bộ ví dụ 10 em: gõ `70` thay vì
`7.0` làm **ba** em đổi chỗ.

Hai bản vá ở đây:

  A. Màn hình Chấm điểm từ chối điểm âm — trước đó đường nạp tệp từ chối
     mà màn hình chấm thì nhận, nên cùng một lỗi thừa dấu trừ bắt được
     hay không lại tuỳ giáo viên đi cửa nào.

  B. Cảnh báo điểm lệch hẳn khỏi TRUNG VỊ CỦA CHÍNH CLB đó. Không đặt
     trần cứng ở 10 — trường có thể chấm thang 100, chặn cứng là chặn
     nhầm.
"""

import sqlite3

import pytest

from api import PipelineAPI


def _clb_co_diem(api, diem_theo_em, club="clb_a", suc_chua=5):
    api.create_or_update_club(club, "CLB A", suc_chua, 0, "")
    for sid, diem in diem_theo_em.items():
        api.create_student_if_missing(sid, "Em " + sid)
        api.submit_test_selection(sid, [club])
        api.submit_preferences(sid, [club])
        api.submit_club_scores(club, [{"student_id": sid, "score": diem}])
    return api


def _ma_canh_bao(api):
    return [w["code"] for w in api.get_data_health_report()["data"]["warnings"]]


def _diem_da_luu(api, sid, club="clb_a"):
    conn = sqlite3.connect(api.db_path)
    r = conn.execute(
        "SELECT score FROM club_scores WHERE student_id = ? AND club_id = ?",
        (sid, club),
    ).fetchone()
    conn.close()
    return r[0] if r else None


# ------------------------------------------------------------------ #
# A — điểm âm
# ------------------------------------------------------------------ #

def test_man_hinh_cham_diem_tu_choi_diem_am(api):
    _clb_co_diem(api, {"HS01": 9.0, "HS02": 8.0})
    res = api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": -9}])
    assert res["ok"] is True                       # không làm hỏng cả lượt lưu
    assert [w["code"] for w in res["data"]["warnings"]] == ["score_negative"]
    assert res["data"]["n_saved"] == 0
    # Điểm cũ phải CÒN NGUYÊN, không bị ghi đè bằng số âm.
    assert _diem_da_luu(api, "HS01") == 9.0


def test_hai_duong_nhap_cung_mot_luat_voi_diem_am(api, tmp_path):
    """Cùng giá trị −9: trước bản vá, nạp tệp từ chối còn màn hình chấm
    thì nhận. Bắt được hay không tuỳ cửa là một lỗi riêng."""
    _clb_co_diem(api, {"HS01": 9.0, "HS02": 8.0})
    qua_man_hinh = api.submit_club_scores(
        "clb_a", [{"student_id": "HS01", "score": -9}])

    api2 = PipelineAPI(str(tmp_path / "qua_tep.db"))
    api2.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    qua_tep = api2.import_test_selection_csv(
        "student_id,name,test_club_1,score_1\nHS01,Em,clb_a,-9\n")

    assert "score_negative" in [w["code"] for w in qua_man_hinh["data"]["warnings"]]
    assert "csv_score_negative" in [w["code"] for w in qua_tep["data"]["warnings"]]
    assert _diem_da_luu(api2, "HS01") is None


def test_diem_0_van_luu_duoc(api):
    """0 là điểm hợp lệ — em làm bài mà không được điểm nào. Chỉ số ÂM
    mới là dấu hiệu gõ nhầm."""
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    api.create_student_if_missing("HS01", "Em")
    api.submit_test_selection("HS01", ["clb_a"])
    res = api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": 0}])
    assert res["data"]["n_saved"] == 1
    assert _diem_da_luu(api, "HS01") == 0


# ------------------------------------------------------------------ #
# B — điểm lệch hẳn khỏi phân bố của CLB
# ------------------------------------------------------------------ #

BINH_THUONG = {"HS01": 9.0, "HS02": 8.5, "HS03": 8.0, "HS04": 7.5, "HS05": 7.0}


def test_diem_binh_thuong_thi_khong_canh_bao(api):
    _clb_co_diem(api, BINH_THUONG)
    assert "health_score_outlier" not in _ma_canh_bao(api)


@pytest.mark.parametrize("mo_ta,diem", [
    ("70 thay vì 7.0", 70),
    ("85 thay vì 8.5", 85),
    ("0.85 thay vì 8.5", 0.85),
])
def test_bat_duoc_loi_lech_dau_cham(api, mo_ta, diem):
    """Bắt cả hai phía: thừa một chữ số lẫn thiếu một chữ số."""
    _clb_co_diem(api, dict(BINH_THUONG, HS06=diem))
    canh_bao = api.get_data_health_report()["data"]["warnings"]
    la = [w for w in canh_bao if w["code"] == "health_score_outlier"]
    assert la, "khong bat duoc %s" % mo_ta
    assert la[0]["severity"] == "high"
    assert la[0]["params"]["club_id"] == "clb_a"
    assert "HS06" in la[0]["params"]["sample"]


def test_diem_thap_that_thi_khong_bao(api):
    """Em học yếu, 4.0 giữa những em 7–9. Đó là dữ liệu thật, không phải
    lỗi gõ — báo ở đây là báo nhiễu."""
    _clb_co_diem(api, dict(BINH_THUONG, HS06=4.0))
    assert "health_score_outlier" not in _ma_canh_bao(api)


def test_truong_cham_thang_100_khong_bi_bao_nham(api):
    """Không có trần cứng ở 10: so với trung vị của chính CLB đó nên
    thang điểm nào cũng đúng."""
    _clb_co_diem(api, {"HS01": 92.0, "HS02": 85.0, "HS03": 78.0,
                       "HS04": 71.0, "HS05": 64.0})
    assert "health_score_outlier" not in _ma_canh_bao(api)


def test_clb_it_hon_3_diem_thi_khong_ket_luan(api):
    """Hai điểm thì chưa có phân bố nào để mà so — đoán bừa là báo nhiễu."""
    _clb_co_diem(api, {"HS01": 8.0, "HS02": 80.0})
    assert "health_score_outlier" not in _ma_canh_bao(api)


def test_moi_clb_xet_rieng(api):
    """CLB chấm thang 10 và CLB chấm thang 100 nằm cạnh nhau vẫn yên."""
    _clb_co_diem(api, BINH_THUONG, club="clb_a")
    _clb_co_diem(api, {"HS11": 92.0, "HS12": 85.0, "HS13": 78.0}, club="clb_b")
    assert "health_score_outlier" not in _ma_canh_bao(api)


def test_bao_kem_ma_hoc_sinh_va_diem_cu_the(api):
    """Cảnh báo phải dẫn được tới chỗ sửa, không bắt người dùng tự dò."""
    _clb_co_diem(api, dict(BINH_THUONG, HS06=70))
    la = next(w for w in api.get_data_health_report()["data"]["warnings"]
              if w["code"] == "health_score_outlier")
    assert la["params"]["n"] == 1
    assert "HS06" in la["params"]["sample"]
    assert "70" in la["params"]["sample"]
    assert la["params"]["trung_vi"]

    from i18n_errors import format_message
    for lang in ("vi", "en"):
        chu = format_message(la["code"], la["params"], lang=lang)
        assert chu != la["code"]
        assert "{" not in chu


def test_bo_du_lieu_that_khong_sinh_canh_bao_nao(api):
    """Lưới an toàn: hai bộ dữ liệu đã công bố phải im lặng tuyệt đối.

    Đo lúc chọn ngưỡng: tỉ lệ (điểm cao nhất / trung vị) trong một CLB
    cao nhất trên 579 ô điểm thật là 1,42 — cách ngưỡng 3,0 rất xa.
    """
    import base64
    import os

    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for bo in ("vi_du_huong_dan", "bo_sach"):
        tm = os.path.join(goc, "du_lieu_test", bo)
        a = PipelineAPI(os.path.join(os.path.dirname(api.db_path), bo + ".db"))
        for t in sorted(os.listdir(tm)):
            if not t.endswith(".xlsx"):
                continue
            with open(os.path.join(tm, t), "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            d = a.xlsx_to_csv_text(b64, "")["data"]
            a.import_csv_auto(d["csv_text"] if isinstance(d, dict) else d)
        h = a.get_data_health_report()["data"]
        assert h["n_warnings"] == 0, (bo, h["warnings"])


# ------------------------------------------------------------------ #
# Dấu phẩy thập phân kiểu Việt — hai cửa phải cùng một luật
# ------------------------------------------------------------------ #

def _mot_thi_sinh(api):
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    api.create_student_if_missing("HS01", "Em")
    api.submit_test_selection("HS01", ["clb_a"])
    api.submit_preferences("HS01", ["clb_a"])
    return api


@pytest.mark.parametrize("go,mong_doi", [
    ("8,5", 8.5),      # cách viết thập phân của tiếng Việt
    ("8.5", 8.5),      # cách viết quốc tế
    ("9",   9.0),
    (" 7,5 ", 7.5),    # thừa khoảng trắng khi dán từ Excel
    (8.5,   8.5),      # gọi thẳng bằng số, không qua giao diện
])
def test_man_hinh_cham_diem_nhan_ca_hai_cach_viet(api, go, mong_doi):
    _mot_thi_sinh(api)
    res = api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": go}])
    assert res["data"]["n_saved"] == 1, (go, res["data"]["warnings"])
    assert _diem_da_luu(api, "HS01") == mong_doi


@pytest.mark.parametrize("go", ["abc", "1,234.5", "", "8,5,5", "inf", "nan"])
def test_gia_tri_khong_doc_duoc_thi_khong_ghi_de_diem_cu(api, go):
    """`1,234.5` là cách viết NGHÌN, không phải thập phân — không đoán bừa.
    `inf`/`nan` thì `float()` cũ nhận, `_doc_diem` loại."""
    _mot_thi_sinh(api)
    api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": "7,5"}])
    assert _diem_da_luu(api, "HS01") == 7.5

    res = api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": go}])
    assert res["data"]["n_saved"] == 0, go
    if go != "":
        assert [w["code"] for w in res["data"]["warnings"]] == ["score_not_a_number"]
    # Điểm cũ phải còn nguyên (ô rỗng là lệnh XOÁ, nên bỏ qua ca đó).
    if go != "":
        assert _diem_da_luu(api, "HS01") == 7.5


def test_diem_am_viet_bang_dau_phay_van_bi_chan(api):
    """Hai luật phải cộng dồn được: đọc được dấu phẩy KHÔNG có nghĩa là
    thôi kiểm tra số âm."""
    _mot_thi_sinh(api)
    api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": "7,5"}])
    res = api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": "-8,5"}])
    assert [w["code"] for w in res["data"]["warnings"]] == ["score_negative"]
    assert _diem_da_luu(api, "HS01") == 7.5


def test_hai_cua_cho_cung_ket_qua_voi_dau_phay(api, tmp_path):
    """Cùng giá trị '8,5' vào bằng hai đường phải ra cùng một số."""
    _mot_thi_sinh(api)
    api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": "8,5"}])

    api2 = PipelineAPI(str(tmp_path / "qua_tep.db"))
    api2.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    api2.import_test_selection_csv(
        "student_id,name,test_club_1,score_1\nHS01,Em,clb_a,\"8,5\"\n")

    assert _diem_da_luu(api, "HS01") == _diem_da_luu(api2, "HS01") == 8.5
