"""Tests for get_data_health_report — the pre-flight check for data gaps
that are VALID (validate_data_integrity passes, the pipeline runs) but
silently change who gets into which club."""


def _codes(report):
    return [w["code"] for w in report["data"]["warnings"]]


def _by_code(report, code):
    return next(w for w in report["data"]["warnings"] if w["code"] == code)


def _clean_school(api):
    """A fully-specified school that must produce zero warnings."""
    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_test_selection("s1", ["A"])
    api.submit_preferences("s1", ["A"])
    api.submit_club_scores("A", [{"student_id": "s1", "score": 8.0}])


def test_clean_data_produces_no_warnings(api):
    _clean_school(api)
    res = api.get_data_health_report()
    assert res["ok"] is True
    assert res["data"]["n_warnings"] == 0
    assert res["data"]["n_high"] == 0
    assert res["data"]["warnings"] == []


def test_empty_database_produces_no_warnings(api):
    """An empty DB is 'not set up yet', not 'broken' — don't cry wolf."""
    res = api.get_data_health_report()
    assert res["data"]["n_warnings"] == 0


def test_flags_tryout_with_nobody_scored(api):
    api.create_or_update_club("A", "Club A", 5, 0, "")
    for sid in ("s1", "s2"):
        api.create_student_if_missing(sid, sid)
        api.submit_test_selection(sid, ["A"])
        api.submit_preferences(sid, ["A"])

    res = api.get_data_health_report()
    assert "health_scoring_none" in _codes(res)
    w = _by_code(res, "health_scoring_none")
    assert w["severity"] == "high"
    assert w["params"] == {"club_id": "A", "n_applicants": 2}


def test_flags_partially_scored_tryout(api):
    api.create_or_update_club("A", "Club A", 5, 0, "")
    for sid in ("s1", "s2", "s3"):
        api.create_student_if_missing(sid, sid)
        api.submit_test_selection(sid, ["A"])
        api.submit_preferences(sid, ["A"])
    api.submit_club_scores("A", [{"student_id": "s1", "score": 4.0}])

    res = api.get_data_health_report()
    w = _by_code(res, "health_scoring_partial")
    assert w["severity"] == "high"
    assert w["params"]["n_scored"] == 1
    assert w["params"]["n_applicants"] == 3
    assert w["params"]["n_missing"] == 2


def test_fully_scored_tryout_is_not_flagged(api):
    api.create_or_update_club("A", "Club A", 5, 0, "")
    for sid in ("s1", "s2"):
        api.create_student_if_missing(sid, sid)
        api.submit_test_selection(sid, ["A"])
        api.submit_preferences(sid, ["A"])
    api.submit_club_scores("A", [
        {"student_id": "s1", "score": 7.0},
        {"student_id": "s2", "score": 9.0},
    ])

    res = api.get_data_health_report()
    assert "health_scoring_none" not in _codes(res)
    assert "health_scoring_partial" not in _codes(res)


