"""Canh các kịch bản tham khảo của gói kế hoạch (docs/ke_hoach/tham_khao/).

`de_xuat_verify_nhanh.verify_stability_nhanh` là bản sẽ thay `verify_stability`
ở mục Z4, và `exp_resume.resume_da` là nguyên mẫu của mục G1. Cả hai phải cho
ĐÚNG kết quả của mã thật, kể cả ở các ca biên mà bộ sinh dữ liệu đo đạc không
tạo ra: em đang giữ chỗ mà không có trong base_rank, CLB thừa / thiếu người,
sức chứa sai, nguyện vọng trỏ tới CLB không có, CLB mới sau lần chạy cũ.
`_chung.nap_rb` và `_chung.gen` cũng được kiểm ở đây.

Không dùng numpy (không phải phụ thuộc sản phẩm; test của `gen` tự bỏ qua khi
thiếu). Nạp các kịch bản theo đường dẫn, không sửa sys.path của cả phiên test.
Dữ liệu ở đây là dữ liệu MÔ PHỎNG, sinh ngẫu nhiên có hạt giống.
"""
import dataclasses
import importlib.util
import os
import random
import sys

import pytest

import rbda_priority_pipeline as rb

_GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_THAM_KHAO = os.path.join(_GOC, "docs", "ke_hoach", "tham_khao")


# Nạp exp_resume theo đường dẫn; dùng lại đúng bản _chung mà nó đã nạp (một bản trong tiến trình).
_spec = importlib.util.spec_from_file_location("test_tham_khao_exp_resume", os.path.join(_THAM_KHAO, "exp_resume.py"))
exp_resume = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp_resume)
exp_resume.rb = rb
_chung = exp_resume._chung
verify_stability_nhanh = _chung.nap_canh("de_xuat_verify_nhanh", "test_tham_khao_").verify_stability_nhanh


