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


def verify_stability_nhanh(result, clubs, preferences, is_reserve_eligible_fn):
    """Cùng chữ ký, cùng kết quả và cùng lỗi với rbda_priority_pipeline.verify_stability.

    Trả list[{"code": "blocking_pair", "params": {...}}] dựng bằng `err` của i18n_errors như bản gốc.
    Chỉ đọc dữ liệu của CLB nào thật sự được xét (lười như bản gốc): CLB không ai muốn chuyển tới thì
    không đọc capacity, không gọi hàm đủ tư cách.
    """
    import sys
    from i18n_errors import err
    rb = sys.modules.get("rbda_priority_pipeline")
    if rb is None:
        import rbda_priority_pipeline as rb

    assignment = result.assignment
    held = {cid: [] for cid in clubs}
    for sid, cid in assignment.items():
        if cid is not None:
            held[cid].append(sid)

    chuan_bi = {}

    def lay_chuan_bi(cid, sid):
        if cid in chuan_bi:
            return chuan_bi[cid]
        info = clubs[cid]
        capacity, reserve_capacity = info["capacity"], info["reserve_capacity"]
        rank = result.base_rank.get(cid, {})
        # Lần đầu xét CLB này, gọi ĐÚNG lời gọi của bản gốc (đang giữ + [sid], hàm đủ tư cách thật,
        # thứ hạng thật) bằng club_choice_function của mô-đun đã nạp: mọi kiểm tra đầu vào của nó —
        # hôm nay là sức chứa, sau này có thể thêm — chạy y hệt, cùng thông báo lỗi. Một lần mỗi CLB.
        rb.club_choice_function(held[cid] + [sid], capacity, reserve_capacity,
                                lambda s_: is_reserve_eligible_fn(s_, cid), rank)
        # Cùng thứ hạng như club_choice_function: em không có trong rank xếp cuối.
        hang_cuoi = len(rank)
        e, n = [], []
        for s in held[cid]:
            (e if is_reserve_eligible_fn(s, cid) else n).append(rank.get(s, hang_cuoi))
        e.sort()
        n.sort()
        chuan_bi[cid] = (e, n, len(held[cid]), capacity, reserve_capacity)
        return chuan_bi[cid]

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
            e, n, n_giu, capacity, reserve_capacity = lay_chuan_bi(cid, sid)
            # Bản gốc luôn gọi hàm đủ tư cách cho cả ứng viên (kể cả khi CLB còn chỗ): gọi y như vậy.
            du_tu_cach = is_reserve_eligible_fn(sid, cid)
            if n_giu + 1 <= capacity:
                duoc_nhan = True
            else:
                r = rank[sid]
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
                problems.append(err("blocking_pair", student_id=sid, club_id=cid, current_club=current_club,
                                    n_holders=n_giu, capacity=capacity))
    return problems