def test_flags_tested_but_not_ranked(api):
    """The score is computed and then thrown away — a student can never be
    placed in a club they did not rank."""
    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_or_update_club("B", "Club B", 5, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_test_selection("s1", ["B"])   # tests for B
    api.submit_preferences("s1", ["A"])      # but only ranks A

    res = api.get_data_health_report()
    w = _by_code(res, "health_tested_not_ranked")
    assert w["severity"] == "high"
    assert w["params"]["n"] == 1
    assert "s1" in w["params"]["sample"] and "B" in w["params"]["sample"]


def test_tested_and_ranked_is_not_flagged(api):
    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_test_selection("s1", ["A"])
    api.submit_preferences("s1", ["A"])
    assert "health_tested_not_ranked" not in _codes(api.get_data_health_report())


def test_flags_student_with_no_preferences(api):
    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_student_if_missing("active", "Active")
    api.submit_preferences("active", ["A"])
    api.create_student_if_missing("forgot", "Forgot")   # submitted nothing

    res = api.get_data_health_report()
    w = _by_code(res, "health_student_no_preferences")
    assert w["params"]["n"] == 1
    assert "forgot" in w["params"]["sample"]


def test_flags_reserve_label_no_club_uses(api):
    """The classic typo: student tagged 'chinhsach', club wants 'chinh_sach'.
    The student silently loses reserve eligibility everywhere."""
    api.create_or_update_club("A", "Club A", 5, 1, "chinh_sach")
    api.create_student_if_missing("s1", "Student 1")
    api.bulk_set_reserve_group(["s1"], "chinhsach")     # typo
    api.submit_preferences("s1", ["A"])

    res = api.get_data_health_report()
    w = _by_code(res, "health_orphan_student_group")
    assert w["severity"] == "high"
    # The sample names WHICH student. Without it the warning says "check
    # for a typo" and leaves you to hunt the whole roster by hand.
    assert w["params"] == {"reserve_group": "chinhsach", "n": 1, "sample": "s1"}
    # and the club's own label now matches nobody
    assert "health_club_group_no_students" in _codes(res)


def test_orphan_label_sample_is_capped_and_stable(api):
    """More students than the sample limit: n counts them all, the sample
    shows the first few IN SORTED ORDER.

    Sorting matters. GROUP_CONCAT makes no promise about order, so slicing
    before sorting would show a different handful on each re-check and the
    user would think the data had changed under them."""
    api.create_or_update_club("A", "Club A", 50, 1, "chinh_sach")
    ids = ["s%02d" % i for i in range(1, 10)]
    for sid in ids:
        api.create_student_if_missing(sid, "Student " + sid)
        api.submit_preferences(sid, ["A"])
    api.bulk_set_reserve_group(ids, "chinhsach")        # 9 students, same typo

    w = _by_code(api.get_data_health_report(), "health_orphan_student_group")
    assert w["params"]["n"] == 9
    mau = w["params"]["sample"].split(", ")
    assert len(mau) == api._HEALTH_SAMPLE_LIMIT
    assert mau == sorted(ids)[:api._HEALTH_SAMPLE_LIMIT]
    # Chạy lại phải ra đúng mẫu đó.
    lai = _by_code(api.get_data_health_report(), "health_orphan_student_group")
    assert lai["params"]["sample"] == w["params"]["sample"]


def test_orphan_label_groups_are_reported_separately(api):
    """Two different bad labels must not be merged into one warning —
    each names its own students."""
    api.create_or_update_club("A", "Club A", 50, 1, "chinh_sach")
    for sid, nhan in [("s1", "chinhsach"), ("s2", "khoi10")]:
        api.create_student_if_missing(sid, "Student " + sid)
        api.submit_preferences(sid, ["A"])
        api.bulk_set_reserve_group([sid], nhan)

    res = api.get_data_health_report()
    theo_nhan = {
        w["params"]["reserve_group"]: w["params"]["sample"]
        for w in res["data"]["warnings"]
        if w["code"] == "health_orphan_student_group"
    }
    assert theo_nhan == {"chinhsach": "s1", "khoi10": "s2"}


def test_flags_club_with_reserve_seats_but_no_label(api):
    api.create_or_update_club("A", "Club A", 5, 2, "")   # 2 reserve seats, no label
    res = api.get_data_health_report()
    w = _by_code(res, "health_club_reserve_no_group")
    assert w["severity"] == "high"
    assert w["params"] == {"club_id": "A", "reserve_capacity": 2}


def test_matching_reserve_labels_are_not_flagged(api):
    api.create_or_update_club("A", "Club A", 5, 1, "chinh_sach")
    api.create_student_if_missing("s1", "Student 1")
    api.bulk_set_reserve_group(["s1"], "chinh_sach")
    api.submit_preferences("s1", ["A"])

    codes = _codes(api.get_data_health_report())
    assert "health_orphan_student_group" not in codes
    assert "health_club_group_no_students" not in codes
    assert "health_club_reserve_no_group" not in codes


def test_flags_oversubscription(api):
    api.create_or_update_club("A", "Club A", 2, 0, "")
    for i in range(5):
        sid = f"s{i}"
        api.create_student_if_missing(sid, sid)
        api.submit_preferences(sid, ["A"])

    res = api.get_data_health_report()
    w = _by_code(res, "health_oversubscribed")
    assert w["severity"] == "info"
    assert w["params"] == {"n_seats": 2, "n_students": 5, "n_short": 3}


def test_enough_seats_is_not_flagged_as_oversubscribed(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_preferences("s1", ["A"])
    assert "health_oversubscribed" not in _codes(api.get_data_health_report())


def test_flags_oversubscription_per_session_even_when_week_total_is_enough(api):
    """Each session is matched on its own, so spare seats on thu_5 cannot
    help anyone on thu_2. The old check summed the whole week (150 seats
    for 50 students) and stayed silent while 20 students were certain to
    get nothing on thu_2."""
    for i in range(3):
        api.create_or_update_club(f"T2_{i}", f"T2 {i}", 10, 0, "", "thu_2")
    for i in range(12):
        api.create_or_update_club(f"T5_{i}", f"T5 {i}", 10, 0, "", "thu_5")
    for i in range(50):
        sid = f"s{i:02d}"
        api.create_student_if_missing(sid, sid)
        api.submit_preferences(sid, ["T2_0", "T2_1", "T2_2", "T5_0"])

    res = api.get_data_health_report()
    codes = _codes(res)
    assert "health_oversubscribed" not in codes
    assert codes.count("health_oversubscribed_buoi") == 1
    w = _by_code(res, "health_oversubscribed_buoi")
    assert w["severity"] == "info"
    assert w["params"] == {"buoi": "thu_2", "n_seats": 30,
                           "n_students": 50, "n_short": 20}


def test_session_counts_only_students_who_ranked_in_it(api):
    """A student who ranked nothing on thu_2 is not competing for its seats."""
    api.create_or_update_club("A", "Club A", 1, 0, "", "thu_2")
    api.create_or_update_club("B", "Club B", 10, 0, "", "thu_5")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_preferences("s1", ["A", "B"])
    for sid in ("s2", "s3", "s4"):
        api.create_student_if_missing(sid, sid)
        api.submit_preferences(sid, ["B"])
    codes = _codes(api.get_data_health_report())
    assert "health_oversubscribed" not in codes
    assert "health_oversubscribed_buoi" not in codes


def test_mixed_school_names_unlabelled_clubs_not_whole_school(api):
    """Some clubs have a session, some do not. The unlabelled ones form their
    own group, so the shortage message must not say 'total seats across the
    whole school' — here that group has 1 seat while the school has 21."""
    api.create_or_update_club("U", "Unlabelled", 1, 0, "")
    api.create_or_update_club("B", "Club B", 20, 0, "", "thu_5")
    for sid in ("s1", "s2", "s3"):
        api.create_student_if_missing(sid, sid)
        api.submit_preferences(sid, ["U", "B"])

    res = api.get_data_health_report()
    codes = _codes(res)
    assert "health_oversubscribed" not in codes
    assert "health_oversubscribed_buoi" not in codes
    w = _by_code(res, "health_oversubscribed_chua_khai_buoi")
    assert w["severity"] == "info"
    assert w["params"] == {"n_seats": 1, "n_students": 3, "n_short": 2}


def test_every_health_warning_is_translatable_to_both_languages(api):
    """Whatever the report emits must render in vi and en with no
    unfilled placeholders — otherwise the operator sees a raw code."""
    from i18n_errors import format_message

    # one database that trips as many warnings as possible at once
    api.create_or_update_club("A", "Club A", 1, 2, "")          # reserve, no label
    api.create_or_update_club("B", "Club B", 1, 1, "khoi10")    # label nobody has
    for sid in ("s1", "s2", "s3"):
        api.create_student_if_missing(sid, sid)
        api.submit_preferences(sid, ["A"])
    api.submit_test_selection("s1", ["B"])                      # tested, not ranked
    api.bulk_set_reserve_group(["s2"], "sai_chinh_ta")          # orphan label
    api.create_student_if_missing("forgot", "Forgot")           # no preferences

    res = api.get_data_health_report()
    emitted = set(_codes(res))
    # sanity: this fixture should be tripping most of the checks
    assert len(emitted) >= 5, f"expected a broad spread, got {emitted}"

    for w in res["data"]["warnings"]:
        assert w["severity"] in ("high", "medium", "info")
        for lang in ("vi", "en"):
            text = format_message(w["code"], w["params"], lang=lang)
            assert text != w["code"], f"no {lang} text for {w['code']}"
            assert "{" not in text, f"unfilled placeholder in {lang}: {text!r}"
