# -*- coding: utf-8 -*-
"""Thử tiếp tục DA từ trạng thái cũ (mục G1) và so với chạy lại toàn bộ.
Chạy: python exp_resume.py <thư mục chứa rbda_priority_pipeline.py | PhanBoCauLacBo.exe>
Dữ liệu tự sinh."""
import importlib.util
import json
import os
import random
import sys
import time


def _nap_canh(ten):
    """Nạp mô-đun cùng thư mục theo đường dẫn, không sửa sys.path."""
    duong = os.path.join(os.path.dirname(os.path.abspath(__file__)), ten + ".py")
    spec = importlib.util.spec_from_file_location("tham_khao_" + ten, duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_chung = _nap_canh("_chung")
gen, nap_rb = _chung.gen, _chung.nap_rb

# Gán ở khối __main__ (hoặc từ test) trước khi gọi resume_da / resume_test.
rb = None


def resume_da(res0, clubs, tested, apps, prefs, stb, fn, new_ids):
    """Tiếp tục DA từ kết quả cũ `res0` sau khi thêm `new_ids`; phải cho đúng kết quả của run_rbda.

    Tiền đề: mọi (em, CLB) trong nguyện vọng đều có trong apps của CLB đó — đường thật bảo đảm
    điều này bằng `hop_ung_vien`. Nếu không, các em không có thứ hạng cùng nhận len(rank) và
    club_choice_function phân xử theo thứ tự trong pool, vốn phụ thuộc lịch sử từng vòng nên
    tiếp tục và chạy lại có thể chọn khác em. Vì vậy hàm từ chối dữ liệu như vậy thay vì lặng lẽ lệch.
    """
    for s, ds in prefs.items():
        for c in ds:
            if c in clubs and s not in apps.get(c, ()):
                raise ValueError("resume_da: %s xếp nguyện vọng %s nhưng không có trong apps[%s] "
                                 "(cần apps chứa mọi nguyện vọng, như hop_ung_vien)." % (s, c, c))
    # Tính lại thứ hạng cho CLB em mới đăng ký và CLB chưa có trong lần chạy cũ; bỏ ID CLB không tồn tại.
    touched = set()
    for n in new_ids: touched.update(prefs[n])
    touched = (touched | (set(clubs) - set(res0.base_rank))) & set(clubs)
    base_rank = {c: res0.base_rank.get(c, {}) for c in clubs}
    for c in touched:
        order = rb.compute_club_priority(c, apps.get(c, []), tested.get(c, {}), stb)
        base_rank[c] = {s: i for i, s in enumerate(order)}
    held = {c: [] for c in clubs}
    for s, c in res0.assignment.items():
        if c is not None: held[c].append(s)
    nxt = {s: (res0.rank_in_student_pref[s] - 1 if res0.assignment.get(s) is not None else len(prefs.get(s, [])))
           for s in res0.assignment}
    for n in new_ids: nxt[n] = 0
    un = list(new_ids); props = 0
    while un:
        proposals = {}; still = []
        for s in un:
            ds = prefs.get(s, [])
            if nxt[s] >= len(ds): continue
            c = ds[nxt[s]]
            if c not in clubs:
                # Như run_rbda: nguyện vọng trỏ tới CLB không có -> coi như bị từ chối ngay.
                nxt[s] += 1; still.append(s); continue
            proposals.setdefault(c, []).append(s); props += 1
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
    import numpy as np  # chỉ kịch bản đo cần; không phải phụ thuộc sản phẩm
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
        a_full = {s: c for s, c in full.assignment.items() if c is not None}; a_res = dict(asg)
        same += (a_full == a_res)
    return dict(S=S, K=K, ratio=ratio, m=m, trials=trials, identical=f"{same}/{trials}",
                t_full_ms=round(1000 * float(np.mean(tf)), 1), t_resume_ms=round(1000 * float(np.mean(tr_)), 2),
                mean_proposals=round(float(np.mean(props)), 1))

if __name__ == "__main__":
    rb = nap_rb(sys.argv[1])
    out = []
    for cfg in [(2000, 20, 1.0, 1, 15), (2000, 20, 0.8, 5, 10), (5000, 20, 1.0, 1, 8), (5000, 20, 0.9, 20, 5)]:
        r = resume_test(*cfg); out.append(r); print(json.dumps(r), flush=True)
