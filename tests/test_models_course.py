
import pytest

from gpa_tracker.models import (
    Course,
    CourseStatus,
    ValidationError,
)


def make_course(
    code="CS101",
    name="Introduction to CS",
    credits=3,
    status=CourseStatus.COMPLETED,
    grade="A",
):
    return Course(
        code=code,
        name=name,
        credits=credits,
        status=status,
        grade=grade,
    )


@pytest.mark.parametrize("credits", [1, 7, 9])
def test_course_accepts_valid_credits(credits):
    course = make_course(credits=credits)

    assert course.credits == credits


@pytest.mark.parametrize(
    "credits",
    [0, 10, -1, 3.0, 4.5, True, "3", None],
)
def test_course_rejects_invalid_credits(credits):
    with pytest.raises(ValidationError, match="credits"):
        make_course(credits=credits)


@pytest.mark.parametrize(
    ("field", "value", "error_field"),
    [
        ("code", "", "code"),
        ("code", "   ", "code"),
        ("code", None, "code"),
        ("name", "", "name"),
        ("name", "   ", "name"),
        ("name", 123, "name"),
    ],
)
def test_course_rejects_blank_code_or_name(
    field, value, error_field
):
    with pytest.raises(ValidationError, match=error_field):
        make_course(**{field: value})


@pytest.mark.parametrize(
    ("name", "should_be_valid"),
    [
        ("N" * 100, True),
        ("N" * 101, False),
        (" " + "N" * 100 + " ", True),
        (" " + "N" * 101 + " ", False),
    ],
)
def test_course_validates_name_length_after_stripping(
    name, should_be_valid
):
    if should_be_valid:
        course = make_course(name=name)
        assert course.name == name.strip()
    else:
        with pytest.raises(ValidationError, match="name"):
            make_course(name=name)


@pytest.mark.parametrize(
    ("code", "name", "expected_code", "expected_name"),
    [
        (
            "  CS101  ",
            "  Introduction to CS  ",
            "CS101",
            "Introduction to CS",
        ),
        (
            "\tCS101\n",
            "\tIntroduction to CS\n",
            "CS101",
            "Introduction to CS",
        ),
    ],
)
def test_course_strips_whitespace_from_code_and_name(
    code, name, expected_code, expected_name
):
    course = make_course(code=code, name=name)

    assert course.code == expected_code
    assert course.name == expected_name


@pytest.mark.parametrize(
    ("code", "name"),
    [
        ("CS  101", "Data   Structures"),
        ("CS\t101", "Data\t\tStructures"),
    ],
)
def test_course_preserves_internal_whitespace(code, name):
    course = make_course(code=code, name=name)

    assert course.code == code
    assert course.name == name


@pytest.mark.parametrize(
    ("grade", "expected"),
    [
        (" b+ ", "B+"),
        ("f", "F"),
    ],
)
def test_course_normalizes_grade(grade, expected):
    course = make_course(grade=grade)

    assert course.grade == expected


def test_course_rejects_invalid_status():
    with pytest.raises(ValidationError, match="status"):
        make_course(status="INVALID")


@pytest.mark.parametrize(
    ("status", "grade"),
    [
        (CourseStatus.COMPLETED, None),
        (CourseStatus.IN_PROGRESS, "B"),
        (CourseStatus.IN_PROGRESS, ""),
    ],
)
def test_course_rejects_incompatible_status_and_grade(
    status, grade
):
    with pytest.raises(ValidationError, match="grade"):
        make_course(status=status, grade=grade)


def test_course_accepts_in_progress_course_without_grade():
    course = make_course(
        status=CourseStatus.IN_PROGRESS,
        grade=None,
    )

    assert course.status == CourseStatus.IN_PROGRESS
    assert course.grade is None


@pytest.mark.parametrize("grade", ["", "  ", 3.5])
def test_course_rejects_invalid_grade(grade):
    with pytest.raises(ValidationError, match="grade"):
        make_course(grade=grade)


def test_course_accepts_grade_not_in_grading_table():
    course = make_course(grade="Z")

    assert course.grade == "Z"
