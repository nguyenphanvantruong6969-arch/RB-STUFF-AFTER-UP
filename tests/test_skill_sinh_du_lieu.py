# -*- coding: utf-8 -*-
"""Canh bộ sinh dữ liệu đầu vào của skill `sinh-du-lieu-clb`.

Một bộ sinh dữ liệu mà sinh ra dữ liệu phần mềm không nuốt được thì tệ hơn
không có: người dùng tin nó, mang bộ dữ liệu đi, rồi mới phát hiện hỏng ở
bước nhập — lúc đó không biết lỗi ở bộ sinh hay ở tay mình.

Nên phép kiểm ở đây KHÔNG phải là "đoạn mã chạy không lỗi". Phép kiểm là
**nhập bộ nó vừa sinh vào chính phần mềm, và đếm cảnh báo**. Tiêu chuẩn: 0
cảnh báo khi nhập, 0 cảnh báo sức khoẻ dữ liệu, chạy phân bổ được.

BA BẢO ĐẢM của bộ sinh, và ĐỐI CHỨNG NGƯỢC cho từng cái — đã chạy thật:

| Bỏ bảo đảm nào | Kết quả |
|---|---|
| chỉ gán nhóm dự trữ mà **có câu lạc bộ đặt suất** | 3 test ĐỎ (`csv_reserve_group_unknown`, `health_orphan_student_group`) |
| mỗi em **ít nhất một nguyện vọng** cả tuần | 2 test ĐỎ (`health_student_no_preferences`) |
| nhóm nào có câu lạc bộ đặt suất thì **phải có người** | 1 test ĐỎ (`health_club_group_no_students`) |

Cả ba lỗi đó **không lỗi cú pháp, không ném exception, không sai lược đồ**.
Chỉ phép kiểm "nhập vào phần mềm thật rồi đếm cảnh báo" mới thấy chúng — đó
là lý do tệp này không kiểm bằng cách đọc CSV mà kiểm bằng cách chạy phần mềm.
"""

import base64
import importlib.util
import io
import json
import os
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(GOC, ".claude", "skills", "sinh-du-lieu-clb",
                      "scripts", "sinh_du_lieu.py")


