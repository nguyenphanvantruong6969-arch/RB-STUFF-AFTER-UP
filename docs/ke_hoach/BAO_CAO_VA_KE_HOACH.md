# RB-DA generalisation — package report + staged action plan

## Context
Truong uploaded `goi_cho_claude_code.zip`: a hand-off package for turning the student-research
club-allocation kiosk (RB-DA = student-proposing Deferred Acceptance + soft reserves + single
tie-breaking lottery) into a product for 12 other industries, and for adding real-time change
handling (late arrivals, withdrawals). The package was written by reading bytecode of the built
`.exe`, **without** the repo's `tests/` or `docs/`. This plan (1) reports what the package says,
(2) records what a preliminary cross-check against this repo already shows, and (3) lays out
stages. Decisions taken: **no target industry yet (common core first)**; **first run = Stage 0 only**.

---

## Part 1 — What the package contains (all 11 files read)

| File | Content |
|---|---|
| `CLAUDE.md` | Session rules: project summary, code map, commands, **8 invariants**, work rules, academic-integrity rules, 12 industry codes, reading order |
| `docs/ke_hoach/BOI_CANH_DU_AN.md` | Full background: mechanism, owner goals, 6 prior analyses, findings, measurements, theory, VN legal notes (Law 91/2025/QH15), per-industry notes, **7 open questions**, glossary |
| `docs/ke_hoach/SO_DANG_KY_33_MUC.md` | Registry of 33 change items (Z1–Z7 common; A1–A12 algorithm; B1–B3 data; C1–C3 I/O; E1–E3 ops/security; G1–G5 real-time), each with file/lines/function/current state/change/risk/acceptance/deps/R-O-– per industry; per-industry ordered plans |
| `docs/ke_hoach/ke_hoach_thay_doi.json` | Same registry machine-readable + effort weights (S1/M2/L4/XL8) + measurements |
| `docs/ke_hoach/TIEN_DO.md` | Empty progress table |
| `tham_khao/de_xuat_verify_nhanh.py` | Proposed O(log n) bisect replacement for `verify_stability` (Z4) — valid only for the current 2-pass choice function |
| `tham_khao/kiem_verify_nhanh.py` | Equivalence + timing check: fast vs original verify on 7 configs |
| `tham_khao/exp_resume.py` | Prototype: resume DA from saved state after late arrivals (G1) vs full re-run |
| `PROMPT_BAT_DAU.md` | Kick-off prompt: Stage 0 (read & measure only), then stop |
| `PROMPT_DAY_DU.md` | Pure concatenation of CLAUDE.md + context + registry (verified by line diff: nothing unique) |
| `HUONG_DAN_DAT_TEP.md` | How to drop files into repo root; do not overwrite an existing CLAUDE.md |

### Key claims in the package
- Core DA (`run_rbda`, `club_choice_function`) is reusable; what changes per industry is the
  surroundings: priority function, tie-break rule, eligibility, schema, import/export, and how
  instability is handled.
- **Biggest bottleneck:** `verify_stability` (≈20× `run_rbda` at 10k students: 22.4 s vs 1.08 s);
  proposed fast version gives identical blocking-pair lists on 7 configs, 22.4 s → 0.09 s.
- `max_rounds=1000` is only ≈4.4× the worst observed (227 rounds); docstring claim "rounds = longest
  list" is false. Provable bound = sum of preference-list lengths.
- Late arrivals **do** change earlier students' outcomes (e.g. 20 late → ~41 changed, ~10 lose a seat,
  never better). Resume-from-state reproduces full re-run exactly (38/38) but is only 1.8–3.9× faster.
- Knapsack-type capacity (LG, TC) breaks substitutability → no stability guarantee, but the pipeline
  rolls back on any blocking pair (A12).
- Effort ranking (industry-specific R items only): DT 10 · KTX 20 · SK 22.5 · NT 23.5 · YT 26 · VL 28 ·
  KT 29 · HP 29.5 · TS 37 · NS 37 · LG 44 · TC 50.5. Not-to-sell: national university admission,
  financial trading/lending, instant dispatch.
