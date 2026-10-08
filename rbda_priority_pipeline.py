"""
rbda_priority_pipeline.py
==========================
Module thuật toán cho hệ thống phân bổ Câu lạc bộ dùng
Reserve-Based Deferred Acceptance (RB-DA) với dự trữ mềm
(soft reserves, precedence ordering — Kominers & Sonmez 2016)
và Single Tie-Breaking (STB).

Module này giờ ĐÃ có I/O SQLite đầy đủ (init_db, load_from_sqlite,
write_match_results_to_sqlite) dựa trên DEFAULT_SCHEMA — ĐÃ ĐƯỢC
CHỐT LÀM SCHEMA CHÍNH THỨC (không có 02_schema.sql riêng biệt nào
khác — DEFAULT_SCHEMA trong file này LÀ nguồn sự thật duy nhất).

LƯU Ý NGUỒN: các tệp `03_reference_rbda.py`, `compare_with_reference.py`,
`06_ms_forms_transform.py` và `expected_match_results.csv` được nhắc trong
chú thích dưới đây là bản tham chiếu dùng lúc viết thuật toán và CHƯA BAO
GIỜ được đưa vào kho (xem BAN_GIAO.md mục 8). Phần kiểm chứng còn chạy
được nằm trong kho: `verify_stability()` (không có cặp phá vỡ) và bộ test
`tests/test_pipeline_core.py`, `tests/test_toi_uu_on_dinh.py`.

Định dạng dữ liệu trong bộ nhớ (khớp quy ước 03_reference_rbda.py
và output của 06_ms_forms_transform.py):

    students: dict[str, dict]
        { student_id: {"stb": int} }

    clubs: dict[str, dict]
        { club_id: {"capacity": int, "reserve_capacity": int} }

    tested_scores: dict[str, dict[str, float]]
        { club_id: { student_id: score } }
        -> chỉ chứa học sinh ĐÃ được chấm (Tier 1) cho club đó.
           Học sinh không xuất hiện ở đây nhưng có trong
           `applicants[club_id]` => thuộc Tier 2.

    applicants: dict[str, list[str]]
        { club_id: [student_id, ...] }
        -> toàn bộ học sinh đã tick chọn thi/xét club này
           (từ bước UI tick-box, tách biệt khỏi bước xếp hạng).

    preferences: dict[str, list[str]]
        { student_id: [club_id_rank1, club_id_rank2, ...] }
        -> danh sách nguyện vọng đã xếp hạng của học sinh
           (tối đa 10 club theo giới hạn Microsoft Forms Ranking).
"""

from dataclasses import dataclass, field
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# BUỔI SINH HOẠT
# ---------------------------------------------------------------------------
#
# Một CLB sinh hoạt đúng MỘT buổi trong tuần. Hai CLB cùng giá trị `buoi`
# là trùng giờ, nên một em chỉ vào được một trong hai.
#
# `buoi` cố ý là NHÃN TỰ DO chứ không phải danh sách cố định thứ-2..thứ-7.
# Trường hiện chỉ tổ chức vào tiết 9 nên nhãn bằng ngày là đủ; nếu sau này
# có thêm tiết thì "thu_3_tiet_9" và "thu_3_tiet_10" chạy được ngay mà
# không đổi một dòng thuật toán nào — vì thuật toán chỉ hỏi "hai nhãn này
# có bằng nhau không", không bao giờ diễn giải nội dung nhãn.
#
# CLB chưa khai buổi (NULL/rỗng) thuộc buổi mặc định. Trường chỉ tổ chức
# một buổi thì MỌI CLB nằm ở đây, và toàn bộ phần nhiều buổi thu về đúng
# một lần gọi run_rbda — tức đúng phần mềm cũ.
BUOI_MAC_DINH = "__mac_dinh__"


# ---------------------------------------------------------------------------
# TRẦN SỐ LƯỢNG — ĐẾM THEO TỪNG BUỔI, KHÔNG PHẢI CẢ TUẦN
# ---------------------------------------------------------------------------
#
# Hai con số này từng được đếm cho CẢ TUẦN, và đó là một lỗi có thật, đã đo
# được: em nào chọn 2 CLB mỗi buổi qua sáu buổi là 12 nguyện vọng, vượt trần,
# và bước nạp BỎ QUA TRỌN học sinh đó. Trên bộ `bo_sau_buoi` nó lặng lẽ gạt
# 31 trên 180 em ra khỏi đợt xếp; trên `bo_nhieu_buoi` là 4 em. Nhìn màn hình
# Kết quả thì những em đó hiện ra y như em trượt, mà thật ra chưa bao giờ
# được vào cuộc.
#
# Đếm theo buổi là cách duy nhất đúng, vì các buổi ĐỘC LẬP với nhau: không
# ràng buộc nào nối hai buổi, nên trần của buổi này không có lý do gì ăn vào
# buổi kia.
#
# Trường MỘT buổi: mọi CLB thuộc BUOI_MAC_DINH, nên "10 mỗi buổi" thu về
# đúng "10 tổng" — hành vi y hệt bản cũ, và mọi số liệu trong
# docs/NGHIEN_CUU_TOI_UU.md vẫn nói về phần mềm đang chạy.

# 10 = số mục tối đa của một câu hỏi Ranking trên Microsoft Forms. Mỗi buổi
# là MỘT câu Ranking riêng, nên trần theo buổi khớp đúng công cụ thu phiếu.
TRAN_NGUYEN_VONG_MOI_BUOI = 10

# 5 là chính sách nhà trường, không phải giới hạn kỹ thuật — thi quá năm CLB
# trong một buổi thì không trường nào chấm xuể. Sửa con số này phải kiểm lại
# bộ TEST_02: nó đứng ĐÚNG 5, không có suất dự phòng nào.
TRAN_CLB_THI_MOI_BUOI = 5


def gom_theo_buoi(
    ds_clb: list[str], clubs: dict[str, dict]
) -> dict[str, list[str]]:
    """{buoi: [club_id]} — giữ nguyên thứ tự xuất hiện trong `ds_clb`.

    Giữ thứ tự là bắt buộc, không phải tiện tay: danh sách nguyện vọng là một
    thứ hạng, và thuật toán lọc nó theo buổi rồi dùng phần còn lại. Xáo thứ
    tự ở đây là đổi nguyện vọng của học sinh.

    CLB lạ (không có trong `clubs`) xếp vào buổi mặc định thay vì bị bỏ đi —
    việc báo CLB không tồn tại là của bước kiểm khác, và nuốt mất nó ở đây
    sẽ khiến một danh sách sai lại trông như hợp lệ.
    """
    theo_buoi: dict[str, list[str]] = {}
    for cid in ds_clb:
        buoi = (clubs.get(cid, {}).get("buoi") or BUOI_MAC_DINH)
        theo_buoi.setdefault(buoi, []).append(cid)
    return theo_buoi


# ---------------------------------------------------------------------------
# BƯỚC A — HÀM ƯU TIÊN HAI TẦNG (compute_club_priority)
# ---------------------------------------------------------------------------

def compute_club_priority(
    club_id: str,
    applicants_for_club: list[str],
    tested_scores_for_club: dict[str, float],
    stb_lottery: dict[str, int],
) -> list[str]:
    """
    Tính thứ tự ưu tiên hai tầng cho MỘT club.

    Tầng 1 (đã được chấm điểm — tested):
        sắp giảm dần theo điểm; bằng điểm -> STB tăng dần.
    Tầng 2 (chưa được chấm — untested):
        sắp hoàn toàn theo STB tăng dần.
    Tầng 1 LUÔN đứng trước Tầng 2 toàn bộ (không xen kẽ).

    RÀNG BUỘC BẮT BUỘC (chống nội sinh / endogeneity):
        Hàm này KHÔNG được nhận bất kỳ tham số nào liên quan đến
        thứ hạng nguyện vọng (preference rank) của học sinh.
        Nếu sau này cần mở rộng, TUYỆT ĐỐI không truyền `preferences`
        vào hàm này dưới bất kỳ hình thức nào.

        `tested_scores_for_club` phải đến từ quy trình chấm mù
        (giám khảo không thấy STB / thứ hạng nguyện vọng khi chấm).
        Việc đảm bảo "mù" là ràng buộc ở tầng UI/quy trình nhập liệu,
        hàm này không (và không thể) tự kiểm tra được điều đó.

    Args:
        club_id: id của club (chỉ dùng để thông báo lỗi, không ảnh
            hưởng logic).
        applicants_for_club: toàn bộ student_id đã tick chọn club này.
        tested_scores_for_club: {student_id: score} — tập con của
            applicants_for_club đã được chấm điểm.
        stb_lottery: {student_id: số bốc thăm} toàn hệ thống (một số
            duy nhất/học sinh, dùng chung mọi club — Single
            Tie-Breaking).

    Returns:
        list[str]: student_id đã sắp theo thứ tự ưu tiên giảm dần
        (đầu danh sách = ưu tiên cao nhất).

    Raises:
        ValueError: nếu có applicant thiếu STB (dữ liệu không toàn vẹn).
    """
    # `is None` cũng là thiếu: cột stb_number cho phép NULL (học sinh tạo ở
    # kiosk sau lần bốc thăm), và None lọt qua đây thì phép sắp xếp ở dưới
    # ném TypeError khó hiểu thay vì báo đúng nguyên nhân.
    missing_stb = [
        sid for sid in applicants_for_club if stb_lottery.get(sid) is None
    ]
    if missing_stb:
        raise ValueError(
            f"[{club_id}] Có {len(missing_stb)} học sinh thiếu số bốc "
            f"thăm STB: {missing_stb[:5]}{'...' if len(missing_stb) > 5 else ''}"
        )

    tier1 = [sid for sid in applicants_for_club if sid in tested_scores_for_club]
    tier2 = [sid for sid in applicants_for_club if sid not in tested_scores_for_club]

    # Mã học sinh là khoá phá hoà CUỐI: số bốc thăm bình thường không bao
    # giờ trùng (generate_stb_lottery hoán vị 1..n), nhưng CSDL không có
    # ràng buộc UNIQUE, nên sửa tay hay dữ liệu cũ vẫn có thể trùng. Khi đó
    # thứ tự từng phụ thuộc thứ tự nhập — cùng dữ liệu, khác kết quả.
    tier1_sorted = sorted(
        tier1,
        key=lambda sid: (-tested_scores_for_club[sid], stb_lottery[sid], sid),
    )
    tier2_sorted = sorted(tier2, key=lambda sid: (stb_lottery[sid], sid))

    return tier1_sorted + tier2_sorted


# ---------------------------------------------------------------------------
# BƯỚC B — XỬ LÝ DỰ TRỮ MỀM (soft reserve, precedence ordering)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# BƯỚC B — HÀM LỰA CHỌN CỦA CLUB (choice function), TÍNH LẠI MỖI VÒNG
# ---------------------------------------------------------------------------
#
# LƯU Ý QUAN TRỌNG (bài học từ đối chiếu với 03_reference_rbda.py):
# Bản đầu tiên của em dùng build_processed_priority() để gộp reserve+general
# thành MỘT thứ tự ưu tiên tổng thể, tính MỘT LẦN cho toàn bộ applicant.
# ĐÂY LÀ LỖI: nếu học sinh eligible có ưu tiên cao nhất TOÀN CỤC lại
# KHÔNG xuất hiện trong pool thực tế của một vòng cụ thể (vd đã được giữ
# ở club khác), thứ tự tĩnh đó tính sai — nó để một học sinh KHÔNG eligible
# chen vào suất lẽ ra phải thuộc về học sinh eligible xếp hạng thấp hơn
# nhưng đang có mặt. Đã verify bằng test case cụ thể (xem
# compare_with_reference.py) và bằng cách đối chiếu trực tiếp với
# 03_reference_rbda.py — bản reference tính LẠI reserve pass + general pass
# từ ĐÚNG pool đang có mặt ở MỖI vòng, không dùng thứ tự tĩnh.
#
# club_choice_function() dưới đây thay thế build_processed_priority(),
# đúng theo logic reference: reserve pass trước (chỉ trong nội bộ pool
# hiện tại), general pass sau (phần dư reserve tự động chuyển sang).

def loi_suc_chua(capacity: int, reserve_capacity: int) -> Optional[str]:
    """Luật DUY NHẤT cho sức chứa một CLB; trả về tên lỗi hoặc None.

    Ba nơi nhận sức chứa (form CLB, tệp CSV, kiểm dữ liệu trước khi chạy)
    trước đây tự viết điều kiện riêng, và cả ba cùng quên số dự trữ ÂM.
    Mà âm thì phép cắt `ds[:reserve_capacity]` trong club_choice_function
    hiểu là "tất cả trừ vài em cuối": dự trữ -1 thành gần như toàn bộ
    suất là suất dự trữ, pipeline vẫn chạy và không báo gì.
    """
    if capacity <= 0:
        return "capacity_not_positive"
    if reserve_capacity < 0:
        return "reserve_negative"
    if reserve_capacity > capacity:
        return "reserve_exceeds_capacity"
    return None


