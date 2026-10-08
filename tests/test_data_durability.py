"""Tests for the data-loss/corruption fixes (see the data-loss test plan — an artifact listed in BAN_GIAO.md section 8):

Group A — atomicity: run_pipeline() must do the STB draw, match_results
write, and run_meta/run_history writes as ONE transaction. A crash at any
point rolls back EVERYTHING, including a freshly-drawn STB lottery
("full rollback", the approved design) — never an orphaned STB lock with
no matching results/history row.

Group B — corrupt/missing app.db: PipelineAPI must never die silently
(main.py always opens a window), and recovery.py's RecoveryAPI must be
able to restore from the most recent readable backup, falling back
through older backups if the newest one is also corrupt, or start fresh
as a last resort — never deleting the corrupt file outright.
"""

import os
import sqlite3

import pytest

import api as api_module
from api import PipelineAPI
from recovery import RecoveryAPI


def _seed_small_scenario(api):
    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_or_update_club("B", "Club B", 5, 0, "")
    for sid in ("s1", "s2", "s3"):
        api.create_student_if_missing(sid, sid)
    api.submit_preferences("s1", ["A"])
    api.submit_preferences("s2", ["A", "B"])
    api.submit_preferences("s3", ["B"])


def _snapshot(db_path):
    conn = sqlite3.connect(db_path)
    lock = conn.execute("SELECT is_locked FROM stb_lock WHERE id=1").fetchone()[0]
    n_results = conn.execute("SELECT COUNT(*) FROM match_results").fetchone()[0]
    n_history = conn.execute("SELECT COUNT(*) FROM run_history").fetchone()[0]
    stb_numbers = [r[0] for r in conn.execute("SELECT stb_number FROM students ORDER BY student_id")]
    conn.close()
    return lock, n_results, n_history, stb_numbers


# ------------------------------------------------------------------ #
# Group A — atomicity / full rollback
# ------------------------------------------------------------------ #

def test_run_pipeline_backs_up_db_before_running(api):
    _seed_small_scenario(api)
    backup_dir = os.path.dirname(api.db_path)
    prefix = f"{os.path.basename(api.db_path)}.bak-"
    before = [f for f in os.listdir(backup_dir) if f.startswith(prefix)]
    assert before == []

    res = api.run_pipeline(seed=1)
    assert res["ok"] is True, res

    after = [f for f in os.listdir(backup_dir) if f.startswith(prefix)]
    assert len(after) == 1
    backup_step = next(s for s in res["data"]["steps"] if s["step"] == "backup")
    assert backup_step["status"] == "done"
    assert backup_step["detail"]["code"] == "db_backed_up"


def test_backup_retention_keeps_only_max_backups(api):
    _seed_small_scenario(api)
    for _ in range(api._MAX_BACKUPS + 5):
        api._backup_db()

    backup_dir = os.path.dirname(api.db_path)
    prefix = f"{os.path.basename(api.db_path)}.bak-"
    backups = [f for f in os.listdir(backup_dir) if f.startswith(prefix)]
    assert len(backups) == api._MAX_BACKUPS


# CHO TIEM LOI: `run_rbda_nhieu_buoi`, khong phai `run_rbda`.
#
# Ba test duoi day gia lap mot lan chay no giua chung giao dich, de kiem
# rang MOI THU deu bi rollback — ke ca so boc tham vua ve. Chung lam viec
# do bang cach thay tam ham ma run_pipeline goi.
#
# Tu khi co tinh nang nhieu buoi, run_pipeline goi run_rbda_nhieu_buoi;
# ham do goi run_rbda nhung goi qua ten TRONG module thuat toan, nen vá
# `api_module.run_rbda` khong con chan duoc gi. Test van xanh mot cach vo
# nghia: khong co exception nao duoc nem, pipeline chay tron, va phep so
# "khong doi gi" thanh ra so mot trang thai voi chinh no.
#
# Da vap dung loi do khi lam tinh nang nay (test bao run_history tang 2
# thay vi 1). Doi ten o day la SUA DIEM TIEM, khong phai noi long test.
def test_ordinary_exception_mid_transaction_fully_rolls_back(api):
    """A bug/exception between the STB draw and the final commit must undo
    the STB draw too — never leave a locked-but-resultless STB state."""
    _seed_small_scenario(api)
    res0 = api.run_pipeline(seed=1)
    assert res0["ok"] is True
    baseline = _snapshot(api.db_path)

    original_run_rbda = api_module.run_rbda_nhieu_buoi
    api_module.run_rbda_nhieu_buoi = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("simulated bug"))
    try:
        res = api.run_pipeline(seed=99, force_redraw_stb=True)
    finally:
        api_module.run_rbda_nhieu_buoi = original_run_rbda

    assert res["ok"] is False
    error_steps = [s["step"] for s in res["data"]["steps"] if s["status"] == "error"]
    assert error_steps, "buoc gay loi phai duoc danh dau error trong nhat ky"
    assert "rollback" in [s["step"] for s in res["data"]["steps"]]
    assert _snapshot(api.db_path) == baseline, (
        "STB lock/match_results/run_history/stb_number must be byte-identical "
        "to before the crashed run — full rollback, including the STB draw"
    )


