import pytest

from rbda_priority_pipeline import (
    club_choice_function,
    compute_club_priority,
    default_reserve_eligible_fn,
    generate_stb_lottery,
    load_from_sqlite,
    run_full_pipeline,
    run_rbda,
    sanity_check_result,
    seed_sample_data,
    validate_data_integrity,
    verify_stability,
    MatchResult,
)


def test_generate_stb_lottery_is_deterministic_and_a_bijection():
    ids = ["s1", "s2", "s3", "s4", "s5"]
    lot1 = generate_stb_lottery(ids, seed=1)
    lot2 = generate_stb_lottery(ids, seed=1)
    assert lot1 == lot2
    assert sorted(lot1.values()) == list(range(len(ids)))
    assert set(lot1.keys()) == set(ids)


def test_compute_club_priority_tier1_before_tier2_and_tiebreak_by_stb():
    applicants = ["a", "b", "c", "d"]
    tested_scores = {"a": 8.0, "b": 9.0}
    stb = {"a": 3, "b": 1, "c": 0, "d": 2}

    order = compute_club_priority("X", applicants, tested_scores, stb)

    # tier1 (tested) sorted by score desc: b (9.0) then a (8.0)
    # tier2 (untested) sorted by stb asc: c (0) then d (2)
    assert order == ["b", "a", "c", "d"]


def test_compute_club_priority_raises_on_missing_stb():
    with pytest.raises(ValueError):
        compute_club_priority("X", ["a", "b"], {}, {"a": 0})


def test_club_choice_function_fills_reserve_before_general():
    pool = ["s1", "s2", "s3", "s4"]
    rank = {"s1": 0, "s2": 1, "s3": 2, "s4": 3}

    def reserve_eligible(sid):
        return sid == "s2"

    accepted, tier_of = club_choice_function(
        pool, capacity=2, reserve_capacity=1,
        is_reserve_eligible_fn=reserve_eligible, rank=rank,
    )

    assert accepted == ["s2", "s1"]
    assert tier_of == {"s2": "reserve", "s1": "general"}


def test_club_choice_function_reserve_seat_stays_empty_if_no_eligible_candidate():
    pool = ["s1", "s3"]
    rank = {"s1": 0, "s3": 2}
    accepted, tier_of = club_choice_function(
        pool, capacity=2, reserve_capacity=1,
        is_reserve_eligible_fn=lambda sid: False, rank=rank,
    )
    # no one eligible for the reserved seat -> it rolls into the general pool
    assert accepted == ["s1", "s3"]
    assert tier_of == {"s1": "general", "s3": "general"}


def test_run_rbda_small_deterministic_scenario():
    students = {"s1": {}, "s2": {}, "s3": {}}
    clubs = {
        "A": {"capacity": 1, "reserve_capacity": 0},
        "B": {"capacity": 1, "reserve_capacity": 0},
    }
    tested_scores = {}
    applicants = {"A": ["s1", "s2"], "B": ["s2", "s3"]}
    preferences = {"s1": ["A"], "s2": ["A", "B"], "s3": ["B"]}
    stb_lottery = {"s1": 0, "s2": 1, "s3": 2}

    result = run_rbda(
        students, clubs, tested_scores, applicants, preferences, stb_lottery,
        is_reserve_eligible_fn=lambda sid, cid: False,
    )

    assert result.assignment == {"s1": "A", "s2": "B", "s3": None}
    assert result.rounds_run == 2
    assert result.rank_in_student_pref["s1"] == 1
    assert result.rank_in_student_pref["s2"] == 2

    assert sanity_check_result(result, clubs, preferences) == []
    assert verify_stability(result, clubs, preferences, lambda sid, cid: False) == []


def test_run_rbda_respects_capacity_and_reserve_with_soft_reserves():
    students = {sid: {} for sid in ["s1", "s2", "s3", "s4"]}
    clubs = {"A": {"capacity": 2, "reserve_capacity": 1}}
    # s2 is the only reserve-eligible student, and has the worst STB —
    # the reserved seat should still go to them over higher-priority
    # general students, because the reserve pass runs first.
    applicants = {"A": ["s1", "s2", "s3", "s4"]}
    preferences = {sid: ["A"] for sid in students}
    stb_lottery = {"s1": 0, "s2": 3, "s3": 1, "s4": 2}
    reserve_group = {"s2"}

    result = run_rbda(
        students, clubs, {}, applicants, preferences, stb_lottery,
        is_reserve_eligible_fn=lambda sid, cid: sid in reserve_group,
    )

    assert result.assignment["s2"] == "A"
    assert result.matched_tier["s2"] == "reserve"
    # general seat goes to best remaining STB: s1
    assert result.assignment["s1"] == "A"
    assert result.matched_tier["s1"] == "general"
    assert result.assignment["s3"] is None
    assert result.assignment["s4"] is None

    assert sanity_check_result(result, clubs, preferences) == []
    assert verify_stability(
        result, clubs, preferences, lambda sid, cid: sid in reserve_group
    ) == []