def club_choice_function(
    pool: list[str],
    capacity: int,
    reserve_capacity: int,
    is_reserve_eligible_fn: Callable[[str], bool],
    rank: dict[str, int],
) -> tuple[list[str], dict[str, str]]:
    """
    Áp dụng hàm lựa chọn của MỘT club cho MỘT pool ứng viên cụ thể
    (đây chính là "reserve pass rồi general pass" — Kominers & Sonmez
    2016 — nhưng tính LẠI MỖI LẦN gọi, không dùng thứ tự tĩnh).

    Args:
        pool: danh sách student_id đang cạnh tranh vào club này NGAY
            LÚC NÀY (có thể là 1 vòng DA, hoặc dùng để kiểm chứng
            stability với pool = held ∪ {ứng viên nghi ngờ}).
        capacity: tổng sức chứa.
        reserve_capacity: số suất dự trữ (soft — không khoá cứng).
        is_reserve_eligible_fn: (student_id) -> bool, ĐÃ áp dụng sẵn
            club_id cụ thể (dùng closure/lambda khi gọi).
        rank: {student_id: int} thứ hạng ưu tiên NỀN (từ
            compute_club_priority) — số nhỏ hơn = ưu tiên cao hơn.
            Đây là thứ tự HỢP LỆ để dùng làm khoá sắp xếp cho BẤT KỲ
            tập con nào của applicant (vì compute_club_priority không
            phụ thuộc pool, chỉ phụ thuộc điểm/STB — sắp xếp con của
            một dãy đã sắp xếp vẫn đúng thứ tự). Cái DUY NHẤT phải
            tính lại mỗi vòng là VIỆC PHÂN NHÓM reserve/general, không
            phải bản thân thứ hạng ưu tiên.

    Returns:
        (accepted: list[str], tier_of: dict[str, "reserve"|"general"])
    """
    # Chặn tại chỗ, không chỉ trông vào validate_data_integrity: hàm này
    # được gọi thẳng từ verify_stability và các kịch bản đo đạc, và cắt
    # danh sách bằng số âm thì sai lặng lẽ thay vì báo lỗi.
    loi = loi_suc_chua(capacity, reserve_capacity)
    if loi:
        raise ValueError(
            f"Suc chua khong hop le ({loi}): capacity={capacity}, "
            f"reserve_capacity={reserve_capacity}")
    reserve_candidates = sorted(
        (s for s in pool if is_reserve_eligible_fn(s)),
        key=lambda s: rank.get(s, len(rank)),
    )
    reserve_held = reserve_candidates[:reserve_capacity]
    reserve_held_set = set(reserve_held)

    general_capacity = capacity - len(reserve_held)
    general_candidates = sorted(
        (s for s in pool if s not in reserve_held_set),
        key=lambda s: rank.get(s, len(rank)),
    )
    general_held = general_candidates[:general_capacity]

    tier_of = {s: "reserve" for s in reserve_held}
    tier_of.update({s: "general" for s in general_held})
    return reserve_held + general_held, tier_of


# ---------------------------------------------------------------------------
# BƯỚC C — VÒNG LẶP DEFERRED ACCEPTANCE (student-proposing)
# ---------------------------------------------------------------------------

@dataclass
class MatchResult:
    assignment: dict[str, Optional[str]]  # student_id -> club_id | None
    rounds_run: int
    rejection_log: list[tuple[int, str, str]] = field(default_factory=list)
    # (round_number, student_id, club_id_rejected_from)
    base_rank: dict[str, dict[str, int]] = field(default_factory=dict)
    # club_id -> {student_id: rank} — thứ hạng ưu tiên NỀN (không phải
    # thứ tự đã xử lý dự trữ tĩnh — dùng cùng club_choice_function()
    # để kiểm tra stability đúng với hàm lựa chọn động).
    matched_tier: dict[str, str] = field(default_factory=dict)
    # student_id -> "reserve" | "general", chỉ có với học sinh đã match.
    rank_in_student_pref: dict[str, int] = field(default_factory=dict)
    # student_id -> thứ hạng nguyện vọng (1-indexed) đã được xếp.


def run_rbda(
    students: dict[str, dict],
    clubs: dict[str, dict],
    tested_scores: dict[str, dict[str, float]],
    applicants: dict[str, list[str]],
    preferences: dict[str, list[str]],
    stb_lottery: dict[str, int],
    is_reserve_eligible_fn: Callable[[str, str], bool],
    max_rounds: int = 1000,
) -> MatchResult:
    """
    Chạy thuật toán RB-DA đầy đủ (student-proposing deferred
    acceptance), reserve pass + general pass TÍNH LẠI mỗi vòng cho
    mỗi club (club_choice_function) — đã đối chiếu khớp 100% với
    03_reference_rbda.py trên nhiều bộ dữ liệu (xem compare_with_reference.py).

    Args:
        students: xem docstring đầu file.
        clubs: {club_id: {"capacity": int, "reserve_capacity": int}}
        tested_scores, applicants, preferences, stb_lottery: xem đầu file.
        is_reserve_eligible_fn: (student_id, club_id) -> bool.
        max_rounds: chặn vòng lặp vô hạn nếu có lỗi dữ liệu. ĐÃ ĐO cận
            trên thật: số vòng chạy đúng bằng ĐỘ DÀI DANH SÁCH NGUYỆN
            VỌNG dài nhất (10 nguyện vọng -> 10 vòng; 100 -> 100), vì
            mỗi vòng, mỗi em chưa có chỗ tiến đúng một nguyện vọng. App
            chặn cứng 10 nguyện vọng (api.py), nên trần 1000 ở đây gấp
            100 lần mức cần. Chạm được trần này nghĩa là dữ liệu hỏng
            theo cách chưa từng thấy — xem chỗ raise ngay sau vòng lặp.

    Returns:
        MatchResult
    """
    held: dict[str, list[str]] = {cid: [] for cid in clubs}
    held_tier: dict[str, dict[str, str]] = {cid: {} for cid in clubs}
    next_choice_idx: dict[str, int] = {sid: 0 for sid in students}
    rejection_log: list[tuple[int, str, str]] = []

    # base_rank chỉ phụ thuộc điểm/STB, KHÔNG phụ thuộc pool -> tính
    # một lần là đúng (khác với việc phân nhóm reserve/general, PHẢI
    # tính lại mỗi vòng — xem club_choice_function ở trên).
    base_rank: dict[str, dict[str, int]] = {}
    for club_id in clubs:
        base_order = compute_club_priority(
            club_id=club_id,
            applicants_for_club=applicants.get(club_id, []),
            tested_scores_for_club=tested_scores.get(club_id, {}),
            stb_lottery=stb_lottery,
        )
        base_rank[club_id] = {sid: i for i, sid in enumerate(base_order)}

    unassigned = [
        sid
        for sid in students
        if next_choice_idx[sid] < len(preferences.get(sid, []))
    ]

    round_num = 0
    while unassigned and round_num < max_rounds:
        round_num += 1
        proposals: dict[str, list[str]] = {cid: [] for cid in clubs}

        still_unassigned = []
        for sid in unassigned:
            prefs = preferences.get(sid, [])
            idx = next_choice_idx[sid]
            if idx >= len(prefs):
                continue  # hết nguyện vọng -> không xếp được (unmatched)
            club_id = prefs[idx]
            if club_id not in clubs:
                # Nguyện vọng trỏ tới club không tồn tại -> bỏ qua, coi
                # như bị từ chối ngay, thử nguyện vọng kế tiếp vòng sau.
                next_choice_idx[sid] += 1
                still_unassigned.append(sid)
                continue
            proposals[club_id].append(sid)

        for club_id, new_applicants in proposals.items():
            # CLB không có ai mới nộp thì bỏ qua: hàm lựa chọn áp lên chính
            # kết quả của nó cho ra y hệt (tập đang giữ ≤ sức chứa, và top
            # dự trữ của pool cũ vẫn là top dự trữ của tập con đang giữ).
            # Trước đây mỗi vòng tính lại MỌI CLB, kể cả CLB đứng yên.
            if not new_applicants:
                continue
            pool = held[club_id] + new_applicants
            rank = base_rank[club_id]
            capacity = clubs[club_id]["capacity"]
            reserve_capacity = clubs[club_id]["reserve_capacity"]
            eligible_fn = lambda sid, _cid=club_id: is_reserve_eligible_fn(sid, _cid)

            accepted, tier_of = club_choice_function(
                pool, capacity, reserve_capacity, eligible_fn, rank
            )
            accepted_set = set(accepted)
            rejected = [s for s in pool if s not in accepted_set]

            held[club_id] = accepted
            held_tier[club_id] = tier_of
            for sid in rejected:
                rejection_log.append((round_num, sid, club_id))
                next_choice_idx[sid] += 1
                still_unassigned.append(sid)

        unassigned = [
            sid
            for sid in still_unassigned
            if next_choice_idx[sid] < len(preferences.get(sid, []))
        ]

    # Chạm trần = vòng lặp bị CẮT CỤT giữa chừng, và kết quả trả về là
    # dở dang: có em còn nguyện vọng chưa thử. Trước đây hàm lặng lẽ trả
    # kết quả đó ra; verify_stability() gần như chắc chắn bắt được (em
    # dở dang tạo cặp phá vỡ), nhưng người đọc sẽ nhận một câu báo lỗi
    # nói SAI nguyên nhân. Nói thẳng ra ở đây rẻ hơn nhiều.
    if unassigned and round_num >= max_rounds:
        raise RuntimeError(
            "run_rbda cham tran %d vong ma con %d hoc sinh chua thu het "
            "nguyen vong. Ket qua se DO DANG nen khong tra ve. Can tren "
            "that = do dai danh sach nguyen vong dai nhat, nen cham tran "
            "nghia la du lieu hong hoac max_rounds bi ha xuong qua thap."
            % (max_rounds, len(unassigned))
        )

    assignment: dict[str, Optional[str]] = {sid: None for sid in students}
    matched_tier: dict[str, str] = {}
    rank_in_pref: dict[str, int] = {}
    for club_id, held_students in held.items():
        for sid in held_students:
            assignment[sid] = club_id
            matched_tier[sid] = held_tier[club_id].get(sid, "general")
            rank_in_pref[sid] = next_choice_idx[sid] + 1

    return MatchResult(
        assignment=assignment,
        rounds_run=round_num,
        rejection_log=rejection_log,
        base_rank=base_rank,
        matched_tier=matched_tier,
        rank_in_student_pref=rank_in_pref,
    )


def verify_stability(
    result: MatchResult,
    clubs: dict[str, dict],
    preferences: dict[str, list[str]],
    is_reserve_eligible_fn: Callable[[str, str], bool],
) -> list[dict]:
    """
    Kiểm chứng KHÔNG TỒN TẠI blocking pair, dùng ĐÚNG hàm lựa chọn
    động (club_choice_function) — tức là kiểm tra trực tiếp: "nếu
    thêm sid vào tập đang giữ của club cid, hàm lựa chọn của club đó
    CÓ nhận sid không?" Đây là định nghĩa stability tổng quát, đúng
    cho cả trường hợp choice function không phải một thứ tự tuyến
    tính cố định (như RB-DA) — khác với cách làm cũ (dùng
    processed_priority tĩnh) đã bị phát hiện SAI khi đối chiếu với
    03_reference_rbda.py.

    Định nghĩa blocking pair (student sid, club cid):
        sid thích cid hơn club hiện tại của mình (hoặc đang unmatched
        mà cid vẫn còn nguyện vọng), VÀ khi thêm sid vào
        held[cid] hiện tại rồi áp dụng lại club_choice_function,
        sid NẰM TRONG tập được chọn.

    Returns:
        list[dict]: {"code": "blocking_pair", "params": {...}} cho mỗi
        blocking pair tìm được (xem i18n_errors.py). Rỗng = kết quả ổn
        định (đúng theo lý thuyết, đúng theo club_choice_function thật
        của cơ chế).
    """
    from i18n_errors import err

    problems: list[dict] = []
    assignment = result.assignment

    held_by_club: dict[str, list[str]] = {cid: [] for cid in clubs}
    for sid, cid in assignment.items():
        if cid is not None:
            held_by_club[cid].append(sid)

    for sid, prefs in preferences.items():
        current_club = assignment.get(sid)
        current_idx = prefs.index(current_club) if current_club in prefs else len(prefs)

        for candidate_cid in prefs[:current_idx]:
            if candidate_cid not in clubs:
                continue
            rank = result.base_rank.get(candidate_cid, {})
            if sid not in rank:
                continue  # sid không nằm trong applicant pool của club này -> không thể block

            capacity = clubs[candidate_cid]["capacity"]
            reserve_capacity = clubs[candidate_cid]["reserve_capacity"]
            holders = held_by_club[candidate_cid]
            eligible_fn = lambda s, _cid=candidate_cid: is_reserve_eligible_fn(s, _cid)

            trial_pool = holders + [sid]
            accepted, _ = club_choice_function(
                trial_pool, capacity, reserve_capacity, eligible_fn, rank
            )
            if sid in accepted:
                problems.append(err(
                    "blocking_pair",
                    student_id=sid,
                    club_id=candidate_cid,
                    current_club=current_club,
                    n_holders=len(holders),
                    capacity=capacity,
                ))

    return problems


# ---------------------------------------------------------------------------
# BƯỚC C2 — ĐIỀU PHỐI NHIỀU BUỔI
# ---------------------------------------------------------------------------
#
# VÌ SAO PHẦN NÀY CHỈ LÀ CẮT — GỌI — GHÉP
#
# Mỗi CLB đúng một buổi; mỗi em tối đa một CLB mỗi buổi; không có trần số
# CLB mỗi tuần. Ba điều đó nghĩa là tập CLB khả thi của một em chỉ là
# "chọn tuỳ ý, độc lập, tối đa một CLB trong mỗi buổi" — một ràng buộc
# PHÂN HOẠCH thuần tuý, các buổi KHÔNG ràng buộc lẫn nhau.
#
# Nên bài toán tuần không phải một bài toán lớn hơn: nó là N bản sao ĐỘC
# LẬP của bài toán đã giải. Không hàm nào dưới đây đụng vào logic ưu tiên
# hay logic dự trữ; chúng chỉ cắt dữ liệu theo buổi, gọi ĐÚNG run_rbda
# hiện có, rồi ghép kết quả.
#
# Hệ quả quan trọng: mọi tính chất đã đo cho một buổi (ổn định, tối ưu cho
# học sinh, khai thật có lợi nhất, bền trước nhiễu — xem docs/NGHIEN_CUU_TOI_UU.md)
# tự động đúng cho cả tuần. Riêng tính KHAI THẬT CÓ LỢI NHẤT đúng vì lý do
# rất cụ thể: khai của một em ở buổi d chỉ ảnh hưởng buổi d, nên không có
# kênh nào để hi sinh ngày này lấy ngày kia.
#
# Bỏ BẤT KỲ điều kiện nào ở trên là mất hệ quả đó — xem docs/KE_HOACH_NHIEU_BUOI.md.

