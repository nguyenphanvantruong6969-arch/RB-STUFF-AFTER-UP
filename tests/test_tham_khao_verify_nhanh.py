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
from i18n_errors import err

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
    b = verify_stability_nhanh(res, clubs, prefs, fn, err=err)
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
        verify_stability_nhanh(res, clubs, prefs, fn, err=err)
    assert str(goc.value) == str(nhanh.value)


# ---------------------------------------------------------------------------
# exp_resume.resume_da == chạy lại toàn bộ run_rbda
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("seed", range(15))
def test_tiep_tuc_da_trung_chay_lai_toan_bo(seed):
    students, clubs, tested, apps, prefs, stb, fn, res0 = _sinh(seed)
    rng = random.Random(1000 + seed)
    moi = ["n%d" % i for i in range(6)]
    stb2 = rb.chen_stb_cho_hoc_sinh_moi(sorted(students, key=lambda s: stb[s]), moi, seed)
    # CLB mới mở sau lần chạy cũ: chưa có trong res0.base_rank.
    clubs2 = dict(clubs)
    clubs2["c_moi"] = {"capacity": 3, "reserve_capacity": 1, "reserve_group": "cs"}
    st2 = {s: dict(v) for s, v in students.items()}
    pf2 = dict(prefs)
    te2 = {c: dict(v) for c, v in tested.items()}
    te2["c_moi"] = {}
    ap2 = {c: list(v) for c, v in apps.items()}
    ap2["c_moi"] = []
    for i, n in enumerate(moi):
        # Em mới đủ diện dự trữ và có điểm thi (tầng 1) để đẩy em cũ; có nguyện vọng trỏ
        # tới CLB không tồn tại ("khong_co") phải bị bỏ qua như run_rbda.
        st2[n] = {"reserve_group": "cs" if i % 2 == 0 else None}
        ds = rng.sample(list(clubs2), 3)
        pf2[n] = ["khong_co"] + ds
        for c in ds:
            ap2[c].append(n)
            te2[c][n] = 10.0
    fn2 = rb.default_reserve_eligible_fn(st2, clubs2)
    full = rb.run_rbda(st2, clubs2, te2, ap2, pf2, stb2, fn2)
    asg, _ = exp_resume.resume_da(res0, clubs2, te2, ap2, pf2, stb2, fn2, moi)
    assert {s: c for s, c in full.assignment.items() if c is not None} == asg
    # Tiền đề: em mới thật sự được xếp và có em cũ bị đổi chỗ ở ít nhất vài seed (xem test dưới).
    assert any(asg.get(n) is not None for n in moi)


def test_em_moi_that_su_day_em_cu():
    doi = 0
    for seed in range(15):
        students, clubs, tested, apps, prefs, stb, fn, res0 = _sinh(seed)
        moi = ["n%d" % i for i in range(6)]
        stb2 = rb.chen_stb_cho_hoc_sinh_moi(sorted(students, key=lambda s: stb[s]), moi, seed)
        st2 = {s: dict(v) for s, v in students.items()}
        pf2, ap2 = dict(prefs), {c: list(v) for c, v in apps.items()}
        te2 = {c: dict(v) for c, v in tested.items()}
        for n in moi:
            st2[n] = {"reserve_group": "cs"}
            pf2[n] = list(clubs)
            for c in clubs:
                ap2[c].append(n)
                te2[c][n] = 10.0
        fn2 = rb.default_reserve_eligible_fn(st2, clubs)
        asg, _ = exp_resume.resume_da(res0, clubs, te2, ap2, pf2, stb2, fn2, moi)
        doi += sum(1 for s, c in res0.assignment.items() if asg.get(s) != c)
    assert doi > 0