def test_base_exception_mid_transaction_rolls_back_and_reraises(api):
    """KeyboardInterrupt/SystemExit are not Exception subclasses — they
    must still trigger a full rollback, but must propagate rather than
    being swallowed as an ordinary {ok: False} pipeline failure."""
    _seed_small_scenario(api)
    res0 = api.run_pipeline(seed=1)
    assert res0["ok"] is True
    baseline = _snapshot(api.db_path)

    original_run_rbda = api_module.run_rbda_nhieu_buoi
    api_module.run_rbda_nhieu_buoi = lambda *a, **kw: (_ for _ in ()).throw(KeyboardInterrupt("simulated interrupt"))
    try:
        with pytest.raises(KeyboardInterrupt):
            api.run_pipeline(seed=98, force_redraw_stb=True)
    finally:
        api_module.run_rbda_nhieu_buoi = original_run_rbda

    assert _snapshot(api.db_path) == baseline


def test_pipeline_still_usable_after_a_rolled_back_crash(api):
    _seed_small_scenario(api)
    api.run_pipeline(seed=1)
    n_history_before = _snapshot(api.db_path)[2]

    original_run_rbda = api_module.run_rbda_nhieu_buoi
    api_module.run_rbda_nhieu_buoi = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        api.run_pipeline(seed=2, force_redraw_stb=True)
    finally:
        api_module.run_rbda_nhieu_buoi = original_run_rbda

    # Cùng hạt giống 1 với lần khoá: lần vẽ lại bằng hạt giống 2 đã bị huỷ
    # trọn, nên khoá vẫn giữ hạt giống 1 (tests/test_khoa_hat_giong.py).
    res = api.run_pipeline(seed=1)
    assert res["ok"] is True
    assert _snapshot(api.db_path)[2] == n_history_before + 1


def test_rbda_sanity_or_stability_failure_also_rolls_back_stb_draw(api):
    """The pre-existing sanity/stability check path (not just exceptions)
    must also roll back — it used to commit the STB draw unconditionally
    before this fix."""
    _seed_small_scenario(api)
    res0 = api.run_pipeline(seed=1)
    assert res0["ok"] is True
    baseline = _snapshot(api.db_path)

    original_sanity = api_module.sanity_check_result
    api_module.sanity_check_result = lambda *a, **kw: ["simulated sanity problem"]
    try:
        res = api.run_pipeline(seed=77, force_redraw_stb=True)
    finally:
        api_module.sanity_check_result = original_sanity

    assert res["ok"] is False
    assert _snapshot(api.db_path) == baseline


# ------------------------------------------------------------------ #
# Group B — corrupt / missing app.db + recovery
# ------------------------------------------------------------------ #

def test_garbage_db_file_raises_instead_of_silently_producing_a_broken_api(tmp_path):
    db_path = str(tmp_path / "app.db")
    with open(db_path, "wb") as f:
        f.write(b"not a sqlite file" * 10)

    with pytest.raises(Exception):
        PipelineAPI(db_path)


def test_truncated_db_file_raises(tmp_path):
    db_path = str(tmp_path / "app.db")
    api = PipelineAPI(db_path)
    _seed_small_scenario(api)
    with open(db_path, "r+b") as f:
        f.truncate(20)

    with pytest.raises(Exception):
        PipelineAPI(db_path)


def test_recovery_reports_status_with_no_backups(tmp_path):
    db_path = str(tmp_path / "app.db")
    rec = RecoveryAPI(db_path, "simulated init error")
    res = rec.get_status()
    assert res["ok"] is True
    assert res["data"]["backups"] == []
    assert res["data"]["init_error"] == "simulated init error"