# ---------------------------------------------------------------------------
# Dữ liệu
# ---------------------------------------------------------------------------
def _sinh(seed, n_hs=60, n_clb=5, ty_le=0.7, n_nv=4, du_tru="mot_phan", ngoai_apps=0.0):
    """Bộ dữ liệu nhỏ: CLB đầy, có dự trữ, có em thi và em không thi.

    ngoai_apps: tỉ lệ (em, CLB trong nguyện vọng) KHÔNG được ghi vào apps của CLB
    — ca thật khi dữ liệu nhập lệch: run_rbda vẫn nhận em nhưng em không có thứ hạng.
    """
    rng = random.Random(seed)
    cids = ["c%d" % j for j in range(n_clb)]
    cap = max(2, int(n_hs * ty_le / n_clb))
    rc = {"khong": 0, "mot_phan": cap // 3, "het": cap}[du_tru]
    clubs = {c: {"capacity": cap, "reserve_capacity": rc,
                 "reserve_group": "cs" if j % 2 == 0 else None}
             for j, c in enumerate(cids)}
    students, prefs = {}, {}
    tested = {c: {} for c in cids}
    apps = {c: [] for c in cids}
    for i in range(n_hs):
        sid = "s%03d" % i
        students[sid] = {"reserve_group": "cs" if rng.random() < 0.3 else None}
        ds = rng.sample(cids, n_nv)
        prefs[sid] = ds
        for c in ds[:2]:
            tested[c][sid] = rng.randint(0, 20) / 2
        for c in ds:
            if rng.random() >= ngoai_apps:
                apps[c].append(sid)
    stb = rb.generate_stb_lottery(list(students), seed)
    fn = rb.default_reserve_eligible_fn(students, clubs)
    res = rb.run_rbda(students, clubs, tested, apps, prefs, stb, fn)
    return students, clubs, tested, apps, prefs, stb, fn, res


def _khoa(p):
    q = p["params"]
    return (q["student_id"], q["club_id"], q["current_club"], q["n_holders"], q["capacity"])


def _so_sanh(res, clubs, prefs, fn):
    """Hai bản phải cho cùng danh sách cặp phá vỡ; trả số cặp để test khỏi so hai danh sách rỗng."""
    a = rb.verify_stability(res, clubs, prefs, fn)
    b = verify_stability_nhanh(res, clubs, prefs, fn)
    assert sorted(map(_khoa, a)) == sorted(map(_khoa, b))
    return len(a)


def _bien_doi(res, clubs, rng, so_lan):
    """Làm hỏng kết quả: đổi chỗ, bỏ chỗ, chuyển em sang CLB khác (CLB thừa và thiếu người)."""
    asg = dict(res.assignment)
    ds_hs = list(asg)
    ds_clb = list(clubs)
    for _ in range(so_lan):
        kieu = rng.randrange(3)
        if kieu == 0:
            a, b = rng.sample(ds_hs, 2)
            asg[a], asg[b] = asg[b], asg[a]
        elif kieu == 1:
            asg[rng.choice(ds_hs)] = None
        else:
            asg[rng.choice(ds_hs)] = rng.choice(ds_clb)
    return dataclasses.replace(res, assignment=asg)


# ---------------------------------------------------------------------------
# verify_stability_nhanh == verify_stability
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("du_tru", ["khong", "mot_phan", "het"])
@pytest.mark.parametrize("seed", range(15))
def test_ban_nhanh_trung_ban_goc(seed, du_tru):
    _, clubs, _, _, prefs, _, fn, res = _sinh(seed, du_tru=du_tru)
    assert _so_sanh(res, clubs, prefs, fn) == 0      # kết quả thật của DA: ổn định
    _so_sanh(_bien_doi(res, clubs, random.Random(seed), 25), clubs, prefs, fn)


def test_phep_so_sanh_khong_rong():
    # Không để các test trên qua chỉ vì hai bản cùng trả danh sách rỗng.
    co_cap = sum(
        _so_sanh(_bien_doi(r, c, random.Random(s), 25), c, p, f) > 0
        for s in range(15)
        for (_, c, _, _, p, _, f, r) in [_sinh(s)])
    assert co_cap >= 12


@pytest.mark.parametrize("seed", range(15))
def test_em_trong_nguyen_vong_nhung_khong_trong_apps(seed):
    # Ca thật: em có trong nguyện vọng của CLB nhưng không có trong apps -> run_rbda vẫn có
    # thể xếp em vào CLB đó dù em không có thứ hạng (club_choice_function xếp em cuối).
    _, clubs, _, _, prefs, _, fn, res = _sinh(seed, ngoai_apps=0.25)
    _so_sanh(res, clubs, prefs, fn)
    _so_sanh(_bien_doi(res, clubs, random.Random(seed), 25), clubs, prefs, fn)


def test_ca_em_giu_cho_khong_thu_hang_that_su_xuat_hien():
    # Tiền đề của test trên: dữ liệu sinh ra phải có em đang giữ chỗ mà không có thứ hạng.
    tong = 0
    for seed in range(15):
        _, _, _, _, _, _, _, res = _sinh(seed, ngoai_apps=0.25)
        tong += sum(1 for s, c in res.assignment.items()
                    if c is not None and s not in res.base_rank[c])
    assert tong > 0


def test_thu_hang_trung_khi_xoa_bot_base_rank():
    # Xoá em khỏi base_rank làm len(rank) trùng thứ hạng một em khác: sắp xếp ổn định của
    # club_choice_function đặt ứng viên SAU các em trùng — bản nhanh dùng bisect_right.
    _, clubs, _, _, prefs, _, fn, res = _sinh(7)
    co_cho = [s for s, c in res.assignment.items() if c is not None]
    for s in co_cho[:5]:
        res.base_rank[res.assignment[s]].pop(s, None)
    so_cap = _so_sanh(_bien_doi(res, clubs, random.Random(7), 25), clubs, prefs, fn)
    assert so_cap > 0


@pytest.mark.parametrize("reserve_capacity", [-1, 999])
def test_suc_chua_sai_thi_ca_hai_ban_bao_cung_loi(reserve_capacity):
    _, clubs, _, _, prefs, _, fn, res = _sinh(3)
    res = _bien_doi(res, clubs, random.Random(3), 25)
    for info in clubs.values():
        info["reserve_capacity"] = reserve_capacity
    with pytest.raises(ValueError) as goc:
        rb.verify_stability(res, clubs, prefs, fn)
    with pytest.raises(ValueError) as nhanh:
        verify_stability_nhanh(res, clubs, prefs, fn)
    assert str(goc.value) == str(nhanh.value)


def test_ban_nhanh_khong_doc_clb_khong_ai_xet_toi():
    # Bản gốc chỉ đọc capacity / gọi hàm đủ tư cách của CLB có ứng viên muốn chuyển tới.
    _, clubs, _, _, prefs, _, fn, res = _sinh(5)
    clubs = dict(clubs, c_le={"capacity": 1})        # thiếu reserve_capacity, không ai xếp
    res.base_rank["c_le"] = {}

    def fn2(s, c):
        if c == "c_le":
            raise AssertionError("không được gọi cho CLB không ai xét tới")
        return fn(s, c)
    assert rb.verify_stability(res, clubs, prefs, fn2) == verify_stability_nhanh(res, clubs, prefs, fn2)


def test_ham_du_tu_cach_loi_o_ung_vien_thi_ca_hai_ban_cung_bao_loi():
    _, clubs, _, _, prefs, _, fn, res = _sinh(6)
    res = _bien_doi(res, clubs, random.Random(6), 25)
    nan = next(s for s, ds in prefs.items() for c in ds[:1] if res.assignment.get(s) != c and s in res.base_rank[c])

    def fn2(s, c):
        if s == nan:
            raise KeyError(s)
        return fn(s, c)
    with pytest.raises(KeyError):
        rb.verify_stability(res, clubs, prefs, fn2)
    with pytest.raises(KeyError):
        verify_stability_nhanh(res, clubs, prefs, fn2)


# ---------------------------------------------------------------------------
# exp_resume.resume_da == chạy lại toàn bộ run_rbda (khi tiền đề thoả), từ chối khi không thoả
# ---------------------------------------------------------------------------
def _du_lieu(students, clubs, tested, apps, prefs, stb):
    return dict(students=students, clubs=clubs, tested=tested, apps=apps, prefs=prefs, stb=stb)


def _them_em_moi(seed, so_moi=6, clb_moi=False, giam_suc_chua=0, em_khong_nv=False):
    """Dữ liệu cũ (+ res0) và dữ liệu mới hợp lệ cho G1: em mới, CLB mới chỉ em mới xếp, giảm sức chứa."""
    students, clubs, tested, apps, prefs, stb, fn, res0 = _sinh(seed)
    cu = _du_lieu(students, clubs, tested, apps, prefs, stb)
    rng = random.Random(1000 + seed)
    moi_ids = ["n%d" % i for i in range(so_moi)]
    stb2 = rb.chen_stb_cho_hoc_sinh_moi(sorted(students, key=lambda s: stb[s]), moi_ids, seed)
    clubs2 = {c: dict(v) for c, v in clubs.items()}
    for c in list(clubs2)[:giam_suc_chua]:
        clubs2[c]["capacity"] = max(clubs2[c]["reserve_capacity"], clubs2[c]["capacity"] - 2, 1)
    if clb_moi:
        clubs2["c_moi"] = {"capacity": 3, "reserve_capacity": 1, "reserve_group": "cs"}
    st2 = {s: dict(v) for s, v in students.items()}
    pf2 = dict(prefs)
    te2 = {c: dict(v) for c, v in tested.items()}
    ap2 = {c: list(v) for c, v in apps.items()}
    for c in clubs2:
        te2.setdefault(c, {})
        ap2.setdefault(c, [])
    for i, n in enumerate(moi_ids):
        # Em mới có diện dự trữ, có điểm thi (tầng 1) để đẩy em cũ; có nguyện vọng trỏ tới CLB
        # không tồn tại ("khong_co") phải bị bỏ qua như run_rbda.
        st2[n] = {"reserve_group": "cs" if i % 2 == 0 else None}
        if em_khong_nv and i == 0:
            continue                              # em mới không có dòng nguyện vọng
        ds = rng.sample(list(clubs2), 3)
        pf2[n] = ["khong_co"] + ds
        for c in ds:
            ap2[c].append(n)
            te2[c][n] = 10.0
    moi = _du_lieu(st2, clubs2, te2, ap2, pf2, stb2)
    return cu, moi, moi_ids, res0


def _chay_lai(moi):
    fn = rb.default_reserve_eligible_fn(moi["students"], moi["clubs"])
    kq = rb.run_rbda(moi["students"], moi["clubs"], moi["tested"], moi["apps"], moi["prefs"], moi["stb"], fn)
    return {s: c for s, c in kq.assignment.items() if c is not None}


@pytest.mark.parametrize("bien_the", [
    {}, {"clb_moi": True}, {"giam_suc_chua": 2}, {"em_khong_nv": True},
    {"clb_moi": True, "giam_suc_chua": 3, "em_khong_nv": True}])
@pytest.mark.parametrize("seed", range(12))
def test_tiep_tuc_da_trung_chay_lai_toan_bo(seed, bien_the):
    cu, moi, moi_ids, res0 = _them_em_moi(seed, **bien_the)
    asg, _ = exp_resume.resume_da(res0, cu, moi, moi_ids)
    assert asg == _chay_lai(moi)


def test_tiep_tuc_da_thuc_su_doi_cho_em_cu():
    # Tiền đề cho test trên: các ca có em cũ bị đẩy đi, có em mới được xếp (không so hai thứ rỗng).
    doi = xep_moi = 0
    for seed in range(12):
        cu, moi, moi_ids, res0 = _them_em_moi(seed, giam_suc_chua=2)
        asg, _ = exp_resume.resume_da(res0, cu, moi, moi_ids)
        doi += sum(1 for s, c in res0.assignment.items() if asg.get(s) != c)
        xep_moi += sum(1 for n in moi_ids if n in asg)
    assert doi > 0 and xep_moi > 0


def _sua(ham):
    def lam(cu, moi, moi_ids, res0):
        ham(cu, moi, moi_ids, res0)
        return cu, moi, moi_ids, res0
    return lam


_VI_PHAM = {
    "em_moi_trung_em_cu": (_sua(lambda cu, moi, ids, r: ids.append("s001")), "lần chạy cũ"),
    "new_ids_trung": (_sua(lambda cu, moi, ids, r: ids.append(ids[0])), "trùng"),
    "dong_clb": (_sua(lambda cu, moi, ids, r: moi["clubs"].pop("c0")), "đóng"),
    "tang_suc_chua": (_sua(lambda cu, moi, ids, r: moi["clubs"]["c0"].update(capacity=99)), "tăng"),
    "doi_du_tru": (_sua(lambda cu, moi, ids, r: moi["clubs"]["c1"].update(reserve_capacity=0)), "dự trữ"),
    "doi_nguyen_vong_em_cu": (_sua(lambda cu, moi, ids, r: moi["prefs"].update(s001=["c0"])), "nguyện vọng"),
    "doi_diem_em_cu": (_sua(lambda cu, moi, ids, r: moi["tested"]["c0"].update(
        {next(iter(cu["tested"]["c0"])): 99.0})), "điểm"),
    "doi_nhom_em_cu": (_sua(lambda cu, moi, ids, r: moi["students"]["s001"].update(reserve_group="khac")), "nhóm"),
    "thieu_apps": (_sua(lambda cu, moi, ids, r: moi["apps"][moi["prefs"]["s001"][0]].remove("s001")), "apps|ứng viên"),
    "em_cu_xep_clb_moi": (_sua(lambda cu, moi, ids, r: (
        moi["clubs"].update(c_x={"capacity": 1, "reserve_capacity": 0, "reserve_group": None}),
        moi["prefs"].update(s001=moi["prefs"]["s001"]), cu["prefs"].update(s001=["c_x"] + cu["prefs"]["s001"]),
        moi["prefs"].update(s001=["c_x"] + moi["prefs"]["s001"]))), "CLB mới"),
    "doi_thu_tu_boc_tham": (_sua(lambda cu, moi, ids, r: moi["stb"].update(
        s000=moi["stb"]["s001"], s001=moi["stb"]["s000"])), "thứ tự bốc thăm"),
}


@pytest.mark.parametrize("ten", sorted(_VI_PHAM))
def test_tiep_tuc_da_tu_choi_khi_khong_phai_them_rang_buoc(ten):
    sua, chu = _VI_PHAM[ten]
    cu, moi, moi_ids, res0 = sua(*_them_em_moi(3))
    with pytest.raises(ValueError, match=chu):
        exp_resume.resume_da(res0, cu, moi, moi_ids)


def test_tiep_tuc_da_tu_choi_res0_lap_tu_apps_thieu():
    # Phản ví dụ của rà soát: res0 chạy từ apps thiếu (s1, s3 không có trong apps[c0]) rồi tiếp tục với
    # apps đủ. Không kiểm thì kết quả lệch chạy lại (s1 hay s3 lấy chỗ cuối ở c0); phải từ chối.
    clubs = {"c0": {"capacity": 3, "reserve_capacity": 1, "reserve_group": "g"},
             "c1": {"capacity": 1, "reserve_capacity": 1, "reserve_group": None}}
    st = {s: {"reserve_group": None} for s in ["s0", "s1", "s2", "s3"]}
    prefs = {"s0": ["c0"], "s1": ["c1", "c0"], "s2": ["c0", "c1"], "s3": ["c1", "c0"]}
    apps = {"c0": ["s0", "s2"], "c1": ["s1", "s3"]}
    tested = {"c0": {"s0": 0.0}, "c1": {}}
    stb0 = {"s0": 0, "s2": 1, "s1": 2, "s3": 3}
    res0 = rb.run_rbda(st, clubs, tested, apps, prefs, stb0, rb.default_reserve_eligible_fn(st, clubs))
    st2 = dict(st, n0={"reserve_group": None})
    pf2 = dict(prefs, n0=["c1"])
    ap2 = rb.hop_ung_vien({"c0": ["s0", "s2"], "c1": ["s1", "s3", "n0"]}, pf2)
    stbn = {"s0": 0, "s2": 1, "n0": 2, "s1": 3, "s3": 4}
    cu = _du_lieu(st, clubs, tested, apps, prefs, stb0)
    moi = _du_lieu(st2, clubs, tested, ap2, pf2, stbn)
    with pytest.raises(ValueError):
        exp_resume.resume_da(res0, cu, moi, ["n0"])
    # Khi dữ liệu cũ cũng đủ (như hop_ung_vien), hai đường trùng nhau.
    apps_du = rb.hop_ung_vien(apps, prefs)
    res0b = rb.run_rbda(st, clubs, tested, apps_du, prefs, stb0, rb.default_reserve_eligible_fn(st, clubs))
    cu_du = _du_lieu(st, clubs, tested, apps_du, prefs, stb0)
    asg, _ = exp_resume.resume_da(res0b, cu_du, moi, ["n0"])
    assert asg == _chay_lai(moi)


def _them_hs(cu, moi, moi_ids, so):
    """Thêm `so` em cũ (cùng trong cu và moi), chạy lại res0 cho dữ liệu cũ."""
    hs = ["x%05d" % i for i in range(so)]
    for d in (cu, moi):
        for x in hs:
            d["students"][x] = {"reserve_group": None}
            d["prefs"][x] = list(d["clubs"])[:4]
            for c in d["prefs"][x]:
                d["apps"][c].append(x)
    cu["stb"] = rb.generate_stb_lottery(list(cu["students"]), 1)
    moi["stb"] = rb.chen_stb_cho_hoc_sinh_moi(sorted(cu["students"], key=cu["stb"].__getitem__), moi_ids, 1)
    return rb.run_rbda(cu["students"], cu["clubs"], cu["tested"], cu["apps"], cu["prefs"], cu["stb"],
                       rb.default_reserve_eligible_fn(cu["students"], cu["clubs"]))


class _DanhSachCam(list):
    """Danh sách cấm tra cứu tuyến tính: kiểm tiền đề phải dùng tập hợp, không quét danh sách (bình phương)."""

    def __contains__(self, x):
        raise AssertionError("kiem_tien_de quét danh sách bằng `in`")

    def index(self, *a):
        raise AssertionError("kiem_tien_de quét danh sách bằng .index")

    def count(self, *a):
        raise AssertionError("kiem_tien_de quét danh sách bằng .count")


def test_kiem_tien_de_khong_quet_danh_sach_apps():
    cu, moi, moi_ids, res0 = _them_em_moi(0)
    res0 = _them_hs(cu, moi, moi_ids, 2000)
    moi["apps"] = {c: _DanhSachCam(v) for c, v in moi["apps"].items()}
    cu["apps"] = {c: _DanhSachCam(v) for c, v in cu["apps"].items()}
    exp_resume.kiem_tien_de(res0, cu, moi, moi_ids)
    asg, _ = exp_resume.resume_da(res0, cu, moi, moi_ids, da_kiem=True)
    assert asg == _chay_lai(moi)


def test_kiem_tien_de_dung_khoa_pha_hoa_nhu_compute_club_priority():
    # 20 cặp em cũ có số bốc thăm TRÙNG nhau (a=b=v): compute_club_priority phá hoà bằng mã em (a trước b).
    # Dữ liệu mới tách cặp sao cho b đứng trước a, mọi em khác giữ nguyên thứ tự -> phải từ chối.
    # Kiểm chỉ theo số bốc thăm sẽ thấy cặp trùng theo thứ tự duyệt tập hợp (ngẫu nhiên mỗi tiến trình),
    # nên bỏ lọt mỗi cặp với xác suất 1/2: 20 cặp -> lọt cả 20 với xác suất 2^-20.
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    cu_hs = sorted(cu["students"])
    cu["stb"] = {s: 10 * i for i, s in enumerate(cu_hs)}
    moi["stb"] = dict(cu["stb"], **{n: 10_000 + i for i, n in enumerate(moi_ids)})
    for k in range(20):
        a, b = cu_hs[2 * k], cu_hs[2 * k + 1]            # a < b theo mã
        v = cu["stb"][a]
        cu["stb"][a] = cu["stb"][b] = v
        moi["stb"][a], moi["stb"][b] = v + 2, v + 1       # b trước a, vẫn trước em kế tiếp (v + 20)
    with pytest.raises(ValueError, match="thứ tự bốc thăm"):
        exp_resume.kiem_tien_de(res0, cu, moi, moi_ids)


def test_kiem_tien_de_chap_nhan_tach_cap_trung_giu_dung_thu_tu():
    # Ngược lại với test trên: cặp trùng a=b=v được tách thành a=v, b=v+1 — thứ tự (số, mã) KHÔNG đổi,
    # nên phải chấp nhận và cho đúng kết quả chạy lại. Kiểm chỉ theo số bốc thăm sẽ so thứ tự cặp trùng
    # theo thứ tự duyệt tập hợp và từ chối nhầm mỗi cặp với xác suất 1/2 (20 cặp: gần như chắc chắn).
    cu, moi, moi_ids, _ = _them_em_moi(2)
    cu_hs = sorted(cu["students"])
    cu["stb"] = {s: 10 * i for i, s in enumerate(cu_hs)}
    for k in range(20):
        a, b = cu_hs[2 * k], cu_hs[2 * k + 1]
        cu["stb"][b] = cu["stb"][a]
    moi["stb"] = {s: 10 * i for i, s in enumerate(cu_hs)}
    for k in range(20):
        a, b = cu_hs[2 * k], cu_hs[2 * k + 1]
        moi["stb"][a], moi["stb"][b] = cu["stb"][a], cu["stb"][a] + 1
    moi["stb"].update({n: 10_000 + i for i, n in enumerate(moi_ids)})
    res0 = rb.run_rbda(cu["students"], cu["clubs"], cu["tested"], cu["apps"], cu["prefs"], cu["stb"],
                       rb.default_reserve_eligible_fn(cu["students"], cu["clubs"]))
    asg, _ = exp_resume.resume_da(res0, cu, moi, moi_ids)
    assert asg == _chay_lai(moi)


def test_kiem_tien_de_nhan_so_boc_tham_kieu_numpy():
    np = pytest.importorskip("numpy")
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    moi["stb"] = {s: np.int64(v) for s, v in moi["stb"].items()}
    exp_resume.kiem_tien_de(res0, cu, moi, moi_ids)


def test_kiem_tien_de_bao_runtimeerror_khi_chua_nap_rbda(monkeypatch):
    # Chưa nạp mô-đun rbda là lỗi cài đặt, KHÔNG phải vi phạm tiền đề dữ liệu: RuntimeError, để người gọi
    # bắt ValueError rồi chạy lại toàn bộ không nuốt mất lỗi này.
    monkeypatch.setattr(exp_resume, "rb", None)
    monkeypatch.delitem(sys.modules, "rbda_priority_pipeline")
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    with pytest.raises(RuntimeError, match="chưa nạp"):
        exp_resume.kiem_tien_de(res0, cu, moi, moi_ids)


def test_kiem_tien_de_chap_nhan_diem_nhap_truoc_cho_em_den_muon():
    # Em đến muộn đã có điểm / có trong apps ở dữ liệu cũ (nhập trước khi thêm vào danh sách học sinh):
    # không phải "em cũ đổi dữ liệu".
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    n = moi_ids[1]
    c = moi["prefs"][n][1]
    cu["tested"][c] = dict(cu["tested"][c], **{n: 3.0})
    cu["apps"][c] = list(cu["apps"][c]) + [n]
    asg, _ = exp_resume.resume_da(res0, cu, moi, moi_ids)
    assert asg == _chay_lai(moi)


def test_kiem_tien_de_coi_nhom_rong_va_none_la_mot():
    # default_reserve_eligible_fn coi nhóm '' và None như nhau: dữ liệu CSV ('') và SQLite (None) tương đương.
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    for c, info in moi["clubs"].items():
        if not info.get("reserve_group"):
            info["reserve_group"] = "" if info.get("reserve_group") is None else None
    for s in cu["students"]:
        if not moi["students"][s].get("reserve_group"):
            moi["students"][s]["reserve_group"] = ""
    asg, _ = exp_resume.resume_da(res0, cu, moi, moi_ids)
    assert asg == _chay_lai(moi)


def test_kiem_tien_de_nhan_diem_decimal():
    # Decimal không là numbers.Real nhưng compute_club_priority sắp được: không được từ chối nhầm.
    import decimal
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    for d in (cu, moi):
        d["tested"] = {c: {s: decimal.Decimal(str(v)) for s, v in t.items()} for c, t in d["tested"].items()}
    asg, _ = exp_resume.resume_da(res0, cu, moi, moi_ids)
    assert asg == _chay_lai(moi)


# Vì sao từ chối NaN: compute_club_priority sắp theo (-điểm, ...), NaN làm phép so không nhất quán nên
# thứ tự phụ thuộc thứ tự đầu vào (đã tái hiện: ["a","b","c"] và ["c","b","a"] cho hai thứ tự khác nhau).
@pytest.mark.parametrize("gia_tri", [float("nan"), "7.5", None, True])
@pytest.mark.parametrize("ben", ["cu_va_moi", "chi_em_moi"])
def test_kiem_tien_de_tu_choi_diem_khong_hop_le(ben, gia_tri):
    # NaN (thứ tự phụ thuộc đầu vào), chuỗi CSV, None, bool: compute_club_priority không sắp đúng được.
    # Phải là ValueError rõ ràng (người gọi bắt để chạy lại toàn bộ), không phải TypeError giữa chừng.
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    if ben == "cu_va_moi":
        c = next(c for c, t in cu["tested"].items() if t)
        s = next(iter(cu["tested"][c]))
        cu["tested"][c] = dict(cu["tested"][c], **{s: gia_tri})
        moi["tested"][c] = dict(moi["tested"][c], **{s: gia_tri})
    else:
        n = moi_ids[0]
        c = moi["prefs"][n][1]
        moi["tested"][c] = dict(moi["tested"][c], **{n: gia_tri})
    with pytest.raises(ValueError, match="điểm không hợp lệ"):
        exp_resume.resume_da(res0, cu, moi, moi_ids)


def test_kiem_tien_de_khong_bo_qua_kiem_suc_chua_khi_chua_gan_rb(monkeypatch):
    # exp_resume.rb chưa gán: vẫn phải kiểm sức chứa bằng bản rbda đã nạp trong tiến trình.
    monkeypatch.setattr(exp_resume, "rb", None)
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    c = next(c for c, v in moi["clubs"].items() if v["reserve_capacity"] > 0)
    moi["clubs"][c]["capacity"] = moi["clubs"][c]["reserve_capacity"] - 1
    with pytest.raises(ValueError, match="sức chứa mới"):
        exp_resume.kiem_tien_de(res0, cu, moi, moi_ids)


def test_kiem_tien_de_bao_ro_suc_chua_moi_sai():
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    c = next(c for c, v in moi["clubs"].items() if v["reserve_capacity"] > 0)
    moi["clubs"][c]["capacity"] = moi["clubs"][c]["reserve_capacity"] - 1
    with pytest.raises(ValueError, match="sức chứa mới của CLB %s" % c):
        exp_resume.kiem_tien_de(res0, cu, moi, moi_ids)


@pytest.mark.parametrize("gia_tri", ["thieu", None, "7", float("nan"), True])
def test_kiem_tien_de_bao_ro_khi_thieu_so_boc_tham(gia_tri):
    cu, moi, moi_ids, res0 = _them_em_moi(2)
    if gia_tri == "thieu":
        moi["stb"].pop("s003")
    else:
        moi["stb"]["s003"] = gia_tri
    with pytest.raises(ValueError, match="thiếu số bốc thăm hoặc không phải số"):
        exp_resume.kiem_tien_de(res0, cu, moi, moi_ids)


# ---------------------------------------------------------------------------
# _chung: bộ nạp và bộ sinh
# ---------------------------------------------------------------------------
def test_nap_rb_tra_ban_da_nap_khi_cung_thu_muc():
    mod = _chung.nap_rb(_GOC)
    assert mod is rb
    assert os.path.realpath(mod.__file__) == os.path.realpath(os.path.join(_GOC, "rbda_priority_pipeline.py"))


def test_nap_rb_bao_loi_khi_tien_trinh_da_nap_ban_khac(tmp_path):
    for ten in ("rbda_priority_pipeline.py", "i18n_errors.py"):
        (tmp_path / ten).write_text(open(os.path.join(_GOC, ten), encoding="utf-8").read(), encoding="utf-8")
    with pytest.raises(SystemExit, match="tiến trình riêng"):
        _chung.nap_rb(str(tmp_path))


def test_nap_rb_nap_dung_thu_muc_trong_tien_trinh_moi(tmp_path):
    import subprocess
    for ten in ("rbda_priority_pipeline.py", "i18n_errors.py"):
        (tmp_path / ten).write_text(open(os.path.join(_GOC, ten), encoding="utf-8").read(), encoding="utf-8")
    ma = ("import importlib.util, sys;"
          "sp = importlib.util.spec_from_file_location('c', sys.argv[1]);"
          "m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m);"
          "r = m.nap_rb(sys.argv[2]); print(r.__file__);"
          "print(sys.modules['i18n_errors'].__file__); print(sys.argv[2] in sys.path)")
    kq = subprocess.run([sys.executable, "-I", "-c", ma, os.path.join(_THAM_KHAO, "_chung.py"), str(tmp_path)],
                        capture_output=True, text=True, check=True, cwd=str(tmp_path.parent))
    tep_rb, tep_loi, con_trong_path = kq.stdout.split()
    assert os.path.realpath(tep_rb) == os.path.realpath(str(tmp_path / "rbda_priority_pipeline.py"))
    assert os.path.realpath(tep_loi) == os.path.realpath(str(tmp_path / "i18n_errors.py"))
    assert con_trong_path == "False"


def test_nap_rb_nap_i18n_errors_khi_mo_dun_chinh_da_co(tmp_path):
    # Tiến trình đã có rbda_priority_pipeline (từ thư mục đó) nhưng chưa có i18n_errors (mô-đun chỉ
    # import nó bên trong hàm): nap_rb phải nạp nốt i18n_errors từ cùng thư mục.
    import subprocess
    for ten in ("rbda_priority_pipeline.py", "i18n_errors.py"):
        (tmp_path / ten).write_text(open(os.path.join(_GOC, ten), encoding="utf-8").read(), encoding="utf-8")
    ma = ("import importlib.util, sys;"
          "sys.path.insert(0, sys.argv[2]); import rbda_priority_pipeline; sys.path.remove(sys.argv[2]);"
          "assert 'i18n_errors' not in sys.modules;"
          "sp = importlib.util.spec_from_file_location('c', sys.argv[1]);"
          "m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); m.nap_rb(sys.argv[2]);"
          "print(sys.modules['i18n_errors'].__file__)")
    kq = subprocess.run([sys.executable, "-I", "-c", ma, os.path.join(_THAM_KHAO, "_chung.py"), str(tmp_path)],
                        capture_output=True, text=True, check=True, cwd=str(tmp_path.parent))
    assert os.path.realpath(kq.stdout.strip()) == os.path.realpath(str(tmp_path / "i18n_errors.py"))


def _tao_exe_gia(duong, ma_rb="GIA_TRI = 42\n", pyver=None, kieu_cu=False, thieu_rbda=False):
    """Dựng một tệp PyInstaller tối thiểu (CArchive + PYZ) chứa i18n_errors và rbda_priority_pipeline."""
    import marshal
    import struct
    import zlib
    if pyver is None:
        pyver = sys.version_info.major * 100 + sys.version_info.minor
    than, muc = b"", []
    for ten, ma in (("i18n_errors", "def err(code, **p):\n    return {'code': code, 'params': p}\n"),
                    ("rbda_priority_pipeline", ma_rb))[:1 if thieu_rbda else 2]:
        nen = zlib.compress(marshal.dumps(compile(ma, ten + ".py", "exec")))
        muc.append((ten, (0, 12 + len(than), len(nen))))
        than += nen
    # kieu_cu: PyInstaller < 6 — mục lục PYZ là dict và mục CArchive tên "PYZ-00.pyz".
    pyz = (b"PYZ\0" + b"\0" * 4 + struct.pack("!i", 12 + len(than)) + than
           + marshal.dumps(dict(muc) if kieu_cu else muc))
    nen_pyz = zlib.compress(pyz)
    ten_b = (b"PYZ-00.pyz\0" + b"\0" * 3) if kieu_cu else (b"PYZ.pyz\0" + b"\0" * 6)
    toc = struct.pack("!IIIIBc", 18 + len(ten_b), 0, len(nen_pyz), len(pyz), 1, b"z") + ten_b
    goi = nen_pyz + toc
    cookie_len = 88
    cookie = struct.pack("!8sIIII64s", b"MEI\x0c\x0b\x0a\x0b\x0e", len(goi) + cookie_len,
                         len(nen_pyz), len(toc), pyver, b"python")
    with open(duong, "wb") as f:
        f.write(b"MZ-dau-tep" + goi + cookie)


def _chay_tien_trinh_moi(ma, *thong_so):
    import subprocess
    dau = ("import importlib.util, sys;"
           "sp = importlib.util.spec_from_file_location('c', sys.argv[1]);"
           "m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m);")
    return subprocess.run([sys.executable, "-I", "-c", dau + ma, os.path.join(_THAM_KHAO, "_chung.py"), *thong_so],
                          capture_output=True, text=True)


def test_nap_rb_doc_ban_build_va_nap_lai_cung_tep(tmp_path):
    exe = tmp_path / "PhanBoCauLacBo.exe"
    _tao_exe_gia(str(exe))
    lien_ket = tmp_path / "lien_ket.exe"
    try:
        lien_ket.symlink_to(exe)
        lien_ket = str(lien_ket)
    except OSError:
        # Windows không quyền tạo liên kết: cùng tệp nhưng viết khác (chuỗi, để pathlib không gộp "."),
        # và đổi hoa/thường — Windows coi là cùng tệp.
        lien_ket = os.path.join(str(tmp_path), ".", "PhanBoCauLacBo.exe").upper()
    kq = _chay_tien_trinh_moi(
        "r = m.nap_rb(sys.argv[2]); print(r.GIA_TRI, sys.modules['i18n_errors'].err('x')['code']);"
        "print(m.nap_rb(sys.argv[3]) is r)", str(exe), lien_ket)
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.split() == ["42", "x", "True"]


def test_nap_rb_doc_ban_build_pyinstaller_cu(tmp_path):
    exe = tmp_path / "PhanBoCauLacBo.exe"
    _tao_exe_gia(str(exe), kieu_cu=True)
    kq = _chay_tien_trinh_moi("print(m.nap_rb(sys.argv[2]).GIA_TRI)", str(exe))
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.strip() == "42"


def test_nap_rb_bao_loi_ro_khi_duong_dan_khong_ton_tai(tmp_path):
    kq = _chay_tien_trinh_moi("m.nap_rb(sys.argv[2])", str(tmp_path / "khong_ton_tai"))
    assert kq.returncode != 0 and "không tồn tại" in kq.stderr and "Traceback" not in kq.stderr


def test_nap_rb_lay_ca_hai_tep_tu_thu_muc_nguoi_dung_dua(tmp_path):
    # rbda_priority_pipeline.py trong A là liên kết sang B; A có i18n_errors riêng -> phải nạp i18n_errors của A.
    a, b = tmp_path / "A", tmp_path / "B"
    a.mkdir()
    b.mkdir()
    (b / "rbda_priority_pipeline.py").write_text("GIA_TRI = 1\n", encoding="utf-8")
    (b / "i18n_errors.py").write_text("NGUON = 'B'\n", encoding="utf-8")
    (a / "i18n_errors.py").write_text("NGUON = 'A'\n", encoding="utf-8")
    try:
        (a / "rbda_priority_pipeline.py").symlink_to(b / "rbda_priority_pipeline.py")
    except OSError:
        pytest.skip("không tạo được liên kết trên máy này")
    kq = _chay_tien_trinh_moi("m.nap_rb(sys.argv[2]); print(sys.modules['i18n_errors'].NGUON)", str(a))
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.strip() == "A"


def test_nap_rb_tu_choi_thu_muc_thieu_i18n_errors(tmp_path):
    # Thư mục chỉ có rbda_priority_pipeline.py; tiến trình có một i18n_errors khác trên sys.path (kho mã).
    # Import theo tên sẽ lấy nhầm tệp đó: phải từ chối và không để mô-đun nào lại trong tiến trình.
    (tmp_path / "rbda_priority_pipeline.py").write_text("GIA_TRI = 1\n", encoding="utf-8")
    kq = _chay_tien_trinh_moi(
        "sys.path.insert(0, sys.argv[3])\n"
        "try:\n    m.nap_rb(sys.argv[2])\nexcept SystemExit as e:\n"
        "    print('TU_CHOI', 'i18n_errors' in sys.modules, 'rbda_priority_pipeline' in sys.modules)",
        str(tmp_path), _GOC)
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.split() == ["TU_CHOI", "False", "False"]


def _bien_dich_vao_pycache(nguon):
    """Ghi <thư mục>/__pycache__/<tên>.<thẻ>.pyc ở ĐÚNG chỗ đó (bỏ qua PYTHONPYCACHEPREFIX), và kiểm là có."""
    import py_compile
    if sys.implementation.cache_tag is None:
        pytest.skip("trình thông dịch này không dùng __pycache__ (cache_tag None)")
    dich = nguon.parent / "__pycache__" / ("%s.%s.pyc" % (nguon.stem, sys.implementation.cache_tag))
    py_compile.compile(str(nguon), cfile=str(dich))
    assert dich.is_file()


def _ghi_hai_tep(thu_muc, ma_rb="GIA_TRI = 1\n", ma_loi="NGUON = 'py'\n"):
    (thu_muc / "rbda_priority_pipeline.py").write_text(ma_rb, encoding="utf-8")
    (thu_muc / "i18n_errors.py").write_text(ma_loi, encoding="utf-8")


def test_nap_rb_nap_dung_tep_nguon_du_co_thu_cung_ten_nam_canh(tmp_path):
    # Bản mở rộng cũ (.so/.pyd, Python sẽ ưu tiên khi import theo tên), gói cùng tên và gói namespace cùng
    # tên nằm cạnh: nạp thẳng tệp .py nên không thứ nào chen vào được.
    import importlib.machinery
    _ghi_hai_tep(tmp_path, "GIA_TRI = 'nguon'\n")
    (tmp_path / ("rbda_priority_pipeline" + importlib.machinery.EXTENSION_SUFFIXES[0])).write_bytes(b"cu")
    (tmp_path / "i18n_errors").mkdir()                 # gói namespace cùng tên
    kq = _chay_tien_trinh_moi("r = m.nap_rb(sys.argv[2]); print(r.GIA_TRI, sys.modules['i18n_errors'].NGUON)",
                              str(tmp_path))
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.split() == ["nguon", "py"]


def test_nap_rb_nap_dung_tep_nguon_du_co_goi_cung_ten(tmp_path):
    _ghi_hai_tep(tmp_path, "GIA_TRI = 'nguon'\n")
    (tmp_path / "rbda_priority_pipeline").mkdir()
    (tmp_path / "rbda_priority_pipeline" / "__init__.py").write_text("GIA_TRI = 'goi'\n", encoding="utf-8")
    kq = _chay_tien_trinh_moi("print(m.nap_rb(sys.argv[2]).GIA_TRI)", str(tmp_path))
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.strip() == "nguon"


@pytest.mark.parametrize("kieu", ["pyc_canh", "pycache", "namespace"])
def test_nap_rb_tu_choi_khi_thieu_tep_nguon(tmp_path, kieu):
    # Thiếu i18n_errors.py: chỉ có bản biên dịch cạnh, chỉ có .pyc trong __pycache__, hoặc chỉ có thư mục
    # con cùng tên — báo rõ "không có i18n_errors.py", không traceback, không để mô-đun nào lại.
    import py_compile
    (tmp_path / "rbda_priority_pipeline.py").write_text("GIA_TRI = 1\n", encoding="utf-8")
    nguon = tmp_path / "i18n_errors.py"
    nguon.write_text("NGUON = 'py'\n", encoding="utf-8")
    if kieu == "pyc_canh":
        py_compile.compile(str(nguon), cfile=str(tmp_path / "i18n_errors.pyc"))
    elif kieu == "pycache":
        _bien_dich_vao_pycache(nguon)
    nguon.unlink()
    if kieu == "namespace":
        (tmp_path / "i18n_errors").mkdir()
    kq = _chay_tien_trinh_moi(
        "\ntry:\n    m.nap_rb(sys.argv[2])\nexcept SystemExit as e:\n"
        "    print(e); print('i18n_errors' in sys.modules, 'rbda_priority_pipeline' in sys.modules)",
        str(tmp_path))
    assert kq.returncode == 0, kq.stderr
    assert "không có i18n_errors.py" in kq.stdout
    assert kq.stdout.split()[-2:] == ["False", "False"]


def test_tep_nguon_bao_loi_doc_thu_muc_that(tmp_path):
    # Thư mục thật không có quyền đọc (chmod 000): báo lỗi đọc, không phải "không có".
    # root bỏ qua quyền tệp và Windows không dùng chmod kiểu này: bỏ qua ở đó (CI Linux chạy được).
    if os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0):
        pytest.skip("cần người dùng thường trên hệ POSIX")
    khoa = tmp_path / "khoa"
    khoa.mkdir()
    _ghi_hai_tep(khoa)
    khoa.chmod(0)
    try:
        with pytest.raises(SystemExit, match="Không đọc được thư mục"):
            _chung._tep_nguon(str(khoa), "rbda_priority_pipeline")
    finally:
        khoa.chmod(0o755)


