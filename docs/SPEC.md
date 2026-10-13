# GPA Tracker V1: Specification and Implementation Plan

Status: specification approved (Decisions 1-11). Implementation not started.
Language: Python 3.x, standard library only (pytest for tests).

Labels used below: **Decided** = approved by the owner. **Proposed** = suggested, not yet approved. Everything in sections 1-9 is Decided unless marked otherwise.

---

## 1. Purpose and Scope

**Problem.** Students at universities using a 4.0 or 5.0 scale need an accurate way to track semesters, courses, semester GPA, and cumulative GPA (CGPA), and to see what their GPA would be with expected grades.

**Users.** Students from multiple universities, each using one of four predefined grading configurations.

**In scope (V1)**
- Student profile, semesters, courses (add, edit, delete).
- Semester GPA, CGPA, completed credits, best and lowest semester.
- Semester Summary and Academic Summary.
- Automatic saving to a JSON file; loading on start.
- Prediction of semester GPA and CGPA from expected grades for in-progress courses.

**Out of scope (V1)**
- Customizable grading tables.
- Target-GPA planning ("what grades do I need").
- Retake handling (a repeated course is just another entry).
- Fractional or zero credit hours.
- Converting grades between systems.
- Saving predictions or scenarios.
- GUI, web, database, multiple profiles per file, multiple languages.

---

## 2. Grading Configurations (Decided, fixed)

| Grade | 4.0 Plus Only | 4.0 Plus/Minus | 5.0 Plus Only | 5.0 Plus/Minus |
|---|---|---|---|---|
| A+ | 4.00 | 4.00 | 5.00 | 5.00 |
| A | 3.75 | 3.75 | 4.75 | 4.75 |
| A- | n/a | 3.67 | n/a | 4.50 |
| B+ | 3.50 | 3.33 | 4.50 | 4.25 |
| B | 3.00 | 3.00 | 4.00 | 4.00 |
| B- | n/a | 2.67 | n/a | 3.75 |
| C+ | 2.50 | 2.33 | 3.50 | 3.50 |
| C | 2.00 | 2.00 | 3.00 | 3.00 |
| C- | n/a | 1.67 | n/a | 2.75 |
| D+ | 1.50 | 1.33 | 2.50 | 2.50 |
| D | 1.00 | 1.00 | 2.00 | 2.00 |
| D- | n/a | 0.67 | n/a | 1.75 |
| F | 0.00 | 0.00 | 1.00 | 1.00 |

- These tables are the owner's baseline and are not verified against any university's official scale.
- **Passing:** any grade except F passes. Decided by letter, never by points (F = 1.00 on 5.0 scales).
- **F credits** count in GPA calculations (attempted credits) but not in completed credits.
- Grade input is normalized (case, spaces, "b+" becomes B+). A letter not in the active table is rejected.

---

## 3. Data Model and Validation Rules

```
Student -> Semesters (ordered) -> Courses
```

**Student:** full name, GPA scale (4.0 or 5.0), grading system (Plus Only or Plus/Minus).
- Name: non-empty after trimming, at most 100 characters. Editable at any time.
- Scale and system are chosen at creation. They are **locked only while at least one course exists**. If all courses are deleted, they can be changed again.

**Semester:** name only.
- Non-empty, at most 50 characters, unique within the profile. Free text, never parsed.
- **Uniqueness (clarified, T2):** names are compared after trimming leading and trailing whitespace, collapsing each run of internal whitespace to a single space, and ignoring case. So `" Fall 2026 "` and `"fall 2026"` are the same name, while `"Fall 2026"` and `"Fall2026"` are different.
- **Storage (clarified, T2):** the name is stored in its cleaned form (trimmed, internal whitespace collapsed) with its original capitalization kept. Entering `" Fall 2026 "` stores `"Fall 2026"`. Case is ignored only when checking uniqueness, never when storing. The 50-character limit applies to the cleaned name.
- Rename and delete are allowed. Deleting removes its courses, after explicit confirmation.
- Order is the order of addition.