def test_recovery_restore_fails_cleanly_with_no_backups(tmp_path):
    db_path = str(tmp_path / "app.db")
    rec = RecoveryAPI(db_path, "err")
    res = rec.restore_from_backup()
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "recovery_no_backups"


def test_recovery_start_fresh_preserves_corrupt_file_and_creates_new_db(tmp_path):
    db_path = str(tmp_path / "app.db")
    with open(db_path, "wb") as f:
        f.write(b"garbage")

    rec = RecoveryAPI(db_path, "simulated init error")
    res = rec.start_fresh()
    assert res["ok"] is True
    assert res["data"]["detail"]["code"] == "recovery_fresh_created"

    corrupt_files = [f for f in os.listdir(tmp_path) if ".corrupt-" in f]
    assert len(corrupt_files) == 1
    with open(tmp_path / corrupt_files[0], "rb") as f:
        assert f.read() == b"garbage"

    # a fresh, working PipelineAPI must now be constructible
    PipelineAPI(db_path)


def test_recovery_restore_from_backup_recovers_full_history(tmp_path):
    db_path = str(tmp_path / "app.db")
    api = PipelineAPI(db_path)
    _seed_small_scenario(api)
    res = api.run_pipeline(seed=1)
    assert res["ok"] is True
    backup_path = api._backup_db()

    with open(db_path, "r+b") as f:
        f.truncate(10)

    rec = RecoveryAPI(db_path, "simulated crash")
    res = rec.restore_from_backup()
    assert res["ok"] is True
    assert res["data"]["restored_from"] == os.path.basename(backup_path)
    assert res["data"]["skipped"] == []

    api2 = PipelineAPI(db_path)
    hist = api2.get_run_history()
    assert len(hist["data"]) == 1


def test_recovery_falls_back_through_multiple_corrupt_backups(tmp_path):
    """If the newest backup is ALSO corrupt, restore must skip it and use
    the next older good one — never stop at the first failure."""
    db_path = str(tmp_path / "app.db")
    api = PipelineAPI(db_path)
    _seed_small_scenario(api)
    api.run_pipeline(seed=1)

    good_backup = api._backup_db()
    bad_backup = api._backup_db()
    assert bad_backup != good_backup
    with open(bad_backup, "wb") as f:
        f.write(b"corrupt backup file")

    with open(db_path, "r+b") as f:
        f.truncate(5)

    rec = RecoveryAPI(db_path, "simulated crash")
    res = rec.restore_from_backup()
    assert res["ok"] is True
    assert res["data"]["restored_from"] == os.path.basename(good_backup)
    assert os.path.basename(bad_backup) in res["data"]["skipped"]


def test_recovery_all_backups_corrupt_fails_cleanly(tmp_path):
    db_path = str(tmp_path / "app.db")
    api = PipelineAPI(db_path)
    _seed_small_scenario(api)
    api.run_pipeline(seed=1)  # also creates one auto-backup as its first step
    api._backup_db()

    backup_dir = os.path.dirname(db_path)
    prefix = f"{os.path.basename(db_path)}.bak-"
    all_backups = [f for f in os.listdir(backup_dir) if f.startswith(prefix)]
    assert len(all_backups) == 2, "sanity check: expected exactly 2 backups by this point"
    for name in all_backups:
        with open(os.path.join(backup_dir, name), "wb") as f:
            f.write(b"also corrupt")

    with open(db_path, "r+b") as f:
        f.truncate(5)

    rec = RecoveryAPI(db_path, "simulated crash")
    res = rec.restore_from_backup()
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "recovery_all_backups_corrupt"
    assert res["errors"][0]["params"]["n_tried"] == 2


def test_every_recovery_message_is_translatable_to_both_languages(tmp_path):
    from i18n_errors import format_message

    db_path = str(tmp_path / "app.db")
    rec = RecoveryAPI(db_path, "err")
    entries = [
        rec.restore_from_backup()["errors"][0],
        rec.start_fresh()["data"]["detail"],
    ]
    for entry in entries:
        for lang in ("vi", "en"):
            text = format_message(entry["code"], entry["params"], lang=lang)
            assert text != entry["code"], f"no {lang} text for {entry['code']}"
            assert "{" not in text, f"unfilled placeholder in {lang}: {text!r}"