def _codes(entries):
    return [e["code"] for e in entries]


def test_validate_data_integrity_flags_duplicate_and_overflowing_preferences():
    students = {"s1": {}}
    clubs = {"A": {"capacity": 5, "reserve_capacity": 0}}
    preferences = {"s1": ["A", "A"]}
    errors = validate_data_integrity(students, clubs, preferences, {})
    assert "pref_duplicate_club" in _codes(errors)
    assert errors[_codes(errors).index("pref_duplicate_club")]["params"]["student_id"] == "s1"


def test_validate_data_integrity_flags_too_many_preferences():
    students = {"s1": {}}
    clubs = {f"c{i}": {"capacity": 5, "reserve_capacity": 0} for i in range(11)}
    preferences = {"s1": [f"c{i}" for i in range(11)]}
    errors = validate_data_integrity(students, clubs, preferences, {})
    assert "pref_too_many" in _codes(errors)


def test_validate_data_integrity_flags_unknown_club_and_student_refs():
    students = {}
    clubs = {}
    preferences = {"ghost": ["nowhere"]}
    applicants = {"nowhere": ["ghost"]}
    errors = validate_data_integrity(students, clubs, preferences, applicants)
    assert "pref_student_not_in_students" in _codes(errors)
    assert "pref_unknown_club" in _codes(errors)


def test_validate_data_integrity_flags_bad_club_capacities():
    students = {}
    clubs = {
        "zero_cap": {"capacity": 0, "reserve_capacity": 0},
        "over_reserve": {"capacity": 5, "reserve_capacity": 10},
    }
    errors = validate_data_integrity(students, clubs, {}, {})
    assert "club_capacity_not_positive" in _codes(errors)
    assert "club_reserve_exceeds_capacity" in _codes(errors)


def test_sanity_check_result_flags_over_capacity_and_out_of_preference_assignment():
    clubs = {"A": {"capacity": 1, "reserve_capacity": 0}}
    preferences = {"s1": ["A"], "s2": ["B"]}
    result = MatchResult(
        assignment={"s1": "A", "s2": "A"},  # over capacity, and A not in s2's prefs
        rounds_run=1,
    )
    problems = sanity_check_result(result, clubs, preferences)
    assert "club_over_capacity" in _codes(problems)
    assert "assignment_not_in_preferences" in _codes(problems)


def test_error_entries_are_translatable_to_both_languages():
    """Every {code, params} entry the algorithm can emit must render
    cleanly in both languages via i18n_errors.format_message — this is
    the regression guard for the bilingual UI."""
    from i18n_errors import format_message

    students = {"s1": {}}
    clubs = {
        "A": {"capacity": 5, "reserve_capacity": 0},
        "over_reserve": {"capacity": 0, "reserve_capacity": 10},
    }
    preferences = {"s1": ["A", "A", "ghost_club"]}
    applicants = {"ghost_club_2": ["ghost_student"]}
    errors = validate_data_integrity(students, clubs, preferences, applicants)
    assert errors, "expected this deliberately-broken data to produce errors"

    for entry in errors:
        for lang in ("vi", "en"):
            text = format_message(entry["code"], entry["params"], lang=lang)
            assert text != entry["code"], f"missing {lang} translation for {entry['code']}"
            assert "{" not in text, f"unfilled placeholder in {lang} text: {text!r}"


@pytest.mark.parametrize("n_clubs", [1, 2, 6, 9, 10, 15])
def test_seed_sample_data_works_for_any_club_count(tmp_path, n_clubs):
    """A school having fewer than 10 clubs is normal. seed_sample_data used
    to hardcode randint(4, 10) preferences per student and crash in
    rng.sample() whenever there were fewer clubs than that."""
    club_defs = [(f"club_{i:02d}", 10, 0, None) for i in range(1, n_clubs + 1)]
    db_path = str(tmp_path / f"sample_{n_clubs}.db")

    seed_sample_data(db_path, n_students=15, club_defs=club_defs, seed=7)

    students, clubs, tested_scores, applicants, preferences, _ = load_from_sqlite(db_path)
    assert len(clubs) == n_clubs
    assert validate_data_integrity(students, clubs, preferences, applicants) == []
    # nobody may be given more preferences than there are clubs to rank
    assert all(len(prefs) <= n_clubs for prefs in preferences.values())