**Course:** code, name, credit hours, status, grade.
- Code: non-empty, unique within its semester (ignoring case). The same code may appear in different semesters.
- Name: non-empty, at most 100 characters.
- Credit hours: whole number from 1 to 9. No per-semester limit.
- **Status: `COMPLETED` or `IN_PROGRESS`**, an explicit field.
  - `COMPLETED` requires a valid grade letter from the active table.
  - `IN_PROGRESS` has no grade. It is a registered course whose actual grade is not yet available, **not** a completed course with a missing grade.
  - A status with a mismatched grade (completed with no grade, in progress with a grade) is invalid everywhere: in the model, on load, and in the CLI.
- All course fields are editable. A course may be deleted after confirmation.
- When the real grade arrives, the user edits the course, changes the status to Completed, and enters the grade. Nothing converts automatically.

---

## 4. Calculation Rules

All arithmetic uses `decimal.Decimal`, never floats.

| Item | Rule |
|---|---|
| Quality points | grade points x credit hours |
| Semester GPA | total quality points / total credits of **completed** courses in that semester (F included as attempted) |
| CGPA | total quality points / total credits of completed courses across all semesters. Credit-weighted, never an average of semester GPAs. |
| Completed credits | credits of completed courses with a passing grade (not F) |
| In-progress courses | excluded from every actual result |
| Display | 2 decimal places, rounded half up |
| Comparisons | best/lowest semester use unrounded values |
| No completed courses in a semester | GPA is "N/A"; semester skipped for best/lowest |
| No completed courses at all | CGPA is "N/A"; no best/lowest |
| Ties | earliest semester (order of addition) wins |

**Semester Summary:** number of courses, graded credits, quality points, semester GPA, and a separate line for in-progress courses.
**Academic Summary:** number of semesters, completed credits, quality points, CGPA, best semester, lowest semester.

---

## 5. Prediction Rules

- Applies to **one semester at a time**, chosen by the user. It must contain at least one in-progress course.
- Only in-progress courses receive expected grades. Completed courses keep their real grades.
- Expected grades must be letters from the active table. They are **memory-only, never saved**, discarded on exit, and **never become actual grades automatically**.
- Every in-progress course in the chosen semester needs an expected grade. Otherwise no prediction is calculated and the missing courses are listed.
- **Predicted semester GPA** = (actual quality points of completed courses + expected quality points) / (credits of all courses in that semester).
- **Predicted CGPA** = all other semesters' actual results plus the chosen semester with expected grades, credit-weighted.
- Other semesters with in-progress courses stay excluded.
- Predicted completed credits are shown too (an expected F is not counted).
- Output shows actual and predicted values side by side, labeled "Predicted". Best/lowest are never affected.
- Editing or deleting a course in the chosen semester clears that semester's expected grades.

---

## 6. Persistence

- One JSON file, one profile per file, standard `json` module.
- Default path `~/.gpa_tracker/data.json` (via `Path.home()`), overridable with `--file PATH`.
- Stores raw facts only: profile, semesters, courses (code, name, credits, status, grade). Never GPA values, never predictions.
- Includes `"schema_version": 1`.
- Saved after every successful change, using a temporary file and `os.replace`.
- Validated on load. A damaged or invalid file produces a clear error and the program exits. **It is never overwritten or repaired automatically.**
- A failed save (disk full, locked file) is reported to the user, leaves the previous file intact, and the in-memory change is rolled back.

Sketch of the file shape (illustrative, not final):

```json
{
  "schema_version": 1,
  "student": {"name": "...", "scale": "4.0", "system": "plus_minus"},
  "semesters": [
    {"name": "Fall 2026",
     "courses": [
       {"code": "CS101", "name": "Intro", "credits": 3, "status": "completed", "grade": "B+"},
       {"code": "CS102", "name": "Data Structures", "credits": 3, "status": "in_progress", "grade": null}
     ]}
  ]
}
```

---

## 7. CLI Specification

