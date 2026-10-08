# -*- coding: utf-8 -*-
"""
de_xuat_verify_nhanh.py — ĐỀ XUẤT thay thế cho rbda_priority_pipeline.verify_stability (L456–524).

Vì sao: verify_stability gọi lại club_choice_function cho MỖI cặp (học sinh, CLB học sinh ưa hơn
CLB hiện tại) trên tập "đang giữ + 1 em", tức là sắp xếp lại cả tập mỗi lần. Đo trên mã thật
(20 CLB, tỉ lệ chỗ 1,0): 10.000 học sinh -> run_rbda 1,08 s, verify_stability 24,3 s.

Ý tưởng: với một CLB, tập đang giữ H cố định. Sắp sẵn một lần thứ hạng của các em đủ tư cách dự trữ (E)
và không đủ tư cách (N). Khi thêm em s vào H:
  * nếu |H| + 1 <= capacity: club_choice_function nhận tất cả -> s được nhận;
  * ngược lại: lượt dự trữ giữ E[:reserve_capacity]; lượt phổ thông xếp phần còn lại theo thứ hạng,
    nên chỉ cần biết vị trí của s trong dãy đó = (#E đứng trước s, trừ reserve_capacity) + (#N đứng trước s),
    tra bằng bisect_right (O(log n)).

Chỉ đúng cho CẤU TRÚC HAI LƯỢT hiện tại của club_choice_function (dự trữ rồi phổ thông). Hàm lựa chọn
khác (A3 trong sổ đăng ký) phải dùng bản gốc hoặc có bản nhanh riêng.

Đã thử (xem kiem_verify_nhanh.py): trả đúng cùng danh sách cặp phá vỡ (kể cả các trường params) với bản gốc
trên 7 cấu hình: 3 kết quả thật (0 cặp ở 2.000, 5.000, 10.000 học sinh) và 4 kết quả bị hoán đổi, trong đó mọi CLB
đều đầy và có suất dự trữ (23.110 cặp phá vỡ nhân tạo, giống hệt). Thời gian ở 10.000 học sinh: 22,4 s (gốc) so với 0,09 s.
"""
from bisect import bisect_right


def verify_stability_nhanh(result, clubs, preferences, is_reserve_eligible_fn, err=None):
    """Cùng chữ ký và cùng hình dạng kết quả với verify_stability.

    Trả về list[{"code": "blocking_pair", "params": {...}}] nếu truyền `err` (hàm err của i18n_errors);
    nếu không truyền, trả về list[dict] cùng khoá params.
    """
    import sys
    rb = sys.modules.get("rbda_priority_pipeline")
    if rb is None:
        import rbda_priority_pipeline as rb
    # Kiểm sức chứa bằng CHÍNH club_choice_function của mô-đun đã nạp (kho mã hay bản build),
    # nên cùng luật, cùng thông báo lỗi, và bản build cũ không có luật này thì cũng không báo.
    da_kiem = set()

    assignment = result.assignment
    held = {cid: [] for cid in clubs}
    for sid, cid in assignment.items():
        if cid is not None:
            held[cid].append(sid)

    chuan_bi = {}
    for cid, info in clubs.items():
        rank = result.base_rank.get(cid, {})
        # Cùng thứ hạng như club_choice_function: em không có trong rank xếp cuối.
        hang_cuoi = len(rank)
        e, n = [], []
        for s in held[cid]:
            (e if is_reserve_eligible_fn(s, cid) else n).append(rank.get(s, hang_cuoi))
        e.sort()
        n.sort()
        chuan_bi[cid] = (e, n, len(held[cid]), info["capacity"], info["reserve_capacity"])

    problems = []
    for sid, prefs in preferences.items():
        current_club = assignment.get(sid)
        current_idx = prefs.index(current_club) if current_club in prefs else len(prefs)
        for cid in prefs[:current_idx]:
            if cid not in clubs:
                continue
            rank = result.base_rank.get(cid, {})
            if sid not in rank:
                continue
            e, n, n_giu, capacity, reserve_capacity = chuan_bi[cid]
            if cid not in da_kiem:
                # verify_stability gọi club_choice_function ở đây, và nó báo lỗi sức chứa trước tiên.
                rb.club_choice_function([], capacity, reserve_capacity, lambda _s: False, {})
                da_kiem.add(cid)
            if n_giu + 1 <= capacity:
                duoc_nhan = True
            else:
                r = rank[sid]
                du_tu_cach = is_reserve_eligible_fn(sid, cid)
                # bisect_right: club_choice_function sắp ổn định trên (đang giữ + [sid]),
                # nên khi trùng thứ hạng (em không có trong rank nhận len(rank)) sid đứng SAU.
                p = bisect_right(e, r)
                if du_tu_cach and p < reserve_capacity:
                    duoc_nhan = True
                else:
                    vi_tri = max(0, p - reserve_capacity) + bisect_right(n, r)
                    cho_pho_thong = capacity - min(reserve_capacity, len(e) + (1 if du_tu_cach else 0))
                    duoc_nhan = vi_tri < cho_pho_thong
            if duoc_nhan:
                params = dict(student_id=sid, club_id=cid, current_club=current_club,
                              n_holders=n_giu, capacity=capacity)
                problems.append(err("blocking_pair", **params) if err else {"code": "blocking_pair", "params": params})
    return problems
