"""Fixed grading tables and grade-related helpers for GPA Tracker."""

from decimal import Decimal


FOUR_POINT_PLUS_ONLY = {
    "A+": Decimal("4.00"),
    "A": Decimal("3.75"),
    "B+": Decimal("3.50"),
    "B": Decimal("3.00"),
    "C+": Decimal("2.50"),
    "C": Decimal("2.00"),
    "D+": Decimal("1.50"),
    "D": Decimal("1.00"),
    "F": Decimal("0.00"),
}

FOUR_POINT_PLUS_MINUS = {
    "A+": Decimal("4.00"),
    "A": Decimal("3.75"),
    "A-": Decimal("3.67"),
    "B+": Decimal("3.33"),
    "B": Decimal("3.00"),
    "B-": Decimal("2.67"),
    "C+": Decimal("2.33"),
    "C": Decimal("2.00"),
    "C-": Decimal("1.67"),
    "D+": Decimal("1.33"),
    "D": Decimal("1.00"),
    "D-": Decimal("0.67"),
    "F": Decimal("0.00"),
}

FIVE_POINT_PLUS_ONLY = {
    "A+": Decimal("5.00"),
    "A": Decimal("4.75"),
    "B+": Decimal("4.50"),
    "B": Decimal("4.00"),
    "C+": Decimal("3.50"),
    "C": Decimal("3.00"),
    "D+": Decimal("2.50"),
    "D": Decimal("2.00"),
    "F": Decimal("1.00"),
}

FIVE_POINT_PLUS_MINUS = {
    "A+": Decimal("5.00"),
    "A": Decimal("4.75"),
    "A-": Decimal("4.50"),
    "B+": Decimal("4.25"),
    "B": Decimal("4.00"),
    "B-": Decimal("3.75"),
    "C+": Decimal("3.50"),
    "C": Decimal("3.00"),
    "C-": Decimal("2.75"),
    "D+": Decimal("2.50"),
    "D": Decimal("2.00"),
    "D-": Decimal("1.75"),
    "F": Decimal("1.00"),
}

GRADING_TABLES = {
    ("4.0", "plus_only"): FOUR_POINT_PLUS_ONLY,
    ("4.0", "plus_minus"): FOUR_POINT_PLUS_MINUS,
    ("5.0", "plus_only"): FIVE_POINT_PLUS_ONLY,
    ("5.0", "plus_minus"): FIVE_POINT_PLUS_MINUS,
}


def normalize_grade(grade: str) -> str:
    """Normalize a grade by removing whitespace and uppercasing it.

    For example, " b + " becomes "B+". Empty or whitespace-only input
    raises ValueError.
    """
    normalized = "".join(grade.split()).upper()
    if not normalized:
        raise ValueError("Grade cannot be empty.")
    return normalized


def _get_table_and_grade(grade: str, scale: str, grading_system: str):
    """Validate the grading configuration and grade, then return both."""
    normalized_grade = normalize_grade(grade)
    try:
        table = GRADING_TABLES[(scale, grading_system)]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported grading configuration: {scale!r}, {grading_system!r}."
        ) from exc

    if normalized_grade not in table:
        raise ValueError(
            f"Grade {normalized_grade!r} is not valid for {scale} {grading_system}."
        )
    return table, normalized_grade


def grade_points(grade: str, scale: str, grading_system: str) -> Decimal:
    """Return the Decimal grade points for a valid grade and configuration."""
    table, normalized_grade = _get_table_and_grade(grade, scale, grading_system)
    return table[normalized_grade]


def is_passing(grade: str, scale: str, grading_system: str) -> bool:
    """Determine whether a valid grade passes; only F is failing."""
    _, normalized_grade = _get_table_and_grade(grade, scale, grading_system)
    return normalized_grade != "F"
