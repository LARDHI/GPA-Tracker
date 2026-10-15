# GPA Tracker

A command-line tool for students to track semesters, courses, semester GPA and cumulative GPA (CGPA), and to predict GPA from expected grades. Supports 4.0 and 5.0 scales, with Plus Only or Plus/Minus grading.

**Status:** V1 under development. Done so far: grading tables and functions (T1) and the data models with validation (T2). Not implemented yet: calculator, prediction, storage, formatting and the command-line interface (T3 onward), so there is nothing to run yet.

- Language: Python 3.x, standard library only (pytest for tests).
- Specification: [docs/SPEC.md](docs/SPEC.md) is the source of truth.

## Development setup

```
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## Install and run

Not available yet. Install and run instructions, the data file location and the known V1 limits will be added at release (task T10).