# BA THIẾT KẾ BỐC THĂM — MỘT ĐỂ DÙNG, HAI ĐỂ ĐO
#
# Phần mềm chạy DUY NHẤT `stb_ngay`. Không có bộ chọn trên giao diện, và
# `api.run_pipeline` không nhận tham số chế độ — có test canh chữ ký hàm đó.
#
# `stb_tuan` và `stb_co_bu` còn nằm đây vì chúng là ĐỐI CHỨNG của TN7
# (`du_lieu_test/do_boc_tham.py`): không có chúng thì không chạy lại được phép
# đo đã dùng để chọn `stb_ngay`, và mọi con số TN7 trong docs/NGHIEN_CUU_TOI_UU.md
# mất khả năng tái lập. Chúng là DỤNG CỤ ĐO, không phải lựa chọn sản phẩm.
#
# Căn cứ chọn `stb_ngay` (TN7, 200 seed, ghép cặp, khoảng tin cậy bootstrap):
#   * không thua `stb_tuan` ở ô nào đã đo, và hơn hẳn ở mọi vùng mà bốc thăm
#     thật sự quyết định — cứu 1,2 tới 79,0 em trên 200;
#   * một buổi thì nó NGẮN MẠCH về đúng bộ số đã khoá, nên kết quả y hệt phần
#     mềm trước khi có tính năng nhiều buổi (TestTrungKhit);
#   * `stb_co_bu` bị loại vì mở kênh khai gian có thật: 113/300 em giấu bớt
#     buổi thì có lợi, trong khi hai thiết kế kia đều 0/300 (TN7d).
#
# Thêm lại một đường cho api.py chạy `stb_tuan` hay `stb_co_bu` là đi ngược
# quyết định trên. Muốn đổi thì đo lại trước, đừng đổi rồi đo sau.
CHE_DO_BOC_THAM = ("stb_tuan", "stb_ngay", "stb_co_bu")
CHE_DO_BOC_THAM_MAC_DINH = "stb_ngay"


def buoi_cua_club(clubs: dict[str, dict]) -> dict[str, str]:
    """{club_id: buoi}. NULL/rỗng -> BUOI_MAC_DINH."""
    return {
        cid: (info.get("buoi") or BUOI_MAC_DINH)
        for cid, info in clubs.items()
    }


# Nhãn buổi là CHỮ TỰ DO do trường đặt, nhưng gần như trường nào cũng đặt
# theo ngày trong tuần. Bảng này để sắp chúng theo THỨ TỰ NGÀY chứ không
# theo vần chữ cái.
#
# VÌ SAO CẦN. Trường ghi "Thứ Hai / Thứ Ba / Thứ Tư / Thứ Năm" thì sắp theo
# vần ra: Ba, Hai, Năm, Tư — thứ Ba đứng trước thứ Hai. Trên màn hình đã
# khó đọc, mà ở tính năng chọn KHOẢNG buổi ("từ thứ Hai đến thứ Năm") thì
# nó chọn ra một tập hoàn toàn khác với điều người dùng định nói.
#
# Số theo đúng cách gọi tiếng Việt: thứ Hai là 2, ..., thứ Bảy là 7, Chủ
# nhật là 8 (xếp cuối tuần, đúng thứ tự lịch học).
_SO_CUA_THU = {
    "2": 2, "hai": 2, "mon": 2, "monday": 2,
    "3": 3, "ba": 3, "tue": 3, "tuesday": 3,
    "4": 4, "tu": 4, "tư": 4, "wed": 4, "wednesday": 4,
    "5": 5, "nam": 5, "năm": 5, "thu": 5, "thursday": 5,
    "6": 6, "sau": 6, "sáu": 6, "fri": 6, "friday": 6,
    "7": 7, "bay": 7, "bảy": 7, "sat": 7, "saturday": 7,
    "cn": 8, "chu_nhat": 8, "chủ_nhật": 8, "sun": 8, "sunday": 8,
}


