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


def _nap(ten):
    spec = importlib.util.spec_from_file_location(
        "test_tham_khao_" + ten, os.path.join(_THAM_KHAO, ten + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


verify_stability_nhanh = _nap("de_xuat_verify_nhanh").verify_stability_nhanh
exp_resume = _nap("exp_resume")
exp_resume.rb = rb
_chung = _nap("_chung")


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
        s000=moi["stb"]["s001"], s001=moi["stb"]["s000"])), "bốc thăm"),
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


def test_kiem_tien_de_tuyen_tinh():
    # Kiểm tiền đề dùng tập hợp: 3.000 em, mỗi CLB hàng nghìn ứng viên vẫn chạy nhanh.
    cu, moi, moi_ids, res0 = _them_em_moi(0)
    hs = ["x%04d" % i for i in range(3000)]
    for d in (cu, moi):
        for s in hs:
            d["students"][s] = {"reserve_group": None}
            d["prefs"][s] = list(d["clubs"])[:4]
            for c in d["prefs"][s]:
                d["apps"][c].append(s)
    stb_cu = rb.generate_stb_lottery(list(cu["students"]), 1)
    cu["stb"] = stb_cu
    moi["stb"] = rb.chen_stb_cho_hoc_sinh_moi(sorted(cu["students"], key=stb_cu.__getitem__), moi_ids, 1)
    res0 = rb.run_rbda(cu["students"], cu["clubs"], cu["tested"], cu["apps"], cu["prefs"], stb_cu,
                       rb.default_reserve_eligible_fn(cu["students"], cu["clubs"]))
    import time
    t = time.perf_counter()
    exp_resume.kiem_tien_de(res0, cu, moi, moi_ids)
    assert time.perf_counter() - t < 0.5
    asg, _ = exp_resume.resume_da(res0, cu, moi, moi_ids, da_kiem=True)
    assert asg == _chay_lai(moi)


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
          "print(m.nap_rb(sys.argv[2]).__file__)")
    kq = subprocess.run([sys.executable, "-I", "-c", ma, os.path.join(_THAM_KHAO, "_chung.py"), str(tmp_path)],
                        capture_output=True, text=True, check=True, cwd=str(tmp_path.parent))
    assert os.path.realpath(kq.stdout.strip()) == os.path.realpath(str(tmp_path / "rbda_priority_pipeline.py"))


def test_nap_rb_bao_loi_ro_khi_tep_khong_phai_pyinstaller(tmp_path):
    tep = tmp_path / "khong_phai.exe"
    tep.write_bytes(b"MZ" + b"\x00" * 200)
    with pytest.raises(SystemExit, match="PyInstaller"):
        _chung.nap_rb(str(tep))


def test_gen_sinh_du_lieu_dung_hinh_dang():
    pytest.importorskip("numpy")
    students, clubs, tested, apps, prefs = _chung.gen(50, 5, 0.8, npref=3, ntest=2, seed=2)
    assert len(students) == 50 and len(clubs) == 5
    assert all(len(p) == 3 and len(set(p)) == 3 for p in prefs.values())
    for sid, p in prefs.items():
        assert all(sid in apps[c] for c in p)
        assert all(sid in tested[c] for c in p[:2])
    assert all(0 <= v["reserve_capacity"] <= v["capacity"] for v in clubs.values())
