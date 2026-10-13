
from decimal import Decimal

import pytest

from gpa_tracker.grading import (
    FOUR_POINT_PLUS_ONLY,
    FOUR_POINT_PLUS_MINUS,
    FIVE_POINT_PLUS_ONLY,
    FIVE_POINT_PLUS_MINUS,
    GRADING_TABLES,
    normalize_grade,
    grade_points,
    is_passing,
)


# All grading tables.
TABLES = (
    FOUR_POINT_PLUS_ONLY,
    FOUR_POINT_PLUS_MINUS,
    FIVE_POINT_PLUS_ONLY,
    FIVE_POINT_PLUS_MINUS,
)


# --------------------------------------------------
# Grading table values
# --------------------------------------------------

@pytest.mark.parametrize(
    "table, grade, expected",
    [
        # 4.0 - Plus Only
        (FOUR_POINT_PLUS_ONLY, "A+", Decimal("4.00")),
        (FOUR_POINT_PLUS_ONLY, "A", Decimal("3.75")),
        (FOUR_POINT_PLUS_ONLY, "B+", Decimal("3.50")),
        (FOUR_POINT_PLUS_ONLY, "B", Decimal("3.00")),
        (FOUR_POINT_PLUS_ONLY, "C+", Decimal("2.50")),
        (FOUR_POINT_PLUS_ONLY, "C", Decimal("2.00")),
        (FOUR_POINT_PLUS_ONLY, "D+", Decimal("1.50")),
        (FOUR_POINT_PLUS_ONLY, "D", Decimal("1.00")),
        (FOUR_POINT_PLUS_ONLY, "F", Decimal("0.00")),

        # 4.0 - Plus/Minus
        (FOUR_POINT_PLUS_MINUS, "A+", Decimal("4.00")),
        (FOUR_POINT_PLUS_MINUS, "A", Decimal("3.75")),
        (FOUR_POINT_PLUS_MINUS, "A-", Decimal("3.67")),
        (FOUR_POINT_PLUS_MINUS, "B+", Decimal("3.33")),
        (FOUR_POINT_PLUS_MINUS, "B", Decimal("3.00")),
        (FOUR_POINT_PLUS_MINUS, "B-", Decimal("2.67")),
        (FOUR_POINT_PLUS_MINUS, "C+", Decimal("2.33")),
        (FOUR_POINT_PLUS_MINUS, "C", Decimal("2.00")),
        (FOUR_POINT_PLUS_MINUS, "C-", Decimal("1.67")),
        (FOUR_POINT_PLUS_MINUS, "D+", Decimal("1.33")),
        (FOUR_POINT_PLUS_MINUS, "D", Decimal("1.00")),
        (FOUR_POINT_PLUS_MINUS, "D-", Decimal("0.67")),
        (FOUR_POINT_PLUS_MINUS, "F", Decimal("0.00")),

        # 5.0 - Plus Only
        (FIVE_POINT_PLUS_ONLY, "A+", Decimal("5.00")),
        (FIVE_POINT_PLUS_ONLY, "A", Decimal("4.75")),
        (FIVE_POINT_PLUS_ONLY, "B+", Decimal("4.50")),
        (FIVE_POINT_PLUS_ONLY, "B", Decimal("4.00")),
        (FIVE_POINT_PLUS_ONLY, "C+", Decimal("3.50")),
        (FIVE_POINT_PLUS_ONLY, "C", Decimal("3.00")),
        (FIVE_POINT_PLUS_ONLY, "D+", Decimal("2.50")),
        (FIVE_POINT_PLUS_ONLY, "D", Decimal("2.00")),
        (FIVE_POINT_PLUS_ONLY, "F", Decimal("1.00")),

        # 5.0 - Plus/Minus
        (FIVE_POINT_PLUS_MINUS, "A+", Decimal("5.00")),
        (FIVE_POINT_PLUS_MINUS, "A", Decimal("4.75")),
        (FIVE_POINT_PLUS_MINUS, "A-", Decimal("4.50")),
        (FIVE_POINT_PLUS_MINUS, "B+", Decimal("4.25")),
        (FIVE_POINT_PLUS_MINUS, "B", Decimal("4.00")),
        (FIVE_POINT_PLUS_MINUS, "B-", Decimal("3.75")),
        (FIVE_POINT_PLUS_MINUS, "C+", Decimal("3.50")),
        (FIVE_POINT_PLUS_MINUS, "C", Decimal("3.00")),
        (FIVE_POINT_PLUS_MINUS, "C-", Decimal("2.75")),
        (FIVE_POINT_PLUS_MINUS, "D+", Decimal("2.50")),
        (FIVE_POINT_PLUS_MINUS, "D", Decimal("2.00")),
        (FIVE_POINT_PLUS_MINUS, "D-", Decimal("1.75")),
        (FIVE_POINT_PLUS_MINUS, "F", Decimal("1.00")),
    ],
)
def test_table_values(table, grade, expected):
    assert table[grade] == expected


def test_all_grading_table_values_are_decimals():
    for table in TABLES:
        for grade, value in table.items():
            assert isinstance(value, Decimal), (
                f"Value for grade '{grade}' in table {table} is not a Decimal: {value}"
                f" (type: {type(value)})"
            )


