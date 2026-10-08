# Design Fix Plan — RB-DA Kiosk

> **Status:** Tasks 0.1, 0.2, 1.1, 1.2, 3.1, 4.1 and 3.2 are DONE (see §10). The rest is still a plan.
> **Branch for all work:** `claude/program-design-review-oxjnp1`
> **Written:** 27/09/2026, after the design review of the same date.
> **Owner of every decision marked ⚖️:** Truong. Claude does not start a task
> that has an open ⚖️ decision.

---

## 0. How to read this plan

Every task has the same six parts:

| Part | Meaning |
|---|---|
| **Why** | The problem, with the file and line where it lives |
| **Steps** | What will be done, in order |
| **Files touched** | So the AI log can cite them exactly |
| **Risks** | What could break, and how it is prevented |
| **Done when** | A checklist. The task is not done until every box is ticked |
| **Size** | Rough effort |

### 0.1 Ground rules for every task

1. **One task = one commit** (or a small series), pushed only when the full test
   suite is green. Commit messages say which task number they implement.
2. **Red first for any behaviour change.** A test that fails on the current code
   is written and committed *before* the fix, so the fix is proven.
3. **Pure refactors change no behaviour.** They must pass the unchanged test
   suite *and* the golden-master check (Task 0.2) with identical results.
4. **Both translation catalogs change together** (`i18n_errors.py` and
   `i18n.js`); `tests/test_i18n_sync.py` must pass.
5. **Docs follow code in the same commit.** If a task changes what the user
   sees, the matching section of `HUONG_DAN_SU_DUNG.md` (and `README.md`
   where relevant) is updated in that commit.
6. **AI log entry per task** (see §7). Required by Phụ lục 1: AI-written code
   must be cited.
7. **No task widens its own scope.** Anything found along the way goes into
   §8 "Found during work", not into the current commit.

### 0.2 Global definition of done (applies to every task, on top of its own list)

- [ ] `python -m pytest tests/ -q` passes, **including the browser tests**
      (Playwright + Chromium under `xvfb-run -a`), with zero new skips.
- [ ] Golden-master check (Task 0.2) shows identical results, unless the task
      is explicitly allowed to change results (only Task 1.1 is).
- [ ] `git diff` re-read once end to end, looking for leftovers, debug prints,
      and accidental edits outside the files listed for the task.
- [ ] AI-log entry written (§7).
- [ ] Pushed to `claude/program-design-review-oxjnp1`.

---

## Phase 0 — Safety net (before touching anything)

### Task 0.1 — Record the baseline

**Why.** Every later claim of "nothing broke" needs a number to compare to.
The review ran only the non-browser tests (649 passed, 2 skipped, 44 s).

**Steps.**
1. Build a clean `.venv` from `requirements-dev.txt`.
2. Run the full suite, browser tests included, under `xvfb-run -a`.
3. Write the counts (passed / skipped / failed / duration) into §9 of this file.

**Files touched.** This file only.

**Done when.**
- [ ] Full-suite counts recorded in §9.
- [ ] If anything fails on the untouched code, it is recorded in §8 and
      reported to Truong **before** Phase 1 starts.

**Size.** 15 minutes.

### Task 0.2 — Golden-master test for results

**Why.** Phases 2–4 restructure code that produces the allocation. The existing
tests check properties (stability, capacity, etc.); they do not check that *the
exact same student lands in the exact same club*. A refactor could change
results while still passing every property test.

**Steps.**
1. New file `tests/test_ket_qua_khong_doi.py`.
2. For each sample dataset — `du_lieu_test/bo_sach`, `bo_can_bang`,
   `bo_nhieu_buoi`, `bo_sau_buoi`, `vi_du_huong_dan`, `mau_csv/vi_du_day_du`
   — import the three files into a fresh DB, run the pipeline with seed 42,
   read `match_results` sorted by `(student_id, buoi)`, and hash it.
3. Store the expected hashes as constants in the test, with a comment saying
   which commit produced them.
4. The test fails if any hash changes. A task that is *allowed* to change
   results (only 1.1, and only if Truong picks option A or B there) must update
   the hash in the same commit and say why in the commit message.

**Files touched.** `tests/test_ket_qua_khong_doi.py` (new).

**Risks.** None to the product; test-only.

**Done when.**
- [ ] The test passes on untouched code.
- [ ] Deliberately changing one line of `compute_club_priority` (locally, not
      committed) makes it fail — proves it actually guards something.

**Size.** 1 hour.

---

## Phase 1 — Must do now

