# -*- coding: utf-8 -*-
"""Thử tiếp tục DA từ trạng thái cũ (mục G1) và so với chạy lại toàn bộ.
Chạy: python exp_resume.py <thư mục chứa rbda_priority_pipeline.py | PhanBoCauLacBo.exe>
Dữ liệu tự sinh."""
import importlib.util
import json
import numbers
import os
import random
import sys
import time


# Nạp _chung theo đường dẫn (không sửa sys.path); các mô-đun cùng thư mục khác nạp qua _chung.nap_canh.
_spec = importlib.util.spec_from_file_location(
    "tham_khao__chung", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_chung.py"))
_chung = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_chung)
gen, nap_rb = _chung.gen, _chung.nap_rb

# Gán ở khối __main__ (hoặc từ test) trước khi gọi resume_da / resume_test.
rb = None


_KHOA = ("students", "clubs", "tested", "apps", "prefs", "stb")


def _lay_rb():
    """Mô-đun rbda đang dùng: biến `rb` (gán ở __main__ / test), hoặc bản đã nạp trong tiến trình."""
    if rb is not None:
        return rb
    mod = sys.modules.get("rbda_priority_pipeline")
    if mod is None:
        raise ValueError("resume_da: chưa nạp rbda_priority_pipeline (gán exp_resume.rb hoặc dùng nap_rb).")
    return mod


def _so_boc_tham_hop_le(v):
    # Số thực bất kỳ (int, numpy.int64, float) nhưng không bool, không NaN; chuỗi đọc từ CSV thì không.
    return isinstance(v, numbers.Real) and not isinstance(v, bool) and v == v


def _nhom(v):
    # Như default_reserve_eligible_fn: nhóm rỗng ('' hay None) đều là "không có nhóm".
    return v or None


def _cung_diem(a, b):
    # So hai bảng điểm; NaN coi như bằng NaN (dict != thì NaN luôn khác).
    return a.keys() == b.keys() and all(a[k] == b[k] or (a[k] != a[k] and b[k] != b[k]) for k in a)