def so_thu_trong_tuan(buoi: str) -> Optional[int]:
    """Nhãn buổi này là thứ mấy? Không nhận ra được thì trả None.

    Nhận các cách viết thường gặp — `thu_2`, `thu 2`, `thứ_hai`, `t2`,
    `monday` — và cả nhãn có ĐUÔI như `thu_3_tiet_9`, vì trường có thêm
    tiết thì vẫn là thứ Ba.

    Không nhận ra thì KHÔNG đoán bừa: trả None để chỗ gọi xếp nhãn đó
    xuống cuối theo vần chữ cái. Đoán sai một nhãn lạ còn tệ hơn không
    đoán, vì nó lặng lẽ đổi thứ tự chạy mà không ai thấy.
    """
    ten = (buoi or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not ten or ten == BUOI_MAC_DINH:
        return None
    # Nhãn TOÀN CHỮ SỐ là SỐ BUỔI, không phải thứ trong tuần. Trường đánh
    # số buổi "1".."5" thì bảng tra nhận "2".."7" là thứ Ba..thứ Bảy nhưng
    # không nhận "1", "8", "9" — nên "1" rơi xuống cuối và
    # sap_buoi(['1','2','3','4','5']) ra ['2','3','4','5','1']. Cách sắp
    # theo vần CŨ lại đúng ở đây. Nhãn như vậy để `khoa_sap_buoi` sắp theo
    # GIÁ TRỊ SỐ ở một tầng riêng.
    if ten.isdigit():
        return None
    for tien_to in ("thứ_", "thu_", "thứ", "thu", "t"):
        if not ten.startswith(tien_to):
            continue
        con_lai = ten[len(tien_to):]
        if not con_lai:
            continue
        # Có tiền tố "thứ" rồi thì cắt được phần đuôi: "3_tiet_9" thử lần
        # lượt "3_tiet_9", "3_tiet", rồi "3" — trường thêm tiết vào nhãn thì
        # vẫn là thứ Ba.
        manh = con_lai.split("_")
        for n in range(len(manh), 0, -1):
            khoa = "_".join(manh[:n])
            if khoa in _SO_CUA_THU:
                return _SO_CUA_THU[khoa]

    # Không có tiền tố "thứ" thì đòi khớp TRỌN nhãn, không cắt đuôi. Cho
    # cắt đuôi ở đây là nhận nhầm: "sau_gio" thành thứ Sáu, "tu_chon" thành
    # thứ Tư. Nhận nhầm chỉ đổi THỨ TỰ chứ không đổi kết quả xếp lớp, nhưng
    # nó đổi cái tập mà "từ ... đến ..." chọn ra — im lặng và khó thấy.
    return _SO_CUA_THU.get(ten)


def khoa_sap_buoi(buoi: str):
    """Khoá sắp xếp bốn tầng.

    | Tầng | Nhãn                        | Sắp theo      |
    |------|-----------------------------|---------------|
    | 0    | buổi mặc định               | (đứng đầu)    |
    | 1    | thứ trong tuần nhận ra được | số thứ        |
    | 2    | toàn chữ số                 | GIÁ TRỊ SỐ    |
    | 3    | còn lại                     | vần chữ cái   |

    Tầng 2 tồn tại vì sắp nhãn số theo vần là sai theo hai kiểu cùng lúc:
    "10" đứng trước "2", và bảng tra thứ nhận "2".."7" mà không nhận "1"
    nên "1" bị đẩy xuống cuối. Trường đang đặt "2".."6" theo nghĩa thứ
    trong tuần KHÔNG bị ảnh hưởng — sắp theo số cho ra đúng thứ tự đó.

    Nhãn không nhận ra được xếp SAU mọi nhãn nhận ra được, và trong nhóm đó
    thì theo vần chữ cái — giữ đúng nếp cũ cho dữ liệu đặt tên tuỳ ý.
    """
    if buoi == BUOI_MAC_DINH:
        return (0, 0, "")
    so = so_thu_trong_tuan(buoi)
    if so is not None:
        return (1, so, buoi)
    ten = (buoi or "").strip()
    if ten.isdigit():
        return (2, int(ten), buoi)
    return (3, 0, buoi)


def sap_buoi(ds_buoi) -> list[str]:
    """Sắp danh sách buổi theo thứ tự ngày trong tuần."""
    return sorted(ds_buoi, key=khoa_sap_buoi)


def nhom_theo_buoi(clubs: dict[str, dict]) -> dict[str, list[str]]:
    """{buoi: [club_id]} — buổi sắp theo THỨ TỰ NGÀY, club sắp theo mã.

    Sắp xếp không phải để cho đẹp: thứ tự xét buổi QUYẾT ĐỊNH kết quả ở chế
    độ `stb_co_bu` (buổi xét trước sinh ra "số CLB đã có" cho buổi xét sau).
    Thứ tự đến từ dict của Python là thứ tự chèn, mà thứ tự chèn phụ thuộc
    thứ tự đọc từ CSDL — không tái lập được. Sắp ở đây là chốt nó lại.

    Trước đây sắp theo vần chữ cái. Đổi sang thứ tự ngày KHÔNG làm đổi số
    liệu TN7: bộ mẫu dùng `thu_2`..`thu_6` và bộ mô phỏng dùng `buoi_1`..
    `buoi_5`, cả hai vần chữ cái đều trùng thứ tự ngày. Có phép đối chiếu
    lại `so_lieu_boc_tham.json` xác nhận điều đó.
    """
    theo_buoi: dict[str, list[str]] = {}
    cua = buoi_cua_club(clubs)
    for cid in sorted(clubs):
        theo_buoi.setdefault(cua[cid], []).append(cid)
    return {b: theo_buoi[b] for b in sap_buoi(theo_buoi)}


def cat_du_lieu_theo_buoi(
    buoi: str,
    ds_club_cua_buoi: list[str],
    clubs: dict[str, dict],
    tested_scores: dict[str, dict[str, float]],
    applicants: dict[str, list[str]],
    preferences: dict[str, list[str]],
):
    """Cắt toàn bộ dữ liệu xuống đúng một buổi.

    `buoi` không tham gia tính toán — phần cắt chỉ dựa vào
    `ds_club_cua_buoi`. Giữ tham số để lời gọi đọc ra đang cắt buổi nào
    (và để thông báo lỗi sau này có chỗ lấy tên buổi).

    CHỖ TINH TẾ NHẤT CỦA CẢ TỆP — nguyện vọng.

    Nguyện vọng của một em được LỌC chứ không đánh số lại:

        prefs_buoi[sid] = [c for c in prefs[sid] if c thuộc buổi này]

    Lọc một dãy đã sắp thì phần còn lại vẫn đúng thứ tự. Nên cách này cho
    đúng thứ tự nguyện vọng TRONG BUỔI, bất kể cột `rank` trong CSDL đang
    là thứ hạng toàn cục (dữ liệu nhập bằng bản cũ) hay thứ hạng trong buổi
    (dữ liệu nhập bằng bộ cột mới). Không cần di trú dữ liệu nguyện vọng,
    và hai kiểu dữ liệu sống chung được trong cùng một CSDL.
    """
    tap = set(ds_club_cua_buoi)
    clubs_b = {cid: clubs[cid] for cid in ds_club_cua_buoi}
    scores_b = {cid: tested_scores.get(cid, {}) for cid in ds_club_cua_buoi}
    app_b = {cid: list(applicants.get(cid, [])) for cid in ds_club_cua_buoi}
    prefs_b = {
        sid: [cid for cid in ds if cid in tap]
        for sid, ds in preferences.items()
    }
    return clubs_b, scores_b, app_b, prefs_b


def _seed_cua_buoi(seed: int, buoi: str) -> int:
    """Seed dẫn xuất cho một buổi — phải TÁI LẬP được giữa hai lần mở máy.

    KHÔNG dùng hash() của Python: từ Python 3.3, hash() của chuỗi được ngẫu
    nhiên hoá theo từng tiến trình (PYTHONHASHSEED), nên cùng dữ liệu cùng
    seed sẽ cho hai kết quả khác nhau ở hai lần chạy. Với một phần mềm mà
    cả tính minh bạch dựa trên "chạy lại ra đúng số cũ" thì đó là lỗi chí
    mạng, và là loại lỗi im lặng — không ai nhận ra cho tới khi có người
    đối chiếu hai lần chạy.

    crc32 cho cùng một số trên mọi máy, mọi phiên bản Python.
    """
    import zlib

    return (int(seed) + zlib.crc32(buoi.encode("utf-8"))) % (2 ** 31)


def sinh_stb_theo_buoi(
    stb_goc: dict[str, int], ds_buoi: list[str], seed: int, che_do: str,
) -> dict[str, dict[str, int]]:
    """Bộ số bốc thăm cho từng buổi.

    `stb_ngay` là thiết kế phần mềm DÙNG. Hai chế độ kia chỉ để TN7 đối
    chứng, và để đọc lại trung thực một lần chạy cũ đã ghi trong nhật ký —
    không có đường nào từ giao diện chọn chúng.

    Cả ba thiết kế đều là HÀM CỦA `stb_goc` — bộ số đã bốc và đã KHOÁ. Đó
    là điều kiện để cơ chế khoá bốc thăm còn nguyên ý nghĩa ở mọi chế độ:
    không chế độ nào tự bốc một bộ số mới ngoài tầm kiểm soát của `stb_lock`.

      stb_ngay  — ĐANG DÙNG. Hoán vị VỊ TRÍ trong dàn số, mỗi buổi một
                  hoán vị dẫn xuất từ (seed, tên buổi). May rủi SAN ĐỀU
                  qua các ngày.
      stb_tuan  — đối chứng. Dùng thẳng `stb_goc` cho MỌI buổi, nên em số
                  xấu đứng cuối Tầng 2 ở mọi buổi: may rủi CỘNG DỒN.

    `stb_co_bu` không sinh được ở đây vì nó cần biết kết cục của buổi
    trước — nó được dựng dần trong run_rbda_nhieu_buoi, cũng từ `stb_goc`.

    Vì sao stb_ngay hoán vị VỊ TRÍ chứ không bốc lại từ đầu: hoán vị một
    dàn số đã có cho đúng một hoán vị ngẫu nhiên đều (hợp của hai hoán vị
    vẫn là hoán vị đều), nhưng nó KHÔNG đưa thêm một nguồn ngẫu nhiên nào
    ngoài `stb_goc` và `seed`. Tính "không phụ thuộc thứ tự nhập liệu" mà
    generate_stb_lottery đã bảo đảm cho `stb_goc` được thừa kế nguyên vẹn.
    """
    if che_do not in CHE_DO_BOC_THAM:
        raise ValueError(
            "che_do phai la mot trong %r, nhan duoc %r" % (list(CHE_DO_BOC_THAM), che_do))

    # MỘT buổi thì cả ba cách phải cho CÙNG kết quả, và phải là kết quả của
    # bộ số đã khoá.
    #
    # "Bốc thăm lại mỗi buổi" chỉ có nghĩa khi có nhiều buổi để san may rủi
    # qua. Với một buổi, xáo lại chỉ là một phép hoán vị tuỳ tiện: nó đổi ai
    # đỗ ai trượt mà không làm gì công bằng hơn, và nó phá mất lời hứa
    # "một buổi thì kết quả y hệt bản cũ" — một trường chỉ tổ chức một buổi
    # mà lỡ chọn cách này sẽ nhận kết quả khác đi, không vì lý do nào cả.
    #
    # Test canh: TestTrungKhit::test_mot_buoi_thi_ba_cach_boc_tham_cho_cung_ket_qua.
    if len(ds_buoi) <= 1 or che_do != "stb_ngay":
        # stb_tuan dung thang; stb_co_bu dung ban nay lam khoa pha hoa.
        return {b: dict(stb_goc) for b in ds_buoi}

    import random

    # Sap theo (so boc tham, ma hoc sinh): so boc tham co the co lo hong
    # neu mot hoc sinh da bi xoa, va ma hoc sinh pha hoa not phan con lai.
    # Ca hai khoa deu khong phu thuoc thu tu doc tu CSDL.
    thu_tu = sorted(stb_goc, key=lambda sid: (stb_goc[sid], sid))
    ra: dict[str, dict[str, int]] = {}
    for buoi in ds_buoi:
        vi_tri = list(range(len(thu_tu)))
        random.Random(_seed_cua_buoi(seed, buoi)).shuffle(vi_tri)
        ra[buoi] = {sid: vi_tri[i] for i, sid in enumerate(thu_tu)}
    return ra


def _stb_co_bu(stb_goc: dict[str, int], so_clb_da_co: dict[str, int]) -> dict[str, int]:
    """Đánh lại bộ số cho một buổi: em đang có ÍT CLB hơn được lên trước.

    Đây là cách cài `stb_co_bu`, và cách cài này CÓ CHỦ ĐÍCH: nó chỉ đánh
    lại BỘ SỐ BỐC THĂM rồi truyền vào như thường. compute_club_priority
    không hề biết chuyện gì đang xảy ra, và ràng buộc chống nội sinh ghi ở
    docstring của hàm đó còn nguyên chữ.

    ĐỪNG NHẦM ĐÂY LÀ MỘT CẢI TIẾN. Nó làm ưu tiên buổi sau phụ thuộc KẾT CỤC
    buổi trước, mà kết cục lại phụ thuộc nguyện vọng đã khai — tức là mở đúng
    cái kênh khai gian mà cả dự án được dựng lên để bịt: một em có thể cố ý
    bỏ trống buổi đầu để giành ưu tiên buổi sau. Chế độ này có mặt để ĐO,
    không phải để khuyến nghị. Xem docs/KE_HOACH_NHIEU_BUOI.md mục 5.3.

    ĐÃ ĐO VÀ ĐÃ BỊ LOẠI. TN7d dựng đúng kênh nói trên rồi đếm: 113/300 em
    tìm được cách giấu bớt buổi có lợi dưới chế độ này, còn `stb_tuan` và
    `stb_ngay` đều 0/300. Phần mềm không chạy nó nữa; hàm còn ở đây để
    `du_lieu_test/do_boc_tham.py` chạy lại được phép đo ấy, và để đọc lại
    một lần chạy cũ đã ghi chế độ này trong nhật ký.
    """
    thu_tu = sorted(stb_goc, key=lambda sid: (so_clb_da_co.get(sid, 0), stb_goc[sid]))
    return {sid: i for i, sid in enumerate(thu_tu)}


@dataclass
class KetQuaTuan:
    """Kết quả phân bổ cho cả tuần."""

    assignment: dict[str, dict[str, Optional[str]]] = field(default_factory=dict)
    # student_id -> {buoi: club_id | None}. Có khoá cho MỌI buổi, kể cả buổi
    # em không có suất — người đọc phân biệt được "trống buổi này" với
    # "buổi này không tồn tại".
    per_buoi: dict[str, MatchResult] = field(default_factory=dict)
    ds_buoi: list[str] = field(default_factory=list)
    che_do_boc_tham: str = CHE_DO_BOC_THAM_MAC_DINH
    stb_theo_buoi: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def rounds_run(self) -> int:
        """Số vòng của buổi chạy lâu nhất — để so với MatchResult.rounds_run."""
        return max((kq.rounds_run for kq in self.per_buoi.values()), default=0)

    def so_clb_moi_em(self) -> dict[str, int]:
        return {
            sid: sum(1 for cid in theo_buoi.values() if cid is not None)
            for sid, theo_buoi in self.assignment.items()
        }

    def cac_dong_ket_qua(self):
        """Sinh (student_id, buoi, club_id, round_num, tier, rank) cho CSDL."""
        for buoi in self.ds_buoi:
            kq = self.per_buoi[buoi]
            for sid, cid in kq.assignment.items():
                yield (
                    sid, buoi, cid, kq.rounds_run,
                    kq.matched_tier.get(sid),
                    kq.rank_in_student_pref.get(sid),
                )


def run_rbda_nhieu_buoi(
    students: dict[str, dict],
    clubs: dict[str, dict],
    tested_scores: dict[str, dict[str, float]],
    applicants: dict[str, list[str]],
    preferences: dict[str, list[str]],
    stb_lottery: dict[str, int],
    is_reserve_eligible_fn: Callable[[str, str], bool],
    che_do_boc_tham: str = CHE_DO_BOC_THAM_MAC_DINH,
    seed: int = 0,
    max_rounds: int = 1000,
    chi_buoi: Optional[list[str]] = None,
) -> KetQuaTuan:
    """Xếp CLB cho cả tuần: cắt theo buổi, gọi run_rbda từng buổi, ghép lại.

    Dữ liệu chỉ có MỘT buổi (không CLB nào khai `buoi`) thì hàm này gọi
    run_rbda đúng một lần với đúng dữ liệu đó — kết quả TRÙNG KHÍT phần mềm
    trước khi có tính năng nhiều buổi, và trùng khít với BẤT KỲ chế độ nào
    trong ba chế độ, nhờ nhánh ngắn mạch trong `sinh_stb_theo_buoi`. Chính
    vì thế việc đổi mặc định sang 'stb_ngay' không làm sai một con số nào
    trong docs/NGHIEN_CUU_TOI_UU.md. Có test canh trên ba bộ dữ liệu × 20 seed
    (tests/test_nhieu_buoi.py::TestTrungKhit).

    Args:
        stb_lottery: bộ số bốc thăm ĐÃ KHOÁ, giống hệt tham số cùng tên của
            run_rbda. Cả ba thiết kế đều dẫn xuất từ bộ số này.
        che_do_boc_tham: mặc định 'stb_ngay' — thiết kế DUY NHẤT phần mềm
            chạy. 'stb_tuan' và 'stb_co_bu' chỉ dành cho bộ đo TN7 và cho
            việc đọc lại một lần chạy cũ; `api.run_pipeline` không nhận
            tham số này và có test canh chữ ký của nó.
        seed: chỉ dùng để dẫn xuất hoán vị cho 'stb_ngay'. Hai chế độ kia
            bỏ qua nó hoàn toàn.
        chi_buoi: chạy CHỈ những buổi này (None = chạy hết). Dùng khi trường
            muốn xếp riêng một buổi, hoặc một dải buổi trong tuần.

    BẤT BIẾN QUAN TRỌNG NHẤT CỦA `chi_buoi`
    ---------------------------------------
    Chạy riêng thứ Năm phải cho ra ĐÚNG kết quả thứ Năm của lần chạy cả
    tuần. Không giữ được điều đó thì kết quả phụ thuộc vào việc người vận
    hành bấm chạy mấy lần và chạy theo nhóm nào — một thứ không giải thích
    được với phụ huynh, và không tái lập được.

    Chỗ dễ hỏng nằm ở bộ số bốc thăm: `sinh_stb_theo_buoi` ngắn mạch khi
    danh sách buổi chỉ có một phần tử. Truyền danh sách ĐÃ LỌC vào đó thì
    chạy riêng một buổi sẽ rơi vào nhánh ngắn mạch và dùng bộ số gốc thay
    vì hoán vị của buổi ấy — ra kết quả khác hẳn. Nên bộ số vẫn sinh từ
    TOÀN BỘ danh sách buổi của trường, việc lọc chỉ áp vào vòng lặp chạy.
    Có test canh: `TestChonBuoi::test_chay_rieng_mot_buoi_giong_chay_ca_tuan`.

    `stb_co_bu` KHÔNG giữ được bất biến này, và đó là bản chất của nó: số
    của buổi sau phụ thuộc kết cục các buổi trước, nên bỏ bớt buổi là đổi
    đầu vào. Chế độ đó chỉ còn dùng cho phép đo TN7, và TN7 không dùng
    `chi_buoi`.
    """
    if che_do_boc_tham not in CHE_DO_BOC_THAM:
        raise ValueError(
            "che_do_boc_tham phai la mot trong %r, nhan duoc %r"
            % (list(CHE_DO_BOC_THAM), che_do_boc_tham))

    theo_buoi = nhom_theo_buoi(clubs)
    ds_buoi_tat_ca = list(theo_buoi)

    if chi_buoi is None:
        ds_buoi = ds_buoi_tat_ca
    else:
        la = [b for b in chi_buoi if b not in ds_buoi_tat_ca]
        if la:
            raise ValueError(
                "chi_buoi co buoi khong ton tai: %r (dang co: %r)"
                % (sorted(la), ds_buoi_tat_ca))
        chon = set(chi_buoi)
        ds_buoi = [b for b in ds_buoi_tat_ca if b in chon]
        if not ds_buoi:
            raise ValueError("chi_buoi rong: khong co buoi nao de chay")

    # Bộ số bốc thăm sinh từ TOÀN BỘ danh sách buổi, không phải danh sách đã
    # lọc — xem phần "BẤT BIẾN QUAN TRỌNG NHẤT" ở docstring.
    stb_tinh = sinh_stb_theo_buoi(
        stb_lottery, ds_buoi_tat_ca, seed, che_do_boc_tham)

    ket = KetQuaTuan(
        assignment={sid: {} for sid in students},
        ds_buoi=ds_buoi,
        che_do_boc_tham=che_do_boc_tham,
    )
    so_clb_da_co: dict[str, int] = {sid: 0 for sid in students}

    for buoi in ds_buoi:
        clubs_b, scores_b, app_b, prefs_b = cat_du_lieu_theo_buoi(
            buoi, theo_buoi[buoi], clubs, tested_scores, applicants, preferences)

        if che_do_boc_tham == "stb_co_bu":
            stb_b = _stb_co_bu(stb_tinh[buoi], so_clb_da_co)
        else:
            stb_b = stb_tinh[buoi]

        kq = run_rbda(
            students, clubs_b, scores_b, app_b, prefs_b, stb_b,
            is_reserve_eligible_fn, max_rounds=max_rounds,
        )

        ket.per_buoi[buoi] = kq
        ket.stb_theo_buoi[buoi] = stb_b
        for sid, cid in kq.assignment.items():
            ket.assignment.setdefault(sid, {})[buoi] = cid
            if cid is not None:
                so_clb_da_co[sid] = so_clb_da_co.get(sid, 0) + 1

    return ket


def verify_stability_tuan(
    ket_qua: KetQuaTuan,
    clubs: dict[str, dict],
    preferences: dict[str, list[str]],
    is_reserve_eligible_fn: Callable[[str, str], bool],
) -> dict[str, list[dict]]:
    """Kiểm cặp phá vỡ cho từng buổi. {buoi: [vấn đề]} — rỗng hết = ổn định.

    Không cần định nghĩa ổn định mới cho cả tuần: không ràng buộc nào nối
    hai buổi, nên không cặp (học sinh, CLB) nào bắc cầu được giữa chúng.
    Kết quả tuần ổn định khi và chỉ khi kết quả mỗi buổi ổn định.
    """
    theo_buoi = nhom_theo_buoi(clubs)
    ra: dict[str, list[dict]] = {}
    for buoi, ds_club in theo_buoi.items():
        kq = ket_qua.per_buoi.get(buoi)
        if kq is None:
            continue
        clubs_b, _sc, _ap, prefs_b = cat_du_lieu_theo_buoi(
            buoi, ds_club, clubs, {}, {}, preferences)
        ra[buoi] = verify_stability(kq, clubs_b, prefs_b, is_reserve_eligible_fn)
    return ra


# ---------------------------------------------------------------------------
# BƯỚC D — PIPELINE 5 BƯỚC (khung — cần khớp schema thật)
# ---------------------------------------------------------------------------

def validate_data_integrity(
    students: dict[str, dict],
    clubs: dict[str, dict],
    preferences: dict[str, list[str]],
    applicants: dict[str, list[str]],
) -> list[dict]:
    """
    Trả về danh sách lỗi dạng {"code": ..., "params": {...}} (xem
    i18n_errors.py) — rỗng = dữ liệu hợp lệ. Không raise exception để
    pipeline có thể báo cáo TOÀN BỘ lỗi một lần thay vì dừng ở lỗi đầu.
    Dùng err()/format_message() từ i18n_errors.py nếu cần chuỗi văn bản
    (vd để in ra CLI) thay vì object có cấu trúc.
    """
    from i18n_errors import err

    errors: list[dict] = []

    for sid, prefs in preferences.items():
        if sid not in students:
            errors.append(err("pref_student_not_in_students", student_id=sid))
        if len(prefs) != len(set(prefs)):
            errors.append(err("pref_duplicate_club", student_id=sid))
        # Đếm THEO BUỔI. Lỗi phải nêu tên buổi: câu "em này quá nhiều nguyện
        # vọng" mà không nói buổi nào thì trường không biết sửa ở đâu.
        #
        # Trừ trường MỘT buổi. Ở đó nhãn buổi là BUOI_MAC_DINH — một chuỗi
        # nội bộ, không phải thứ đọc lên được. Nêu nó ra là bắt người dùng
        # đọc một khái niệm trường họ không có. Hai mã lỗi vì thế, và trường
        # một buổi thấy đúng câu như bản cũ.
        for buoi, ds in gom_theo_buoi(prefs, clubs).items():
            if len(ds) > TRAN_NGUYEN_VONG_MOI_BUOI:
                if buoi == BUOI_MAC_DINH:
                    errors.append(err("pref_too_many", student_id=sid,
                                      count=len(ds)))
                else:
                    errors.append(err("pref_too_many_buoi", student_id=sid,
                                      buoi=buoi, count=len(ds)))
        for cid in prefs:
            if cid not in clubs:
                errors.append(err("pref_unknown_club", student_id=sid, club_id=cid))

    for cid, info in clubs.items():
        loi = loi_suc_chua(info["capacity"], info["reserve_capacity"])
        if loi == "capacity_not_positive":
            errors.append(err("club_capacity_not_positive", club_id=cid))
        elif loi == "reserve_negative":
            errors.append(err("club_reserve_negative", club_id=cid))
        elif loi == "reserve_exceeds_capacity":
            errors.append(err("club_reserve_exceeds_capacity", club_id=cid))

    # KHÔNG kiểm TRAN_CLB_THI_MOI_BUOI ở đây: `applicants` là ô tick thi ĐÃ
    # TRỘN với nguyện vọng (`hop_ung_vien`), nên đếm nó là đếm nhầm sang
    # nguyện vọng — thêm phép kiểm đó vào đây từng làm `bo_sach` không chạy
    # được, vì có em xếp 6 nguyện vọng một buổi, hoàn toàn hợp lệ.
    #
    # Trần 5 được kiểm ở hai chỗ, đều trên ô tick còn nguyên:
    #   * NƠI NHẬP — `submit_test_selection`, `import_test_selection_csv`;
    #   * bảng sức khoẻ dữ liệu (`health_thi_qua_tran_buoi`) — bắt trường
    #     hợp nhập hợp lệ rồi CLB đổi buổi làm vượt trần. Là cảnh báo chứ
    #     không chặn: trần là chính sách, thuật toán vẫn chạy đúng.
    for cid, applicant_list in applicants.items():
        if cid not in clubs:
            errors.append(err("applicants_unknown_club", club_id=cid))
        for sid in applicant_list:
            if sid not in students:
                errors.append(err("applicants_unknown_student", student_id=sid))

    return errors


def generate_stb_lottery(student_ids: list[str], seed: int) -> dict[str, int]:
    """
    Sinh số bốc thăm (STB) — một số duy nhất/học sinh, dùng chung mọi
    club (Single Tie-Breaking). seed cố định để có thể tái lập kết quả
    khi cần kiểm tra/audit.
    """
    import random

    rng = random.Random(seed)
    # SẮP XẾP trước khi xáo. random.shuffle xáo ĐÚNG danh sách được đưa
    # vào, mà load_from_sqlite đọc bảng students không có ORDER BY nên
    # trả về theo thứ tự CHÈN. Không sắp thì cùng một trường, cùng seed,
    # nhập học sinh theo thứ tự khác là ra kết quả khác — đo được 6/10 em
    # đổi CLB. Thứ tự nhập không ai ghi lại và không màn hình nào hiện,
    # nên đó là một điều kiện ngầm không thể tái lập.
    #
    # Sắp xếp KHÔNG làm mã học sinh quyết định kết quả: xáo xong thì mã
    # không còn vai trò gì, hoán vị vẫn ngẫu nhiên đều. Nó chỉ khiến bộ
    # số bốc thăm phụ thuộc đúng hai thứ: TẬP mã học sinh và seed.
    # set(): mã lặp từng làm một em nhận hai số, số sau đè số trước và để
    # lại một lỗ trong dãy. Với mã không lặp thì kết quả y hệt trước.
    shuffled = sorted(set(student_ids))
    rng.shuffle(shuffled)
    return {sid: idx for idx, sid in enumerate(shuffled)}


def chen_stb_cho_hoc_sinh_moi(
    thu_tu_cu: list[str], ma_moi: list[str], seed: int
) -> dict[str, int]:
    """
    Cấp số bốc thăm cho học sinh được thêm vào SAU khi bộ số đã khoá.

    Bài toán: bộ số đã khoá cho `thu_tu_cu` (đã sắp theo số bốc thăm hiện
    có, đầu danh sách = ưu tiên cao nhất). Giờ có thêm `ma_moi`. Cấp số
    cho các em mới thế nào cho công bằng?

    CÁCH CŨ ĐÃ BỎ — và vì sao:
        Bản đầu cấp số nối tiếp sau số lớn nhất (`MAX(stb)+1`). Vì số nhỏ
        = ưu tiên cao (xem compute_club_priority), cách đó đặt em mới
        đứng SAU **mọi** em cũ, ở **mọi** CLB, vĩnh viễn. Với nhóm đó bốc
        thăm không còn tồn tại. Đo được: 20 em cũ + 10 em mới tranh 10
        suất (đều Tầng 2, thuần bốc thăm) -> em mới được 0 suất, trong
        khi công bằng thì kỳ vọng ~3,3.

        Ghi chú trong mã lúc đó chỉ nói mục đích là "tránh trùng số" —
        việc xếp cuối là hệ quả không ai định, không tài liệu nào nói ra,
        và không test nào canh.

    CÁCH ĐANG DÙNG — chèn ngẫu nhiên đều:
        Chọn ngẫu nhiên `k` vị trí trong `n + k` chỗ cho các em mới, phần
        còn lại giữ nguyên `thu_tu_cu` theo đúng thứ tự cũ.

    HAI TÍNH CHẤT ĐƯỢC BẢO ĐẢM, cả hai đều có test canh:

      1. Thứ tự TƯƠNG ĐỐI giữa các em cũ KHÔNG BAO GIỜ đổi. Đây là lời
         hứa thật của việc khoá bộ số — không phải "số tuyệt đối không
         đổi", vì số tuyệt đối không ai nhìn thấy (không hiện trên giao
         diện, không nằm trong tệp xuất, màn chấm điểm cố ý giấu).
      2. Mỗi em mới rơi vào vị trí phân bố đều trong dàn số — có thể trên
         hoặc dưới em cũ, đúng nghĩa bốc thăm.

    Kết quả vẫn là một hoán vị 0..n+k-1, giống generate_stb_lottery.

    Args:
        thu_tu_cu: mã học sinh đã có số, ĐÃ SẮP theo số bốc thăm tăng dần.
        ma_moi: mã học sinh chưa có số.
        seed: hạt giống, để chạy lại ra đúng kết quả cũ.

    Returns:
        dict[str, int]: {mã học sinh: số bốc thăm} cho TOÀN BỘ hai nhóm.
    """
    import random

    if not ma_moi:
        return {sid: i for i, sid in enumerate(thu_tu_cu)}

    rng = random.Random(seed)

    # SẮP XẾP trước khi xáo — cùng hạng lỗi với lỗi 19 đã sửa ở
    # generate_stb_lottery: `ma_moi` đến từ thứ tự CHÈN trong CSDL, nên
    # không sắp thì thứ tự nhập liệu lại lén quyết định ai được số tốt.
    moi = sorted(ma_moi)
    rng.shuffle(moi)

    n, k = len(thu_tu_cu), len(moi)
    vi_tri_cua_em_moi = set(rng.sample(range(n + k), k))

    ra: dict[str, int] = {}
    i_cu = i_moi = 0
    for cho in range(n + k):
        if cho in vi_tri_cua_em_moi:
            ra[moi[i_moi]] = cho
            i_moi += 1
        else:
            ra[thu_tu_cu[i_cu]] = cho
            i_cu += 1
    return ra


def cac_dong_match_results(ket_qua) -> list[tuple]:
    """Đổi MatchResult (một buổi) hoặc KetQuaTuan (cả tuần) thành dòng CSDL.

    Nhận cả hai kiểu để đường ghi chỉ có MỘT chỗ: dù gọi run_rbda hay
    run_rbda_nhieu_buoi thì bảng match_results vẫn được ghi bằng cùng một
    hàm, với cùng một hình dạng dòng.
    """
    if isinstance(ket_qua, KetQuaTuan):
        return list(ket_qua.cac_dong_ket_qua())
    return [
        (
            sid, BUOI_MAC_DINH, cid, ket_qua.rounds_run,
            ket_qua.matched_tier.get(sid),
            ket_qua.rank_in_student_pref.get(sid),
        )
        for sid, cid in ket_qua.assignment.items()
    ]


def export_match_results(match_result, output_path: str) -> None:
    """
    Xuất kết quả ra CSV: student_id, buoi, club_id, matched_tier,
    rank_in_student_pref (club_id rỗng = không có suất buổi đó).

    Nhận MatchResult (một buổi) hoặc KetQuaTuan (cả tuần) — cùng đi qua
    cac_dong_match_results nên hai đường cho ra đúng một hình dạng tệp.
    """
    import csv

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "buoi", "club_id", "matched_tier",
                         "rank_in_student_pref"])
        # Theo thứ tự NGÀY, không theo vần: sắp thô thì "chu_nhat" đứng
        # trước "thu_2". Khớp ORDER BY ... COLLATE THU_TU_BUOI bên api.py.
        for sid, buoi, cid, _vong, tier, hang in sorted(
            cac_dong_match_results(match_result),
            key=lambda d: (d[0], khoa_sap_buoi(d[1])),
        ):
            writer.writerow([sid, buoi, cid or "", tier or "", hang or ""])