### Task 1.1 — Make the seed consistent with the lottery lock ⚖️

**Why.**
The lottery lock (`stb_lock`) protects `students.stb_number`. Redrawing it
needs a two-step confirmation (`force_redraw_stb`). But in a school with more
than one session, each session's priority order is derived from the locked
numbers **plus the `seed`** (`sinh_stb_theo_buoi`,
`rbda_priority_pipeline.py:707`), and the seed box (`index.html:116`) is freely
editable.

Measured on `bo_nhieu_buoi`: run with seed 42 (lottery locks), then run the
full week with seed 43 without redrawing → **22 of 800 result rows change**.
The only confirmation shown is the generic "this will overwrite results" bar.

**This is documented, not hidden:** `HUONG_DAN_SU_DUNG.md:295-299` tells
operators to change the seed by running the full week. `run_history` also
records the seed, so it is auditable. The problem is an **inconsistency**:
two actions with the same effect on published results (redraw vs. seed change)
have different protection levels.

Also: `get_pipeline_run_warning` already returns `last_run_seed`
(`api.py:520`), but `app.js:434` never uses it.

Single-session schools are not affected by the seed while locked (the
single-session path short-circuits at `rbda_priority_pipeline.py:~740`),
except that the seed also drives where *newly added* students are inserted
into the locked lottery (`chen_stb_cho_hoc_sinh_moi`, `api.py:~919`).

**⚖️ Decision needed from Truong — pick one:**

| Option | What it does | Result for the user |
|---|---|---|
| **A (recommended)** | The seed is locked together with the lottery. Changing it requires the same two-step "redraw" confirmation. | One rule: "locked means locked". Simplest to explain to judges. |
| **B** | The seed stays editable, but a changed seed triggers its own two-step confirmation that names the old and new seed. | More flexible, but two different confirmations for one idea. |
| **C** | No code change; only the docs are made clearer. | Cheapest; the inconsistency remains. |

The steps below are for **Option A**. B differs only in steps 3 and 5.

**Steps (Option A).**
1. **Red test first.** New file `tests/test_khoa_hat_giong.py`:
   - full-week run with seed 42 → locked;
   - full-week run with seed 43, no redraw → expect `ok: False` with error code
     `hat_giong_da_khoa` and params `{cu: 42, moi: 43}`;
   - `match_results` unchanged after the rejected run;
   - `run_history` has no row for the rejected run;
   - same seed again → succeeds;
   - seed 43 **with** `force_redraw_stb=True` → succeeds and the lock now
     stores 43;
   - single-session data: same rules apply (one rule for everyone);
   - supplementing new students while locked uses the **locked** seed, not the
     typed one.
   Commit this test alone; it must fail on the current code.
2. **Schema.** Add `seed INTEGER` to `stb_lock` in `DEFAULT_SCHEMA`
   (`rbda_priority_pipeline.py:1265`). In `di_tru_schema`
   (`rbda_priority_pipeline.py:1304`) add the column if missing, then
   **backfill**: if `is_locked = 1` and `seed IS NULL`, copy `run_meta.seed`
   (the seed that produced the results currently in the DB). If there is no
   `run_meta` row, leave `NULL`.
3. **`run_pipeline`** (`api.py:681`):
   - when locking (the redraw branch, `api.py:~860`), also write `seed` into
     `stb_lock`;
   - when locked and not redrawing: if `stb_lock.seed` is `NULL` (legacy DB),
     adopt the typed seed and store it; otherwise if it differs from the typed
     seed, return `_fail(err("hat_giong_da_khoa", cu=..., moi=...))` **before**
     any write;
   - keep the existing partial-run seed check (`api.py:~829`) in place and in
     front, so its existing tests keep their expected error code;
   - `chen_stb_cho_hoc_sinh_moi` receives the locked seed.
4. **Read paths.** `get_stb_lock_status` and `get_pipeline_run_warning` also
   return the locked seed. `get_so_boc_tham_theo_buoi` (`api.py:~2920`) reads
   the seed from `stb_lock`, falling back to `run_meta` for legacy rows.
5. **UI** (`app.js`, `index.html`):
   - when locked, the seed box shows the locked seed and is read-only, with a
     short line under it: "Locked together with the lottery numbers. To change
     it, use Redraw.";
   - arming the Redraw button unlocks the box;
   - unlocked state: box behaves exactly as today.
6. **Translations.** New error `hat_giong_da_khoa` and the new UI strings, in
   both `i18n_errors.py` and `i18n.js`, Vietnamese and English.
