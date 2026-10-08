# -*- coding: utf-8 -*-
"""Tái lập phép kiểm: de_xuat_verify_nhanh.verify_stability_nhanh == rbda_priority_pipeline.verify_stability.
Chạy:  python kiem_verify_nhanh.py <thư mục chứa rbda_priority_pipeline.py | PhanBoCauLacBo.exe>
Dữ liệu tự sinh (không phải dữ liệu thật)."""
import sys, struct, zlib, marshal, types, random, time, dataclasses, json
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from de_xuat_verify_nhanh import verify_stability_nhanh

import os

def nap_rb(duong_dan):
    """duong_dan = thư mục chứa rbda_priority_pipeline.py (kho mã) HOẶC tệp PhanBoCauLacBo.exe (bản build)."""
    if os.path.isdir(duong_dan):
        sys.path.insert(0, os.path.abspath(duong_dan))
        import rbda_priority_pipeline as rb_mod
        return rb_mod
    import struct, zlib, marshal, types
    data = open(duong_dan, 'rb').read()
    pos = data.rfind(b'MEI\x0c\x0b\x0a\x0b\x0e')
    magic, pkglen, tocpos, toclen, pyver, pylib = struct.unpack('!8sIIII64s', data[pos:pos + 88])
    pkg_start = pos + 88 - pkglen
    def carch(name):
        toc = data[pkg_start + tocpos: pkg_start + tocpos + toclen]; p = 0
        while p < len(toc):
            esz, epos, dlen, ulen, cflag, typ = struct.unpack('!IIIIBc', toc[p:p + 18])
            n = toc[p + 18:p + esz].split(b'\x00')[0].decode()
            if n == name:
                raw = data[pkg_start + epos: pkg_start + epos + dlen]
                return zlib.decompress(raw) if cflag else raw
            p += esz
    pyz = carch('PYZ.pyz'); tocoff = struct.unpack('!i', pyz[8:12])[0]
    mods = {n: v for n, v in marshal.loads(pyz[tocoff:])}
    def load_mod(name):
        ispkg, off, ln = mods[name]
        co = marshal.loads(zlib.decompress(pyz[off:off + ln]))
        m = types.ModuleType(name); m.__file__ = name + '.py'; sys.modules[name] = m
        exec(co, m.__dict__); return m
    load_mod('i18n_errors')
    return load_mod('rbda_priority_pipeline')

rb = nap_rb(sys.argv[1])
from i18n_errors import err

def gen(S, K, ratio, npref=10, ntest=4, skew=1.0, seed=1, ngroup_frac=0.15):
    rng = random.Random(seed)
    cids = [f"c{j:03d}" for j in range(K)]
    pop = np.array([1.0 / ((j + 1) ** skew) for j in range(K)]); pop /= pop.sum()
    caps = np.maximum(1, np.round(int(S * ratio) * np.ones(K) / K)).astype(int)
    clubs = {c: {'capacity': int(caps[j]), 'reserve_capacity': int(caps[j] * 0.1), 'reserve_group': 'cs' if j % 3 == 0 else None} for j, c in enumerate(cids)}
    students = {}; prefs = {}; tested = {c: {} for c in cids}; apps = {c: [] for c in cids}
    nrng = np.random.default_rng(seed)
    for i in range(S):
        sid = f"s{i:06d}"
        students[sid] = {'reserve_group': 'cs' if rng.random() < ngroup_frac else None}
        pl = list(nrng.choice(K, size=min(npref, K), replace=False, p=pop))
        prefs[sid] = [cids[j] for j in pl]
        for j in pl[:ntest]:
            tested[cids[j]][sid] = round(float(nrng.normal(6.5, 1.5)) * 2) / 2
        for j in pl: apps[cids[j]].append(sid)
    return students, clubs, tested, apps, prefs

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