# ---------------------------------------------------------------------------
# NĂM BẢNG CÓ RÀNG BUỘC — viết MỘT lần, dùng cho cả CSDL mới lẫn di trú
# ---------------------------------------------------------------------------
#
# Trước đây lược đồ không có FOREIGN KEY hay CHECK nào: mọi ràng buộc nằm ở
# mã Python. Cửa nào quên kiểm là dữ liệu hỏng lọt vào im lặng — một nguyện
# vọng trỏ tới học sinh đã xoá, một CLB sức chứa 0, một điểm âm gõ thẳng vào
# tệp CSDL. Giờ CSDL tự từ chối những dòng đó, dù chúng đi cửa nào.
#
# Ràng buộc KHỚP ĐÚNG luật phần mềm đã có, không đặt luật mới:
#   * capacity > 0, 0 <= reserve_capacity <= capacity — như create_or_update_club
#   * rank >= 1 — thứ hạng nguyện vọng đánh từ 1
#   * score >= 0 — như submit_club_scores và csv_score_negative. KHÔNG có trần
#     trên: trường có thể chấm thang 10 hay thang 100.
#   * mọi student_id / club_id ở bảng con phải có thật ở bảng cha.
#
# KHÔNG dùng ON DELETE CASCADE: xoá học sinh hay CLB vẫn do mã Python làm
# tường minh, theo đúng thứ tự con trước cha, và chặn khi có kết quả tham
# chiếu. Cascade sẽ lặng lẽ xoá kết quả đã công bố — đúng thứ các chặn đó
# được dựng lên để tránh.
#
# Sửa một định nghĩa ở đây là đổi cả CSDL mới lẫn đích di trú của CSDL cũ.
# `_BANG_RANG_BUOC` giữ THỨ TỰ: bảng cha trước bảng con.
_BANG_RANG_BUOC = {
    "clubs": """
    club_id TEXT PRIMARY KEY,
    name TEXT,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    reserve_capacity INTEGER NOT NULL DEFAULT 0
        CHECK (reserve_capacity >= 0 AND reserve_capacity <= capacity),
    reserve_group TEXT,         -- nhóm được ưu tiên dự trữ cho club này, NULL = không có dự trữ
    buoi TEXT                   -- buổi sinh hoạt. NULL = BUOI_MAC_DINH (trường chỉ có một buổi)
""",
    "club_test_selection": """
    student_id TEXT NOT NULL REFERENCES students (student_id),
    club_id TEXT NOT NULL REFERENCES clubs (club_id),
    PRIMARY KEY (student_id, club_id)
""",
    "club_scores": """
    student_id TEXT NOT NULL REFERENCES students (student_id),
    club_id TEXT NOT NULL REFERENCES clubs (club_id),
    score REAL NOT NULL CHECK (score >= 0),
    PRIMARY KEY (student_id, club_id)
""",
    "preferences": """
    student_id TEXT NOT NULL REFERENCES students (student_id),
    club_id TEXT NOT NULL REFERENCES clubs (club_id),
    rank INTEGER NOT NULL CHECK (rank >= 1),
    PRIMARY KEY (student_id, club_id)
""",
    # Khoa chinh (student_id, buoi) TU NO canh rang buoc "moi em toi da MOT
    # CLB moi buoi" o tang CSDL. club_id NULL = khong co suat o buoi nay.
    "match_results": """
    student_id TEXT NOT NULL REFERENCES students (student_id),
    buoi TEXT NOT NULL,         -- BUOI_MAC_DINH neu truong khong dung nhieu buoi
    club_id TEXT REFERENCES clubs (club_id),
    round_num INTEGER,
    matched_tier TEXT,          -- 'reserve' | 'general' | NULL
    rank_in_student_pref INTEGER, -- thu hang nguyen vong TRONG BUOI (1-indexed), NULL neu khong co suat
    PRIMARY KEY (student_id, buoi)
""",
}

DEFAULT_SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT,
    stb_number INTEGER,
    reserve_group TEXT          -- vd: 'khoi10', 'chinh_sach', hoặc NULL
);
""" + "".join(
    "\nCREATE TABLE IF NOT EXISTS %s (%s);\n" % (ten, than)
    for ten, than in _BANG_RANG_BUOC.items()
) + """
CREATE TABLE IF NOT EXISTS run_meta (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- chi 1 dong duy nhat, luon ghi de (lan chay GAN NHAT)
    seed INTEGER,
    run_at TEXT,
    rounds_run INTEGER,
    n_matched INTEGER,
    n_total INTEGER,
    che_do_boc_tham TEXT,       -- 'stb_tuan' | 'stb_ngay' | 'stb_co_bu'
    so_buoi INTEGER,
    buoi_da_chay TEXT           -- cac buoi lan chay do phu, ngan cach bang dau phay
);