7. **Existing tests.** Some tests call `run_pipeline` with a different seed
   after the lottery is locked (candidates: `test_api.py`,
   `test_data_durability.py`, `test_du_lieu_ket_qua.py`,
   `test_pipeline_core.py`, `test_nhieu_buoi.py`,
   `test_giao_dien_danh_sach_clb.py`). For each one that now fails, decide
   individually:
   - if the seed change was incidental → use the same seed;
   - if the test is *about* a seed change → add `force_redraw_stb=True`.
   **Never weaken an assertion** to make a test pass. Each changed test is
   listed in the commit message with the reason.
8. **Docs.** Rewrite `HUONG_DAN_SU_DUNG.md:295-302` (the "don't change the
   seed" warning) and the seed paragraph near line 383 to the new rule. Update
   the lock section in `README.md`. Check `CO_CHE_THUAT_TOAN.md` and
   `GIAI_DAP_BOC_THAM.md` for statements about the seed and fix any that become
   false. Their `.html` copies are hand-maintained (no generator script
   exists), so matching edits go into the `.html` files too.

**Files touched.** `rbda_priority_pipeline.py`, `api.py`, `app.js`,
`index.html`, `i18n.js`, `i18n_errors.py`, `tests/test_khoa_hat_giong.py`
(new), the existing tests from step 7, `HUONG_DAN_SU_DUNG.md`, `README.md`,
possibly `CO_CHE_THUAT_TOAN.md/.html`, `GIAI_DAP_BOC_THAM.md/.html`.

**Risks.**
- *Existing school DBs.* A DB that is already locked has no stored seed.
  → Backfill from `run_meta` (step 2); tested with a DB built by the current
  code, then opened by the new code.
- *Operators blocked mid-season.* → The error message names the locked seed,
  so they can type it back in one step.
- *Golden master.* Option A does **not** change results for seed 42, so the
  hashes must stay identical.

**Done when.**
- [ ] `tests/test_khoa_hat_giong.py` was committed failing, and now passes.
- [ ] Re-running the review experiment (42 then 43, full week, no redraw) is
      **rejected**, and 0 rows change.
- [ ] A DB created by the pre-change code, locked with seed 42, opens with the
      new code, gets `stb_lock.seed = 42` from the backfill, and runs with seed
      42 without error.
- [ ] In the real app window (checked with Playwright): when locked, the seed
      box shows the locked seed and cannot be edited; arming Redraw makes it
      editable.
- [ ] The error message is correct in both Vietnamese and English.
- [ ] Every existing test changed in step 7 is listed in the commit message
      with its reason; no assertion was removed or loosened.
- [ ] No sentence in `HUONG_DAN_SU_DUNG.md`, `README.md`,
      `CO_CHE_THUAT_TOAN.*` or `GIAI_DAP_BOC_THAM.*` still says the seed can be
      changed freely while locked.
- [ ] Global DoD (§0.2).

**Size.** 2–3 hours, mostly step 7 and the docs.

### Task 1.2 — Bring `BAN_GIAO.md` up to date

**Why.** It is the file every new session reads first, and it is stale:
- names the repo as `nguyenphanvantruong6969-arch/truong`, folder
  `rbda-kiosk/` (actual repo: `nguyenphanvantruong6969-arch/rbda-kiosk`, root);
- names an old branch (`claude/project-testing-development-zf9ajs`);
- says 483 tests (the non-browser tests alone are now 649);
- gives old line counts (`i18n.js` 830, `i18n_errors.py` 415, `browser_host.py` 237);
- says "last updated 06/09/2026".

**Steps.**
1. Correct every fact above against the live repository.
2. Add a short "Design review 27/09/2026" entry pointing to this plan.
3. Remove exact line counts (they go stale every commit); keep file roles.

**Files touched.** `BAN_GIAO.md`.

**Done when.**
- [ ] Repo name, branch, test count and date match reality at the commit.
- [ ] No line counts remain.
- [ ] Every file path mentioned in `BAN_GIAO.md` exists (checked by script).

**Size.** 30 minutes.

---

## Phase 2 — Structure of the API layer

**Constraint for the whole phase:** the public surface of `PipelineAPI` must
not change. Three things depend on it by name:
1. pywebview exposes every public method of the object passed as `js_api`
   (`main.py`), and `app.js` calls them by name;
2. `browser_host.py` dispatches `/__api__/<name>` to public methods by name;
3. 27 files (tests and scripts) import `PipelineAPI`, and tests call three private methods
   directly: `_backup_db` (5×), `_set_window` (2×), `_ket_noi_ghi` (1×).

So `PipelineAPI` stays as a **facade** with the same method names and
signatures; bodies move out.

### Task 2.1 — Split `run_pipeline` into step functions

**Why.** `run_pipeline` is 492 lines (`api.py:681-1173`) in one function:
validation, lottery draw/lock, matching, sanity + stability checks, result
writing with three separate delete sweeps, run log, CSV export and three
different exit paths. It is the most important function in the program and
the hardest to read.

**Steps.**
1. Keep one connection and one transaction exactly as now — this is the
   property that must survive.
2. Extract, as private methods or functions that receive the open cursor and
   return values (no hidden commits):
   - `_kiem_tra_dau_vao(...)` — steps 1–2 and the partial-run guards;
   - `_buoc_boc_tham(cur, ...)` — step 3, returns `(stb_lottery, stb_redrawn, detail)`;
   - `_buoc_xep(...)` — step 4, matching + sanity + stability, returns result or problems;
   - `_buoc_ghi_ket_qua(cur, result)` — step 5, the three delete sweeps + insert;
   - `_buoc_ghi_nhat_ky(cur, ...)` — `run_meta` + `run_history`;
   - `_buoc_xuat(...)` — step 6, after commit.
3. `run_pipeline` becomes the orchestrator (target: under 80 lines) that owns
   the connection, the `commit`, the `rollback` and the `steps_log`.
4. Move the long incident comments that explain *why a sweep exists* next to
   the sweep they explain; move the *history* part of them to the commit
   message (see Task 3.5).

**Files touched.** `api.py`.

**Risks.** Breaking the single-transaction guarantee.
→ Existing tests in `test_data_durability.py` cover mid-run crashes; the
DoD adds one explicit check.

**Done when.**
- [ ] `run_pipeline` is under 80 lines; no step function is over 120.
- [ ] Only `run_pipeline` calls `commit()` / `rollback()`; `grep` proves no
      step function does.
- [ ] A test forces an exception inside each step function in turn (via
      monkeypatch) and asserts the DB is byte-for-byte unchanged afterwards
      (lottery numbers, lock, results, run_history).
- [ ] Golden master identical. Global DoD.

**Size.** Half a day.

### Task 2.2 — Break `api.py` into modules behind the facade

**Why.** `api.py` is 4,111 lines with 81 methods in one class. Importers,
reports, export, health checks and pipeline orchestration are unrelated jobs.

**Target layout** (new package `kiosk/`, so the root stops growing):

| New module | Moves there | Approx. current lines |
|---|---|---|
| `kiosk/nhap_lieu.py` | `_parse_csv_rows`, `xlsx_to_csv_text`, `detect_csv_kind`, `import_csv_auto`, `import_clubs_csv`, `preview_import_csv`, `import_preferences_csv`, `import_test_selection_csv`, the `_soat_*` checks, reserve-group normalisation | `api.py:1196-2272` |
| `kiosk/cham_diem.py` | `get_scoring_overview`, `get_club_applicants_for_scoring`, `submit_club_scores` | `2273-2394` |
| `kiosk/ket_qua.py` | `get_match_results`, `get_club_fill_stats`, `get_tai_theo_buoi`, `get_thoi_khoa_bieu`, `get_do_phu`, `get_danh_sach_clb`, `get_phan_bo_nguyen_vong`, `get_em_chua_co_cho`, `get_suat_du_tru`, `get_so_boc_tham_theo_buoi`, `get_danh_sach_buoi` | `2395-2987` |
| `kiosk/xuat_tep.py` | `export_csv`, `_xuat_excel`, `_bang_tong_hop`, `_ten_file_an_toan`, `_xuat_match_results_csv` | `2988-3556`, `648-680` |
| `kiosk/quan_tri.py` | club / student / reserve-group admin, kiosk entry, `reset_data` | `3557-4111` |
| `kiosk/suc_khoe.py` | `check_data_integrity`, `get_data_health_report` | `279-496` |
| `kiosk/chay_xep.py` | `run_pipeline` + its step functions (from 2.1), `_backup_db`, run history/lock status | `497-1173` |
| `kiosk/csdl.py` | `_ket_noi_doc`, `_ket_noi_ghi` | `565-614` |

`api.py` keeps `PipelineAPI` with every public method as a one-line delegate,
plus the three private methods tests use.

**Steps.**
1. Move **one module per commit**, in the order of the table (least coupled
   first). Full suite + golden master after each.
2. Each module gets plain functions taking `db_path` (or a cursor) — no class
   hierarchy, no framework.
3. Add `kiosk/` to `kiosk.spec` (PyInstaller) and verify the Windows bundle
   check in `.github/workflows/build-windows-exe.yml` still lists every file
   the `.exe` needs.
4. Add a test that compares the list of public `PipelineAPI` method names to a
   frozen list, so the facade cannot silently lose a method.

**Files touched.** `api.py`, new `kiosk/*.py`, `kiosk.spec`, possibly the
workflow file, `README.md` (structure section), `BAN_GIAO.md` (code map).

**Risks.**
- *Windows build misses the new package.* → Step 3, and one manual run of the
  build workflow before the phase is called done.
- *pywebview exposes new public helpers by accident.* → Helpers live in
  modules, not on the class; the frozen-name test catches additions too.

**Done when.**
- [ ] `api.py` under 600 lines, and no new module over 1,000.
- [ ] Public method names of `PipelineAPI` identical to before (frozen-list test).
- [ ] `app.js` and `browser_host.py` unchanged by this task.
- [ ] Windows build workflow run once, green, and the `.exe` starts
      (Truong confirms on a Windows machine — Claude cannot run the `.exe`).
- [ ] `README.md` and `BAN_GIAO.md` code maps describe the new layout.
- [ ] Golden master identical. Global DoD.

**Size.** 1–2 days (8 small commits).

---

## Phase 3 — Model and codebase clarity

### Task 3.1 — Separate the two meanings of `applicants` ⚖️

**Why.** `load_from_sqlite` (`rbda_priority_pipeline.py:~1450`) merges "ticked
to take the test" with "listed this club in preferences" into one
`applicants` dict. After that point the two cannot be told apart, which is why
`validate_data_integrity` cannot check the 5-test limit and has a long comment
explaining why (`rbda_priority_pipeline.py:~1010`).

**⚖️ Decision:** this changes the algorithm's input contract, which is part of
the research write-up (Tier 1 / Tier 2 description). Truong confirms the
change is acceptable for the report before it starts.

**Steps.**
1. `load_from_sqlite` returns `dang_ky_thi` (ticks only) and computes
   `applicants` = ticks ∪ preferences explicitly, in one named helper.
2. `validate_data_integrity` gains the per-session 5-test check using
   `dang_ky_thi`; the duplicate checks at import stay (early feedback).
3. `run_rbda` keeps receiving `applicants` — the algorithm itself does not
   change.

**Files touched.** `rbda_priority_pipeline.py`, callers in `api.py`/`kiosk/`,
tests that unpack `load_from_sqlite`'s return value (about 29 import statements across
tests and scripts; the exact set is found with `grep` at the start of the task).

