import os
import re
import sqlite3


def test_every_error_code_used_in_api_py_is_in_the_i18n_catalog():
    """Static-analysis guard: every err("code", ...) call site in api.py
    (and in rbda_priority_pipeline.py) must have a matching entry with
    both "vi" and "en" text in i18n_errors.MESSAGES — otherwise the UI
    would silently fall back to showing the raw code instead of text."""
    from i18n_errors import MESSAGES

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = re.compile(r'err\(\s*["\'](\w+)["\']')

    used_codes = set()
    # api.py nay tach thanh nhieu tep api_*.py — quet het, khong thi ma loi
    # nam trong tep con se lot khoi luoi nay.
    import glob
    ten_tep = [os.path.basename(p) for p in glob.glob(os.path.join(base_dir, "api*.py"))]
    ten_tep += ["rbda_priority_pipeline.py", "recovery.py"]
    for filename in ten_tep:
        source = open(os.path.join(base_dir, filename), encoding="utf-8").read()
        used_codes.update(pattern.findall(source))

    assert used_codes, "sanity check: should have found at least one err(...) call"

    missing = used_codes - set(MESSAGES.keys())
    assert not missing, f"error codes used but not in i18n_errors.MESSAGES: {missing}"

    incomplete = {
        code for code in used_codes
        if not MESSAGES[code].get("vi") or not MESSAGES[code].get("en")
    }
    assert not incomplete, f"error codes missing a vi or en translation: {incomplete}"


def test_dashboard_status_on_empty_db(api):
    res = api.get_dashboard_status()
    assert res["ok"] is True
    assert res["data"] == {
        "n_students": 0,
        "n_clubs": 0,
        "n_students_with_preferences": 0,
        "n_matched": 0,
        "has_results": False,
    }


def test_create_or_update_club_validates_and_upserts(api):
    ok = api.create_or_update_club("A", "Club A", 10, 2, "policy")
    assert ok["ok"] is True

    clubs = api.list_clubs()["data"]
    assert clubs == [{"club_id": "A", "name": "Club A", "capacity": 10,
                      "reserve_capacity": 2, "buoi": "__mac_dinh__"}]

    # upsert: same club_id updates in place, not a duplicate row
    api.create_or_update_club("A", "Club A renamed", 12, 2, "policy")
    clubs = api.list_clubs()["data"]
    assert len(clubs) == 1
    assert clubs[0]["name"] == "Club A renamed"
    assert clubs[0]["capacity"] == 12

    assert api.create_or_update_club("B", "Club B", 0, 0, "")["ok"] is False
    assert api.create_or_update_club("C", "Club C", 5, 6, "")["ok"] is False