- Common order: `Z6 → Z3 → Z7 → Z4 → Z5 → Z2 → Z1 → …` (full 33-item order in CLAUDE.md).

### 8 invariants that every stage must keep
1. Default config ⇒ byte-identical `match_results` (3 datasets × 20 seeds).
2. `compute_club_priority` never reads preference rank or prior-session outcome.
3. STB: locked after first run, crc32-seeded, late arrivals inserted uniformly preserving old order.
4. `run_history` append-only.
5. Pipeline order: backup → validate → lock seed/STB → solve → sanity/verify → write in ONE transaction → export; rollback on error.
6. UI↔backend contract `{ok, data, errors:[{code, params}]}`; single error source `i18n_errors.py → tao_i18n_js.py`.
7. CSV column contract only changes when an item says so; `di_tru_schema` idempotent with backup.
8. New choice functions must pass substitutability + law-of-aggregate-demand tests, else flagged "không bảo đảm ổn định".

---

## Part 2 — Preliminary cross-check against this repo (already done, read-only)

Repo = single commit `0e4d774 Import snapshot of rbda-kiosk (main @ 52981bb)`, branch `claude/upbeat-ride-vsdibu`.

| Area | Package says | Repo reality | Verdict |
|---|---|---|---|
| `rbda_priority_pipeline.py` | ~2,187 lines; fn lines L91, 96, 123, 218, 236, 300, 315, 456, 605, 649, 683, 757, 877, 988, 1016, 1086, 1112, 1416, 1568, 1709, 1723, 1756, 1961, 2128 | 2,187 lines, **all identical**; call sites L357/L404/L511 identical | ✅ exact |
| Schema "L1251–1290" | `DEFAULT_SCHEMA` | Constraint tables live in `_BANG_RANG_BUOC` (L1251); `DEFAULT_SCHEMA` starts L1290 | ⚠ name the dict too (B1, B2, Z1) |
| `api.py` | ~1,316 lines; `_run_pipeline_da_khoa` L744–1316; reserve fn L1041; solve L1046; rollback L1052–1071 | 1,364 lines; **L784–1364 (~581 lines)**; L1089; L1094; L1107–1118 | ⚠ drift +40–48 (Z3, Z7, A12, G1, G4) |
| `api_nhap.py` | import_csv_auto L240–320; clubs L339; prefs L814–994; test_sel L996 | 1,424 lines; **L483, L565, L1041, L1226** + new `import_so_nhap` (L364), `xem_truoc_so_nhap` | ⚠ drift +~230; **C1 "current state" outdated** — a one-workbook Excel "Sổ nhập" (`so_nhap.py`, `so_excel.py`) now exists |
| `api_xuat.py` | get_thay_doi L468; export_dau_vao L594; _export_csv L825 | **L679, L845, L1087** | ⚠ drift +210–260 (C2, C3, G3, E3) |
| `api_quan_ly.py` | submit_prefs L430; reset_entry L495; delete_student L519; reset_data L569 | L435, L500, L524, L574 | ⚠ +5; G2 claim (delete blocked if matched) ✅ confirmed |
| `api_bao_cao.py`, `browser_host.py`, `api_cham_diem.py` | various | match (±1) | ✅ |
| Z2 constants | Python L91/96 + JS `05_quan_ly.js` L33–34 | ✅ confirmed; used in api.py, api_nhap, api_quan_ly, `04_nhap_tai_cho.js` L397/441 | ✅ |
| Tests | ~37 files, ~483 cases, ~95 s | **91 files, 1,078 `def test_`**; BAN_GIAO.md: **1,160 tests, ~3.5 min** (Playwright GUI tests incl.) | ❌ stale |
| CHANGELOG | "update CHANGELOG after each item" | **No CHANGELOG exists**; history is kept in `BAN_GIAO.md` | ❌ must decide (create `CHANGELOG.md`) |
| CLAUDE.md | drop into root | none exists → can be placed as-is | ✅ |
| `run_full_pipeline` (Z7 "forward params") | treated as a real path | Docstring: **test-only path**, refuses to run on real DB, no verify/rollback | ⚠ Z7 should not invest there |
| Z1 counts | 252 "CLB" / 231 "học sinh" in UI | ~202 / ~138 in `index.html`+`i18n.js`+`js/*` (method differs) | ⚠ re-count |