**Done when.**
- [ ] `load_from_sqlite` returns both concepts, clearly named.
- [ ] A DB with 6 test ticks in one session (inserted directly with SQL, which
      bypasses import) is now rejected by `validate_data_integrity`.
- [ ] Golden master identical. Global DoD.

**Size.** Half a day.

### Task 3.2 — One source of truth for translations

**Why.** Error messages exist twice (`i18n_errors.py`, `i18n.js`); a test
(`tests/test_i18n_sync.py`) catches drift, but every change is double work.

**Steps.**
1. Move the error catalog to `i18n/loi.json`.
2. `i18n_errors.py` loads it; `i18n.js` gets it through one generated file
   `i18n_loi.js` (a small script `tao_i18n_js.py` writes it), because the page
   must work offline without fetching JSON from disk.
3. `test_i18n_sync.py` becomes: "generated file is up to date with the JSON".
4. Add the JSON and the generated JS to `kiosk.spec` and the workflow's bundle
   check.

**Files touched.** `i18n_errors.py`, `i18n.js`, new `i18n/loi.json`,
new `i18n_loi.js`, new `tao_i18n_js.py`, `index.html`, `recovery.html`,
`kiosk.spec`, workflow, `tests/test_i18n_sync.py`.

**Done when.**
- [ ] Adding one error means editing exactly one file plus running one script.
- [ ] Every message renders identically to before in both languages
      (browser test compares a sample of 20 codes before/after).