@pytest.fixture(scope="module")
def sdl():
    """Nạp đoạn mã của skill như một module."""
    if not os.path.exists(SCRIPT):
        pytest.skip("khong thay script cua skill")
    spec = importlib.util.spec_from_file_location("sinh_du_lieu", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _nhap_va_dem_canh_bao(api, thu_muc):
    """Nạp Sổ nhập CLB qua đúng cửa giao diện dùng.
    Trả (tổng cảnh báo khi nhập, cảnh báo sức khoẻ dữ liệu)."""
    with open(os.path.join(thu_muc, "SO_NHAP_CLB.xlsx"), "rb") as f:
        kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert kq["ok"], kq
    tong = len(kq["data"].get("warnings") or [])
    # Bo qua DUNG MOT ma: buoi it cho hon so em xep buoi do. Do la su that
    # ve do choi, khong phai loi du lieu — bo sinh ra co y chat cho de ket qua
    # co nghia. Loc theo MA chu khong theo muc "info": loc theo muc thi moi
    # canh bao "info" them sau nay cung lot qua ma khong ai hay.
    canh_bao = api.get_data_health_report()["data"]["warnings"]
    return tong, sum(1 for w in canh_bao
                     if w["code"] != "health_oversubscribed_buoi")


# ------------------------------------------------------------------ #
# PHÉP KIỂM CHÍNH: phần mềm thật có nuốt được không
# ------------------------------------------------------------------ #

# Bon cau hinh chon co chu y, khong phai chon bua:
#   - truong TI HON (12 em): moi loi "nhom mo coi" deu lo ra o day, vi xac
#     suat 22% gan nhom tren 12 em rat de boc ra thieu mot nhom;
#   - truong mot buoi: nhanh `pref_N` khac han nhanh `<buoi>_pref_N`;
#   - truong 6 buoi: nhieu buoi nhat, nhieu cau lac bo nhat;
#   - truong 200 em: kich thuoc that.
# Da quet rong hon truoc khi chot: 160 cau hinh (12/20/60/200 em x 5 cach
# chia buoi x 2-3 CLB moi buoi x 4 hat giong) — 0 cau hinh hong.
@pytest.mark.parametrize("n_hs,ds_buoi,seed", [
    (12, ["thu_2", "thu_4"], 99),
    (40, [""], 5),
    (90, ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7"], 7),
    (200, ["thu_2", "thu_4", "thu_6"], 42),
    # Cau hinh nay co mat vi MOT ly do: no la cau hinh duy nhat trong 160 cau
    # da quet lam lo bao dam "nhom nao co cau lac bo dat suat thi phai co
    # nguoi". 20 em x 22% co nhom, boc ra toan mot nhom -> ba cau lac bo giu
    # cho cho mot dien khong ai thuoc. Bo cau hinh nay di la bao dam do het
    # duoc canh.
    (20, ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7"], 99),
])
def test_bo_ngau_nhien_nhap_sach(sdl, api, tmp_path, n_hs, ds_buoi, seed):
    """Phép kiểm thật: nhập vào phần mềm và đếm cảnh báo."""
    clb, hs = sdl.sinh_ngau_nhien(n_hs, ds_buoi, 3, seed)
    assert sdl.soat(clb, hs) == []
    ra = str(tmp_path / "bo")
    sdl.ghi_bo(ra, clb, hs)

    n_nhap, n_suc_khoe = _nhap_va_dem_canh_bao(api, ra)
    assert n_nhap == 0, "sinh ra du lieu lam phan mem canh bao khi nhap"
    assert n_suc_khoe == 0

    kq = api.run_pipeline(seed=42)
    assert kq["ok"], kq
    qua = [c for c in api.get_club_fill_stats()["data"]
           if c["matched"] > c["capacity"]]
    assert qua == []


def test_truong_mot_buoi_cung_nhap_sach(sdl, api, tmp_path):
    """Trường một buổi: cột Buổi của sổ để trống hết."""
    clb, hs = sdl.sinh_ngau_nhien(40, [""], 3, seed=5)
    ra = str(tmp_path / "bo1")
    assert sdl.ghi_bo(ra, clb, hs) == [os.path.join(ra, "SO_NHAP_CLB.xlsx")]
    assert os.listdir(ra) == ["SO_NHAP_CLB.xlsx"], "chi duoc ghi MOT tep"

    clb_doc, hs_doc = sdl.doc_bo(ra)
    assert {c["buoi"] for c in clb_doc} == {""}, "truong mot buoi khong duoc co buoi"
    assert len(hs_doc) == 40

    n_nhap, n_suc_khoe = _nhap_va_dem_canh_bao(api, ra)
    assert (n_nhap, n_suc_khoe) == (0, 0)


def test_cung_hat_giong_cho_ra_cung_bo(sdl):
    """Tất định — nếu không thì không tái lập được một lần đo nào."""
    a = sdl.sinh_ngau_nhien(30, ["thu_2", "thu_4"], 2, seed=9)
    b = sdl.sinh_ngau_nhien(30, ["thu_2", "thu_4"], 2, seed=9)
    assert a == b


# ------------------------------------------------------------------ #
# BỘ SOÁT: bắt được cái gì
# ------------------------------------------------------------------ #

def test_soat_bat_ma_clb_khong_co_that(sdl):
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"}]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"thu_2": ["clb_khong_co"]}, "diem": {}}]
    loi = sdl.soat(clb, hs)
    assert any("clb_khong_co" in e for e in loi), loi


def test_soat_bat_clb_nam_sai_cot_buoi(sdl):
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_4"}]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"thu_2": ["clb_a"]}, "diem": {}}]
    assert any("thu_2" in e and "thu_4" in e for e in sdl.soat(clb, hs))


def test_soat_bat_hai_tran_moi_buoi(sdl):
    clb = [{"club_id": "c%02d" % i, "name": "C", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"}
           for i in range(12)]
    ma = [c["club_id"] for c in clb]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"thu_2": ma[:11]},          # 11 > tran 10
           "diem": {c: "8,0" for c in ma[:6]}}]        # 6  > tran 5
    loi = sdl.soat(clb, hs)
    assert any("vượt trần %d" % sdl.TRAN_NGUYEN_VONG_MOI_BUOI in e for e in loi), loi
    assert any("vượt trần %d" % sdl.TRAN_CLB_THI_MOI_BUOI in e for e in loi), loi


def test_soat_bat_diem_cho_clb_em_khong_khai_nguyen_vong(sdl):
    """Điểm không dùng tới — và gần như chắc chắn là gõ lệch cột."""
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"},
           {"club_id": "clb_b", "name": "B", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"}]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"thu_2": ["clb_a"]}, "diem": {"clb_b": "8,0"}}]
    assert any("clb_b" in e for e in sdl.soat(clb, hs))


def test_soat_bat_du_tru_lon_hon_suc_chua_va_thieu_nhom(sdl):
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 3,
            "reserve_capacity": 5, "reserve_group": "chinh_sach", "buoi": ""},
           {"club_id": "clb_b", "name": "B", "capacity": 5,
            "reserve_capacity": 2, "reserve_group": "", "buoi": ""}]
    loi = sdl.soat(clb, [])
    assert any("lớn hơn sức chứa" in e for e in loi), loi
    assert any("không ghi nhóm dự trữ" in e for e in loi), loi


