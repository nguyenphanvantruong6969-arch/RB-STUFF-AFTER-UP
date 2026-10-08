# -*- coding: utf-8 -*-
"""Thử tiếp tục DA từ trạng thái cũ (mục G1) và so với chạy lại toàn bộ.
Chạy: python exp_resume.py <thư mục chứa rbda_priority_pipeline.py | PhanBoCauLacBo.exe>
Dữ liệu tự sinh."""
import os, sys, struct, zlib, marshal, types, random, time, json
import numpy as np

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


def gen(S, K, ratio, npref=10, ntest=4, skew=1.0, seed=1, ngroup_frac=0.15):
    rng = random.Random(seed)
    cids = [f"c{j:03d}" for j in range(K)]
    pop = np.array([1.0 / ((j + 1) ** skew) for j in range(K)]); pop /= pop.sum()
    total_cap = int(S * ratio)
    caps = np.maximum(1, np.round(total_cap * np.ones(K) / K)).astype(int)
    clubs = {c: {'capacity': int(caps[j]), 'reserve_capacity': int(caps[j] * 0.1), 'reserve_group': 'cs' if j % 3 == 0 else None} for j, c in enumerate(cids)}
    students = {}; prefs = {}; tested = {c: {} for c in cids}; apps = {c: [] for c in cids}
    nrng = np.random.default_rng(seed)
    for i in range(S):
        sid = f"s{i:06d}"
        students[sid] = {'reserve_group': 'cs' if rng.random() < ngroup_frac else None}
        k = min(npref, K)
        pl = list(nrng.choice(K, size=k, replace=False, p=pop))
        prefs[sid] = [cids[j] for j in pl]
        for j in pl[:ntest]:
            tested[cids[j]][sid] = round(float(nrng.normal(6.5, 1.5)) * 2) / 2
        for j in pl: apps[cids[j]].append(sid)
    return students, clubs, tested, apps, prefs

def resume_da(res0, clubs, tested, apps, prefs, stb, fn, new_ids):
    touched = set()
    for n in new_ids: touched.update(prefs[n])
    base_rank = {c: res0.base_rank[c] for c in clubs}
    for c in touched:
        order = rb.compute_club_priority(c, apps.get(c, []), tested.get(c, {}), stb)
        base_rank[c] = {s: i for i, s in enumerate(order)}
    held = {c: [] for c in clubs}
    for s, c in res0.assignment.items():
        if c: held[c].append(s)
    nxt = {s: (res0.rank_in_student_pref[s] - 1 if res0.assignment.get(s) else len(prefs[s])) for s in res0.assignment}
    for n in new_ids: nxt[n] = 0
    un = list(new_ids); props = 0
    while un:
        proposals = {}; still = []
        for s in un:
            if nxt[s] >= len(prefs[s]): continue
            c = prefs[s][nxt[s]]; proposals.setdefault(c, []).append(s); props += 1
        for c, newa in proposals.items():
            pool = held[c] + newa
            acc, tr = rb.club_choice_function(pool, clubs[c]['capacity'], clubs[c]['reserve_capacity'], (lambda s_, c=c: fn(s_, c)), base_rank[c])
            accs = set(acc); held[c] = acc
            for s in pool:
                if s not in accs:
                    nxt[s] += 1; still.append(s)
        un = still
    asg = {}
    for c, l in held.items():
        for s in l: asg[s] = c
    return asg, props

def resume_test(S, K, ratio, m, trials, seed=500):
    students, clubs, tested, apps, prefs = gen(S, K, ratio, seed=3)
    ids = list(students); stb = rb.generate_stb_lottery(ids, 42)
    for s in ids: students[s]['stb'] = stb[s]
    fn = rb.default_reserve_eligible_fn(students, clubs)
    res0 = rb.run_rbda(students, clubs, tested, apps, prefs, stb, fn)
    order_old = sorted(ids, key=lambda s: stb[s]); cids = list(clubs)
    pop = np.array([1.0 / ((j + 1) ** 1.0) for j in range(K)]); pop /= pop.sum()
    same = 0; tf = []; tr_ = []; props = []
    for tr in range(trials):
        rg = np.random.default_rng(seed + tr); rr = random.Random(seed + tr)
        new_ids = [f"n{tr}_{i}" for i in range(m)]
        stbn = rb.chen_stb_cho_hoc_sinh_moi(order_old, new_ids, seed + tr)
        st2 = {s: {'reserve_group': v['reserve_group']} for s, v in students.items()}
        for n in new_ids: st2[n] = {'reserve_group': 'cs' if rr.random() < 0.15 else None}
        for s in st2: st2[s]['stb'] = stbn[s]
        pf2 = dict(prefs); te2 = {c: dict(v) for c, v in tested.items()}; ap2 = {c: list(v) for c, v in apps.items()}
        for n in new_ids:
            pl = list(rg.choice(K, size=min(10, K), replace=False, p=pop)); pf2[n] = [cids[j] for j in pl]
            for j in pl[:4]: te2[cids[j]][n] = round(float(rg.normal(6.5, 1.5)) * 2) / 2
            for j in pl: ap2[cids[j]].append(n)
        fn2 = rb.default_reserve_eligible_fn(st2, clubs)
        t = time.perf_counter(); full = rb.run_rbda(st2, clubs, te2, ap2, pf2, stbn, fn2); tf.append(time.perf_counter() - t)
        t = time.perf_counter(); asg, pp = resume_da(res0, clubs, te2, ap2, pf2, stbn, fn2, new_ids); tr_.append(time.perf_counter() - t); props.append(pp)
        a_full = {s: c for s, c in full.assignment.items() if c}; a_res = {s: c for s, c in asg.items() if c}
        same += (a_full == a_res)
    return dict(S=S, K=K, ratio=ratio, m=m, trials=trials, identical=f"{same}/{trials}",
                t_full_ms=round(1000 * float(np.mean(tf)), 1), t_resume_ms=round(1000 * float(np.mean(tr_)), 2),
                mean_proposals=round(float(np.mean(props)), 1))

out = []
for cfg in [(2000, 20, 1.0, 1, 15), (2000, 20, 0.8, 5, 10), (5000, 20, 1.0, 1, 8), (5000, 20, 0.9, 20, 5)]:
    r = resume_test(*cfg); out.append(r); print(json.dumps(r), flush=True)