- [ ] `.exe` bundle check lists the new files. Global DoD.

**Size.** Half a day.

### Task 3.3 — Move research-only code out of the production module

**Why.** `rbda_priority_pipeline.py` contains code the app never runs:
`stb_tuan` / `stb_co_bu` modes (measured and rejected in TN7),
`seed_sample_data`, and measurement helpers. It makes the production path
harder to read and defend.

**Steps.**
1. Create `nghien_cuu/` with `che_do_boc_tham_doi_chung.py` (the two rejected
   modes) and `du_lieu_mau.py` (`seed_sample_data`).
2. Production `sinh_stb_theo_buoi` supports only `stb_ngay`; the research
   module wraps it to add the other two for `du_lieu_test/do_boc_tham.py`.
3. **Keep the ability to re-read old runs** whose `run_meta.che_do_boc_tham`
   is `stb_tuan`: `get_so_boc_tham_theo_buoi` imports the research module for
   that one case, and a test covers it.
4. Re-run `du_lieu_test/do_boc_tham.py` and confirm `so_lieu_boc_tham.json` is
   reproduced exactly — the published TN7 numbers must not move.

**Done when.**
- [ ] Production module has no code path for `stb_tuan` / `stb_co_bu` except
      the documented legacy re-read.
- [ ] `so_lieu_boc_tham.json` reproduced byte-identical.
- [ ] Golden master identical. Global DoD.