def test_soat_bat_khai_buoi_nua_voi(sdl):
    """Khai buổi cho một nửa câu lạc bộ thì nửa kia bị gom chung một buổi."""
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"},
           {"club_id": "clb_b", "name": "B", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": ""}]
    assert any("khai thì phải khai hết" in e for e in sdl.soat(clb, []))


def test_soat_bat_ma_hoc_sinh_trung(sdl):
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": ""}]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"": ["clb_a"]}, "diem": {}}] * 2
    assert any("trùng" in e for e in sdl.soat(clb, hs))


# ------------------------------------------------------------------ #
# SAI THÌ KHÔNG GHI TỆP NÀO
# ------------------------------------------------------------------ #

def test_spec_sai_thi_khong_ghi_tep_nao(sdl, tmp_path):
    """Một bộ dữ liệu hỏng còn tệ hơn không có, vì nó trông y như thật."""
    spec = {
        "cau_lac_bo": [{"club_id": "clb_a", "name": "A", "capacity": 0,
                        "reserve_capacity": 0, "reserve_group": "",
                        "buoi": "thu_2"}],
        "hoc_sinh": [{"student_id": "HS1", "name": "X", "reserve_group": "",
                      "nguyen_vong": {"thu_2": ["clb_a"]}, "diem": {}}],
    }
    p = tmp_path / "spec.json"
    with io.open(str(p), "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False)
    ra = tmp_path / "ra"

    ma = sdl.main(["tao", "--spec", str(p), "--ra", str(ra)])
    assert ma != 0, "spec sai ma van tra ve ma thoat 0"
    assert not ra.exists() or list(ra.iterdir()) == [], "da ghi tep du spec sai"


def test_soat_bo_mau_da_kiem_chung(sdl):
    """Bộ `mau_csv/vi_du_day_du/` (cả sổ lẫn bộ ba CSV) phải qua được chính
    bộ soát này — hai thứ nói về cùng một định dạng thì không được mâu thuẫn."""
    bo = os.path.join(GOC, "mau_csv", "vi_du_day_du")
    if not os.path.isdir(bo):
        pytest.skip("chua co bo mau")
    clb, hs = sdl.doc_bo(os.path.join(bo, "SO_NHAP_CLB_vi_du.xlsx"))
    assert sdl.soat(clb, hs) == []
    assert len(clb) == 9 and len(hs) == 24


def test_vong_tron_ghi_roi_doc_lai_so(sdl, tmp_path):
    clb, hs = sdl.sinh_ngau_nhien(30, ["thu_2", "thu_5"], 3, seed=3)
    ra = str(tmp_path / "vt")
    sdl.ghi_bo(ra, clb, hs)
    clb2, hs2 = sdl.doc_bo(ra)
    assert [c["club_id"] for c in clb2] == [c["club_id"] for c in clb]
    goc = {h["student_id"]: h for h in hs}
    for h in hs2:
        g = goc[h["student_id"]]
        assert {b: ds for b, ds in h["nguyen_vong"].items()} == \
            {b: ds for b, ds in g["nguyen_vong"].items() if ds}
        assert set(h["diem"]) == set(g["diem"])


# ------------------------------------------------------------------ #
# SKILL.md phải mô tả đúng đoạn mã đi kèm
# ------------------------------------------------------------------ #

def test_skill_md_neu_dung_hai_tran(sdl):
    p = os.path.join(os.path.dirname(os.path.dirname(SCRIPT)), "SKILL.md")
    with io.open(p, encoding="utf-8") as f:
        s = f.read()
    assert "%d nguyện vọng mỗi buổi" % sdl.TRAN_NGUYEN_VONG_MOI_BUOI in s
    assert "%d câu lạc bộ dự thi mỗi buổi" % sdl.TRAN_CLB_THI_MOI_BUOI in s


def test_tran_trong_skill_khop_voi_tran_cua_phan_mem(sdl):
    """Trần do phần mềm áp, không phải do bộ sinh nghĩ ra. Hai bên trôi khỏi
    nhau thì bộ sinh sẽ đẻ ra dữ liệu bị phần mềm gạt."""
    sys.path.insert(0, GOC)
    import rbda_priority_pipeline as loi
    assert sdl.TRAN_NGUYEN_VONG_MOI_BUOI == loi.TRAN_NGUYEN_VONG_MOI_BUOI
    assert sdl.TRAN_CLB_THI_MOI_BUOI == loi.TRAN_CLB_THI_MOI_BUOI