-- Nhat ky TOAN BO cac lan chay pipeline (khong bao gio xoa/ghi de) —
-- giai quyet van de "chay lan 2 xoa mat dau vet lan 1". match_results
-- van chi giu ban ghi MOI NHAT (vi la nguon cho UI Ket qua), nhung
-- run_history cho biet CO nhung lan chay nao, khi nao, ai lam, ket qua
-- tong quan the nao, phuc vu kiem toan (audit).
CREATE TABLE IF NOT EXISTS run_history (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    seed INTEGER,
    run_at TEXT,
    rounds_run INTEGER,
    n_matched INTEGER,
    n_total INTEGER,
    stb_redrawn INTEGER NOT NULL DEFAULT 0, -- 1 neu lan nay ve lai so bac tham, 0 neu tai su dung STB da khoa
    -- Khong co hai cot duoi thi sau nay khong truy duoc ket qua cu da
    -- chay bang thiet ke boc tham nao — ma ba thiet ke cho ket qua khac
    -- nhau, nen thieu no la mat kha nang kiem toan.
    che_do_boc_tham TEXT,
    so_buoi INTEGER,
    -- Chay duoc RIENG tung buoi, nen mot bo ket qua trong CSDL co the la
    -- hop cua nhieu lan chay. Khong ghi lai lan chay nay phu nhung buoi
    -- nao thi khong ai truy nguoc duoc "ket qua thu Nam den tu dau".
    buoi_da_chay TEXT
);

-- Khoa so bac tham (STB). Chi 1 dong duy nhat. Khi da_khoa = 1, nut
-- "Chay pipeline" se KHONG duoc phep sinh lai stb_number cho hoc sinh
-- (tru khi nguoi dung chu dong go khoa qua xac nhan 2 buoc tren UI).
-- Day la co che chong "vo tinh bac tham lai" anh huong toi tinh minh
-- bach/audit trust cua ket qua da cong bo.
--
-- `seed`: hat giong khoa CUNG bo so. O truong nhieu buoi, thu tu tung buoi
-- dan xuat tu bo so + hat giong, nen khoa bo so ma de ho hat giong thi van
-- doi duoc ket qua da cong bo. NULL = chua khoa lan nao.
-- Ban chup `match_results` NGAY TRUOC lan chay gan nhat ghi de len no —
-- nguon cua tep "thay doi so voi lan chay truoc". Chup trong CUNG giao
-- dich voi lan chay: chay hong thi ban chup cu con nguyen. KHONG co khoa
-- ngoai: day la anh chup, khong phai du lieu song; xoa hoc sinh / xoa du
-- lieu tu don no (`delete_student`, `reset_data`).
CREATE TABLE IF NOT EXISTS ket_qua_truoc (
    student_id TEXT NOT NULL,
    buoi TEXT NOT NULL,
    club_id TEXT,
    round_num INTEGER,
    matched_tier TEXT,
    rank_in_student_pref INTEGER,
    run_at TEXT,                -- thoi diem cua lan chay DA SINH RA cac dong nay
    PRIMARY KEY (student_id, buoi)
);

-- Dau van tay du lieu dau vao luc ket qua trong `match_results` duoc tinh.
-- Khac dau van tay hien tai = du lieu da sua sau lan chay -> ket qua co the
-- da cu. Xem `PipelineAPI._dau_van_tay_du_lieu`.
CREATE TABLE IF NOT EXISTS dau_van_tay_chay (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    dau_van_tay TEXT,
    luc TEXT
);