**Size.** Half a day.

### Task 3.4 — Repository layout ⚖️

**Why.** The root mixes app code, `.md` + `.html` copies of the same
documents, `.docx` survey files, `.exe.config`, logos and build scripts.
`du_lieu_test/` mixes test fixtures with experiment scripts.

**⚖️ Decision:** some documents may already be linked from the research
report or sent to judges (e.g. `CO_CHE_THUAT_TOAN.html`,
`GIAI_DAP_BOC_THAM.html`). Moving them breaks those links. Truong lists which
paths must not move.

**Proposed layout.**
```
/            main.py, api.py, rbda_priority_pipeline.py, requirements*.txt,
             kiosk.spec, build_windows.bat, README.md, BAN_GIAO.md
kiosk/       (from Task 2.2)
giao_dien/   index.html, app.js, style.css, i18n*.js, recovery.*, assets/, logo.*
tai_lieu/    all .md/.html documents, .docx survey files
nghien_cuu/  (from Task 3.3) + experiment scripts now in du_lieu_test/
du_lieu_test/ fixtures only
tests/
```

**Steps.** One `git mv` commit (history preserved), then one commit fixing
paths in: `main.py` (UI path), `browser_host.py`, `kiosk.spec`, the workflow's
bundle check, tests that open fixture/doc files, and links inside documents.

**Done when.**
- [ ] App starts from source (`python main.py`) and in browser-fallback mode.
- [ ] Windows build workflow green; `.exe` starts (Truong confirms).
- [ ] A script finds no broken relative link in any `.md`/`.html` document.
- [ ] Global DoD.

**Size.** Half a day.

### Task 3.5 — Comments and naming

**Why.** Many comments are incident logs ("measured 6/10 students changed…",
"this used to…"). Docstrings are often longer than the code. Some comments are
Vietnamese without diacritics (schema, `app.js`, parts of `api.py`), others
with. Function names mix Vietnamese and English.

**Rules to apply.**
1. A comment keeps the **why** and the **invariant**. The **history** (what
   was wrong before, how it was measured) moves to `BAN_GIAO.md` or stays in
   git history — nothing is lost.
2. All comments use Vietnamese **with** diacritics.
3. Naming: new names follow one rule — ⚖️ Truong chooses Vietnamese or
   English. **Existing public API names are not renamed** (the UI and tests
   depend on them); only private helpers are.

**Done when.**
- [ ] No comment in the three core files describes a past bug without also
      stating the current rule.
- [ ] No diacritic-free Vietnamese comment remains (checked by a small script).
- [ ] `git diff --stat` shows only comment/docstring/private-name changes;
      golden master identical. Global DoD.

**Size.** 1 day, low risk, can be done file by file at any time.

---

## Phase 4 — Database constraints (last, highest risk)

### Task 4.1 — Add foreign keys and CHECK constraints ⚖️

**Why.** The schema has no `FOREIGN KEY` and no `CHECK`
(`rbda_priority_pipeline.py:1173-1270`). Integrity depends entirely on Python
validation. `match_results`' primary key already shows the right pattern.

**Constraints to add.**
- `clubs`: `CHECK (capacity > 0)`, `CHECK (reserve_capacity BETWEEN 0 AND capacity)`.
- `club_test_selection`, `club_scores`, `preferences`, `match_results`:
  `FOREIGN KEY (student_id) REFERENCES students ON DELETE CASCADE`,
  `FOREIGN KEY (club_id) REFERENCES clubs` (with the delete behaviour matching
  what `delete_club` does today).
- `preferences`: `CHECK (rank >= 1)`.
- `club_scores`: range check ⚖️ — Truong confirms the valid score range (the
  current code does not enforce one).
