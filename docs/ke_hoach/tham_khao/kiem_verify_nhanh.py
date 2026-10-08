# -*- coding: utf-8 -*-
"""Tái lập phép kiểm: de_xuat_verify_nhanh.verify_stability_nhanh == rbda_priority_pipeline.verify_stability.
Chạy:  python kiem_verify_nhanh.py <thư mục chứa rbda_priority_pipeline.py | PhanBoCauLacBo.exe>
Dữ liệu tự sinh (không phải dữ liệu thật)."""
import dataclasses
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _chung import gen, nap_rb  # noqa: E402
from de_xuat_verify_nhanh import verify_stability_nhanh  # noqa: E402

rb = nap_rb(sys.argv[1])
from i18n_errors import err  # noqa: E402

def setup(S, K, ratio, seed, ngroup):
    students, clubs, tested, apps, prefs = gen(S, K, ratio, seed=seed, ngroup_frac=ngroup)
    ids = list(students); stb = rb.generate_stb_lottery(ids, 42)
    for s in ids: students[s]['stb'] = stb[s]
    fn = rb.default_reserve_eligible_fn(students, clubs)
    res = rb.run_rbda(students, clubs, tested, apps, prefs, stb, fn)
    return clubs, prefs, fn, res

def key(p): return (p['params']['student_id'], p['params']['club_id'], p['params']['current_club'], p['params']['n_holders'], p['params']['capacity'])

out = []
# 1) kết quả thật: phải 0 cặp, hai bản giống nhau
for S in (2000, 5000, 10000):
    clubs, prefs, fn, res = setup(S, 20, 1.0, 11, 0.15)
    t = time.perf_counter(); a = rb.verify_stability(res, clubs, prefs, fn); ta = time.perf_counter() - t
    t = time.perf_counter(); b = verify_stability_nhanh(res, clubs, prefs, fn, err=err); tb = time.perf_counter() - t
    out.append(dict(loai='ket_qua_that', S=S, goc=len(a), nhanh=len(b), giong=(sorted(map(key, a)) == sorted(map(key, b))), t_goc=round(ta, 2), t_nhanh=round(tb, 3)))
    print(json.dumps(out[-1]), flush=True)
# 2) kết quả bị hoán đổi: CLB đầy, có dự trữ, nhiều cặp phá vỡ
for (S, K, ratio, seed, nswap) in [(1500, 10, 0.6, 1, 200), (1500, 15, 0.5, 2, 50), (800, 8, 0.7, 3, 300), (1200, 12, 0.8, 5, 150)]:
    clubs, prefs, fn, res = setup(S, K, ratio, seed, 0.3)
    rg = random.Random(seed); asg = dict(res.assignment); matched = [s for s, c in asg.items() if c]; done = tries = 0
    while done < nswap and tries < 50 * nswap + 10:
        tries += 1; a_, b_ = rg.sample(matched, 2); ca, cb = asg[a_], asg[b_]
        if ca == cb or a_ not in res.base_rank[cb] or b_ not in res.base_rank[ca]: continue
        asg[a_], asg[b_] = cb, ca; done += 1
    pres = dataclasses.replace(res, assignment=asg)
    a = rb.verify_stability(pres, clubs, prefs, fn); b = verify_stability_nhanh(pres, clubs, prefs, fn, err=err)
    out.append(dict(loai='hoan_doi', S=S, K=K, ratio=ratio, hoan_doi=done, goc=len(a), nhanh=len(b), giong=(sorted(map(key, a)) == sorted(map(key, b)))))
    print(json.dumps(out[-1]), flush=True)
print('TAT_CA_GIONG_NHAU', all(o['giong'] for o in out))
