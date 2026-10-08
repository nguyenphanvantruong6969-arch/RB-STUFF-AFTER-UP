# -*- coding: utf-8 -*-
"""Canh BỘ TOÀN TUẦN trong `du_lieu_test/bo_toan_tuan/`.

Bộ này giữ một lời hứa chặt hơn bộ kịch trần: không phải "có em chạm
trần" mà **mọi em, mọi buổi đều kín trần**, trên cả bảy nhãn buổi phần
mềm nhận ra. Chùng một ô là bộ này thành một bộ mẫu bình thường nữa, mà
chùng thì không cảnh báo nào kêu — phần mềm chỉ hỏi "có quá không",
không hỏi "đã đủ chưa". Không test canh thì hỏng lặng lẽ.

Canh thêm một thứ không bộ nào khác canh: bảy nhãn buổi phải được phần
mềm hiểu là bảy THỨ trong tuần chứ không phải bảy chuỗi lạ. Nhãn lạ vẫn
chạy đúng kết quả xếp lớp, nhưng bị sắp theo vần — `chu_nhat` nhảy lên
đầu vì chữ "c" — và không test kết quả nào đỏ.
"""

import csv
import io
import os

from rbda_priority_pipeline import (
    TRAN_CLB_THI_MOI_BUOI,
    TRAN_NGUYEN_VONG_MOI_BUOI,
    so_thu_trong_tuan,
)

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO = os.path.join(_GOC, "du_lieu_test", "bo_toan_tuan")

TEN_FILE = [
    "TOANTUAN_01_danh_sach_CLB.csv",
    "TOANTUAN_02_chon_CLB_muon_thi.csv",
    "TOANTUAN_03_xep_hang_nguyen_vong.csv",
]

SO_HOC_SINH = 200
SO_CLB = 84
BUOI = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7", "chu_nhat"]
SO_COT_THI = len(BUOI) * TRAN_CLB_THI_MOI_BUOI      # 35


def _doc(ten):
    with io.open(os.path.join(BO, ten), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _nap(api):
    canh_bao = []
    for ten in TEN_FILE:
        with io.open(os.path.join(BO, ten), encoding="utf-8-sig") as f:
            res = api.import_csv_auto(f.read())
        assert res["ok"], (ten, res)
        canh_bao += res["data"].get("warnings") or []
    return canh_bao


def test_ca_ba_tep_ton_tai():
    for ten in TEN_FILE:
        assert os.path.exists(os.path.join(BO, ten)), ten


def test_du_bay_buoi_va_moi_buoi_tren_muoi_clb():
    dem = {}
    for c in _doc(TEN_FILE[0]):
        dem[c["buoi"]] = dem.get(c["buoi"], 0) + 1
    assert sorted(dem) == sorted(BUOI), dem
    assert sum(dem.values()) == SO_CLB, dem
    for b, n in dem.items():
        assert n > TRAN_NGUYEN_VONG_MOI_BUOI, (b, n)


def test_bay_nhan_buoi_deu_duoc_hieu_la_thu_trong_tuan():
    """Nhãn lạ vẫn chạy đúng nhưng bị sắp theo vần — im lặng và khó thấy."""
    so = [so_thu_trong_tuan(b) for b in BUOI]
    assert None not in so, dict(zip(BUOI, so))
    assert so == sorted(so), dict(zip(BUOI, so))


def test_moi_em_moi_buoi_kin_tran_nguyen_vong():
    rows = _doc(TEN_FILE[2])
    assert len(rows) == SO_HOC_SINH
    for r in rows:
        for b in BUOI:
            n = sum(1 for i in range(1, TRAN_NGUYEN_VONG_MOI_BUOI + 1)
                    if r.get("%s_pref_%d" % (b, i)))
            assert n == TRAN_NGUYEN_VONG_MOI_BUOI, (r["student_id"], b, n)


def test_moi_em_moi_buoi_kin_tran_du_thi_va_co_du_diem():
    buoi_cua = {c["club_id"]: c["buoi"] for c in _doc(TEN_FILE[0])}
    rows = _doc(TEN_FILE[1])
    assert len(rows) == SO_HOC_SINH
    for r in rows:
        theo_buoi = {}
        for i in range(1, SO_COT_THI + 1):
            cid = r.get("test_club_%d" % i)
            if not cid:
                continue
            assert r.get("score_%d" % i), (r["student_id"], cid)
            b = buoi_cua[cid]
            theo_buoi[b] = theo_buoi.get(b, 0) + 1
        for b in BUOI:
            assert theo_buoi.get(b, 0) == TRAN_CLB_THI_MOI_BUOI, (
                r["student_id"], b, theo_buoi.get(b, 0))


def test_du_thi_luon_la_tap_con_cua_nguyen_vong():
    buoi_cua = {c["club_id"]: c["buoi"] for c in _doc(TEN_FILE[0])}
    nv = {}
    for r in _doc(TEN_FILE[2]):
        for b in BUOI:
            nv[(r["student_id"], b)] = {
                r["%s_pref_%d" % (b, i)]
                for i in range(1, TRAN_NGUYEN_VONG_MOI_BUOI + 1)
                if r.get("%s_pref_%d" % (b, i))
            }
    for r in _doc(TEN_FILE[1]):
        for i in range(1, SO_COT_THI + 1):
            cid = r.get("test_club_%d" % i)
            if cid:
                assert cid in nv[(r["student_id"], buoi_cua[cid])], (
                    r["student_id"], cid)


def test_nap_khong_mot_canh_bao_nao(api):
    assert _nap(api) == []
    # Bỏ qua ĐÚNG MỘT mã: buổi ít chỗ hơn số học sinh xếp buổi đó là sự thật
    # về độ chọi (mức "info"), không phải lỗi dữ liệu. Lọc theo MÃ, không
    # theo mức, để cảnh báo "info" thêm sau này không lọt qua.
    canh_bao = [w for w in api.get_data_health_report()["data"]["warnings"]
                if w["code"] != "health_oversubscribed_buoi"]
    assert canh_bao == [], canh_bao


def test_chay_duoc_o_muc_tran_tuyet_doi(api):
    """14 000 nguyện vọng và 7 000 ô điểm — mức cao nhất còn hợp lệ."""
    _nap(api)
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    assert r["data"]["n_total"] == SO_HOC_SINH
    assert r["data"]["n_matched"] == SO_HOC_SINH


def test_bay_buoi_deu_ra_ket_qua_va_duoi_nguyen_vong_duoc_dung(api):
    _nap(api)
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    buoi_cua = {c["club_id"]: c["buoi"] for c in _doc(TEN_FILE[0])}
    with io.open(r["data"]["export_path"], encoding="utf-8-sig") as f:
        rows = [x for x in csv.DictReader(f) if x.get("club_id")]
    co = {buoi_cua[x["club_id"]] for x in rows}
    assert co == set(BUOI), co
    sau = [x for x in rows if int(x["rank_in_student_pref"]) >= 7]
    assert len(sau) >= 100, len(sau)
    assert any(int(x["rank_in_student_pref"]) == TRAN_NGUYEN_VONG_MOI_BUOI
               for x in rows)