- `PRAGMA foreign_keys = ON` in `connect_db`.

**Why last.** SQLite cannot add constraints to existing tables. Every table
must be rebuilt and copied, and **a school's existing data that violates a new
rule would stop the upgrade**.

**Steps.**
1. Write a pre-flight check that lists every row in a DB that would violate the
   new constraints, without changing anything.
2. Migration in `di_tru_schema`: backup first (existing `_backup_db`), then for
   each table: create new → copy → drop old → rename, all in one transaction.
   **`run_history` is never rebuilt** (audit trail; only columns may be added,
   as today).
3. If the pre-flight finds violations: do not migrate, open the app normally,
   and show the list in the data health panel so the operator can fix them.
4. Update `delete_student` / `delete_club` / `reset_data` to rely on
   `ON DELETE` where that is equivalent, and keep explicit code where it is not.

**Done when.**
- [ ] Every sample DB and `du_lieu_test/app_DEMO_da_cham_diem.db` migrates
      cleanly; row counts identical before/after for every table.
- [ ] A DB with a deliberate orphan row is **not** migrated, the app still
      opens, and the orphan is listed in the health panel.
- [ ] Killing the process in the middle of the migration (test with
      monkeypatch) leaves the original DB intact.
- [ ] Inserting an orphan preference directly with SQL now fails.
- [ ] Golden master identical. Global DoD.

**Size.** 1 day.

---

## 5. Order and total effort

| Order | Task | Size | Needs decision first |
|---|---|---|---|
| 1 | 0.1 Baseline | 15 min | — |
| 2 | 0.2 Golden master | 1 h | — |
| 3 | 1.1 Seed and lock | 2–3 h | ⚖️ Option A/B/C |
| 4 | 1.2 `BAN_GIAO.md` | 30 min | — |
| 5 | 2.1 Split `run_pipeline` | ½ day | — |
| 6 | 2.2 Split `api.py` | 1–2 days | — |
| 7 | 3.1 `applicants` | ½ day | ⚖️ report impact |
| 8 | 3.2 Translations | ½ day | — |
| 9 | 3.3 Research code | ½ day | — |
| 10 | 3.4 Layout | ½ day | ⚖️ paths that must not move |
| 11 | 3.5 Comments/naming | 1 day | ⚖️ naming language |
| 12 | 4.1 DB constraints | 1 day | ⚖️ score range |

**Total:** Phase 0–1 ≈ half a day. Phase 2 ≈ 2 days. Phase 3 ≈ 3 days.
Phase 4 ≈ 1 day. **All of it ≈ 6–7 working days.**

Each phase is independently useful. Stopping after any phase leaves the
program in a consistent, fully tested state.

---

## 6. Out of scope (deliberately not in this plan)

- Changing the matching algorithm, the tier rules, or the lottery design.
- A frontend framework or rewriting `app.js` (splitting it per tab could be a
  later Task 3.6 if wanted).
- Anything in the research report, survey, or conclusions (Phụ lục 1 forbids AI
  writing those).
- Performance work — no measured problem exists.

---

## 7. AI-log entry template (one per task)

```
Task:        <number and name>
Date:        <dd/mm/yyyy>
Prompt:      <Truong's instruction, verbatim>
AI-written:  <files and functions created or changed>
Student-written code affected: <functions in api.py / rbda_priority_pipeline.py
             / app.js / main.py that were modified or moved, and how>
Tests:       <new tests; existing tests changed and why>
Verified by: <test counts, golden master result>
Commit:      <hash>
```

The *Student-written code affected* line matters most in Phase 2 and 3, because
`BAN_GIAO.md` §3 lists `api.py`, `rbda_priority_pipeline.py`, `main.py`,
`index.html`, `style.css`, `app.js` as written by the student.

---

## 8. Found during work

1. **`delete_club` leaked its connection on failure** (pre-existing). A failed
   delete left the write lock held, so the next save reported "database is
   locked". The new foreign keys made that failure reachable; fixed in 4.1 by
   using `_ket_noi_ghi` and deleting child rows first.
2. **Negative reserve seats were accepted** by the club form and club CSV
   import (pre-existing). Now a clear error / skipped row (4.1).
3. **`seed_sample_data` deleted parents before children** — found by the code
   review of this branch; broke on a second run once foreign keys were on.
   Fixed in `1c30b69`.
4. **A SQL comment inside a `CREATE TABLE`** made SQLite's `DROP COLUMN` fail;
   moved above the table (1.1).

## 9. Baseline numbers