def test_full_pipeline_on_seeded_sample_data_has_no_integrity_problems(tmp_path):
    db_path = str(tmp_path / "app.db")
    csv_path = str(tmp_path / "match_results.csv")
    seed_sample_data(db_path, n_students=120, seed=7)

    result = run_full_pipeline(db_path, seed=42, output_csv_path=csv_path)

    students, clubs, tested_scores, applicants, preferences, stb_lottery = (
        load_from_sqlite(db_path)
    )

    assert sanity_check_result(result, clubs, preferences) == []
    assert verify_stability(
        result, clubs, preferences,
        default_reserve_eligible_fn(students, clubs),
    ) == []
    assert sum(1 for v in result.assignment.values() if v) > 0


# ---------------------------------------------------------------------------
# run_full_pipeline() là đường THỬ NGHIỆM — không được chạm dữ liệu thật
# ---------------------------------------------------------------------------

def test_run_full_pipeline_tu_choi_chay_tren_csdl_da_dung_that(tmp_path):
    """Đường dòng lệnh thiếu BỐN lớp bảo vệ mà api.run_pipeline có: không
    tôn trọng stb_lock, không chèn ngẫu nhiên cho em vào sau, không kiểm
    cặp phá vỡ, không ghi run_history.

    Chạy nhầm nó lên app.db thật là vẽ lại toàn bộ số bốc thăm và lật kết
    quả đã công bố — mà KHÔNG để lại dấu vết nào để kiểm toán. Chốt chặn
    này là thứ duy nhất ngăn điều đó.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api import PipelineAPI

    db_path = str(tmp_path / "app.db")
    api = PipelineAPI(db_path)
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    for i in range(1, 6):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Em " + sid)
        api.submit_preferences(sid, ["clb_a"])
    api.run_pipeline(seed=42)          # khoá STB + ghi run_history

    truoc = _bo_so_boc_tham(db_path)
    with pytest.raises(RuntimeError) as loi_bat_duoc:
        run_full_pipeline(db_path, seed=99, output_csv_path=str(tmp_path / "x.csv"))

    assert "TU CHOI CHAY" in str(loi_bat_duoc.value)
    assert _bo_so_boc_tham(db_path) == truoc, "đã kịp đổi số bốc thăm rồi mới chặn"


def test_run_full_pipeline_van_chay_binh_thuong_tren_csdl_sach(tmp_path):
    """Chốt chặn không được làm hỏng công dụng thật của hàm: chạy nhanh
    không cần giao diện, trên CSDL mới tinh."""
    db_path = str(tmp_path / "sach.db")
    seed_sample_data(db_path, n_students=40, seed=7)

    result = run_full_pipeline(db_path, seed=42,
                               output_csv_path=str(tmp_path / "kq.csv"))
    assert sum(1 for v in result.assignment.values() if v) > 0


def _bo_so_boc_tham(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    try:
        return dict(conn.execute("SELECT student_id, stb_number FROM students"))
    finally:
        conn.close()


def test_run_rbda_cham_tran_vong_thi_BAO_LOI_chu_khong_tra_ket_qua_do_dang():
    """Trước đây chạm trần thì vòng lặp lặng lẽ thoát và trả kết quả dở
    dang. verify_stability() gần như chắc chắn bắt được (em chưa thử hết
    nguyện vọng tạo cặp phá vỡ), nhưng người đọc nhận một câu báo lỗi nói
    SAI nguyên nhân.

    Cận trên thật đã đo: số vòng = độ dài danh sách nguyện vọng dài nhất,
    mà app chặn cứng 10 — nên trần 1000 không chạm được bằng dữ liệu thật.
    Test này hạ trần xuống để dựng lại tình huống.
    """
    students = {"HS%02d" % i: {"stb": i, "reserve_group": ""} for i in range(20)}
    clubs = {"c%d" % j: {"capacity": 1, "reserve_capacity": 0, "reserve_group": ""}
             for j in range(5)}
    prefs = {s: ["c%d" % j for j in range(5)] for s in students}
    applicants = {c: list(students) for c in clubs}
    stb = {s: i for i, s in enumerate(students)}
    fn = default_reserve_eligible_fn(students, clubs)

    with pytest.raises(RuntimeError, match="cham tran"):
        run_rbda(students, clubs, {c: {} for c in clubs}, applicants, prefs, stb,
                 fn, max_rounds=2)

    # trần mặc định: chạy trọn, số vòng đúng bằng số nguyện vọng
    kq = run_rbda(students, clubs, {c: {} for c in clubs}, applicants, prefs, stb, fn)
    assert kq.rounds_run == 5