def test_tep_nguon_bao_loi_doc_thu_muc(tmp_path, monkeypatch):
    # Như test trên nhưng chạy được mọi nơi (kể cả root): giả lập lỗi quyền khi mở thư mục.
    def tu_choi(_):
        raise PermissionError("không có quyền")
    monkeypatch.setattr(_chung.os, "scandir", tu_choi)
    with pytest.raises(SystemExit, match="Không đọc được thư mục"):
        _chung._tep_nguon(str(tmp_path), "rbda_priority_pipeline")


def test_nap_rb_thu_muc_sai_bao_thieu_mo_dun_chinh(tmp_path):
    kq = _chay_tien_trinh_moi("m.nap_rb(sys.argv[2])", str(tmp_path))
    assert kq.returncode != 0 and "không có rbda_priority_pipeline.py" in kq.stderr


def test_nap_rb_khong_dung_toi_sys_path_va_cache(tmp_path):
    # Không thêm gì vào sys.path / sys.path_importer_cache; mục cache sẵn có (kể cả None cũ) giữ nguyên
    # và không ảnh hưởng tới tệp được nạp.
    _ghi_hai_tep(tmp_path)
    kq = _chay_tien_trinh_moi(
        "sys.path.append(sys.argv[2]); sys.path_importer_cache[sys.argv[2]] = None\n"
        "truoc = list(sys.path)\n"
        "r = m.nap_rb(sys.argv[2])\n"
        "print(r.GIA_TRI, sys.path_importer_cache[sys.argv[2]] is None, sys.path == truoc)", str(tmp_path))
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.split() == ["1", "True", "True"]


