# -*- coding: utf-8 -*-
"""Canh BỘ KỊCH TRẦN trong `du_lieu_test/bo_kich_tran/`.

Bộ này tồn tại vì một lời hứa hẹp hơn bộ sạch: nó phải đứng **ĐÚNG** trần
10 nguyện vọng và 5 câu lạc bộ dự thi mỗi buổi — không chỉ "không vượt".
Tụt xuống 9 là nó mất lý do tồn tại, mà tụt thì không cảnh báo nào kêu:
phần mềm chỉ hỏi "có quá không", không hỏi "đã đủ chưa". Vậy nên phải có
test canh.

Canh cả hai phía của ranh giới:

  * `bo_kich_tran/`           — đúng trần   -> nhận, không một cảnh báo
  * `bo_kich_tran/vuot_tran/` — quá một đơn vị -> bỏ ĐÚNG buổi sai của
    ĐÚNG em sai, không bỏ cả em, không bỏ cả tệp

Phía thứ hai mới là phía dễ hỏng lặng lẽ: đổi phạm vi từ chối từ "một
buổi" thành "cả học sinh" vẫn làm mọi test cảnh báo hiện có xanh, vì số
cảnh báo không đổi — chỉ test này thấy.
"""

import csv
import io
import os

import pytest

from rbda_priority_pipeline import (
    TRAN_CLB_THI_MOI_BUOI,
    TRAN_NGUYEN_VONG_MOI_BUOI,
)

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO = os.path.join(_GOC, "du_lieu_test", "bo_kich_tran")
BO_SAI = os.path.join(BO, "vuot_tran")

TEN_FILE = [
    "KICHTRAN_01_danh_sach_CLB.csv",
    "KICHTRAN_02_chon_CLB_muon_thi.csv",
    "KICHTRAN_03_xep_hang_nguyen_vong.csv",
]
TEN_FILE_SAI = [
    "VUOTTRAN_01_danh_sach_CLB.csv",
    "VUOTTRAN_02_chon_CLB_muon_thi.csv",
    "VUOTTRAN_03_xep_hang_nguyen_vong.csv",
]

SO_HOC_SINH = 150
SO_CLB = 36
BUOI = ["thu_2", "thu_4", "thu_6"]