def kiem_tien_de(res0, cu, moi, new_ids):
    """Kiểm tiền đề của resume_da; vi phạm thì ValueError nêu rõ chỗ sai.

    `cu` là dữ liệu đã cho ra `res0`, `moi` là dữ liệu bây giờ; cả hai là dict có các khoá
    students, clubs, tested, apps, prefs, stb. Tiếp tục DA cho đúng kết quả chạy lại CHỈ khi thay đổi
    là "thêm ràng buộc" (mục G1): thêm em mới, hoặc GIẢM sức chứa. Mọi thay đổi khác (bớt ràng buộc,
    sửa dữ liệu em cũ, mở/đóng CLB mà em cũ có xếp) cần chạy lại toàn bộ (G2).
    Tra cứu bằng tập hợp (tuyến tính theo dữ liệu), cộng MỘT lần sắp em cũ theo số bốc thăm (n log n).
    """
    for k in _KHOA:
        if k not in cu or k not in moi:
            raise ValueError("resume_da: cu/moi thiếu khoá %r." % k)
    moi_set = set(new_ids)
    if len(moi_set) != len(new_ids):
        raise ValueError("resume_da: new_ids có mã trùng.")
    cu_hs = set(cu["students"])
    if moi_set & cu_hs:
        raise ValueError("resume_da: %s đã có trong lần chạy cũ (nộp lại cần chạy lại toàn bộ)."
                         % sorted(moi_set & cu_hs)[:5])
    if set(moi["students"]) != cu_hs | moi_set:
        raise ValueError("resume_da: danh sách học sinh mới phải đúng bằng em cũ cộng new_ids.")
    if set(res0.assignment) != cu_hs:
        raise ValueError("resume_da: res0 không phải kết quả của dữ liệu cũ (khác tập học sinh).")
    clubs0, clubs1 = cu["clubs"], moi["clubs"]
    if set(clubs0) - set(clubs1):
        raise ValueError("resume_da: CLB %s bị đóng (bớt ràng buộc, cần chạy lại)." % sorted(set(clubs0) - set(clubs1)))
    for c, info0 in clubs0.items():
        info1 = clubs1[c]
        if (info1["reserve_capacity"] != info0["reserve_capacity"]
                or _nhom(info1.get("reserve_group")) != _nhom(info0.get("reserve_group"))):
            raise ValueError("resume_da: CLB %s đổi dự trữ (cần chạy lại)." % c)
        if info1["capacity"] > info0["capacity"]:
            raise ValueError("resume_da: CLB %s tăng sức chứa (bớt ràng buộc, mục G2, cần chạy lại)." % c)
    loi_suc_chua = getattr(_lay_rb(), "loi_suc_chua", None)   # bản build cũ có thể chưa có luật này
    for c, info1 in clubs1.items():
        loi = loi_suc_chua(info1["capacity"], info1["reserve_capacity"]) if loi_suc_chua else None
        if loi:
            raise ValueError("resume_da: sức chứa mới của CLB %s không hợp lệ (%s)." % (c, loi))
    clb_moi = set(clubs1) - set(clubs0)
    for s in cu_hs:
        p0, p1 = cu["prefs"].get(s, []), moi["prefs"].get(s, [])
        if p0 != p1:
            raise ValueError("resume_da: nguyện vọng của em cũ %s đã đổi (cần chạy lại)." % s)
        if clb_moi.intersection(p1):
            raise ValueError("resume_da: em cũ %s có xếp CLB mới mở %s (cần chạy lại)."
                             % (s, sorted(clb_moi.intersection(p1))))
        if _nhom(cu["students"][s].get("reserve_group")) != _nhom(moi["students"][s].get("reserve_group")):
            raise ValueError("resume_da: nhóm dự trữ của em cũ %s đã đổi (cần chạy lại)." % s)
    for c in set(clubs0) | set(cu["tested"]):
        # Bỏ em mới ở CẢ hai phía: điểm nhập trước cho em đến muộn không phải "em cũ đổi điểm".
        t0 = {k: v for k, v in cu["tested"].get(c, {}).items() if k not in moi_set}
        t1 = {k: v for k, v in moi["tested"].get(c, {}).items() if k not in moi_set}
        if not _cung_diem(t0, t1):
            raise ValueError("resume_da: điểm của em cũ ở CLB %s đã đổi (cần chạy lại)." % c)
    apps_set = {c: set(v) for c, v in moi["apps"].items()}
    for c in clubs1:
        cu_apps = set(cu["apps"].get(c, ())) - moi_set
        if apps_set.get(c, set()) - moi_set != cu_apps:
            raise ValueError("resume_da: ứng viên cũ của CLB %s đã đổi (cần chạy lại)." % c)
    for s, ds in moi["prefs"].items():
        for c in ds:
            if c in clubs1 and s not in apps_set.get(c, ()):
                # Em không có thứ hạng cùng nhận len(rank); club_choice_function phân xử theo thứ tự
                # pool, vốn phụ thuộc lịch sử từng vòng -> tiếp tục và chạy lại có thể chọn khác em.
                raise ValueError("resume_da: %s xếp nguyện vọng %s nhưng không có trong apps[%s] "
                                 "(cần apps chứa mọi nguyện vọng, như hop_ung_vien)." % (s, c, c))
    cu_stb, moi_stb = cu["stb"], moi["stb"]
    for ten, bang, ds in (("cũ", cu_stb, cu_hs), ("mới", moi_stb, cu_hs | moi_set)):
        thieu = [s for s in ds if not _so_boc_tham_hop_le(bang.get(s))]
        if thieu:
            raise ValueError("resume_da: thiếu số bốc thăm hoặc không phải số (dữ liệu %s) của %s."
                             % (ten, sorted(thieu)[:5]))
    # Cùng khoá phá hoà như compute_club_priority: (số bốc thăm, mã em) — số bốc thăm có thể trùng.
    # Sắp một lần theo khoá cũ, rồi khoá mới phải tăng ngặt theo đúng thứ tự đó.
    thu_tu = sorted(cu_hs, key=lambda s: (cu_stb[s], s))
    khoa_moi = [(moi_stb[s], s) for s in thu_tu]
    if any(khoa_moi[i] >= khoa_moi[i + 1] for i in range(len(khoa_moi) - 1)):
        raise ValueError("resume_da: thứ tự bốc thăm của em cũ đã đổi (phải chèn bằng chen_stb_cho_hoc_sinh_moi).")