### Risks the package does not mention (found in repo config)
1. **CI will break if `tham_khao/*.py` are committed as-is.** `.github/workflows/tests.yml` runs
   `ruff check .` (rules `F` etc.); `kiem_verify_nhanh.py`/`exp_resume.py` re-import
   `struct, zlib, marshal, types` inside functions and twice-import `os` → F401/F811.
2. **Coverage floor 85 %** (`pyproject.toml`, `source=["."]`): ~200 unexecuted statements in
   `docs/ke_hoach/tham_khao/` may drag coverage under the floor. Fix: add `"docs/*"` to
   `[tool.coverage.run] omit` and `docs/ke_hoach/tham_khao` to ruff `extend-exclude`.
3. Reference scripts need **numpy**, which is not in any requirements file → install only in the
   Stage 0 venv, never as a product dependency.
4. Environment here is Python 3.13, project targets 3.11; no venv/pytest installed yet.

### Registry gaps / dependency notes to formalise in Stage 0 (task 6)
- Z7 lists Z3 as prerequisite, but Z7's change is in `run_rbda`/`verify_stability` signatures;
  only the api.py call site touches Z3 → Z7 can largely precede Z3 (keep order, but note it).
- Z4's fast verify is tied to the 2-pass choice function → Z7 must route `choice_fn` ≠ default to
  the slow verifier automatically (registry says it, but no item owns that dispatch).
- G1 depends on Z4 only for speed, not correctness.
- C1 must start from `so_nhap.py` (single source for the workbook format), not just CSV.
- A2 `nhan_het` also impacts `club_choice_function`'s `loi_suc_chua` (L271) and DB `CHECK`s, not just sanity L2128.
- `.claude/skills/` (3 skills) consume `so_nhap.py`; Z1/C1/B1 changes must keep skills working.

---

## Part 3 — Staged action plan

### Stage 0 — Install docs, read, measure (NO product-code changes) ← first run
1. **Install package into repo** (branch `claude/upbeat-ride-vsdibu`): extract to an isolated
   scratch dir, copy `CLAUDE.md`, `docs/ke_hoach/**` (incl. `tham_khao/`) into root; do not commit
   `PROMPT_*.md`/`HUONG_DAN_DAT_TEP.md` (one-off kick-off files). Add to `pyproject.toml`:
   ruff `extend-exclude += ["docs/ke_hoach/tham_khao"]`, coverage `omit += ["docs/*"]`.
   Patch CLAUDE.md "Lệnh" line: tests ≈1,160 / ~3.5 min, and point "CHANGELOG" to a new `CHANGELOG.md`.