- Plain `input()` / `print()` numbered menus. No third-party libraries, no colors, no screen clearing. English only.
- First run with no file: create profile, then main menu.
- Navigation: stay in a section until `0` (Back). `/cancel` at any prompt abandons the operation with no changes.
- Empty input is invalid and re-prompted. Invalid input gets a specific message and a re-prompt. No silent auto-correction except grade normalization.
- Items are chosen from numbered lists. Deleting requires typing `yes`.
- `Ctrl+C` or end-of-input exits cleanly (safe, since every change is already saved).

**Main menu:** 1 Summary, 2 Semesters, 3 Courses, 4 Predict GPA, 5 Profile, 0 Exit.

| Screen | Contents |
|---|---|
| Summary | Semester Summaries and the Academic Summary together |
| Semesters | list, add, rename, delete |
| Courses | choose a semester, then list, add, edit, delete |
| Predict GPA | choose a semester with in-progress courses, enter expected grades, see actual vs. predicted, stay in section to adjust |
| Profile | edit name; change scale/system only if no courses exist, otherwise explain why it is locked |

**Course prompts (clarification, Decision 11).** The add and edit prompts ask for the status explicitly before anything else about the grade:

```
Course status:
  1. Completed (final grade is known)
  2. In Progress (no final grade yet)
```

- Choosing 1 asks for the grade, and an empty grade is rejected.
- Choosing 2 skips the grade prompt entirely.
- Course lists and summaries label each course "Completed" or "In Progress".
- This replaces the earlier idea of "press Enter on an empty grade", so an in-progress course is always a deliberate choice, never an accident.

**Save rule.** A screen collects and validates all input first, then applies the change and saves in one step. Cancelled operations and invalid input therefore never modify saved data.

---

## 8. Architecture

```
gpa_tracker/
  grading.py      # four fixed tables, normalize, points lookup, is_passing
  models.py       # dataclasses, CourseStatus, validation, ValidationError
  calculator.py   # pure functions: quality points, GPA, CGPA, best/lowest, rounding
  prediction.py   # pure functions: predicted semester GPA and CGPA
  storage.py      # JSON save/load, atomic write, load validation
  prompts.py      # reusable input helpers (number, grade, yes/no, status), loop until valid or cancelled
  formatting.py   # pure functions: results to text, never prints
  cli.py          # menus and screen flow
  __main__.py     # entry point, --file argument
tests/
```

Rule: `grading`, `models`, `calculator`, `prediction`, `storage`, and `formatting` never call `input()` or `print()`.

---

## 9. Worked Examples (become acceptance tests)

| # | Setup | Expected |
|---|---|---|
| W1 | 4.0 Plus Only, B+, 3 credits | 10.50 quality points |
| W2 | 4.0 Plus/Minus, B+, 3 credits | 9.99 quality points |
| W3 | 4.0 Plus Only: A 3 cr, B 4 cr | 23.25 QP, 7 credits, GPA 3.32 |
| W4 | 4.0 Plus Only: Sem 1 = A+ 1 cr; Sem 2 = B 5 cr | CGPA 19/6 = **3.17** (not 3.50, the average of 4.00 and 3.00) |
| W5 | 4.0 Plus Only: A 4 cr, C+ 4 cr | 25/8 = 3.125, displays **3.13** (half up; Python `round` would give 3.12) |
| W6 | 5.0 Plus Only: F 3 cr, A 3 cr | QP 3.00 + 14.25 = 17.25, GPA 2.875 displays 2.88, completed credits 3 |
| W7 | 4.0 Plus Only: A 3 cr plus an in-progress 3 cr course | GPA 3.75, completed credits 3, in-progress excluded |
| W8 | W7 semester with expected B+ for the in-progress course | predicted GPA 21.75/6 = 3.625, displays **3.63** |
| W9 | Sem 1: B 3 cr; Sem 2 as W7 | actual CGPA 20.25/6 = 3.375 -> 3.38; predicted CGPA 30.75/9 -> 3.42 |
| W10 | Two semesters with equal unrounded GPA | earliest is reported as best (and as lowest) |
| W11 | Semester with no completed courses; profile with none | "N/A", no crash |

