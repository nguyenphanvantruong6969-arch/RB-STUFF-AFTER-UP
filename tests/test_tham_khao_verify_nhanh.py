"""Canh hai kịch bản tham khảo của gói kế hoạch (docs/ke_hoach/tham_khao/).

`de_xuat_verify_nhanh.verify_stability_nhanh` là bản sẽ thay `verify_stability`
ở mục Z4, và `exp_resume.resume_da` là nguyên mẫu của mục G1. Cả hai phải cho
ĐÚNG kết quả của mã thật, kể cả ở các ca biên mà bộ sinh dữ liệu đo đạc không
bao giờ tạo ra: em đang giữ chỗ không có trong base_rank, sức chứa sai, nguyện
vọng trỏ tới CLB không có. Không dùng numpy (không phải phụ thuộc sản phẩm).
Dữ liệu ở đây là dữ liệu MÔ PHỎNG, sinh ngẫu nhiên có hạt giống.
"""
import dataclasses
import os
import random
import sys

import pytest

import rbda_priority_pipeline as rb

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "ke_hoach", "tham_khao"))

import exp_resume  # noqa: E402
from de_xuat_verify_nhanh import verify_stability_nhanh  # noqa: E402
from i18n_errors import err  # noqa: E402


def _sinh(seed, n_hs=60, n_clb=5, ty_le=0.7, n_nv=4):
    """Bộ dữ liệu nhỏ: CLB đầy, có dự trữ, có em thi và em không thi."""
    rng = random.Random(seed)
    cids = ["c%d" % j for j in range(n_clb)]
    cap = max(2, int(n_hs * ty_le / n_clb))
    clubs = {c: {"capacity": cap, "reserve_capacity": cap // 3,
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
            apps[c].append(sid)
    stb = rb.generate_stb_lottery(list(students), seed)
    fn = rb.default_reserve_eligible_fn(students, clubs)
    res = rb.run_rbda(students, clubs, tested, apps, prefs, stb, fn)
    return students, clubs, tested, apps, prefs, stb, fn, res


def _khoa(p):
    q = p["params"]
    return (q["student_id"], q["club_id"], q["current_club"], q["n_holders"], q["capacity"])


def _cung_ket_luan(res, clubs, prefs, fn):
    a = rb.verify_stability(res, clubs, prefs, fn)
    b = verify_stability_nhanh(res, clubs, prefs, fn, err=err)
    assert sorted(map(_khoa, a)) == sorted(map(_khoa, b))
    return a


def _hoan_doi(res, rng, so_lan):
    asg = dict(res.assignment)
    co_cho = [s for s, c in asg.items() if c is not None]
    for _ in range(so_lan):
        a, b = rng.sample(co_cho, 2)
        asg[a], asg[b] = asg[b], asg[a]
    return dataclasses.replace(res, assignment=asg)


@pytest.mark.parametrize("seed", range(30))
def test_ban_nhanh_trung_ban_goc_ca_ket_qua_that_lan_ket_qua_hoan_doi(seed):
    _, clubs, _, _, prefs, _, fn, res = _sinh(seed)
    assert _cung_ket_luan(res, clubs, prefs, fn) == []
    _cung_ket_luan(_hoan_doi(res, random.Random(seed), 15), clubs, prefs, fn)


def test_em_giu_cho_khong_co_trong_base_rank_khong_lam_hong_ban_nhanh():
    # Em đề nghị CLB mà không có trong applicants của CLB đó: run_rbda vẫn nhận
    # và xếp em cuối (rank.get(s, len(rank))). Bản nhanh phải làm y như vậy.
    _, clubs, _, _, prefs, _, fn, res = _sinh(7)
    co_cho = [s for s, c in res.assignment.items() if c is not None]
    for s in co_cho[:5]:
        cid = res.assignment[s]
        res.base_rank[cid].pop(s, None)
    _cung_ket_luan(res, clubs, prefs, fn)


@pytest.mark.parametrize("reserve_capacity", [-1, 999])
def test_suc_chua_sai_thi_ca_hai_ban_deu_bao_loi(reserve_capacity):
    _, clubs, _, _, prefs, _, fn, res = _sinh(3)
    res = _hoan_doi(res, random.Random(3), 15)
    for info in clubs.values():
        info["reserve_capacity"] = reserve_capacity
    with pytest.raises(ValueError):
        rb.verify_stability(res, clubs, prefs, fn)
    with pytest.raises(ValueError):
        verify_stability_nhanh(res, clubs, prefs, fn, err=err)


@pytest.mark.parametrize("seed", range(10))
def test_tiep_tuc_da_bo_qua_clb_khong_ton_tai_nhu_run_rbda(seed):
    students, clubs, tested, apps, prefs, stb, fn, res0 = _sinh(seed)
    exp_resume.rb = rb
    rng = random.Random(1000 + seed)
    moi = ["n%d" % i for i in range(4)]
    order_cu = sorted(students, key=lambda s: stb[s])
    stb2 = rb.chen_stb_cho_hoc_sinh_moi(order_cu, moi, seed)
    st2 = {s: dict(v) for s, v in students.items()}
    pf2 = dict(prefs)
    te2 = {c: dict(v) for c, v in tested.items()}
    ap2 = {c: list(v) for c, v in apps.items()}
    for n in moi:
        st2[n] = {"reserve_group": None}
        # CLB "khong_co" không tồn tại: phải bị bỏ qua chứ không ném KeyError.
        pf2[n] = ["khong_co"] + rng.sample(list(clubs), 3)
        for c in pf2[n][1:]:
            ap2[c].append(n)
    fn2 = rb.default_reserve_eligible_fn(st2, clubs)
    full = rb.run_rbda(st2, clubs, te2, ap2, pf2, stb2, fn2)
    asg, _ = exp_resume.resume_da(res0, clubs, te2, ap2, pf2, stb2, fn2, moi)
    assert {s: c for s, c in full.assignment.items() if c} == asg