def test_nap_rb_tu_choi_mo_dun_anh_em_nap_tu_cho_khac(tmp_path):
    # Một phiên bản khác của rbda_priority_pipeline import mô-đun anh em (khong_co_trong_chuan) ở đầu tệp;
    # nó không nằm trong thư mục đã chọn mà ở một thư mục khác trên sys.path -> đo lẫn mã: phải từ chối.
    chon, khac = tmp_path / "chon", tmp_path / "khac"
    chon.mkdir()
    khac.mkdir()
    _ghi_hai_tep(chon, "import mo_dun_anh_em\nGIA_TRI = 1\n")
    (khac / "mo_dun_anh_em.py").write_text("X = 1\n", encoding="utf-8")
    kq = _chay_tien_trinh_moi("sys.path.insert(0, sys.argv[3]); m.nap_rb(sys.argv[2])", str(chon), str(khac))
    assert kq.returncode != 0 and "mo_dun_anh_em" in kq.stderr and "Traceback" not in kq.stderr


def test_nap_rb_bao_ro_muc_sys_modules_khong_ro_nguon():
    kq = _chay_tien_trinh_moi("sys.modules['i18n_errors'] = None\nm.nap_rb(sys.argv[2])", _GOC)
    assert kq.returncode != 0 and "không rõ nguồn" in kq.stderr