def _doc(thu_muc, ten):
    with io.open(os.path.join(thu_muc, ten), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _nap(api, thu_muc, ds_ten):
    """Nạp cả ba tệp theo đúng thứ tự, trả về danh sách cảnh báo."""
    canh_bao = []
    for ten in ds_ten:
        with io.open(os.path.join(thu_muc, ten), encoding="utf-8-sig") as f:
            res = api.import_csv_auto(f.read())
        assert res["ok"], (ten, res)
        canh_bao += res["data"].get("warnings") or []
    return canh_bao


def _buoi_cua_clb(thu_muc, ten_clb):
    return {c["club_id"]: c["buoi"] for c in _doc(thu_muc, ten_clb)}


# ---------------------------------------------------------------------------
# Bộ chính — đứng đúng trần
# ---------------------------------------------------------------------------

def test_ca_ba_tep_ton_tai():
    for ten in TEN_FILE:
        assert os.path.exists(os.path.join(BO, ten)), ten


def test_moi_buoi_phai_co_TREN_muoi_clb():
    """Không có điều này thì trần thật là số CLB, không phải con số 10."""
    dem = {}
    for c in _doc(BO, TEN_FILE[0]):
        dem[c["buoi"]] = dem.get(c["buoi"], 0) + 1
    assert sorted(dem) == BUOI, dem
    for b, n in dem.items():
        assert n > TRAN_NGUYEN_VONG_MOI_BUOI, (b, n)


def test_cham_dung_tran_nguyen_vong():
    cham = 0
    for r in _doc(BO, TEN_FILE[2]):
        for b in BUOI:
            n = sum(1 for i in range(1, TRAN_NGUYEN_VONG_MOI_BUOI + 1)
                    if r.get("%s_pref_%d" % (b, i)))
            assert n <= TRAN_NGUYEN_VONG_MOI_BUOI, (r["student_id"], b, n)
            cham = max(cham, n)
    assert cham == TRAN_NGUYEN_VONG_MOI_BUOI, cham


def test_cham_dung_tran_du_thi():
    buoi_cua = _buoi_cua_clb(BO, TEN_FILE[0])
    cham = 0
    for r in _doc(BO, TEN_FILE[1]):
        theo_buoi = {}
        for i in range(1, 16):
            cid = r.get("test_club_%d" % i)
            if not cid:
                continue
            assert r.get("score_%d" % i), (r["student_id"], cid)
            b = buoi_cua[cid]
            theo_buoi[b] = theo_buoi.get(b, 0) + 1
        for b, n in theo_buoi.items():
            assert n <= TRAN_CLB_THI_MOI_BUOI, (r["student_id"], b, n)
            cham = max(cham, n)
    assert cham == TRAN_CLB_THI_MOI_BUOI, cham


def test_du_thi_luon_la_tap_con_cua_nguyen_vong():
    """Thi một CLB không xếp nguyện vọng là lượt thi bỏ phí."""
    buoi_cua = _buoi_cua_clb(BO, TEN_FILE[0])
    nv = {}
    for r in _doc(BO, TEN_FILE[2]):
        for b in BUOI:
            nv[(r["student_id"], b)] = {
                r["%s_pref_%d" % (b, i)]
                for i in range(1, TRAN_NGUYEN_VONG_MOI_BUOI + 1)
                if r.get("%s_pref_%d" % (b, i))
            }
    for r in _doc(BO, TEN_FILE[1]):
        for i in range(1, 16):
            cid = r.get("test_club_%d" % i)
            if cid:
                assert cid in nv[(r["student_id"], buoi_cua[cid])], (
                    r["student_id"], cid)


def test_nap_khong_mot_canh_bao_nao(api):
    assert _nap(api, BO, TEN_FILE) == []
    # Bỏ qua ĐÚNG MỘT mã: buổi ít chỗ hơn số học sinh xếp buổi đó là sự thật
    # về độ chọi (mức "info"), không phải lỗi dữ liệu. Lọc theo MÃ, không
    # theo mức, để cảnh báo "info" thêm sau này không lọt qua.
    canh_bao = [w for w in api.get_data_health_report()["data"]["warnings"]
                if w["code"] != "health_oversubscribed_buoi"]
    assert canh_bao == [], canh_bao


def test_chay_duoc_va_moi_em_co_it_nhat_mot_clb(api):
    _nap(api, BO, TEN_FILE)
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    assert r["data"]["n_total"] == SO_HOC_SINH
    assert r["data"]["n_matched"] == SO_HOC_SINH


def test_duoi_danh_sach_nguyen_vong_thuc_su_duoc_dung(api):
    """Lý do bộ này đáng có: nguyện vọng 7-10 phải nhận được suất thật.

    Bộ mẫu nào cũng chứng minh được nguyện vọng 1-3 chạy. Chưa bộ nào
    chạm tới vùng đuôi, mà đuôi mới là chỗ thuật toán đẩy dây chuyền.
    """
    _nap(api, BO, TEN_FILE)
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    with io.open(r["data"]["export_path"], encoding="utf-8-sig") as f:
        rows = [x for x in csv.DictReader(f) if x.get("club_id")]
    sau = [x for x in rows if int(x["rank_in_student_pref"]) >= 7]
    assert len(sau) >= 30, len(sau)
    assert any(int(x["rank_in_student_pref"]) == TRAN_NGUYEN_VONG_MOI_BUOI
               for x in rows)


# ---------------------------------------------------------------------------
# Bộ vuot_tran — quá trần một đơn vị
# ---------------------------------------------------------------------------

def test_bo_vuot_tran_ton_tai():
    for ten in TEN_FILE_SAI:
        assert os.path.exists(os.path.join(BO_SAI, ten)), ten


def test_vuot_tran_bo_dung_buoi_sai_cua_dung_em_sai(api):
    canh_bao = _nap(api, BO_SAI, TEN_FILE_SAI)
    ma = {(w["code"], w["params"].get("student_id"), w["params"].get("buoi"))
          for w in canh_bao if isinstance(w, dict) and w.get("params")}

    assert ("csv_pref_bo_buoi_qua_tran", "HS001", "thu_2") in ma, canh_bao
    assert ("csv_thi_bo_buoi_qua_tran", "HS002", "thu_4") in ma, canh_bao
    assert ("csv_pref_bo_buoi_qua_tran", "HS003", "thu_6") in ma, canh_bao
    assert ("csv_thi_bo_buoi_qua_tran", "HS003", "thu_6") in ma, canh_bao
    for b in BUOI:
        assert ("csv_pref_bo_buoi_qua_tran", "HS004", b) in ma, canh_bao
    # Hai em khai đúng trần KHÔNG được dính cảnh báo nào.
    assert not [w for w in canh_bao
                if isinstance(w, dict)
                and w.get("params", {}).get("student_id") in ("HS005", "HS006")]


@pytest.mark.parametrize("sid,buoi_mat", [
    ("HS001", {"thu_2"}),          # quá nguyện vọng -> mất nguyện vọng buổi đó
    ("HS003", {"thu_6"}),
    ("HS004", set(BUOI)),          # quá cả ba buổi -> mất trắng
    ("HS005", set()),              # đúng trần -> nguyên vẹn
])
def test_vuot_tran_chi_mat_nguyen_vong_cua_buoi_sai(api, sid, buoi_mat):
    _nap(api, BO_SAI, TEN_FILE_SAI)
    buoi_cua = _buoi_cua_clb(BO_SAI, TEN_FILE_SAI[0])
    dem = {}
    with api._ket_noi_doc() as cur:
        cur.execute("SELECT club_id FROM preferences WHERE student_id = ?", (sid,))
        for r in cur.fetchall():
            b = buoi_cua[r["club_id"]]
            dem[b] = dem.get(b, 0) + 1
    for b in BUOI:
        if b in buoi_mat:
            assert dem.get(b, 0) == 0, (sid, b, dem)
        else:
            assert dem.get(b, 0) > 0, (sid, b, dem)


def test_vuot_tran_bo_ca_diem_cua_buoi_bi_bo(api):
    """Giữ điểm của một CLB em không còn dự thi chỉ tạo ra dòng mồ côi."""
    _nap(api, BO_SAI, TEN_FILE_SAI)
    buoi_cua = _buoi_cua_clb(BO_SAI, TEN_FILE_SAI[0])
    dem = {}
    with api._ket_noi_doc() as cur:
        cur.execute("SELECT club_id FROM club_scores WHERE student_id = 'HS002'")
        for r in cur.fetchall():
            b = buoi_cua[r["club_id"]]
            dem[b] = dem.get(b, 0) + 1
    assert dem.get("thu_4", 0) == 0, dem
    assert dem.get("thu_2", 0) == TRAN_CLB_THI_MOI_BUOI, dem
    assert dem.get("thu_6", 0) == TRAN_CLB_THI_MOI_BUOI, dem
