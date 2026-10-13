# GPA Tracker V1: Implementation Guide

A working companion to [SPEC.md](SPEC.md). It records how each task is built, what was decided along the way, and what to watch out for. **The spec always wins.** If this guide and the spec disagree, the spec is right and this guide is wrong; fix the guide.

Labels: **Decided** = owner-approved. **Implemented** = merged code. **Proposed** = suggestion, not yet approved.

---

## 1. Working agreement

- One branch and one pull request per task, named `t<N>-<short-name>` (for example `t3-calculator`). Nothing is committed to `main` directly.
- Tasks marked **(you)** are written by the owner. Claude gives hints first and reviews, but does not hand over a full solution. Tasks marked **(delegate)** are generated, then reviewed by the owner.
- Order inside a task: **tests first, review the tests, implementation, review the implementation, pull request.**
- Each pull request description has the sections **Decided / Implemented / Proposed / Still open**, and states the task's acceptance criteria from spec section 10.
- Each task adds one line to `CHANGELOG.md` under Unreleased.
- A task is done only when its acceptance criteria are met and `pytest` passes from a clean checkout.
- Planning stays minimal. If a rule is missing from the spec, decide it, write it into the spec (and its project copy), then code it.

Running the tests:

```
python -m venv .venv
.venv\Scripts\activate          # Windows;  Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## 2. Status

| Task | Module | Who | Status |
|---|---|---|---|
| T0 | project setup | owner | Implemented (PR #1 merged) |
| T1 | `grading.py` | owner | Implemented (PR #4 merged) |
| T2 | `models.py` | owner + generated skeleton | In progress: skeleton and spec clarifications on `t2-models`; `Course` tests being written |
| T3 | `calculator.py` | owner | Not started |
| T4 | `prediction.py` | owner | Not started |
| T5 | `storage.py` | owner + generated tests | Not started |
| T6 | `prompts.py` | generated, then reviewed | Not started |
| T7 | `formatting.py` | generated, then reviewed | Not started |
| T8 | `cli.py` | owner + generated | Not started |
| T9 | verification | owner | Not started |
| T10 | release (`v1.0`) | owner | Not started |

## 3. Decision log

**Decided in the spec:** Decisions 1-11 (grading tables, calculation rules, prediction rules, persistence, CLI behaviour, explicit course status).

**Clarified during implementation (owner-approved):**

| Task | Clarification | Recorded in |
|---|---|---|
| T1 | `scale` and `system` are passed as strings: `"4.0"`/`"5.0"` and `"plus_only"`/`"plus_minus"`. Bad grade, bad configuration and non-text input all raise `ValueError`. | `grading.py` (Implemented) |
| T1 | Grade normalization removes **all** whitespace and uppercases: `" b + "` becomes `"B+"`. | `grading.py` and its tests (Implemented). **Not yet in spec section 2**, which says only "case, spaces". See section 6. |
| T2 | Semester names are compared after trimming, collapsing internal whitespace runs and ignoring case: `" Fall 2026 "` equals `"fall 2026"`, `"Fall2026"` differs. | Spec section 3 |
| T2 | Semester names are stored cleaned (trimmed, collapsed) with their capitalization kept. The 50-character limit applies to the cleaned name. | Spec section 3 |
| T2 | Course code and name are stored trimmed. The 100-character name limit applies to the trimmed name. Code uniqueness compares trimmed codes, ignoring case. | Spec section 3 |
| T2 | A course's grade is normalized and stored (`" b+ "` becomes `"B+"`). `Course` checks only type and status consistency. `Student` checks the letter exists in the active table, so `Course(grade="Z")` can exist but `add_course` rejects it. | Spec section 3 |
| T2 | Credits must be a real `int` from 1 to 9. `True`, `3.0`, `3.5` and `"3"` are rejected. | Spec section 3 |
| T2 | `Student(...)` created with existing semesters validates them with the same rules as `add_semester` and `add_course` (cleaned unique names, unique course codes per semester, grades valid in the active table) and raises `ValidationError` on bad data. Storage later loads files through this same path. | Spec section 3 |
| T2 | `ValidationError` subclasses `ValueError`. | `models.py` docstring |
| T2 | Editing a course means building a new, already-valid `Course` and calling `replace_course`. If validation fails, the original course stays unchanged and in the same position. | `models.py` docstring |
| T2 | Validation is split: `Course` and `Semester` check their own fields; `Student` checks anything needing several objects or the scale/system (uniqueness, grade in table, lock rule). | `models.py` docstring |

---

## 4. Task playbooks

### T0 and T1 (done)

Nothing to add except two lessons. A test that compares a value to itself proves nothing, so type expected values from the spec by hand. And `Decimal("3.5") == 3.5` is `True`, so a float hidden in a table passes a value test; check `isinstance(value, Decimal)` as well.

### T2: `models.py` (in progress)

**Files:** `gpa_tracker/models.py`, `tests/test_models_*.py`.
**Spec:** section 3. **Acceptance:** invalid data cannot be constructed; error messages are specific.

**Test order:**
1. `Course`: credits 1, 7, 9 accepted; 0, 10, -1, 3.0, 3.5, `True`, `"3"`, `None` rejected. Blank or non-text code and name rejected. Trimmed storage. Name length 100 accepted, 101 rejected, measured after trimming. Status/grade pairs. A string status rejected. Grade stored normalized. `""`, `"  "` and non-text grades rejected.
2. `Semester`: blank name and a 51-character cleaned name rejected.
3. `Student`, construction: invalid `semesters=[...]` is rejected (duplicate semester names, duplicate course codes in one semester, a grade not in the active table) with the same error type as `add_semester` and `add_course`; valid initial data is accepted.
4. `Student`, semesters: duplicates rejected whatever the case or spacing; stored name is the cleaned one; renaming to its own name is allowed.
5. `Student`, courses: same code twice in a semester rejected (any case, trimmed); same code in two semesters allowed; grade letter checked against the active table; `A-` rejected in Plus Only; editing is not a duplicate of itself; a failed `replace_course` leaves the original in place at the same index.
6. Lock rule: scale/system change fails while any course exists, works again after the last course is deleted, and also after deleting a semester that held the only courses.

Use `pytest.raises(ValidationError, match="credits")` so every test checks that the message names the field.

**Pitfalls:**
- `isinstance(True, int)` is `True`. Check `type(x) is int`, or reject `bool` first.
- Check the type before calling `.strip()`, or `None` raises `AttributeError` instead of `ValidationError`.
- Order inside a name check: clean first, then length, then uniqueness.
- Derive `has_courses` from the semesters' course lists. A separate flag drifts out of sync after deletes.
- `normalize_grade` raises `ValueError`; `Course` turns it into `ValidationError`.
- Put the semester and course checks in shared helpers that both `Student.__post_init__` and the `add_*` methods call, so the constructor path and the method path cannot drift apart.

### T3: `calculator.py` (Proposed shape)

**Spec:** sections 4 and 9. **Tests:** W1-W7, W10, W11. **Acceptance:** all examples pass; no float anywhere in the calculation path.

Proposed API: small pure functions plus a frozen dataclass for results, with `None` meaning "N/A" (formatting turns it into the text later):
- `quality_points(course, scale, system)`
- `semester_stats(semester, scale, system)`: course count, graded credits, quality points, GPA or `None`, completed credits, in-progress count
- `cumulative_stats(student)` and `best_and_lowest(student)`
- `round_half_up(value)`

**Pitfalls:**
- Round with `value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`. Both `round(Decimal("3.125"), 2)` and `format(Decimal("3.125"), ".2f")` give `3.12`, which is wrong (W5).
- CGPA is total quality points over total credits, never an average of semester GPAs (W4).
- F counts as attempted credits in GPA but not in completed credits (W6). In-progress courses are excluded everywhere (W7).
- Compare semesters on unrounded values. For ties, iterate in order of addition and use strict `>` / `<` so the earliest wins (W10).
- No completed courses means `None`, never a division by zero (W11).

### T4: `prediction.py` (Proposed shape)

**Spec:** section 5. **Tests:** W8, W9 plus the rules in the spec table. **Acceptance:** prediction never mutates the model.

Proposed: expected grades live in a plain dictionary (course code to letter) owned by the caller, never on the `Course`. The function returns either the predicted numbers or the list of in-progress courses still missing an expected grade.

**Pitfalls:**
- Predicted semester GPA divides by the credits of **all** courses in that semester, completed and in progress.
- Other semesters that still have in-progress courses stay excluded from the predicted CGPA.
- An expected F is not counted in predicted completed credits.
- Validate expected grades against the active table with `grading.grade_points`.
- Do not copy the model and write grades onto it. Compute from the values and leave the original untouched. A test should compare the student before and after.
- Hand-check W9: actual CGPA 20.25/6 = 3.38, predicted 30.75/9 = 3.42.

### T5: `storage.py` (Proposed shape)

**Spec:** section 6. **Acceptance:** a damaged file is never modified. **Open item:** confirm the rollback details here (section 5).

- Build the file from the spec's sketch. Turn the status enum into its string value.
- **Load by rebuilding objects through the same constructors and `Student` methods**, so every rule lives in one place and a hand-edited file cannot slip past validation.
- Every load failure (bad JSON, wrong `schema_version`, missing keys, wrong types, bad grade, status mismatch) gives one clear message and leaves the file untouched.
- Atomic write: write a temporary file **in the same folder**, then `os.replace` it over the real file. On failure delete the temporary file and keep the old one.
- On Windows, `os.replace` fails if another program has the file open; that is the "locked file" case the spec mentions.
- Open files with `encoding="utf-8"`. Create `~/.gpa_tracker/` with `mkdir(parents=True, exist_ok=True)`.
- Tests to write: round trip equality; no GPA or prediction fields in the output; each failure above; a simulated write failure (make `os.replace` raise) leaves the old file byte-identical.

### T6: `prompts.py` (generated, then reviewed)

Helpers for number, grade, yes/no and status, each looping until the input is valid or the user types `/cancel`, which returns `None`. Empty input is invalid. Tests script `builtins.input` with an iterator and check output with `capsys`. `EOFError` and `KeyboardInterrupt` are not caught here; the CLI exits cleanly on them. This module and `cli.py` are the only ones allowed to call `input()` and `print()`.

### T7: `formatting.py` (generated, then reviewed)

Pure functions that return strings and never print. Test with exact text: the "N/A" cases, the "Completed" / "In Progress" labels, and the actual-versus-predicted layout with the word "Predicted". Round with the calculator's `round_half_up`, not an f-string (see the T3 pitfall).

### T8: `cli.py` (owner + generated)

- Follow the Save rule: collect and validate all input first, then apply the change and save in one step. Cancelled or invalid operations then cannot change the file.
- A damaged file prints a clear message and exits with a non-zero code. It is never repaired.
- Make the screens testable by passing the input and output functions in, or by monkeypatching `input`. Write end-to-end scripted sessions: first run, add semesters and courses, edit in progress to completed, delete with confirmation, cancel mid-way, lock rule.
- Acceptance: cancelled and invalid operations leave the file byte-identical.
- If time runs short, cut `--file` and rename-semester first (spec time box).

### T9: verification

Build a table with one row per spec rule and the test or checklist item that proves it. Walk the manual checklist on a real Windows machine. Review all generated code against the spec. You must be able to explain every function.

### T10: release

README with install, run, data location and the known V1 limits (spec section 1, out of scope). Changelog entry, tag `v1.0`, and a final clean-clone install and run.

---

## 5. Open items

1. Check the grade tables against your university's official table (before T3 builds on the numbers).
2. Confirm that `C:\Users\<name>\.gpa_tracker\` is acceptable as the data folder.
3. Confirm the save-failure rollback details at T5. The principle is approved; the exact mechanism is not.

## 6. Housekeeping

- Spec section 2 should state that grade normalization removes all whitespace (matches the T1 code).
- `README.md` still says nothing is implemented yet.
- `CHANGELOG.md` has no T1 entry yet.