2. **Environment**: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt numpy`;
   `playwright install` is NOT allowed — use preinstalled Chromium (`PLAYWRIGHT_BROWSERS_PATH`).
3. **Run full test suite** (`.venv/bin/python -m pytest -q -rs`, xvfb if needed) — record pass/fail/skip + duration; run `ruff check .`.
4. **Run `kiem_verify_nhanh.py <repo root>`** — record identical-list result + timings.
5. **Time-split one 5,000-student run** using `du_lieu_test/thu_tai/chay_thu_tai.py` generator:
   `run_rbda`, `sanity_check_result`, `verify_stability` separately (+ fast verify) → open question 2/4.
6. **Run `exp_resume.py`** to reconfirm G1 numbers on repo code.
7. **Write `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`** (Vietnamese): table per item ·
   function · registry line · actual line · current-state correct/wrong/different · note — all 33
   items; seed it with Part 2 above. Answer open questions §9 (1, 2, 3, 4, 6; 5 = `matching` lib
   comparison: attempt only if installable, else mark "chưa làm"; 7 = owner decision).
8. **Registry errata** section in the same file (Part 2 gaps + anything new).
9. Create `CHANGELOG.md` (entry "Giai đoạn 0") and fill `TIEN_DO.md` rows for Stage 0.
10. Commit (one commit for docs install + config, one for Stage 0 results), push
    `git push -u origin claude/upbeat-ride-vsdibu`, confirm CI green. **Stop and report.**

### Stage 1 — Common core (after Truong's approval), one item per commit, test-first
`Z6 → Z3 → Z7 → Z4 → Z5 → Z2 → Z1`
- **Z6** golden-output harness: `tests/test_trung_khit_mac_dinh.py` snapshots `match_results` for
  3 datasets (`bo_sach`, `bo_nhieu_buoi`, `bo_can_bang`) × 20 seeds via the real
  `PipelineAPI.run_pipeline`; plus generic substitutability/LAD property test helper
  (`tests/kiem_ham_lua_chon.py`) applied to `club_choice_function`. Reuse `TestTrungKhit`
  (`tests/test_nhieu_buoi.py`) patterns.
- **Z3** split `_run_pipeline_da_khoa` (api.py L784–1364) into ordered steps
  (validate → prepare/lock → solve → check → persist → export) over a context object, hooks
  before/after solve; same single transaction; rollback tests must still pass.
- **Z7** add `priority_fn`, `choice_fn`, `eligible_fn` params (defaults = current) to `run_rbda`,
  `verify_stability`, `run_rbda_nhieu_buoi`, `verify_stability_tuan`; registry by name; api.py L1089.
- **Z4** add `verify_stability_nhanh` from `tham_khao/de_xuat_verify_nhanh.py`; use it only when
  `choice_fn is club_choice_function`; keep slow path; equivalence test on swapped results.
- **Z5** default bound = Σ len(prefs) (≥ old 1000 kept as floor), docstring fix, cascade test.
- **Z2** one config source; backend sends limits to UI at startup; JS L33–34 read from it.
- **Z1** vocabulary pack in UI/messages/exports only (SQL names stay `club_id`/`student_id`).
- Gate per item: new test red→green, full suite + ruff + coverage ≥85 %, Z6 golden test identical,
  `CHANGELOG.md` + `TIEN_DO.md` row.

### Stage 2 — First industry pilot (choose after Stage 1)
Suggested: DT (B2 → A3 → A7, SPA) to prove the plug-in architecture cheaply, or NT
(B2, A3, A4, A6, A9, E3, G1–G3) to serve the real-time goal. Order = `nganh[].ke_hoach` in JSON.

### Stage 3 — Real-time track (G1 → G2 → G3 → G4); G5 out of scope
### Stage 4 — Data/compliance/ops per sold industry (B1, B3, C1–C3, E1–E3; E3 needs legal review)

---

## Critical files
- Read-only in Stage 0: `rbda_priority_pipeline.py`, `api.py`, `api_*.py`, `so_nhap.py`, `tests/`, `du_lieu_test/thu_tai/chay_thu_tai.py`, `BAN_GIAO.md`, `docs/CO_CHE_THUAT_TOAN.md`, `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`
- Created/edited in Stage 0: `CLAUDE.md`, `docs/ke_hoach/*` (+ new `DOI_CHIEU_KHO_MA.md`), `CHANGELOG.md`, `pyproject.toml` (lint/coverage excludes only)

## Verification (Stage 0)
- `ruff check .` clean and `pytest -q --cov` ≥ 85 % after adding the docs (proves excludes work).
- Test-suite numbers recorded verbatim with duration; skipped tests listed.
- `kiem_verify_nhanh.py` prints `TAT_CA_GIONG_NHAU True` (or the mismatch is reported as-is).
- `git diff --stat` shows no change to any product `.py`/`.js`/`.html` file.
- CI run on the pushed branch is green.