def test_nap_rb_bao_ro_tep_build_thieu_mo_dun(tmp_path):
    exe = tmp_path / "ChuongTrinhKhac.exe"
    _tao_exe_gia(str(exe), thieu_rbda=True)
    kq = _chay_tien_trinh_moi("m.nap_rb(sys.argv[2])", str(exe))
    assert kq.returncode != 0 and "không chứa mô-đun rbda_priority_pipeline" in kq.stderr
    assert "KeyError" not in kq.stderr


def test_nap_rb_ban_build_hong_khong_de_mo_dun_do_dang(tmp_path):
    exe = tmp_path / "PhanBoCauLacBo.exe"
    _tao_exe_gia(str(exe), ma_rb="raise RuntimeError('hong')\n")
    kq = _chay_tien_trinh_moi(
        "\ntry:\n    m.nap_rb(sys.argv[2])\nexcept RuntimeError:\n"
        "    print('i18n_errors' in sys.modules, 'rbda_priority_pipeline' in sys.modules)", str(exe))
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.split() == ["False", "False"]


def test_nap_rb_ban_build_lech_phien_ban_python(tmp_path):
    exe = tmp_path / "PhanBoCauLacBo.exe"
    _tao_exe_gia(str(exe), pyver=207)
    kq = _chay_tien_trinh_moi("m.nap_rb(sys.argv[2])", str(exe))
    assert kq.returncode != 0 and "Python 2.7" in kq.stderr