@pytest.mark.parametrize(
    "table, expected_keys",
    [
        (
            FOUR_POINT_PLUS_ONLY,
            {"A+", "A", "B+", "B", "C+", "C", "D+", "D", "F"},
        ),
        (
            FOUR_POINT_PLUS_MINUS,
            {
                "A+", "A", "A-", "B+", "B", "B-",
                "C+", "C", "C-", "D+", "D", "D-", "F",
            },
        ),
        (
            FIVE_POINT_PLUS_ONLY,
            {"A+", "A", "B+", "B", "C+", "C", "D+", "D", "F"},
        ),
        (
            FIVE_POINT_PLUS_MINUS,
            {
                "A+", "A", "A-", "B+", "B", "B-",
                "C+", "C", "C-", "D+", "D", "D-", "F",
            },
        ),
    ],
)
def test_grading_table_keys(table, expected_keys):
    assert set(table) == expected_keys


# --------------------------------------------------
# Grade normalization
# --------------------------------------------------

@pytest.mark.parametrize(
    "grade, expected",
    [
        ("A+", "A+"),
        ("A", "A"),
        ("a+", "A+"),
        ("b+", "B+"),
        (" b+ ", "B+"),
        (" b + ", "B+"),
        ("  a  -  ", "A-"),
        ("f", "F"),
        ("\tB+\n", "B+"),
    ],
)
def test_normalize_grade(grade, expected):
    assert normalize_grade(grade) == expected


@pytest.mark.parametrize(
    "grade",
    ["", " ", "   ", "\t", "\n"],
)
def test_normalize_grade_empty(grade):
    with pytest.raises(ValueError):
        normalize_grade(grade)


@pytest.mark.parametrize(
    "grade",
    [None, 123, 4.0],
)
def test_normalize_grade_non_string(grade):
    with pytest.raises(ValueError):
        normalize_grade(grade)


# --------------------------------------------------
# Grade point lookup
# --------------------------------------------------

@pytest.mark.parametrize(
    "scale, grading_system, table",
    [
        ("4.0", "plus_only", FOUR_POINT_PLUS_ONLY),
        ("4.0", "plus_minus", FOUR_POINT_PLUS_MINUS),
        ("5.0", "plus_only", FIVE_POINT_PLUS_ONLY),
        ("5.0", "plus_minus", FIVE_POINT_PLUS_MINUS),
    ],
)
def test_grade_points_matches_table(scale, grading_system, table):
    for grade, expected in table.items():
        assert grade_points(
            grade, scale, grading_system
        ) == expected


@pytest.mark.parametrize(
    "grade, scale, grading_system, expected",
    [
        ("B+", "4.0", "plus_minus", Decimal("3.33")),
        ("B+", "5.0", "plus_minus", Decimal("4.25")),
        ("F", "5.0", "plus_only", Decimal("1.00")),
    ],
)
def test_grade_points_known_values(
    grade, scale, grading_system, expected
):
    assert grade_points(grade, scale, grading_system) == expected


@pytest.mark.parametrize(
    "grade, scale, grading_system",
    [
        ("A++", "4.0", "plus_only"),
        ("E", "4.0", "plus_only"),
        ("A++", "5.0", "plus_minus"),
        ("E", "5.0", "plus_minus"),
        ("A-", "4.0", "plus_only"),
        ("A-", "5.0", "plus_only"),
        ("", "4.0", "plus_minus"),
        ("  ", "5.0", "plus_only"),
    ],
)
def test_grade_points_rejects_invalid_grades(
    grade, scale, grading_system
):
    with pytest.raises(ValueError):
        grade_points(grade, scale, grading_system)


@pytest.mark.parametrize(
    "scale, grading_system",
    [
        ("6.0", "plus_only"),
        ("4.0", "invalid_system"),
        ("5.0", "plus/minus"),
    ],
)
def test_grade_points_rejects_invalid_configuration(
    scale, grading_system
):
    with pytest.raises(ValueError):
        grade_points("A+", scale, grading_system)


def test_grade_points_normalizes_input():
    assert grade_points(
        " b + ", "4.0", "plus_minus"
    ) == Decimal("3.33")


# --------------------------------------------------
# Pass/fail checks
# --------------------------------------------------

@pytest.mark.parametrize(
    "scale, grading_system, grade, expected",
    [
        (scale, system, grade, grade != "F")
        for (scale, system), table in GRADING_TABLES.items()
        for grade in table
    ],
)
def test_is_passing(scale, grading_system, grade, expected):
    assert is_passing(
        grade, scale, grading_system
    ) is expected


@pytest.mark.parametrize(
    "scale",
    ["4.0", "5.0"],
)
def test_a_minus_rejected_in_plus_only(scale):
    with pytest.raises(ValueError):
        is_passing("A-", scale, "plus_only")


def test_fails_on_f_in_all_configurations():
    for (scale, system), table in GRADING_TABLES.items():
        assert is_passing("F", scale, system) is False


def test_grade_points_returns_decimal():
    result = grade_points("B+", "4.0", "plus_minus")
    assert isinstance(result, Decimal)