def resume_da(res0, cu, moi, new_ids, fn=None, da_kiem=False):
    """Tiếp tục DA từ kết quả cũ `res0` (của dữ liệu `cu`) sang dữ liệu `moi` = cu + new_ids.

    Cho đúng kết quả của run_rbda trên `moi` khi tiền đề của `kiem_tien_de` thoả (hàm tự kiểm, trừ
    khi da_kiem=True vì người gọi đã kiểm). Hỗ trợ: em đến muộn, CLB mới chỉ em mới xếp, GIẢM sức chứa.
    `fn` mặc định là default_reserve_eligible_fn của dữ liệu mới; truyền fn khác thì người gọi tự bảo đảm
    nó cho cùng kết quả với em cũ như lần chạy trước. Trả ({em: CLB} cho em có chỗ, số lần đề nghị).
    """
    if not da_kiem:
        kiem_tien_de(res0, cu, moi, new_ids)
    rb = _lay_rb()
    clubs, tested, apps, prefs, stb = (moi[k] for k in ("clubs", "tested", "apps", "prefs", "stb"))
    if fn is None:
        fn = rb.default_reserve_eligible_fn(moi["students"], clubs)
    clubs0 = cu["clubs"]
    # Tính lại thứ hạng ở CLB có em mới xếp và CLB mới mở. CLB khác: chỉ em cũ, cùng điểm, cùng thứ tự
    # bốc thăm tương đối -> thứ hạng cũ vẫn đúng.
    touched = set()
    for n in new_ids:
        touched.update(prefs.get(n, []))
    touched = (touched & set(clubs)) | (set(clubs) - set(clubs0))
    base_rank = {c: res0.base_rank.get(c, {}) for c in clubs}
    for c in touched:
        order = rb.compute_club_priority(c, apps.get(c, []), tested.get(c, {}), stb)
        base_rank[c] = {s: i for i, s in enumerate(order)}
    held = {c: [] for c in clubs}
    for s, c in res0.assignment.items():
        if c is not None:
            held[c].append(s)
    nxt = {s: (res0.rank_in_student_pref[s] - 1 if c is not None else len(prefs.get(s, [])))
           for s, c in res0.assignment.items()}
    for n in new_ids:
        nxt[n] = 0
    un = list(new_ids)
    props = 0

    def chon(c, pool):
        acc, _ = rb.club_choice_function(pool, clubs[c]['capacity'], clubs[c]['reserve_capacity'],
                                         (lambda s_, c=c: fn(s_, c)), base_rank[c])
        accs = set(acc)
        held[c] = acc
        for s in pool:
            if s not in accs:
                nxt[s] += 1
                un.append(s)

    # Giảm sức chứa = thêm ràng buộc: chọn lại trên tập đang giữ, em bị loại đề nghị tiếp.
    for c, info0 in clubs0.items():
        if clubs[c]['capacity'] < info0['capacity']:
            chon(c, held[c])
    while un:
        dot, un = un, []
        proposals = {}
        for s in dot:
            ds = prefs.get(s, [])
            if nxt[s] >= len(ds):
                continue
            c = ds[nxt[s]]
            if c not in clubs:
                # Như run_rbda: nguyện vọng trỏ tới CLB không có -> coi như bị từ chối ngay.
                nxt[s] += 1
                un.append(s)
                continue
            proposals.setdefault(c, []).append(s)
            props += 1
        for c, newa in proposals.items():
            chon(c, held[c] + newa)
    asg = {}
    for c, ds in held.items():
        for s in ds:
            asg[s] = c
    return asg, props


def resume_test(S, K, ratio, m, trials, seed=500):
    import numpy as np  # chỉ kịch bản đo cần; không phải phụ thuộc sản phẩm
    rb = _lay_rb()
    students, clubs, tested, apps, prefs = gen(S, K, ratio, seed=3)
    ids = list(students); stb = rb.generate_stb_lottery(ids, 42)
    for s in ids: students[s]['stb'] = stb[s]
    fn = rb.default_reserve_eligible_fn(students, clubs)
    res0 = rb.run_rbda(students, clubs, tested, apps, prefs, stb, fn)
    order_old = sorted(ids, key=lambda s: stb[s]); cids = list(clubs)
    pop = np.array([1.0 / ((j + 1) ** 1.0) for j in range(K)]); pop /= pop.sum()
    same = 0; tf = []; tr_ = []; tk = []; props = []
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
        cu = dict(students=students, clubs=clubs, tested=tested, apps=apps, prefs=prefs, stb=stb)
        moi = dict(students=st2, clubs=clubs, tested=te2, apps=ap2, prefs=pf2, stb=stbn)
        t = time.perf_counter(); full = rb.run_rbda(st2, clubs, te2, ap2, pf2, stbn, fn2); tf.append(time.perf_counter() - t)
        t = time.perf_counter(); kiem_tien_de(res0, cu, moi, new_ids); tk.append(time.perf_counter() - t)
        t = time.perf_counter(); asg, pp = resume_da(res0, cu, moi, new_ids, fn=fn2, da_kiem=True); tr_.append(time.perf_counter() - t); props.append(pp)
        a_full = {s: c for s, c in full.assignment.items() if c is not None}; a_res = dict(asg)
        same += (a_full == a_res)
    return dict(S=S, K=K, ratio=ratio, m=m, trials=trials, identical=f"{same}/{trials}",
                t_full_ms=round(1000 * float(np.mean(tf)), 1), t_resume_ms=round(1000 * float(np.mean(tr_)), 2),
                t_kiem_tien_de_ms=round(1000 * float(np.mean(tk)), 2),
                mean_proposals=round(float(np.mean(props)), 1))

if __name__ == "__main__":
    rb = nap_rb(sys.argv[1])
    out = []
    for cfg in [(2000, 20, 1.0, 1, 15), (2000, 20, 0.8, 5, 10), (5000, 20, 1.0, 1, 8), (5000, 20, 0.9, 20, 5)]:
        r = resume_test(*cfg); out.append(r); print(json.dumps(r), flush=True)
