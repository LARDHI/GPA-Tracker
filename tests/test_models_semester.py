
import pytest

from gpa_tracker.models import Semester, ValidationError


def make_semester(name="Fall 2026"):
    return Semester(name=name)


@pytest.mark.parametrize("name", ["Fall 2026", "Spring 2027", "Summer"])
def test_semester_accepts_valid_names(name):
    semester = make_semester(name=name)
    assert semester.name == name


@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_semester_rejects_blank_name(name):
    with pytest.raises(ValidationError, match="name"):
        make_semester(name=name)


@pytest.mark.parametrize("name", [123, None, True, [], b"Fall", 4.5])
def test_semester_rejects_non_string_name(name):
    with pytest.raises(ValidationError, match="name"):
        make_semester(name=name)


def test_semester_accepts_name_with_50_characters():
    name = "S" * 50
    semester = make_semester(name=name)
    assert semester.name == name


def test_semester_rejects_name_with_51_characters():
    name = "S" * 51
    with pytest.raises(ValidationError, match="50"):
        make_semester(name=name)


def test_semester_normalizes_whitespace():
    semester = make_semester(name="  Fall\t\n2026  ")
    assert semester.name == "Fall 2026"


def test_semester_preserves_letter_case():
    semester = make_semester(name="fall 2026")
    assert semester.name == "fall 2026"


def test_semester_preserves_internal_characters():
    semester = make_semester(name="Fall-2026")
    assert semester.name == "Fall-2026"


def test_semester_accepts_50_characters_with_outer_whitespace():
    name = " " + ("S" * 50) + " "
    semester = make_semester(name=name)
    assert semester.name == "S" * 50


def test_semester_accepts_raw_name_over_50_characters_if_cleaned_length_is_valid():
    name = ("S" * 30) + "     " + ("S" * 15)
    semester = make_semester(name=name)
    assert semester.name == ("S" * 30) + " " + ("S" * 15)


def test_semester_starts_with_empty_courses():
    semester = make_semester()
    assert semester.courses == []


def test_semesters_have_independent_course_lists():
    first = make_semester(name="Fall 2026")
    second = make_semester(name="Spring 2027")

    first.courses.append("placeholder")

    assert second.courses == []


def test_validation_error_is_value_error():
    assert issubclass(ValidationError, ValueError)