def test_delete_club_blocked_when_referenced_by_preferences(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_student_if_missing("s1", "Nguyen Van A")
    api.submit_preferences("s1", ["A"])

    res = api.delete_club("A")
    assert res["ok"] is False

    # once no longer referenced, deletion succeeds
    api.create_or_update_club("B", "Club B", 10, 0, "")
    api.submit_preferences("s1", ["B"])
    res = api.delete_club("A")
    assert res["ok"] is True
    assert api.list_clubs()["data"] == [{"club_id": "B", "name": "Club B", "capacity": 10,
                                        "reserve_capacity": 0, "buoi": "__mac_dinh__"}]


def test_create_student_if_missing_is_idempotent(api):
    first = api.create_student_if_missing("s1", "Nguyen Van A")
    assert first["ok"] is True
    assert first["data"]["created"] is True

    second = api.create_student_if_missing("s1", "Different Name")
    assert second["data"]["created"] is False


def test_search_students(api):
    api.create_student_if_missing("s001", "Nguyen Van A")
    api.create_student_if_missing("s002", "Tran Thi B")
    res = api.search_students("s00")
    assert res["ok"] is True
    assert {r["student_id"] for r in res["data"]} == {"s001", "s002"}

    res = api.search_students("Nguyen")
    assert [r["student_id"] for r in res["data"]] == ["s001"]


def test_submit_test_selection_success_and_validation(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_or_update_club("B", "Club B", 10, 0, "")
    api.create_student_if_missing("s1", "Nguyen Van A")

    res = api.submit_test_selection("s1", ["A", "B"])
    assert res["ok"] is True
    assert res["data"]["n_selected"] == 2

    state = api.get_student_entry_state("s1")["data"]
    assert sorted(state["tested_clubs"]) == ["A", "B"]

    # overwrite with a smaller set
    res = api.submit_test_selection("s1", ["A"])
    assert res["ok"] is True
    state = api.get_student_entry_state("s1")["data"]
    assert state["tested_clubs"] == ["A"]

    assert api.submit_test_selection("s1", ["ghost_club"])["ok"] is False
    assert api.submit_test_selection("ghost_student", ["A"])["ok"] is False


def test_submit_preferences_success_and_ordering(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_or_update_club("B", "Club B", 10, 0, "")
    api.create_student_if_missing("s1", "Nguyen Van A")

    res = api.submit_preferences("s1", ["B", "A"])
    assert res["ok"] is True
    assert res["data"]["n_ranked"] == 2

    state = api.get_student_entry_state("s1")["data"]
    assert state["ranked_clubs"] == ["B", "A"]


def test_submit_preferences_error_cases(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_student_if_missing("s1", "Nguyen Van A")

    assert api.submit_preferences("s1", [])["ok"] is False
    assert api.submit_preferences("s1", ["A", "A"])["ok"] is False
    assert api.submit_preferences("s1", [f"c{i}" for i in range(11)])["ok"] is False
    assert api.submit_preferences("s1", ["ghost_club"])["ok"] is False
    assert api.submit_preferences("ghost_student", ["A"])["ok"] is False


def test_check_data_integrity(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_student_if_missing("s1", "Nguyen Van A")
    api.submit_preferences("s1", ["A"])

    res = api.check_data_integrity()
    assert res["ok"] is True
    assert res["data"]["n_students"] == 1
    assert res["data"]["n_clubs"] == 1


def _seed_small_scenario(api):
    api.create_or_update_club("A", "Club A", 1, 0, "")
    api.create_or_update_club("B", "Club B", 1, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.create_student_if_missing("s2", "Student 2")
    api.create_student_if_missing("s3", "Student 3")
    api.submit_preferences("s1", ["A"])
    api.submit_preferences("s2", ["A", "B"])
    api.submit_preferences("s3", ["B"])


def test_run_pipeline_full_flow_and_results(api):
    _seed_small_scenario(api)

    res = api.run_pipeline(seed=1)
    assert res["ok"] is True, res
    done_steps = [s["step"] for s in res["data"]["steps"] if s["status"] == "done"]
    assert done_steps == ["backup", "validate", "stb_lottery", "rbda_cascade", "write_results", "export"]
    assert res["data"]["n_total"] == 3

    # step details that carry translatable text are structured {code,
    # params} entries, not pre-formatted Vietnamese strings — this is
    # what lets the frontend render them in whichever language is active.
    by_step = {(s["step"], s["status"]): s for s in res["data"]["steps"]}
    stb_detail = by_step[("stb_lottery", "done")]["detail"]
    assert stb_detail["code"] == "stb_redrawn_and_locked"
    assert stb_detail["params"]["n"] == 3
    rbda_detail = by_step[("rbda_cascade", "done")]["detail"]
    assert rbda_detail["code"] == "rbda_done"
    assert isinstance(rbda_detail["params"]["rounds"], int)

    dashboard = api.get_dashboard_status()["data"]
    assert dashboard["has_results"] is True

    results = api.get_match_results("")["data"]
    assert len(results) == 3
    assigned = {r["student_id"]: r["club_id"] for r in results}
    # A and B have capacity 1 each and s1/s2 both compete for A, so
    # exactly 2 of the 3 students end up matched regardless of the STB
    # draw (which one is unmatched depends on the random seed).
    assert sum(1 for cid in assigned.values() if cid) == 2

    fill = api.get_club_fill_stats()["data"]
    fill_by_id = {f["club_id"]: f for f in fill}
    assert fill_by_id["A"]["matched"] == 1
    assert fill_by_id["B"]["matched"] == 1

    history = api.get_run_history()["data"]
    assert len(history) == 1
    assert history[0]["n_total"] == 3


def test_run_pipeline_locks_stb_and_reuses_on_rerun(api):
    _seed_small_scenario(api)

    api.run_pipeline(seed=1)
    lock = api.get_stb_lock_status()["data"]
    assert lock["is_locked"] is True

    conn = sqlite3.connect(api.db_path)
    stb_before = dict(conn.execute("SELECT student_id, stb_number FROM students").fetchall())
    conn.close()

    res = api.run_pipeline(seed=1)
    assert res["ok"] is True
    assert res["data"]["stb_redrawn"] is False

    conn = sqlite3.connect(api.db_path)
    stb_after = dict(conn.execute("SELECT student_id, stb_number FROM students").fetchall())
    conn.close()
    assert stb_before == stb_after

    history = api.get_run_history()["data"]
    assert len(history) == 2


def test_run_pipeline_force_redraw_reassigns_stb(api):
    _seed_small_scenario(api)
    api.run_pipeline(seed=1)

    conn = sqlite3.connect(api.db_path)
    stb_before = dict(conn.execute("SELECT student_id, stb_number FROM students").fetchall())
    conn.close()

    res = api.run_pipeline(seed=99, force_redraw_stb=True)
    assert res["ok"] is True
    assert res["data"]["stb_redrawn"] is True

    conn = sqlite3.connect(api.db_path)
    stb_after = dict(conn.execute("SELECT student_id, stb_number FROM students").fetchall())
    conn.close()
    assert stb_before != stb_after


def test_run_pipeline_supplements_stb_for_new_student_after_lock(api):
    _seed_small_scenario(api)
    api.run_pipeline(seed=1)

    api.create_student_if_missing("s4", "Student 4")
    api.create_or_update_club("C", "Club C", 5, 0, "")
    api.submit_preferences("s4", ["C"])

    res = api.run_pipeline(seed=1)
    assert res["ok"] is True
    assert res["data"]["stb_redrawn"] is False

    conn = sqlite3.connect(api.db_path)
    stb_s4 = conn.execute(
        "SELECT stb_number FROM students WHERE student_id = 's4'"
    ).fetchone()[0]
    conn.close()
    assert stb_s4 is not None


def test_run_pipeline_reports_validation_errors(api):
    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_preferences("s1", ["A"])

    # corrupt the DB directly to simulate bad data bypassing the API's
    # own validation (e.g. a hand-edited DB) — validate step must catch it.
    conn = sqlite3.connect(api.db_path)
    # CSDL mới tự từ chối sức chứa 0 (CHECK). Dữ liệu như vậy chỉ còn tồn
    # tại ở CSDL cũ có dòng vi phạm — thứ di trú cố ý không đụng tới — nên
    # tắt CHECK trên kết nối này để dựng lại đúng tình huống đó.
    conn.execute("PRAGMA ignore_check_constraints = ON")
    conn.execute("UPDATE clubs SET capacity = 0 WHERE club_id = 'A'")
    conn.commit()
    conn.close()

    res = api.run_pipeline(seed=1)
    assert res["ok"] is False
    steps = res["data"]["steps"]
    error_steps = [s for s in steps if s["status"] == "error"]
    assert len(error_steps) == 1
    assert error_steps[0]["step"] == "validate"

    top_level_errors = res["errors"]
    assert top_level_errors, "validate errors should be surfaced at the top level too"
    assert top_level_errors[0]["code"] == "club_capacity_not_positive"
    assert top_level_errors[0]["params"]["club_id"] == "A"


def test_scoring_is_blind_no_stb_or_preferences_leaked(api):
    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_test_selection("s1", ["A"])
    api.submit_preferences("s1", ["A"])

    applicants = api.get_club_applicants_for_scoring("A")["data"]["applicants"]
    assert applicants == [{"student_id": "s1", "name": "Student 1", "score": None}]
    assert "stb" not in applicants[0]
    assert "rank" not in applicants[0]

    res = api.submit_club_scores("A", [{"student_id": "s1", "score": 8.5}])
    assert res["ok"] is True
    assert res["data"]["n_saved"] == 1

    applicants = api.get_club_applicants_for_scoring("A")["data"]["applicants"]
    assert applicants[0]["score"] == 8.5

    overview = api.get_scoring_overview()["data"]
    assert overview[0]["n_applicants"] == 1
    assert overview[0]["n_scored"] == 1

    # scoring a student not registered for this club is rejected
    api.create_student_if_missing("s2", "Student 2")
    res = api.submit_club_scores("A", [{"student_id": "s2", "score": 9.0}])
    assert res["data"]["n_saved"] == 0
    assert res["data"]["warnings"]


def test_bulk_set_reserve_group_and_list_reserve_groups_in_use(api):
    api.create_student_if_missing("s1", "Student 1")
    api.create_student_if_missing("s2", "Student 2")

    res = api.bulk_set_reserve_group(["s1", "s2", "ghost"], "chinh_sach")
    assert res["ok"] is True
    assert res["data"]["n_updated"] == 2
    assert res["data"]["not_found"] == ["ghost"]

    groups = api.list_reserve_groups_in_use()["data"]
    assert groups == ["chinh_sach"]


def test_list_students_admin_pagination(api):
    for i in range(5):
        api.create_student_if_missing(f"s{i:02d}", f"Student {i}")

    page1 = api.list_students_admin("", page=1, page_size=2)["data"]
    assert page1["total"] == 5
    assert page1["total_pages"] == 3
    assert len(page1["rows"]) == 2

    page3 = api.list_students_admin("", page=3, page_size=2)["data"]
    assert len(page3["rows"]) == 1


def test_import_preferences_csv_wide_format(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_or_update_club("B", "Club B", 10, 0, "")

    csv_text = (
        "student_id,name,pref_1,pref_2\n"
        "s1,Nguyen Van A,A,B\n"
        "s2,Tran Thi B,B,\n"
    )
    preview = api.preview_import_csv(csv_text, "preferences")
    assert preview["ok"] is True
    assert preview["data"]["format"] == "wide"
    assert preview["data"]["n_new_students"] == 2

    res = api.import_preferences_csv(csv_text)
    assert res["ok"] is True
    assert res["data"]["n_students_created"] == 2
    assert res["data"]["n_students_with_preferences_written"] == 2

    state = api.get_student_entry_state("s1")["data"]
    assert state["ranked_clubs"] == ["A", "B"]


def test_reset_student_entry_clears_selection_and_preferences_but_keeps_student(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_or_update_club("B", "Club B", 10, 0, "")
    api.create_student_if_missing("s1", "Nguyen Van A")
    api.submit_test_selection("s1", ["A", "B"])
    api.submit_preferences("s1", ["A", "B"])

    res = api.reset_student_entry("s1")
    assert res["ok"] is True
    # n_scores_removed: không có điểm nào để xoá (xem test_diem_theo_o_tick.py)
    assert res["data"] == {"student_id": "s1", "reset": True, "n_scores_removed": 0}

    state = api.get_student_entry_state("s1")["data"]
    assert state["tested_clubs"] == []
    assert state["ranked_clubs"] == []
    assert state["name"] == "Nguyen Van A"

    # the student can immediately re-enter fresh data afterwards
    res = api.submit_preferences("s1", ["B"])
    assert res["ok"] is True


def test_reset_student_entry_nonexistent_student(api):
    res = api.reset_student_entry("ghost")
    assert res["ok"] is False


def test_delete_student_removes_all_associated_data(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_student_if_missing("s1", "Nguyen Van A")
    api.submit_test_selection("s1", ["A"])
    api.submit_preferences("s1", ["A"])
    api.submit_club_scores("A", [{"student_id": "s1", "score": 7.5}])
    api.bulk_set_reserve_group(["s1"], "chinh_sach")

    res = api.delete_student("s1")
    assert res["ok"] is True
    assert res["data"] == {"student_id": "s1", "deleted": True}

    assert api.search_students("s1")["data"] == []
    assert api.get_student_entry_state("s1")["ok"] is False

    conn = sqlite3.connect(api.db_path)
    for table in ["preferences", "club_test_selection", "club_scores"]:
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE student_id = 's1'"
        ).fetchone()[0]
        assert count == 0, table
    conn.close()

    # club itself must survive — only the student's data was removed
    assert api.list_clubs()["data"][0]["club_id"] == "A"


def test_delete_student_nonexistent_student(api):
    res = api.delete_student("ghost")
    assert res["ok"] is False


def test_delete_student_blocked_after_pipeline_run(api):
    _seed_small_scenario(api)
    api.run_pipeline(seed=1)

    res = api.delete_student("s1")
    assert res["ok"] is False

    # student and their match result are untouched
    results = api.get_match_results("")["data"]
    assert any(r["student_id"] == "s1" for r in results)


def test_import_test_selection_csv_long_format(api):
    api.create_or_update_club("A", "Club A", 10, 0, "")
    api.create_student_if_missing("s1", "Student 1")

    csv_text = "student_id,club_id\ns1,A\n"
    res = api.import_test_selection_csv(csv_text)
    assert res["ok"] is True
    assert res["data"]["n_students_with_selection_written"] == 1

    state = api.get_student_entry_state("s1")["data"]
    assert state["tested_clubs"] == ["A"]


def test_fill_stats_tach_rieng_so_em_vao_bang_suat_du_tru(api):
    """`matched_reserve` là số em THỰC SỰ vào bằng suất dự trữ.

    Khác hẳn `reserve_capacity` — chỉ tiêu dự trữ của CLB. Biểu đồ lấp
    đầy trước đây vẽ theo chỉ tiêu, tức là vẽ một thuộc tính của CLB chứ
    không phải điều đã xảy ra, trong khi chú giải lại ghi như thể đang
    nói về học sinh.
    """
    api.create_or_update_club("clb_dt", "CLB Dự trữ", 2, 1, "chinh_sach")
    api.create_or_update_club("clb_thuong", "CLB Thường", 2, 0, "")
    for sid, nhom, clb, diem in (
        ("HS01", "", "clb_dt", 9.0),
        ("HS02", "chinh_sach", "clb_dt", 5.0),   # thấp điểm nhất, vào bằng dự trữ
        ("HS03", "", "clb_thuong", 8.0),
    ):
        api.create_student_if_missing(sid, "Em " + sid)
        if nhom:
            api.set_student_reserve_group(sid, nhom)
        api.submit_test_selection(sid, [clb])
        api.submit_preferences(sid, [clb])
        api.submit_club_scores(clb, [{"student_id": sid, "score": diem}])
    assert api.run_pipeline(seed=42)["ok"]

    theo_ma = {f["club_id"]: f for f in api.get_club_fill_stats()["data"]}

    dt = theo_ma["clb_dt"]
    assert dt["matched"] == 2
    assert dt["matched_reserve"] == 1
    assert dt["reserve_capacity"] == 1

    # CLB không có ai diện dự trữ -> 0, không phải None (biểu đồ sẽ vẽ
    # một đoạn rộng 0 px nếu để lọt None qua phép so sánh).
    thuong = theo_ma["clb_thuong"]
    assert thuong["matched"] == 1
    assert thuong["matched_reserve"] == 0

    # Không bao giờ được vượt quá số em đã xếp.
    for f in theo_ma.values():
        assert 0 <= f["matched_reserve"] <= f["matched"]


def test_fill_stats_clb_chua_ai_vao_thi_khong_tra_ve_None(api):
    """CLB rỗng: LEFT JOIN không khớp dòng nào nên SUM(...) trả NULL nếu
    câu lệnh viết hớ. Biểu đồ nhận None rồi làm phép tính là ra NaN."""
    api.create_or_update_club("clb_rong", "CLB Rỗng", 3, 1, "chinh_sach")
    f = api.get_club_fill_stats()["data"][0]
    assert f["matched"] == 0
    assert f["matched_reserve"] in (0, None)
    # Dù SQLite trả về gì, phía JS đã có `c.matched_reserve || 0`.


# --- Traceback Python không bao giờ tới giao diện --------------------------

def _co_traceback(obj):
    return "Traceback (most recent call last)" in repr(obj) or 'File "' in repr(obj)


def test_ma_nguon_khong_tra_traceback_ve_giao_dien():
    """Canh ở tầng mã nguồn: `format_exc()` từng nằm trong 8 lời trả về
    của api.py và một của browser_host.py."""
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for ten in ("api.py", "browser_host.py"):
        with open(os.path.join(goc, ten), encoding="utf-8") as f:
            assert "format_exc" not in f.read(), ten


def test_loi_bat_ngo_ghi_vao_nhat_ky_va_tra_cau_da_dich(api, monkeypatch):
    import api as api_module
    import chan_doan

    def hong(*a, **k):
        raise RuntimeError("csdl hong")
    monkeypatch.setattr(api_module, "load_from_sqlite", hong)

    res = api.check_data_integrity()
    assert res["ok"] is False
    assert not _co_traceback(res), res
    assert [e["code"] for e in res["errors"]] == ["error_checking_integrity", "xem_nhat_ky"]
    assert res["errors"][1]["params"]["file"] == chan_doan.TEN_LOG_UNG_DUNG

    log = os.path.join(os.path.dirname(api.db_path), chan_doan.TEN_LOG_UNG_DUNG)
    with open(log, encoding="utf-8") as f:
        noi_dung = f.read()
    assert "Traceback" in noi_dung and "csdl hong" in noi_dung, "chi tiết phải còn trong tệp nhật ký"


def test_chay_hong_giua_chung_khong_tra_traceback(api, monkeypatch):
    import api as api_module

    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_preferences("s1", ["A"])

    def hong(*a, **k):
        raise RuntimeError("hong giua chung")
    monkeypatch.setattr(api_module, "generate_stb_lottery", hong)

    res = api.run_pipeline(seed=1)
    assert res["ok"] is False
    assert not _co_traceback(res), res
    # Hợp đồng lỗi của run_pipeline: bước nằm ở data, lỗi là một danh sách.
    codes = [e["code"] for e in res["errors"]]
    assert codes == ["error_running_pipeline", "xem_nhat_ky"], codes