CREATE TABLE IF NOT EXISTS stb_lock (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    is_locked INTEGER NOT NULL DEFAULT 0,
    locked_at TEXT,
    unlocked_at TEXT,
    seed INTEGER
);
"""

# busy_timeout dai hon mac dinh (5s) — nhieu tien trinh cung mo app.db
# (vd may kiosk + script doi soat chay song song) se CHO thay vi nem
# "database is locked" ngay lap tuc. synchronous=FULL danh doi mot it
# toc do ghi de lay dam bao: sau khi commit() tra ve, du lieu da nam
# tren dia that (khong chi trong page cache cua he dieu hanh), song
# song voi mot ban ghi WAL da bi loai bo — xem ke hoach mat du lieu,
# journal_mode giu nguyen mac dinh DELETE de file .db la BAN SAO DUY
# NHAT can, tuong thich voi quy trinh sao luu USB copy-file don gian.
_BUSY_TIMEOUT_MS = 15000


def chuan_hoa_tim_kiem(s) -> str:
    """Đưa chuỗi về dạng so khớp: bỏ dấu, `đ`→`d`, không phân biệt hoa/thường.

    `LIKE` của SQLite chỉ bỏ qua hoa/thường với chữ Latin trơn, nên "BÌNH"
    không ra "Bình", còn gõ không dấu "binh" thì không ra gì — trong khi
    người vận hành ở kiosk gõ không dấu là chuyện thường.
    """
    import unicodedata

    if s is None:
        return ""
    s = unicodedata.normalize("NFD", str(s).replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in s if not unicodedata.combining(ch)).casefold()


def khop_tim(cot, q) -> int:
    """Hàm SQL `khop_tim(cot, q)`: 1 nếu `q` nằm trong `cot` sau khi chuẩn hoá.

    Thay cho `cot LIKE '%q%'`. So chuỗi con thật, nên `%` và `_` người dùng
    gõ là chữ thường chứ không phải ký tự đại diện (gõ "_" từng liệt kê cả
    trường).
    """
    return 1 if chuan_hoa_tim_kiem(q) in chuan_hoa_tim_kiem(cot) else 0


def connect_db(db_path: str):
    """
    Mo mot ket noi sqlite3 toi app.db voi cac pragma do ben vung da
    thong nhat (busy_timeout dai + synchronous=FULL, KHONG WAL). Moi
    noi trong code can ghi/doc app.db nen di qua ham nay thay vi goi
    sqlite3.connect() truc tiep, de dam bao hanh vi nhat quan.
    """
    import sqlite3

    conn = sqlite3.connect(db_path, timeout=_BUSY_TIMEOUT_MS / 1000)
    conn.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA synchronous = FULL")
    # SQLite TẮT kiểm khoá ngoại theo mặc định, và bật theo TỪNG kết nối.
    # Không bật ở đây thì mọi REFERENCES trong lược đồ chỉ là chữ trang trí.
    conn.execute("PRAGMA foreign_keys = ON")
    # `ORDER BY buoi COLLATE THU_TU_BUOI`: sắp buổi theo THỨ TỰ NGÀY. SQLite
    # tự nó chỉ sắp theo vần chữ cái, nên "chu_nhat" (c) đứng trước "thu_2"
    # (t) — Chủ nhật hiện ra trước thứ Hai ở bảng kết quả, bảng lấp đầy,
    # danh sách CLB và tệp xuất, trong khi thuật toán (sap_buoi) vẫn coi
    # Chủ nhật là ngày cuối tuần. Quy tắc này dùng ĐÚNG khoa_sap_buoi của
    # thuật toán, nên màn hình, tệp xuất và thuật toán không thể lệch nhau.
    conn.create_collation("THU_TU_BUOI", _so_sanh_buoi)
    # Đăng ký theo TỪNG kết nối, như khoá ngoại ở trên: mọi ô tìm kiếm của
    # phần mềm gọi `khop_tim` trong câu SQL.
    conn.create_function("khop_tim", 2, khop_tim, deterministic=True)
    return conn


def _so_sanh_buoi(a: str, b: str) -> int:
    """Hàm so sánh cho collation THU_TU_BUOI (âm / 0 / dương)."""
    ka, kb = khoa_sap_buoi(a), khoa_sap_buoi(b)
    return (ka > kb) - (ka < kb)


# Mỗi phép soát: (mã, câu SQL trả về các dòng vi phạm). Đọc được trên CSDL CŨ
# (chưa có ràng buộc) lẫn CSDL mới — trên CSDL mới thì luôn rỗng.
_SOAT_RANG_BUOC = [
    ("clb_suc_chua_sai",
     "SELECT club_id FROM clubs WHERE capacity IS NULL OR capacity <= 0 "
     "OR reserve_capacity IS NULL OR reserve_capacity < 0 "
     "OR reserve_capacity > capacity"),
    ("nguyen_vong_hang_sai",
     "SELECT student_id || '→' || club_id FROM preferences "
     "WHERE rank IS NULL OR rank < 1"),
    ("diem_am",
     "SELECT student_id || '→' || club_id FROM club_scores WHERE score < 0"),
] + [
    ("mo_coi_hoc_sinh:" + bang,
     "SELECT DISTINCT student_id FROM %s WHERE student_id NOT IN "
     "(SELECT student_id FROM students)" % bang)
    for bang in ("club_test_selection", "club_scores", "preferences", "match_results")
] + [
    ("mo_coi_clb:" + bang,
     "SELECT DISTINCT club_id FROM %s WHERE club_id IS NOT NULL AND club_id "
     "NOT IN (SELECT club_id FROM clubs)" % bang)
    for bang in ("club_test_selection", "club_scores", "preferences", "match_results")
]


def soat_vi_pham_rang_buoc(cur) -> list[dict]:
    """Những dòng sẽ vi phạm ràng buộc của `_BANG_RANG_BUOC`.

    Trả `[{"loai": mã, "bang": bảng, "n": số dòng, "mau": [vài dòng]}]`,
    rỗng = sạch. Chỉ ĐỌC, không sửa gì: dữ liệu hỏng là của nhà trường, và
    xoá hộ họ là mất dữ liệu mà không ai đồng ý. Di trú dùng nó để quyết định
    có dựng lại bảng hay không; bảng sức khoẻ dữ liệu dùng nó để chỉ ra
    dòng nào cần sửa.
    """
    ra = []
    for ma, sql in _SOAT_RANG_BUOC:
        dong = [r[0] for r in cur.execute(sql).fetchall()]
        if dong:
            loai, _, bang = ma.partition(":")
            bang = bang or {"clb_suc_chua_sai": "clubs",
                            "nguyen_vong_hang_sai": "preferences",
                            "diem_am": "club_scores"}[loai]
            ra.append({"loai": loai, "bang": bang, "n": len(dong),
                       "mau": sorted(str(x) for x in dong)[:5]})
    return ra


def _co_khoa_ngoai(cur, bang: str) -> bool:
    return bool(cur.execute("PRAGMA foreign_key_list(%s)" % bang).fetchall())


def _dung_lai_bang_co_rang_buoc(db_path: str) -> bool:
    """Dựng lại năm bảng theo `_BANG_RANG_BUOC`. True = đã dựng lại.

    Chỉ chạy khi CSDL SẠCH (`soat_vi_pham_rang_buoc` rỗng). CSDL có dòng vi
    phạm thì để nguyên — phần mềm vẫn chạy như trước, và bảng sức khoẻ dữ
    liệu chỉ ra dòng nào cần sửa. Chặn mở phần mềm vì dữ liệu cũ không khớp
    luật mới là đổi một lỗi tiềm ẩn lấy một lỗi chắc chắn.

    AN TOÀN:
      * sao lưu trước bằng SQLite Backup API, tên `<db>.bak-<thời điểm>` như
        `PipelineAPI._backup_db`, nên màn phục hồi thấy được bản này;
      * cả năm bảng trong MỘT giao dịch, gọi `execute` từng câu — không dùng
        `executescript`, vì nó tự commit giữa chừng;
      * `PRAGMA foreign_key_check` phải rỗng trước khi commit;
      * lỗi ở bất kỳ đâu -> rollback, CSDL y nguyên như trước khi gọi.
    """
    import datetime
    import sqlite3

    conn = sqlite3.connect(db_path, isolation_level=None)
    try:
        cur = conn.cursor()
        co_bang = {r[0] for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}
        if not set(_BANG_RANG_BUOC) <= co_bang:
            return False
        if all(_co_khoa_ngoai(cur, b) for b in _BANG_RANG_BUOC if b != "clubs"):
            return False
        if soat_vi_pham_rang_buoc(cur):
            return False

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        with sqlite3.connect("%s.bak-%s" % (db_path, ts)) as dich:
            conn.backup(dich)
        dich.close()

        # Tắt kiểm khoá ngoại TRƯỚC giao dịch (trong giao dịch thì PRAGMA này
        # bị bỏ qua), để thả bảng cha lúc bảng con còn đó không bị chặn.
        cur.execute("PRAGMA foreign_keys = OFF")
        cur.execute("BEGIN IMMEDIATE")
        try:
            for ten, than in _BANG_RANG_BUOC.items():
                cot = [r[1] for r in cur.execute("PRAGMA table_info(%s)" % ten)]
                cur.execute("CREATE TABLE %s__moi (%s)" % (ten, than))
                cot_moi = [r[1] for r in cur.execute(
                    "PRAGMA table_info(%s__moi)" % ten)]
                chung = ", ".join(c for c in cot_moi if c in cot)
                cur.execute("INSERT INTO %s__moi (%s) SELECT %s FROM %s"
                            % (ten, chung, chung, ten))
                cur.execute("DROP TABLE %s" % ten)
                cur.execute("ALTER TABLE %s__moi RENAME TO %s" % (ten, ten))
            if cur.execute("PRAGMA foreign_key_check").fetchall():
                raise RuntimeError("foreign_key_check khong rong sau khi dung lai")
            cur.execute("COMMIT")
        except BaseException:
            cur.execute("ROLLBACK")
            raise
        return True
    finally:
        conn.close()


def _co_cot(cur, bang: str, cot: str) -> bool:
    """Bảng `bang` đã có cột `cot` chưa? Dùng để di trú idempotent."""
    return any(r[1] == cot for r in cur.execute("PRAGMA table_info(%s)" % bang))


def di_tru_schema(db_path: str) -> list[str]:
    """Nâng CSDL cũ lên schema có buổi sinh hoạt. Chạy lại bao nhiêu lần cũng được.

    Năm việc, đều có đường lùi:

      1. `clubs` thêm cột `buoi` — ALTER TABLE ADD COLUMN, giá trị cũ thành
         NULL, mà NULL nghĩa là BUOI_MAC_DINH. Không mất gì.
      2. `run_meta` / `run_history` thêm `che_do_boc_tham`, `so_buoi`.
      3. `match_results` đổi khoá chính `student_id` -> `(student_id, buoi)`.
         SQLite không đổi được khoá chính tại chỗ, nên phải dựng bảng mới rồi
         chép sang. Dòng cũ nhận `buoi = BUOI_MAC_DINH`.
      4. `stb_lock` thêm cột `seed` — hạt giống khoá cùng bộ số bốc thăm.
      5. Năm bảng nhận FOREIGN KEY và CHECK (`_BANG_RANG_BUOC`) — dựng lại
         bảng, có sao lưu trước, và CHỈ khi dữ liệu sạch
         (`_dung_lai_bang_co_rang_buoc`).

    CHỖ PHẢI CẨN THẬN: `run_history` là dấu vết kiểm toán — `reset_data` cũng
    không xoá nó. Hàm này chỉ THÊM cột vào đó, tuyệt đối không dựng lại bảng.

    Returns:
        list[str]: mô tả những việc đã làm (rỗng = CSDL vốn đã đúng schema).
    """
    conn = connect_db(db_path)
    cur = conn.cursor()
    da_lam: list[str] = []
    try:
        co_bang = {
            r[0] for r in cur.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'")
        }

        if "clubs" in co_bang and not _co_cot(cur, "clubs", "buoi"):
            cur.execute("ALTER TABLE clubs ADD COLUMN buoi TEXT")
            da_lam.append("clubs.buoi")

        for bang in ("run_meta", "run_history"):
            if bang not in co_bang:
                continue
            for cot, kieu in (("che_do_boc_tham", "TEXT"), ("so_buoi", "INTEGER"),
                              ("buoi_da_chay", "TEXT")):
                if not _co_cot(cur, bang, cot):
                    cur.execute("ALTER TABLE %s ADD COLUMN %s %s" % (bang, cot, kieu))
                    da_lam.append("%s.%s" % (bang, cot))

        if "match_results" in co_bang and not _co_cot(cur, "match_results", "buoi"):
            cur.executescript("""
                CREATE TABLE match_results_moi (
                    student_id TEXT NOT NULL,
                    buoi TEXT NOT NULL,
                    club_id TEXT,
                    round_num INTEGER,
                    matched_tier TEXT,
                    rank_in_student_pref INTEGER,
                    PRIMARY KEY (student_id, buoi)
                );
            """)
            cur.execute(
                "INSERT INTO match_results_moi "
                "(student_id, buoi, club_id, round_num, matched_tier, rank_in_student_pref) "
                "SELECT student_id, ?, club_id, round_num, matched_tier, rank_in_student_pref "
                "FROM match_results",
                (BUOI_MAC_DINH,),
            )
            cur.executescript("""
                DROP TABLE match_results;
                ALTER TABLE match_results_moi RENAME TO match_results;
            """)
            da_lam.append("match_results.buoi")

        # 4. `stb_lock.seed`. CSDL đã khoá từ bản cũ thì lấy hạt giống của
        #    lần chạy gần nhất — chính hạt giống đã sinh ra kết quả đang nằm
        #    trong CSDL. Không có lần chạy nào thì để NULL: lần chạy kế tiếp
        #    sẽ nhận hạt giống được gõ và ghi vào khoá.
        if "stb_lock" in co_bang and not _co_cot(cur, "stb_lock", "seed"):
            cur.execute("ALTER TABLE stb_lock ADD COLUMN seed INTEGER")
            if "run_meta" in co_bang:
                cur.execute(
                    "UPDATE stb_lock SET seed = "
                    "(SELECT seed FROM run_meta WHERE id = 1) "
                    "WHERE is_locked = 1")
            da_lam.append("stb_lock.seed")

        conn.commit()
    finally:
        conn.close()

    # 5. Ràng buộc khoá ngoại và CHECK — dựng lại năm bảng, chỉ khi dữ liệu
    #    sạch. Chạy SAU bốn việc trên vì bước 3 có thể vừa dựng lại
    #    match_results theo khuôn cũ.
    #
    #    Hỏng giữa chừng thì giao dịch đã rollback, CSDL y nguyên — nên nuốt
    #    lỗi và chạy tiếp như CSDL cũ, KHÔNG để nó lan ra `PipelineAPI` và đẩy
    #    người dùng sang màn phục hồi vì một bước nâng cấp tuỳ chọn.
    try:
        if _dung_lai_bang_co_rang_buoc(db_path):
            da_lam.append("rang_buoc")
    except Exception:
        pass
    return da_lam


# Khoá chính của các bảng nối là (student_id, club_id), nên tra theo
# student_id đã nhanh. Nhưng rất nhiều truy vấn lọc theo club_id —
# chấm điểm một CLB, xoá CLB, danh sách từng CLB khi xuất, thống kê lấp
# đầy — và khi đó SQLite phải quét cả bảng. Vài trăm dòng thì không thấy;
# trường vài nghìn em, mỗi lần xuất chạy các truy vấn đó hàng chục lần.
CHI_MUC = """
CREATE INDEX IF NOT EXISTS idx_club_test_selection_club ON club_test_selection(club_id);
CREATE INDEX IF NOT EXISTS idx_club_scores_club        ON club_scores(club_id);
CREATE INDEX IF NOT EXISTS idx_preferences_club        ON preferences(club_id);
CREATE INDEX IF NOT EXISTS idx_match_results_club      ON match_results(club_id);
"""


def init_db(db_path: str) -> None:
    """Tạo app.db với schema mặc định nếu chưa tồn tại, rồi di trú (idempotent)."""
    conn = connect_db(db_path)
    try:
        conn.executescript(DEFAULT_SCHEMA)
        conn.execute(
            "INSERT OR IGNORE INTO stb_lock (id, is_locked, locked_at, unlocked_at) "
            "VALUES (1, 0, NULL, NULL)"
        )
        conn.commit()
    finally:
        conn.close()
    # CREATE TABLE IF NOT EXISTS không đụng tới bảng đã tồn tại, nên một
    # app.db dựng bằng bản cũ vẫn giữ nguyên schema cũ sau executescript ở
    # trên. Di trú phải chạy SAU, và phải chạy cả ở CSDL mới (khi đó nó
    # không làm gì) để chỉ có một đường đi duy nhất.
    di_tru_schema(db_path)
    # Chỉ mục tạo SAU di trú: di trú có thể dựng lại bảng match_results, và
    # chỉ mục trên bảng cũ sẽ mất theo.
    conn = connect_db(db_path)
    try:
        conn.executescript(CHI_MUC)
        conn.commit()
    finally:
        conn.close()


def default_reserve_eligible_fn(students: dict[str, dict], clubs: dict[str, dict]):
    """
    Diện dự trữ mặc định: học sinh eligible cho club X nếu
    students[sid]['reserve_group'] == clubs[X]['reserve_group']
    (và reserve_group của club khác NULL). Đơn giản, dễ đổi sau.
    """
    def fn(sid: str, cid: str) -> bool:
        club_group = clubs.get(cid, {}).get("reserve_group")
        if not club_group:
            return False
        return students.get(sid, {}).get("reserve_group") == club_group
    return fn


def hop_ung_vien(
    dang_ky_thi: dict[str, list[str]], preferences: dict[str, list[str]],
) -> dict[str, list[str]]:
    """`applicants` = ô tick thi ∪ mọi CLB em có xếp nguyện vọng.

    Hai khái niệm KHÁC nhau, và đây là chỗ DUY NHẤT trộn chúng:

      * `dang_ky_thi` — em đã tick "muốn thi" CLB này. Có trần 5 mỗi buổi
        (chính sách nhà trường), kiểm ở cửa nhập và ở bảng sức khoẻ dữ liệu.
      * `applicants` — em được XÉT vào CLB này: đã tick thi, HOẶC có xếp
        nguyện vọng CLB đó. Em không thi vẫn được xét, ở Tầng 2, xếp theo số
        bốc thăm.

    Sau hàm này không tách ngược được nữa, nên kiểm gì về ô tick thi thì
    phải kiểm TRƯỚC, trên `dang_ky_thi` hoặc thẳng trên CSDL.

    Giữ đúng thứ tự cũ: người tick trước, rồi người chỉ xếp nguyện vọng
    theo thứ tự đọc. Thứ tự này không đổi kết quả (ưu tiên sắp lại theo
    điểm và số bốc thăm), nhưng giữ nguyên để không ai phải chứng minh lại.
    CLB không có trong `dang_ky_thi` (không tồn tại) thì bỏ qua như trước.
    """
    applicants = {cid: list(ds) for cid, ds in dang_ky_thi.items()}
    # Tập song song với từng danh sách: `sid not in list` quét cả danh sách
    # mỗi lần, thành bình phương theo số học sinh của một CLB.
    da_co = {cid: set(ds) for cid, ds in applicants.items()}
    for sid, ranked_clubs in preferences.items():
        for cid in ranked_clubs:
            if cid in applicants and sid not in da_co[cid]:
                applicants[cid].append(sid)
                da_co[cid].add(sid)
    return applicants


def dau_van_tay_du_lieu(cur) -> str:
    """SHA-256 của MỌI dữ liệu quyết định kết quả, đọc theo thứ tự cố định.

    Gồm: học sinh (mã, nhãn dự trữ), CLB (mã, sức chứa, suất dự trữ, nhãn,
    buổi), ô tick thi, điểm CÒN TICK (đúng tập `load_from_sqlite` dùng),
    nguyện vọng.

    KHÔNG gồm: số bốc thăm (chỉ lần chạy đổi được nó — tính vào thì mỗi lần
    chạy vẽ bổ sung cho em mới là tự báo "dữ liệu đã đổi"), và TÊN học sinh /
    tên CLB (tệp kết quả nối tên lúc xuất, sửa chính tả tên không làm kết quả
    nào cũ đi).

    Đặt CẠNH `load_from_sqlite` có chủ ý: dấu vân tay của một lần chạy phải
    lấy trong CÙNG lần đọc với dữ liệu nó dùng — xem
    `load_from_sqlite_kem_dau_van_tay`.
    """
    import hashlib

    h = hashlib.sha256()
    cac_phan = [
        ("hs", "SELECT student_id, COALESCE(reserve_group, '') FROM students "
               "ORDER BY student_id"),
        ("clb", "SELECT club_id, capacity, reserve_capacity, "
                "COALESCE(reserve_group, ''), COALESCE(NULLIF(buoi, ''), '%s') "
                "FROM clubs ORDER BY club_id" % BUOI_MAC_DINH),
        ("tick", "SELECT student_id, club_id FROM club_test_selection "
                 "ORDER BY student_id, club_id"),
        ("diem", "SELECT sc.student_id, sc.club_id, sc.score FROM club_scores sc "
                 "JOIN club_test_selection t ON t.student_id = sc.student_id "
                 "AND t.club_id = sc.club_id ORDER BY sc.student_id, sc.club_id"),
        ("nv", "SELECT student_id, club_id, rank FROM preferences "
               "ORDER BY student_id, rank, club_id"),
    ]
    for ten, sql in cac_phan:
        h.update(("\x1e" + ten).encode("utf-8"))
        for row in cur.execute(sql):
            h.update(("\x1f".join(repr(v) for v in row) + "\n").encode("utf-8"))
    return h.hexdigest()


def _doc_du_lieu(cur):
    """Phần đọc của `load_from_sqlite`, trên một con trỏ có sẵn."""
    students = {}
    for row in cur.execute("SELECT student_id, stb_number, reserve_group FROM students ORDER BY student_id"):
        students[row["student_id"]] = {
            "stb": row["stb_number"],
            "reserve_group": row["reserve_group"],
        }

    clubs = {}
    for row in cur.execute(
        "SELECT club_id, capacity, reserve_capacity, reserve_group, buoi FROM clubs ORDER BY club_id"
    ):
        clubs[row["club_id"]] = {
            "capacity": row["capacity"],
            "reserve_capacity": row["reserve_capacity"],
            "reserve_group": row["reserve_group"],
            "buoi": row["buoi"] or BUOI_MAC_DINH,
        }

    # CHỈ điểm còn ô tick "muốn thi" đi kèm. Điểm không có tick là bài thi
    # em đã rút (bỏ tick sau khi đã chấm): màn hình chấm điểm không còn
    # thấy nó, nên để nó xếp em lên Tầng 1 là để một con số không ai nhìn
    # thấy quyết định chỗ. Các cửa ghi đã tự dọn điểm đó; JOIN ở đây giữ
    # cho CSDL cũ (còn sẵn điểm như thế) cũng chạy đúng. Bảng sức khoẻ dữ
    # liệu báo những dòng này (`health_diem_khong_dang_ky_thi`).
    tested_scores: dict[str, dict[str, float]] = {cid: {} for cid in clubs}
    for row in cur.execute(
        "SELECT sc.student_id, sc.club_id, sc.score FROM club_scores sc "
        "JOIN club_test_selection t "
        "  ON t.student_id = sc.student_id AND t.club_id = sc.club_id "
        "ORDER BY sc.club_id, sc.student_id"
    ):
        tested_scores.setdefault(row["club_id"], {})[row["student_id"]] = row["score"]

    # Ô tick "muốn thi" — CHỈ ô tick, chưa trộn với nguyện vọng.
    # ORDER BY: thu tu nay la thu tu applicants[cid]. Khong co ORDER BY thi
    # do la thu tu SQLite tra ve — phu thuoc lich su ghi, khong phai du lieu.
    dang_ky_thi: dict[str, list[str]] = {cid: [] for cid in clubs}
    for row in cur.execute(
        "SELECT student_id, club_id FROM club_test_selection ORDER BY club_id, student_id"
    ):
        dang_ky_thi.setdefault(row["club_id"], []).append(row["student_id"])

    preferences_raw: dict[str, list[tuple[int, str]]] = {}
    for row in cur.execute(
        "SELECT student_id, club_id, rank FROM preferences ORDER BY student_id, rank"
    ):
        preferences_raw.setdefault(row["student_id"], []).append(
            (row["rank"], row["club_id"])
        )
    preferences = {
        sid: [cid for _, cid in sorted(entries)]
        for sid, entries in preferences_raw.items()
    }

    applicants = hop_ung_vien(dang_ky_thi, preferences)

    stb_lottery = {sid: info["stb"] for sid, info in students.items()}
    return students, clubs, tested_scores, applicants, preferences, stb_lottery


def _mo_doc_nhat_quan(db_path: str):
    """Kết nối + giao dịch ĐỌC tường minh: mọi SELECT sau đó thấy CÙNG một
    trạng thái CSDL.

    Không có `BEGIN`, module sqlite3 để mỗi SELECT tự là một giao dịch, nên
    một lần lưu từ kiosk có thể chen GIỮA hai SELECT — đọc học sinh trước khi
    lưu, đọc điểm sau khi lưu. Trong giao dịch đọc, SQLite (chế độ journal,
    không WAL) giữ khoá SHARED: bên ghi chờ tới khi đọc xong (busy_timeout).
    """
    import sqlite3

    conn = connect_db(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("BEGIN")
    return conn


def load_from_sqlite(db_path: str):
    """
    Đọc toàn bộ dữ liệu cần thiết từ app.db theo DEFAULT_SCHEMA và
    trả về đúng format mà run_rbda() cần.

    Returns:
        (students, clubs, tested_scores, applicants, preferences, stb_lottery)
    """
    conn = _mo_doc_nhat_quan(db_path)
    try:
        return _doc_du_lieu(conn.cursor())
    finally:
        conn.rollback()
        conn.close()


def load_from_sqlite_kem_dau_van_tay(db_path: str):
    """Như `load_from_sqlite`, kèm `dau_van_tay_du_lieu` của ĐÚNG dữ liệu đó.

    Trả `(du_lieu, dau_van_tay)`. Lần chạy sắp xếp dùng hàm này: dấu vân tay
    đóng lên kết quả phải là của dữ liệu đã dùng để tính. Lấy ở bước ghi (một
    lần đọc khác, muộn hơn) thì một lần lưu từ kiosk giữa chừng lọt vào dấu
    vân tay mà không vào kết quả — và phần mềm báo "kết quả còn khớp" cho kết
    quả đã cũ (tests/test_sua_theo_danh_gia.py).
    """
    conn = _mo_doc_nhat_quan(db_path)
    try:
        cur = conn.cursor()
        du_lieu = _doc_du_lieu(cur)
        return du_lieu, dau_van_tay_du_lieu(cur)
    finally:
        conn.rollback()
        conn.close()


def write_match_results_to_sqlite(db_path: str, match_result) -> None:
    """Ghi kết quả vào bảng match_results (ghi đè toàn bộ).

    `match_result` nhận MatchResult (một buổi) hoặc KetQuaTuan (cả tuần).
    """
    conn = connect_db(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM match_results")
    cur.executemany(
        "INSERT INTO match_results "
        "(student_id, buoi, club_id, round_num, matched_tier, rank_in_student_pref) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        cac_dong_match_results(match_result),
    )
    conn.commit()
    conn.close()


def _chan_neu_la_du_lieu_that(db_path: str) -> None:
    """Từ chối chạy đường dòng lệnh trên một CSDL đã dùng thật.

    Xem cảnh báo dài ở run_full_pipeline(). Dấu hiệu "đã dùng thật" là một
    trong hai: số bốc thăm ĐÃ KHOÁ, hoặc bảng run_history đã có dòng nào.
    Cả hai chỉ xuất hiện sau khi chạy qua PipelineAPI.run_pipeline().
    """
    import sqlite3

    conn = connect_db(db_path)
    try:
        cur = conn.cursor()
        try:
            row = cur.execute("SELECT is_locked FROM stb_lock WHERE id = 1").fetchone()
            da_khoa = bool(row[0]) if row else False
            so_lan_chay = cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0]
        except sqlite3.Error:
            return                       # CSDL cũ chưa có bảng -> coi như sạch
    finally:
        conn.close()

    if da_khoa or so_lan_chay:
        raise RuntimeError(
            "TU CHOI CHAY: '%s' da duoc dung that (so boc tham %s, %d lan chay "
            "trong run_history).\n"
            "run_full_pipeline() la duong THU NGHIEM: no ve lai TOAN BO so boc "
            "tham bat ke khoa, khong kiem cap pha vo, khong ghi run_history — "
            "chay tiep se lat ket qua da cong bo va KHONG de lai dau vet.\n"
            "Dung giao dien phan mem, hoac PipelineAPI(db).run_pipeline(seed)."
            % (db_path, "DA KHOA" if da_khoa else "chua khoa", so_lan_chay)
        )


def run_full_pipeline(db_path: str, seed: int, output_csv_path: str) -> MatchResult:
    """
    Chạy trọn 5 bước: validate -> STB -> RB-DA -> ghi DB -> export CSV.
    Raise RuntimeError nếu validate_data_integrity() phát hiện lỗi.

    ĐÂY LÀ ĐƯỜNG THỬ NGHIỆM — KHÔNG PHẢI ĐƯỜNG CHẠY THẬT
    ====================================================
    Đường thật là `PipelineAPI.run_pipeline()` trong api.py, và đó là thứ
    giao diện gọi. Hàm này tồn tại để chạy nhanh không cần giao diện lúc
    gỡ lỗi, và nó **thiếu bốn lớp bảo vệ** mà đường thật có:

      1. KHÔNG tôn trọng `stb_lock` — luôn vẽ lại số bốc thăm cho MỌI học
         sinh, kể cả khi bộ số đã khoá và kết quả đã công bố.
      2. KHÔNG chèn ngẫu nhiên cho học sinh thêm vào sau
         (`chen_stb_cho_hoc_sinh_moi`) — nó vẽ lại tất, nên câu hỏi đó
         không đặt ra.
      3. KHÔNG gọi `verify_stability()` hay `sanity_check_result()`, và
         KHÔNG có rollback. Kết quả sai vẫn được ghi thẳng vào CSDL.
      4. KHÔNG ghi `run_history` — không để lại dấu vết nào cho việc kiểm
         toán. Đây là lớp quan trọng nhất trong ba lớp chống dò seed
         (xem BAN_GIAO.md mục 5).

    Vì thế hàm **TỪ CHỐI CHẠY** nếu CSDL đã được dùng thật — tức đã khoá
    số bốc thăm hoặc đã có lịch sử chạy. Trên CSDL sạch (ví dụ do
    `seed_sample_data` dựng) nó chạy như cũ.
    """
    _chan_neu_la_du_lieu_that(db_path)
    init_db(db_path)
    students, clubs, tested_scores, applicants, preferences, _ = load_from_sqlite(
        db_path
    )

    errors = validate_data_integrity(students, clubs, preferences, applicants)
    if errors:
        from i18n_errors import format_all
        raise RuntimeError("Loi du lieu:\n" + "\n".join(format_all(errors)))

    stb_lottery = generate_stb_lottery(list(students.keys()), seed=seed)
    # Ghi STB vừa sinh ngược lại vào DB để tái sử dụng / audit.
    conn = connect_db(db_path)
    conn.executemany(
        "UPDATE students SET stb_number = ? WHERE student_id = ?",
        [(v, k) for k, v in stb_lottery.items()],
    )
    conn.commit()
    conn.close()

    reserve_fn = default_reserve_eligible_fn(students, clubs)
    result = run_rbda(
        students,
        clubs,
        tested_scores,
        applicants,
        preferences,
        stb_lottery,
        is_reserve_eligible_fn=reserve_fn,
    )

    write_match_results_to_sqlite(db_path, result)
    export_match_results(result, output_csv_path)
    return result


# ---------------------------------------------------------------------------
# BƯỚC E — SEED DỮ LIỆU MẪU (để chạy thử full pipeline end-to-end)
# ---------------------------------------------------------------------------

def seed_sample_data(
    db_path: str,
    n_students: int = 200,
    club_defs: Optional[list[tuple[str, int, int, Optional[str]]]] = None,
    seed: int = 7,
) -> None:
    """
    Sinh dữ liệu mẫu ngẫu nhiên nhưng thực tế (đúng ràng buộc: tối đa
    10 nguyện vọng, tick-box tách biệt khỏi xếp hạng, một phần học
    sinh được chấm điểm tier1) và ghi vào app.db.

    club_defs: list[(club_id, capacity, reserve_capacity, reserve_group)]
        Mặc định tạo 10 club nếu không truyền vào.
    """
    import random

    rng = random.Random(seed)
    init_db(db_path)

    if club_defs is None:
        club_defs = []
        for i in range(1, 11):
            reserve_cap = 2 if i % 3 == 0 else 0
            reserve_group = "chinh_sach" if reserve_cap else None
            club_defs.append((f"club_{i:02d}", 15, reserve_cap, reserve_group))

    student_ids = [f"stu_{i:04d}" for i in range(1, n_students + 1)]
    reserve_groups = ["chinh_sach", None, None, None]  # ~25% thuộc diện dự trữ

    conn = connect_db(db_path)
    cur = conn.cursor()
    # Con trước, cha sau — khoá ngoại chặn xoá students/clubs khi còn dòng
    # trỏ tới chúng. Cùng thứ tự với `PipelineAPI._RESET_BANG`.
    cur.execute("DELETE FROM match_results")
    cur.execute("DELETE FROM club_scores")
    cur.execute("DELETE FROM preferences")
    cur.execute("DELETE FROM club_test_selection")
    cur.execute("DELETE FROM students")
    cur.execute("DELETE FROM clubs")

    cur.executemany(
        "INSERT INTO students (student_id, name, stb_number, reserve_group) VALUES (?, ?, ?, ?)",
        [
            (sid, sid, None, rng.choice(reserve_groups))
            for sid in student_ids
        ],
    )
    cur.executemany(
        "INSERT INTO clubs (club_id, name, capacity, reserve_capacity, reserve_group) VALUES (?, ?, ?, ?, ?)",
        [(cid, cid, cap, rcap, rgrp) for cid, cap, rcap, rgrp in club_defs],
    )

    club_ids = [c[0] for c in club_defs]
    test_rows, score_rows, pref_rows = [], [], []

    for sid in student_ids:
        # Kẹp theo số club THỰC CÓ: trường có ít hơn 10 club là hoàn toàn
        # bình thường, và rng.sample() sẽ ném ValueError nếu xin nhiều hơn
        # số phần tử đang có (trước đây cứng randint(4, 10) -> crash với
        # mọi bộ club_defs dưới 10 club).
        lo, hi = min(4, len(club_ids)), min(10, len(club_ids))
        n_prefs = rng.randint(lo, hi)
        ranked_clubs = rng.sample(club_ids, n_prefs)
        for rank, cid in enumerate(ranked_clubs, start=1):
            pref_rows.append((sid, cid, rank))

        # Tick-box thi: chọn ngẫu nhiên 1-3 club trong số đã xếp hạng để "thi"
        n_tested = rng.randint(0, min(3, n_prefs))
        tested_clubs = rng.sample(ranked_clubs, n_tested)
        for cid in tested_clubs:
            test_rows.append((sid, cid))
            score_rows.append((sid, cid, round(rng.uniform(4.0, 10.0), 2)))

        # applicants (tick-box) cũng cần bao gồm mọi club đã xếp hạng,
        # kể cả club không thi (Tier 2) -> ghi vào club_test_selection
        # với vai trò "đã đăng ký xét" (không nhất thiết = đã thi).
        for cid in ranked_clubs:
            if (sid, cid) not in test_rows:
                test_rows.append((sid, cid))

    cur.executemany(
        "INSERT OR IGNORE INTO club_test_selection (student_id, club_id) VALUES (?, ?)",
        test_rows,
    )
    cur.executemany(
        "INSERT INTO club_scores (student_id, club_id, score) VALUES (?, ?, ?)",
        score_rows,
    )
    cur.executemany(
        "INSERT INTO preferences (student_id, club_id, rank) VALUES (?, ?, ?)",
        pref_rows,
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# BƯỚC F — KIỂM TRA TÍNH ĐÚNG ĐẮN (sanity checks, không thay expected_match_results.csv)
# ---------------------------------------------------------------------------

def sanity_check_result(
    result: MatchResult,
    clubs: dict[str, dict],
    preferences: dict[str, list[str]],
) -> list[dict]:
    """
    Kiểm tra các bất biến bắt buộc của một kết quả matching hợp lệ
    (giống validate_results() trong 03_reference_rbda.py):
      1. Không club nào vượt capacity.
      2. Không club nào có số suất TIER DỰ TRỮ vượt reserve_capacity.
      3. Mỗi học sinh chỉ được xếp vào ĐÚNG 1 club (hoặc None).
      4. Club được gán phải nằm trong danh sách nguyện vọng của học sinh đó.
    Kiểm tra stability đầy đủ nằm ở verify_stability() (dùng
    club_choice_function thật, không phải suy luận tĩnh). Trả về list
    các entry {"code": ..., "params": {...}} (xem i18n_errors.py).
    """
    from i18n_errors import err

    problems: list[dict] = []

    club_counts: dict[str, int] = {}
    club_reserve_counts: dict[str, int] = {}
    for sid, cid in result.assignment.items():
        if cid is None:
            continue
        club_counts[cid] = club_counts.get(cid, 0) + 1
        if result.matched_tier.get(sid) == "reserve":
            club_reserve_counts[cid] = club_reserve_counts.get(cid, 0) + 1
        if cid not in preferences.get(sid, []):
            problems.append(err("assignment_not_in_preferences", student_id=sid, club_id=cid))

    for cid, count in club_counts.items():
        cap = clubs[cid]["capacity"]
        if count > cap:
            problems.append(err("club_over_capacity", club_id=cid, count=count, capacity=cap))

    for cid, count in club_reserve_counts.items():
        reserve_cap = clubs[cid]["reserve_capacity"]
        if count > reserve_cap:
            problems.append(err(
                "club_over_reserve_capacity",
                club_id=cid, count=count, reserve_capacity=reserve_cap,
            ))

    return problems


if __name__ == "__main__":
    import sys

    # CANH BAO: day la duong THU NGHIEM, khong phai duong chay that.
    # No se TU CHOI CHAY neu app.db da duoc dung that. Xem docstring cua
    # run_full_pipeline() de biet bon lop bao ve no khong co.
    db_path = sys.argv[1] if len(sys.argv) > 1 else "app.db"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    out_csv = sys.argv[3] if len(sys.argv) > 3 else "match_results.csv"
    result = run_full_pipeline(db_path, seed, out_csv)
    print(f"Xong. {sum(1 for v in result.assignment.values() if v)} / "
          f"{len(result.assignment)} hoc sinh duoc xep club. "
          f"So vong chay: {result.rounds_run}. Ket qua: {out_csv}")