def test_nap_rb_thu_muc_hong_khong_de_mo_dun_do_dang(tmp_path):
    (tmp_path / "i18n_errors.py").write_text("def err(code, **p):\n    return code\n", encoding="utf-8")
    (tmp_path / "rbda_priority_pipeline.py").write_text("raise RuntimeError('hong')\n", encoding="utf-8")
    kq = _chay_tien_trinh_moi(
        "\ntry:\n    m.nap_rb(sys.argv[2])\nexcept RuntimeError:\n"
        "    print('i18n_errors' in sys.modules, 'rbda_priority_pipeline' in sys.modules)", str(tmp_path))
    assert kq.returncode == 0, kq.stderr
    assert kq.stdout.split() == ["False", "False"]


def test_nap_rb_tu_choi_ban_build_khi_da_nap_ban_kho_ma(tmp_path):
    tep = tmp_path / "PhanBoCauLacBo.exe"
    tep.write_bytes(b"MZ")
    with pytest.raises(SystemExit, match="bản build"):
        _chung.nap_rb(str(tep))


def test_nap_rb_bao_loi_ro_khi_tep_khong_phai_pyinstaller(tmp_path):
    # Cần tiến trình chưa nạp bản nào (bộ test đã nạp bản kho mã).
    import subprocess
    tep = tmp_path / "khong_phai.exe"
    tep.write_bytes(b"MZ" + b"\x00" * 200)
    ma = ("import importlib.util, sys;"
          "sp = importlib.util.spec_from_file_location('c', sys.argv[1]);"
          "m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); m.nap_rb(sys.argv[2])")
    kq = subprocess.run([sys.executable, "-I", "-c", ma, os.path.join(_THAM_KHAO, "_chung.py"), str(tep)],
                        capture_output=True, text=True)
    assert kq.returncode != 0 and "PyInstaller" in kq.stderr


def test_gen_sinh_du_lieu_dung_hinh_dang():
    pytest.importorskip("numpy")
    students, clubs, tested, apps, prefs = _chung.gen(50, 5, 0.8, npref=3, ntest=2, seed=2)
    assert len(students) == 50 and len(clubs) == 5
    assert all(len(p) == 3 and len(set(p)) == 3 for p in prefs.values())
    for sid, p in prefs.items():
        assert all(sid in apps[c] for c in p)
        assert all(sid in tested[c] for c in p[:2])
    assert all(0 <= v["reserve_capacity"] <= v["capacity"] for v in clubs.values())
