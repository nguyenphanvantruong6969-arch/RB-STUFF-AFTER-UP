# -*- coding: utf-8 -*-
"""Canh bộ dữ liệu đầu vào mẫu ở `mau_csv/vi_du_day_du/`.

Bộ này là thứ người dùng mở ra đầu tiên khi muốn biết tệp đầu vào trông thế
nào. Nó phải **nhập vào không một cảnh báo nào** — một bộ mẫu mà phần mềm
phải kêu là một bộ mẫu đang dạy người ta làm sai, và người đọc không có cách
nào biết cảnh báo đó là cố ý hay là lỗi.

Tệp này khoá bốn điều:

1. ba tệp nhập trọn vẹn, **0 cảnh báo**, và bảng sức khoẻ dữ liệu cũng sạch;
2. ba tệp **khớp nhau từng mã** — không mã câu lạc bộ nào trong tệp học sinh
   mà thiếu trong danh sách, không câu lạc bộ nào nằm sai cột buổi;
3. chạy phân bổ được, không câu lạc bộ nào vượt sức chứa;
4. `GIAI_THICH.md` nói đúng những con số bộ này thật sự cho ra — tài liệu
   trích số liệu mà số liệu trôi đi là lỗi đã gặp một lần rồi.

ĐỐI CHỨNG NGƯỢC đã chạy thật: đổi **một** mã câu lạc bộ trong
`03_xep_hang_nguyen_vong.csv` thành mã không tồn tại → **6 trên 10 test ĐỎ**
(nhập có cảnh báo, bảng sức khoẻ có cảnh báo, mã không khớp, buổi không khớp,
và cả hai test tài liệu — vì con số kết quả đổi theo). Khôi phục → xanh lại.
"""

import csv
import io
import os

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO = os.path.join(GOC, "mau_csv", "vi_du_day_du")
TEP = ["01_danh_sach_CLB.csv", "02_chon_CLB_muon_thi.csv",
       "03_xep_hang_nguyen_vong.csv"]