def test_tiep_tuc_da_chiu_em_khong_co_nguyen_vong():
    # Em có trong students nhưng không có dòng nguyện vọng: run_rbda dùng prefs.get(sid, []).
    students, clubs, tested, apps, prefs, stb, fn, _ = _sinh(4)
    students["s_trong"] = {"reserve_group": None}
    stb = rb.generate_stb_lottery(list(students), 4)
    fn = rb.default_reserve_eligible_fn(students, clubs)
    res0 = rb.run_rbda(students, clubs, tested, apps, prefs, stb, fn)
    assert res0.assignment["s_trong"] is None
    moi = ["n0"]
    stb2 = rb.chen_stb_cho_hoc_sinh_moi(sorted(students, key=lambda s: stb[s]), moi, 4)
    st2 = dict(students, n0={"reserve_group": None})
    pf2 = dict(prefs, n0=list(clubs))
    ap2 = {c: list(v) + ["n0"] for c, v in apps.items()}
    fn2 = rb.default_reserve_eligible_fn(st2, clubs)
    full = rb.run_rbda(st2, clubs, tested, ap2, pf2, stb2, fn2)
    asg, _ = exp_resume.resume_da(res0, clubs, tested, ap2, pf2, stb2, fn2, moi)
    assert {s: c for s, c in full.assignment.items() if c is not None} == asg


def test_tiep_tuc_da_tu_choi_em_trong_nguyen_vong_nhung_khong_trong_apps():
    # Phản ví dụ do rà soát tìm ra: s1, s3 không có trong apps[c0] nên cùng thứ hạng len(rank);
    # chạy lại chọn s1, tiếp tục chọn s3. Đường thật không có ca này (hop_ung_vien), nên
    # resume_da phải từ chối thay vì trả kết quả khác run_rbda.
    clubs = {"c0": {"capacity": 3, "reserve_capacity": 1, "reserve_group": "g"},
             "c1": {"capacity": 1, "reserve_capacity": 1, "reserve_group": None}}
    st = {s: {"reserve_group": None} for s in ["s0", "s1", "s2", "s3"]}
    prefs = {"s0": ["c0"], "s1": ["c1", "c0"], "s2": ["c0", "c1"], "s3": ["c1", "c0"]}
    apps = {"c0": ["s0", "s2"], "c1": ["s1", "s3"]}
    tested = {"c0": {"s0": 0.0}, "c1": {}}
    res0 = rb.run_rbda(st, clubs, tested, apps, prefs, {"s0": 0, "s2": 1, "s1": 2, "s3": 3},
                       rb.default_reserve_eligible_fn(st, clubs))
    st2 = dict(st, n0={"reserve_group": None})
    pf2 = dict(prefs, n0=["c1"])
    ap2 = {"c0": ["s0", "s2"], "c1": ["s1", "s3", "n0"]}
    stbn = {"s0": 0, "s2": 1, "n0": 2, "s1": 3, "s3": 4}
    fn2 = rb.default_reserve_eligible_fn(st2, clubs)
    with pytest.raises(ValueError, match="apps"):
        exp_resume.resume_da(res0, clubs, tested, ap2, pf2, stbn, fn2, ["n0"])
    # Khi apps chứa đủ nguyện vọng (như hop_ung_vien), hai đường trùng nhau.
    ap3 = rb.hop_ung_vien(ap2, pf2)
    res0b = rb.run_rbda(st, clubs, tested, rb.hop_ung_vien(apps, prefs), prefs,
                        {"s0": 0, "s2": 1, "s1": 2, "s3": 3}, rb.default_reserve_eligible_fn(st, clubs))
    full = rb.run_rbda(st2, clubs, tested, ap3, pf2, stbn, fn2)
    asg, _ = exp_resume.resume_da(res0b, clubs, tested, ap3, pf2, stbn, fn2, ["n0"])
    assert {s: c for s, c in full.assignment.items() if c is not None} == asg


# ---------------------------------------------------------------------------
# _chung: bộ nạp và bộ sinh
# ---------------------------------------------------------------------------
def test_nap_rb_tu_thu_muc_kho_ma(monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))   # nap_rb sửa sys.path: hoàn lại sau test
    mod = _chung.nap_rb(_GOC)
    assert mod.run_rbda is rb.run_rbda


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