| Run | Passed | Skipped | Failed | Duration |
|---|---|---|---|---|
| Non-browser, review day (27/09) | 649 | 2 | 0 | 44 s |
| Full suite incl. browser, before any change (Task 0.1) | 757 | 0 | 0 | 3 min 24 s |
| Full suite incl. browser, after 0.2 + 1.1 + 3.1 + 4.1 + 3.2 | 816 | 0 | 0 | 3 min 32 s |

## 10. Execution status (27/09/2026)

| Task | Status | Commits |
|---|---|---|
| 0.1 Baseline | ✅ Done | — (numbers in §9) |
| 0.2 Golden master | ✅ Done | `1c4297b` |
| 1.1 Seed and lock (Option A) | ✅ Done | `25c4a5f` (red), `5ad9bfc` |
| 3.1 `applicants` | ✅ Done | `dbcd021` (red), `15b3655` |
| 4.1 DB constraints | ✅ Done | `7e92d29`, `1c30b69` |
| 3.2 Translations | ✅ Done | `8407ec5` |
| 1.2 `BAN_GIAO.md` | ✅ Done | (this commit) |
| 2.1, 2.2, 3.3, 3.4, 3.5 | Not started | — |

**Where the implementation differs from the plan above, and why:**

- **1.1** — `get_so_boc_tham_theo_buoi` still reads `run_meta.seed`. Under the
  new rule the locked seed always equals the seed of the run that produced the
  results, so switching sources would change nothing.
- **3.1** — implemented as a **data-health warning**, not a validation error
  that blocks the run: the 5-test cap is school policy and the result is still
  valid. `load_from_sqlite` keeps its return value (≈29 callers); the merge
  moved into the named helper `hop_ung_vien`. No change to the algorithm's
  input, so nothing in the research write-up is affected.
- **4.1** — score rule is `score >= 0` only (the rule the app already had; no
  upper bound, schools may score out of 10 or 100). If the upgrade itself fails,
  it rolls back and the app carries on with the old schema instead of opening
  the recovery screen.
- **3.2** — the source stays the Python dict in `i18n_errors.py` (no separate
  JSON file); `tao_i18n_js.py` generates `i18n_loi.js`. The staleness test is
  pure Python, so it no longer skips on machines without Node.js.

## 11. AI-log entries for the executed tasks

Per Phụ lục 1, all code below was written by AI (Claude) at Truong's request.
Instruction (verbatim): *"Solve and tackle the first 4 problems mentioned in the
table. define as done is when all 4 problems is tackled. Recheck if it actually
solve the mistake if it actually improve user experience and does not corrupt
or damage the codebase in anyway"*.

| Task | AI-written (new) | Student-written code modified |
|---|---|---|
| 0.2 | `tests/test_ket_qua_khong_doi.py` | — |
| 1.1 | `tests/test_khoa_hat_giong.py`, `tests/test_giao_dien_khoa_hat_giong.py` | `rbda_priority_pipeline.py`: `DEFAULT_SCHEMA` (`stb_lock.seed`), `di_tru_schema` · `api.py`: `run_pipeline` (seed check, seed stored on lock), `get_stb_lock_status`, `get_pipeline_run_warning` · `app.js`: `refreshStbLockLine`, `promptForceRedraw`, new `capNhatOHatGiong`/`datVeLai` · `index.html`, `style.css` (hint line, read-only style) |
| 3.1 | `tests/test_thi_qua_tran_sau_doi_buoi.py` | `rbda_priority_pipeline.py`: new `hop_ung_vien`, `load_from_sqlite`, comment in `validate_data_integrity` · `api.py`: `get_data_health_report` (check 6b) |
| 4.1 | `tests/test_rang_buoc_csdl.py` | `rbda_priority_pipeline.py`: `_BANG_RANG_BUOC`, `DEFAULT_SCHEMA`, `connect_db`, new `soat_vi_pham_rang_buoc`/`_dung_lai_bang_co_rang_buoc`, `di_tru_schema`, `seed_sample_data` · `api.py`: `delete_club`, `create_or_update_club`, `import_clubs_csv`, `get_data_health_report` (check 6c) |
| 3.2 | `tao_i18n_js.py`, `i18n_loi.js` (generated), `tests/test_giao_dien_bang_loi.py` | `index.html` (script tag) · `kiosk.spec` |

AI-written files also changed: `i18n.js`, `i18n_errors.py` (new messages; the
JS copy of the error catalog removed), `recovery.html`, the build workflow,
`README.md`, `HUONG_DAN_SU_DUNG.md`, and five existing test files (each change
explained in its commit message; no assertion loosened).
