# Changelog

All notable changes to this project are recorded here.

## [Unreleased]

### Added
- T0: project setup (spec copy in `docs/SPEC.md`, package skeleton, smoke test, `requirements-dev.txt`).
- T1: grading tables and functions (`grading.py`): four tables, `normalize_grade`, `grade_points`, `is_passing`, with parametrized tests.
- T2: models and validation (`models.py`): `Course`, `Semester`, `Student`, `CourseStatus` and `ValidationError`; lock rule, uniqueness checks, validation of existing data on construction, and failed operations that leave data unchanged.
- Implementation guide (`docs/IMPLEMENTATION_GUIDE.md`) and spec clarifications from T2 (name trimming, credit integers, grade normalization).