---

## 10. Implementation Plan

Principle: each task is small, ordered, and finished only when its tests pass. Do not start a task before the previous one's acceptance criteria are met. Planning stops here; code starts at T0.

Learning mode: **you write** the parts marked (you), where the learning is; AI may help with hints and review. Parts marked (delegate) can be AI-generated against approved specs, then reviewed by you.

| Task | Work | Tests | Acceptance criteria |
|---|---|---|---|
| **T0** Setup | Git repo, virtual environment, `pytest`, package skeleton, README stub, changelog | one trivial passing test | `pytest` runs from a clean clone; first commit made |
| **T1** `grading.py` (you) | Four tables as data, `normalize_grade`, `grade_points`, `is_passing` | every value in section 2 (parametrized); counts 9/13/9/13; A- rejected in Plus Only; normalization cases; only F fails | all 52 table values match section 2 exactly |
| **T2** `models.py` (you + delegate boilerplate) | Dataclasses, `CourseStatus`, validation, lock rule, uniqueness | each rule in section 3, including status/grade mismatch, credits 0/10/decimal, duplicate names/codes, lock lifts when courses are deleted | invalid data cannot be constructed; error messages are specific |
| **T3** `calculator.py` (you) | Quality points, semester stats, CGPA, completed credits, best/lowest, half-up rounding with `Decimal` | W1-W7, W10, W11 | all worked examples pass; no float used anywhere in the calculation path |
| **T4** `prediction.py` (you) | Predicted semester GPA and CGPA; missing-expected-grade detection | W8, W9; incomplete prediction returns the missing list; completed grades untouched; other in-progress semesters excluded | prediction never mutates the model |
| **T5** `storage.py` (you + delegate tests) | Save/load, atomic write, schema version, load validation, rollback on save failure | round-trip equality; no GPA or prediction fields written; corrupted JSON, wrong version, bad grade, status mismatch all give clear errors and leave the file untouched; simulated write failure keeps the old file | a damaged file is never modified |
| **T6** `prompts.py` (delegate, then review) | Helpers for number, grade, yes/no, status; `/cancel` handling | scripted input via monkeypatch: retries on invalid, cancel returns None, empty input rejected, status choice 1/2 | no prompt returns invalid data |
| **T7** `formatting.py` (delegate, then review) | Semester and Academic Summary, prediction view, course list with status labels | exact-text comparisons for N/A cases, "In Progress" label, actual vs. predicted layout | pure functions only, no printing |
| **T8** `cli.py` (you + delegate) | Menus and screens, first-run flow, damaged-file exit, `--file`, save-after-success | scripted end-to-end sessions: first run, add semester and courses, edit in-progress to completed, delete with confirmation, cancel mid-operation, lock rule | cancelled and invalid operations leave the file byte-identical |
| **T9** Verification | Full manual walkthrough of a checklist, review pass of all AI-written code against the spec | whole suite; manual checklist | every spec rule traced to a test or checklist item; you can explain every function |
| **T10** Release | README (install, run, data location, limits), changelog, tag `v1.0` | final full run | clean-clone install and run works |

**Definition of done for V1:** all tests pass, all worked examples pass, the manual checklist passes, and the README lists the known V1 limits (section 1, out of scope).

**Time box:** 3-4 weeks alongside coursework. If it overruns, cut scope (never correctness). Candidates to cut first: `--file`, rename-semester.

---

## 11. Items to Re-check Before Coding

1. The grade tables are unverified against official sources. Confirm them against your own university's published table when possible.
2. The first run creates `~/.gpa_tracker/`; confirm that location is acceptable on your Windows 11 machine (it resolves to `C:\Users\<name>\.gpa_tracker\`).
3. Rollback behavior on save failure (section 6) is proposed in detail but only the principle was approved; confirm during T5.

## 12. Deferred to V2 or Later

Customizable grading tables, target-GPA planning, retake policies, SQLite, saved scenarios, fractional credits, GUI or web interface, multiple profiles, per-course passing rules.