def _doc(ten):
    with io.open(os.path.join(BO, ten), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture
def api_vi_du(api):
    for ten in TEP:
        with io.open(os.path.join(BO, ten), encoding="utf-8-sig") as f:
            kq = api.import_csv_auto(f.read())
        assert kq["ok"], (ten, kq)
    return api


# ------------------------------------------------------------------ #
# 1. NHẬP SẠCH
# ------------------------------------------------------------------ #

def test_ba_tep_nhap_khong_mot_canh_bao_nao(api):
    """Một bộ mẫu mà phần mềm phải kêu là một bộ mẫu dạy người ta làm sai."""
    for ten in TEP:
        with io.open(os.path.join(BO, ten), encoding="utf-8-sig") as f:
            kq = api.import_csv_auto(f.read())
        assert kq["ok"], (ten, kq)
        assert (kq["data"].get("warnings") or []) == [], (ten, kq["data"]["warnings"])


def test_bang_suc_khoe_du_lieu_cung_sach(api_vi_du):
    bc = api_vi_du.get_data_health_report()
    assert bc["ok"], bc
    # Bo qua DUNG MOT ma: buoi it cho hon so em xep buoi do. Bo mau co y de
    # moi buoi chat cho (xem GIAI_THICH.md, "tong so cho moi buoi"), nen canh
    # bao do la DUNG. Loc theo MA, khong theo muc "info" — moi canh bao khac,
    # ke ca "info" them sau nay, van phai bang 0.
    loi = [w for w in bc["data"]["warnings"]
           if w["code"] != "health_oversubscribed_buoi"]
    assert loi == [], loi


# ------------------------------------------------------------------ #
# 2. BA TỆP KHỚP NHAU TỪNG MÃ
# ------------------------------------------------------------------ #

def test_moi_ma_clb_trong_tep_hoc_sinh_deu_co_that():
    clb = {r["club_id"] for r in _doc(TEP[0])}
    assert clb, "danh sach CLB rong"

    thieu = set()
    for r in _doc(TEP[1]):
        for k, v in r.items():
            if k and k.startswith("test_club_") and v:
                thieu |= {v} - clb
    for r in _doc(TEP[2]):
        for k, v in r.items():
            if k and "_pref_" in k and v:
                thieu |= {v} - clb
    assert thieu == set(), "ma CLB khong co trong danh sach: %s" % sorted(thieu)


def test_moi_clb_nam_dung_cot_buoi_cua_no():
    buoi_cua = {r["club_id"]: r["buoi"] for r in _doc(TEP[0])}
    lech = []
    for r in _doc(TEP[2]):
        for k, v in r.items():
            if k and "_pref_" in k and v:
                buoi_cot = k.rsplit("_pref_", 1)[0]
                if buoi_cua.get(v) != buoi_cot:
                    lech.append((r["student_id"], v, buoi_cot, buoi_cua.get(v)))
    assert lech == [], lech


def test_ma_hoc_sinh_duy_nhat_va_khop_giua_hai_tep():
    a = [r["student_id"] for r in _doc(TEP[1])]
    b = [r["student_id"] for r in _doc(TEP[2])]
    assert len(a) == len(set(a)), "tep 02 co ma hoc sinh trung"
    assert len(b) == len(set(b)), "tep 03 co ma hoc sinh trung"
    # Phan biet hoa thuong: 'hs001' va 'HS001' la HAI em khac nhau, nen phep
    # so sanh nay phai la so sanh CHINH XAC chu khong phai casefold.
    assert set(a) == set(b), "hai tep hoc sinh khong cung mot danh sach"


def test_chi_cham_diem_cho_clb_em_do_co_khai_nguyen_vong():
    """Điểm của một câu lạc bộ em không xếp nguyện vọng là điểm không dùng
    tới — và gần như chắc chắn là gõ lệch cột."""
    nv = {}
    for r in _doc(TEP[2]):
        nv[r["student_id"]] = {v for k, v in r.items() if k and "_pref_" in k and v}
    thua = []
    for r in _doc(TEP[1]):
        for k, v in r.items():
            if k and k.startswith("test_club_") and v:
                if v not in nv.get(r["student_id"], set()):
                    thua.append((r["student_id"], v))
    assert thua == [], thua


# ------------------------------------------------------------------ #
# 3. CHẠY ĐƯỢC, VÀ CHẠY ĐÚNG
# ------------------------------------------------------------------ #

def test_chay_duoc_va_khong_clb_nao_vuot_suc_chua(api_vi_du):
    kq = api_vi_du.run_pipeline(seed=42)
    assert kq["ok"], kq
    qua = [c for c in api_vi_du.get_club_fill_stats()["data"]
           if c["matched"] > c["capacity"]]
    assert qua == [], qua


def test_suat_du_tru_that_su_co_nguoi_dung(api_vi_du):
    """Bộ mẫu mà chỉ tiêu dự trữ không ai dùng thì nó không hề minh hoạ cái
    cơ chế trung tâm của cả phần mềm."""
    api_vi_du.run_pipeline(seed=42)
    co_du_tru = [c for c in api_vi_du.get_club_fill_stats()["data"]
                 if c["reserve_capacity"] > 0]
    assert co_du_tru, "bo mau khong co CLB nao co suat du tru"
    assert all(c["matched_reserve"] > 0 for c in co_du_tru), [
        (c["club_id"], c["matched_reserve"]) for c in co_du_tru]


# ------------------------------------------------------------------ #
# 4. TÀI LIỆU NÓI ĐÚNG SỐ THẬT
#
# Trích số liệu vào tài liệu rồi để số liệu trôi đi là lỗi đã gặp một lần
# trong kho này (ba tài liệu cùng dẫn một con số TN7a đã cũ). Lần này có
# test canh.
# ------------------------------------------------------------------ #

def test_giai_thich_noi_dung_so_lieu_that(api_vi_du):
    with io.open(os.path.join(BO, "GIAI_THICH.md"), encoding="utf-8") as f:
        tai_lieu = f.read()

    api_vi_du.run_pipeline(seed=42)
    dp = api_vi_du.get_do_phu()["data"]
    n_clb = len(_doc(TEP[0]))
    n_hs = len(_doc(TEP[2]))
    n_buoi = len({r["buoi"] for r in _doc(TEP[0])})
    da_xep = n_hs - dp["so_em_trang_tay"]

    assert "%d buổi" % n_buoi in tai_lieu
    assert "%d câu lạc bộ" % n_clb in tai_lieu
    assert "%d học sinh" % n_hs in tai_lieu
    assert "%d / %d" % (da_xep, n_hs) in tai_lieu, (
        "tai lieu noi ti le xep khac voi so that %d/%d" % (da_xep, n_hs))
    assert str(dp["trung_binh_clb"]).replace(".", ",") in tai_lieu


def test_giai_thich_neu_dung_ten_em_trang_tay(api_vi_du):
    """Tài liệu giảng kỹ về một em cụ thể — em đó phải đúng là em trắng tay."""
    with io.open(os.path.join(BO, "GIAI_THICH.md"), encoding="utf-8") as f:
        tai_lieu = f.read()
    api_vi_du.run_pipeline(seed=42)
    ds = api_vi_du.get_do_phu()["data"]["em_trang_tay"]
    assert len(ds) == 1, ds
    assert ds[0]["student_id"] in tai_lieu
    assert ds[0]["name"] in tai_lieu
