import pytest

from gpa_tracker.models import (
    Course,
    CourseStatus,
    Semester,
    Student,
    ValidationError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_student(scale="4.0", system="plus_only"):
    return Student(name="Amer Lardhi", scale=scale, system=system)


def make_course(
    code="CS101",
    name="Programming",
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


def assert_same_objects(actual, expected):
    """Assert that two sequences contain the same objects in the same order."""
    assert len(actual) == len(expected)
    assert all(a is b for a, b in zip(actual, expected))


# ===========================================================================
# A. Student construction
# ===========================================================================

@pytest.mark.parametrize(
    "name",
    ["Amer Lardhi", "A", "A" * 100],
)
def test_student_accepts_valid_names(name):
    student = Student(name=name, scale="4.0", system="plus_only")

    assert student.name == name


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        (" Amer ", "Amer"),
        ("\tAmer\n", "Amer"),
    ],
)
def test_student_trims_name(name, expected):
    student = Student(name=name, scale="4.0", system="plus_only")

    assert student.name == expected


@pytest.mark.parametrize(
    "name",
    [
        "",
        "  ",
        "\t\n",
        123,
        None,
        True,
        [],
        b"Amer",
        "A" * 101,
        " " + "A" * 101 + " ",
    ],
)
def test_student_rejects_invalid_names(name):
    with pytest.raises(ValidationError, match="name"):
        Student(name=name, scale="4.0", system="plus_only")


@pytest.mark.parametrize(
    ("scale", "system"),
    [
        ("4.0", "plus_only"),
        ("4.0", "plus_minus"),
        ("5.0", "plus_only"),
        ("5.0", "plus_minus"),
    ],
)
def test_student_accepts_valid_grading_configurations(scale, system):
    student = Student(
        name="Amer Lardhi",
        scale=scale,
        system=system,
    )

    assert student.scale == scale
    assert student.system == system


@pytest.mark.parametrize(
    ("scale", "system"),
    [
        ("3.0", "plus_only"),
        ("6.0", "plus_only"),
        ("4.0", "Plus Only"),
        ("4.0", "invalid"),
        ("4.0", ""),
        ("5.0", None),
        (4.0, "plus_only"),
        (None, "plus_only"),
    ],
)
def test_student_rejects_invalid_grading_configurations(scale, system):
    with pytest.raises(ValidationError, match="grading"):
        Student(
            name="Amer Lardhi",
            scale=scale,
            system=system,
        )


def test_student_starts_without_semesters_or_courses():
    student = make_student()

    assert student.semesters == []
    assert student.has_courses is False


# ===========================================================================
# B. set_name
# ===========================================================================

@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("New Name", "New Name"),
        ("  New Name  ", "New Name"),
    ],
)
def test_student_set_name_accepts_valid_names(name, expected):
    student = make_student()

    student.set_name(name)

    assert student.name == expected


@pytest.mark.parametrize(
    "name",
    ["", "  ", None, 123, "A" * 101],
)
def test_student_set_name_rejects_invalid_names(name):
    student = make_student()
    old_name = student.name

    with pytest.raises(ValidationError, match="name"):
        student.set_name(name)

    assert student.name == old_name


# ===========================================================================
# C. Grading configuration and locking
# ===========================================================================

def test_student_set_grading_without_semesters():
    student = make_student()

    student.set_grading("5.0", "plus_minus")

    assert student.scale == "5.0"
    assert student.system == "plus_minus"


def test_student_set_grading_with_empty_semester():
    student = make_student()
    student.add_semester("Fall 2026")

    student.set_grading("5.0", "plus_only")

    assert student.scale == "5.0"
    assert student.system == "plus_only"


@pytest.mark.parametrize(
    ("scale", "system"),
    [
        ("3.0", "plus_only"),
        ("4.0", "invalid"),
        (4.0, "plus_only"),
    ],
)
def test_student_set_grading_rejects_invalid_configurations(scale, system):
    student = make_student()
    old_scale = student.scale
    old_system = student.system

    with pytest.raises(ValidationError, match="grading"):
        student.set_grading(scale, system)

    assert student.scale == old_scale
    assert student.system == old_system


def test_student_set_grading_is_locked_when_course_exists():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    student.add_course(semester, make_course())
    old_scale = student.scale
    old_system = student.system

    with pytest.raises(ValidationError, match="locked"):
        student.set_grading("5.0", "plus_minus")

    assert student.scale == old_scale
    assert student.system == old_system


def test_student_can_change_grading_after_deleting_last_course():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    course = make_course()

    student.add_course(semester, course)
    student.delete_course(semester, course)
    student.set_grading("5.0", "plus_minus")

    assert student.scale == "5.0"
    assert student.system == "plus_minus"


def test_student_grading_remains_locked_while_course_exists():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    first_course = make_course(code="CS101")
    second_course = make_course(code="CS102", name="Data Structures")

    student.add_course(semester, first_course)
    student.add_course(semester, second_course)
    student.delete_course(semester, first_course)

    old_scale = student.scale
    old_system = student.system

    with pytest.raises(ValidationError, match="locked"):
        student.set_grading("5.0", "plus_minus")

    assert student.scale == old_scale
    assert student.system == old_system


def test_student_can_change_grading_after_deleting_semester_with_courses():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    student.add_course(semester, make_course())

    student.delete_semester(semester)
    student.set_grading("5.0", "plus_minus")

    assert student.scale == "5.0"
    assert student.system == "plus_minus"


def test_student_has_courses_reflects_course_state():
    student = make_student()

    assert student.has_courses is False

    semester = student.add_semester("Fall 2026")
    assert student.has_courses is False

    course = make_course()
    student.add_course(semester, course)
    assert student.has_courses is True

    student.delete_course(semester, course)
    assert student.has_courses is False


# ===========================================================================
# D. add_semester
# ===========================================================================

def test_student_add_semester_returns_stored_semester():
    student = make_student()

    semester = student.add_semester("Fall 2026")

    assert isinstance(semester, Semester)
    assert any(item is semester for item in student.semesters)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("  Fall   2026 ", "Fall 2026"),
        ("fall 2026", "fall 2026"),
        ("Fall\t\n2026", "Fall 2026"),
    ],
)
def test_student_add_semester_normalizes_name(name, expected):
    student = make_student()

    semester = student.add_semester(name)

    assert semester.name == expected


@pytest.mark.parametrize(
    "name",
    ["", "   ", None, 123, "S" * 51],
)
def test_student_add_semester_rejects_invalid_names(name):
    student = make_student()

    with pytest.raises(ValidationError, match="name"):
        student.add_semester(name)


@pytest.mark.parametrize(
    "name",
    [
        " fall   2026 ",
        "FALL 2026",
        "fall 2026",
    ],
)
def test_student_add_semester_rejects_duplicate_names(name):
    student = make_student()
    student.add_semester("Fall 2026")

    with pytest.raises(ValidationError, match="duplicate"):
        student.add_semester(name)


def test_student_add_semester_accepts_different_names():
    student = make_student()

    first = student.add_semester("Fall 2026")
    second = student.add_semester("Fall2026")

    assert first.name == "Fall 2026"
    assert second.name == "Fall2026"
    assert len(student.semesters) == 2


def test_student_add_duplicate_semester_leaves_list_unchanged():
    student = make_student()
    student.add_semester("Fall 2026")
    before = list(student.semesters)

    with pytest.raises(ValidationError, match="duplicate"):
        student.add_semester(" FALL   2026 ")

    assert_same_objects(student.semesters, before)


def test_student_add_semesters_preserves_insertion_order():
    student = make_student()

    first = student.add_semester("Fall 2026")
    second = student.add_semester("Spring 2027")
    third = student.add_semester("Summer 2027")

    assert_same_objects(student.semesters, [first, second, third])


# ===========================================================================
# E. rename_semester
# ===========================================================================

@pytest.mark.parametrize(
    ("new_name", "expected"),
    [
        ("  Spring   2027 ", "Spring 2027"),
        ("spring\t\n2027", "spring 2027"),
    ],
)
def test_student_rename_semester_normalizes_name(new_name, expected):
    student = make_student()
    semester = student.add_semester("Fall 2026")

    student.rename_semester(semester, new_name)

    assert semester.name == expected


@pytest.mark.parametrize(
    ("new_name", "expected"),
    [
        ("fall 2026", "fall 2026"),
        (" Fall   2026 ", "Fall 2026"),
    ],
)
def test_student_rename_semester_allows_own_name(new_name, expected):
    student = make_student()
    semester = student.add_semester("Fall 2026")

    student.rename_semester(semester, new_name)

    assert semester.name == expected


def test_student_rename_semester_rejects_duplicate_name():
    student = make_student()
    student.add_semester("Fall 2026")
    semester = student.add_semester("Spring 2027")
    old_name = semester.name

    with pytest.raises(ValidationError, match="duplicate"):
        student.rename_semester(semester, " fall   2026 ")

    assert semester.name == old_name


@pytest.mark.parametrize(
    "name",
    ["", "S" * 51, None],
)
def test_student_rename_semester_rejects_invalid_names(name):
    student = make_student()
    semester = student.add_semester("Fall 2026")
    old_name = semester.name

    with pytest.raises(ValidationError, match="name"):
        student.rename_semester(semester, name)

    assert semester.name == old_name


def test_student_rename_semester_preserves_courses_and_order():
    student = make_student()
    first = student.add_semester("Fall 2026")
    second = student.add_semester("Spring 2027")
    course = make_course(code="CS102", name="Data Structures")
    student.add_course(second, course)
    semesters_before = list(student.semesters)
    courses_before = list(second.courses)

    student.rename_semester(second, "Summer 2027")

    assert second.name == "Summer 2027"
    assert_same_objects(student.semesters, semesters_before)
    assert_same_objects(second.courses, courses_before)
    assert student.semesters[0] is first
    assert student.semesters[1] is second


def test_student_rename_semester_rejects_foreign_object():
    student = make_student()
    stored_semester = student.add_semester("Fall 2026")
    foreign_semester = Semester(name="Fall 2026")

    with pytest.raises(ValidationError, match="not found"):
        student.rename_semester(foreign_semester, "Spring 2027")

    assert stored_semester.name == "Fall 2026"
    assert_same_objects(student.semesters, [stored_semester])


# ===========================================================================
# F. delete_semester
# ===========================================================================

def test_student_delete_semester_removes_courses_and_preserves_order():
    student = make_student()
    first = student.add_semester("Fall 2026")
    second = student.add_semester("Spring 2027")
    third = student.add_semester("Summer 2027")

    course1 = make_course(code="CS101")
    course2 = make_course(code="CS102", name="Data Structures")
    student.add_course(second, course1)
    student.add_course(second, course2)

    student.delete_semester(second)

    assert_same_objects(student.semesters, [first, third])
    assert not any(item is second for item in student.semesters)


def test_student_delete_semester_rejects_foreign_object():
    student = make_student()
    stored_semester = student.add_semester("Fall 2026")
    foreign_semester = Semester(name="Fall 2026")
    before = list(student.semesters)

    with pytest.raises(ValidationError, match="not found"):
        student.delete_semester(foreign_semester)

    assert_same_objects(student.semesters, before)
    assert any(item is stored_semester for item in student.semesters)
    assert not any(item is foreign_semester for item in student.semesters)


def test_student_delete_semester_allows_reusing_name():
    student = make_student()
    original = student.add_semester("Fall 2026")

    student.delete_semester(original)
    replacement = student.add_semester("Fall 2026")

    assert_same_objects(student.semesters, [replacement])
    assert replacement.name == "Fall 2026"
    assert replacement is not original


# ===========================================================================
# G. add_course
# ===========================================================================

def test_student_add_course_appends_course():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    first_course = make_course(code="CS101")
    second_course = make_course(code="CS102", name="Data Structures")

    student.add_course(semester, first_course)
    student.add_course(semester, second_course)

    assert_same_objects(semester.courses, [first_course, second_course])


def test_student_add_course_rejects_non_course():
    student = make_student()
    semester = student.add_semester("Fall 2026")

    with pytest.raises(ValidationError, match="course"):
        student.add_course(semester, "not a course")

    assert semester.courses == []


@pytest.mark.parametrize(
    "foreign_name",
    ["Fall 2026", "Different Semester"],
)
def test_student_add_course_rejects_foreign_semester(foreign_name):
    student = make_student()
    student.add_semester("Fall 2026")
    foreign_semester = Semester(name=foreign_name)
    course = make_course()

    with pytest.raises(ValidationError, match="not found"):
        student.add_course(foreign_semester, course)

    assert foreign_semester.courses == []
    assert all(
        stored_course is not course
        for semester in student.semesters
        for stored_course in semester.courses
    )


@pytest.mark.parametrize(
    "duplicate_code",
    ["cs101", "CS101", " Cs101 "],
)
def test_student_add_course_rejects_duplicate_code(duplicate_code):
    student = make_student()
    semester = student.add_semester("Fall 2026")
    original_course = make_course(code="CS101")
    duplicate_course = make_course(
        code=duplicate_code,
        name="Different Course",
    )
    student.add_course(semester, original_course)
    before = list(semester.courses)

    with pytest.raises(ValidationError, match="duplicate"):
        student.add_course(semester, duplicate_course)

    assert_same_objects(semester.courses, before)
    assert not any(item is duplicate_course for item in semester.courses)


def test_student_add_course_allows_same_code_in_different_semesters():
    student = make_student()
    first_semester = student.add_semester("Fall 2026")
    second_semester = student.add_semester("Spring 2027")
    first_course = make_course(code="CS101")
    second_course = make_course(code="CS101", name="Programming II")

    student.add_course(first_semester, first_course)
    student.add_course(second_semester, second_course)

    assert_same_objects(first_semester.courses, [first_course])
    assert_same_objects(second_semester.courses, [second_course])


@pytest.mark.parametrize(
    ("scale", "system", "grade"),
    [
        ("4.0", "plus_only", "Z"),
        ("4.0", "plus_only", "A-"),
        ("4.0", "plus_minus", "invalid"),
        ("5.0", "plus_minus", "E"),
    ],
)
def test_student_add_course_rejects_invalid_grade(scale, system, grade):
    student = make_student(scale=scale, system=system)
    semester = student.add_semester("Fall 2026")
    course = make_course(grade=grade)
    before = list(semester.courses)

    with pytest.raises(ValidationError, match="grade"):
        student.add_course(semester, course)

    assert_same_objects(semester.courses, before)
    assert not any(item is course for item in semester.courses)


@pytest.mark.parametrize(
    ("scale", "system", "grade"),
    [
        ("4.0", "plus_minus", "A-"),
        ("5.0", "plus_minus", "D-"),
    ],
)
def test_student_add_course_accepts_valid_plus_minus_grades(
    scale,
    system,
    grade,
):
    student = make_student(scale=scale, system=system)
    semester = student.add_semester("Fall 2026")
    course = make_course(grade=grade)

    student.add_course(semester, course)

    assert_same_objects(semester.courses, [course])


def test_student_add_course_allows_in_progress_without_grade():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    course = make_course(
        code="CS201",
        name="Data Structures",
        status=CourseStatus.IN_PROGRESS,
        grade=None,
    )

    student.add_course(semester, course)

    assert_same_objects(semester.courses, [course])
    assert course.status == CourseStatus.IN_PROGRESS
    assert course.grade is None


# ===========================================================================
# H. replace_course
# ===========================================================================

def test_student_replace_course_replaces_stored_course():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    old_course = make_course(code="CS101")
    new_course = make_course(code="CS102", name="Data Structures")
    student.add_course(semester, old_course)

    student.replace_course(semester, old_course, new_course)

    assert_same_objects(semester.courses, [new_course])
    assert not any(item is old_course for item in semester.courses)


def test_student_replace_course_rejects_non_course():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    old_course = make_course()
    student.add_course(semester, old_course)

    with pytest.raises(ValidationError, match="course"):
        student.replace_course(semester, old_course, "not a course")

    assert_same_objects(semester.courses, [old_course])


def test_student_replace_course_rejects_foreign_semester():
    student = make_student()
    stored_semester = student.add_semester("Fall 2026")
    foreign_semester = Semester(name="Different Semester")
    old_course = make_course()
    new_course = make_course(code="CS102")
    student.add_course(stored_semester, old_course)

    with pytest.raises(ValidationError, match="not found"):
        student.replace_course(foreign_semester, old_course, new_course)

    assert_same_objects(stored_semester.courses, [old_course])
    assert foreign_semester.courses == []


def test_student_replace_course_rejects_course_not_in_semester():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    stored_course = make_course(code="CS101", name="Programming")
    foreign_course = make_course(code="CS101", name="Programming")
    new_course = make_course(code="CS102", name="Data Structures")
    student.add_course(semester, stored_course)

    assert foreign_course == stored_course
    assert foreign_course is not stored_course

    with pytest.raises(ValidationError, match="not found"):
        student.replace_course(semester, foreign_course, new_course)

    assert_same_objects(semester.courses, [stored_course])


def test_student_replace_course_rejects_duplicate_code():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    old_course = make_course(code="CS101")
    existing_course = make_course(code="CS102", name="Data Structures")
    duplicate_course = make_course(code="CS102", name="Database Systems")
    student.add_course(semester, old_course)
    student.add_course(semester, existing_course)
    before = list(semester.courses)

    with pytest.raises(ValidationError, match="duplicate"):
        student.replace_course(semester, old_course, duplicate_course)

    assert_same_objects(semester.courses, before)
    assert not any(item is duplicate_course for item in semester.courses)


def test_student_replace_course_allows_same_code_as_old_course():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    old_course = make_course(code="CS101", name="Old Programming Name")
    new_course = make_course(code="CS101", name="Updated Programming Name")
    student.add_course(semester, old_course)

    student.replace_course(semester, old_course, new_course)

    assert_same_objects(semester.courses, [new_course])
    assert new_course.code == old_course.code
    assert new_course.name == "Updated Programming Name"


@pytest.mark.parametrize(
    ("scale", "system", "grade"),
    [
        ("4.0", "plus_only", "A-"),
        ("4.0", "plus_minus", "Z"),
    ],
)
def test_student_replace_course_rejects_invalid_grade_without_changes(
    scale,
    system,
    grade,
):
    student = make_student(scale=scale, system=system)
    semester = student.add_semester("Fall 2026")
    old_course = make_course(code="CS101", name="Original Course")
    another_course = make_course(code="CS102", name="Another Course")
    replacement = make_course(
        code="CS103",
        name="Replacement",
        grade=grade,
    )
    student.add_course(semester, old_course)
    student.add_course(semester, another_course)
    before = list(semester.courses)
    old_values = (old_course.code, old_course.name, old_course.credits,
                  old_course.status, old_course.grade)

    with pytest.raises(ValidationError, match="grade"):
        student.replace_course(semester, old_course, replacement)

    assert_same_objects(semester.courses, before)
    assert (
        old_course.code,
        old_course.name,
        old_course.credits,
        old_course.status,
        old_course.grade,
    ) == old_values


def test_student_replace_course_replaces_in_progress_with_completed():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    old_course = make_course(
        code="CS101",
        status=CourseStatus.IN_PROGRESS,
        grade=None,
    )
    new_course = make_course(
        code="CS101",
        status=CourseStatus.COMPLETED,
        grade="A",
    )
    student.add_course(semester, old_course)

    student.replace_course(semester, old_course, new_course)

    assert_same_objects(semester.courses, [new_course])
    assert new_course.status == CourseStatus.COMPLETED
    assert new_course.grade == "A"


# ===========================================================================
# I. delete_course
# ===========================================================================

def test_student_delete_course_removes_stored_course():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    first_course = make_course(code="CS101")
    course_to_delete = make_course(code="CS102", name="Data Structures")
    last_course = make_course(code="CS103", name="Database Systems")
    student.add_course(semester, first_course)
    student.add_course(semester, course_to_delete)
    student.add_course(semester, last_course)

    student.delete_course(semester, course_to_delete)

    assert_same_objects(semester.courses, [first_course, last_course])
    assert not any(item is course_to_delete for item in semester.courses)


def test_student_delete_course_rejects_foreign_course():
    student = make_student()
    semester = student.add_semester("Fall 2026")
    stored_course = make_course(code="CS101", name="Programming")
    foreign_course = make_course(code="CS101", name="Programming")
    student.add_course(semester, stored_course)

    assert foreign_course == stored_course
    assert foreign_course is not stored_course

    with pytest.raises(ValidationError, match="not found"):
        student.delete_course(semester, foreign_course)

    assert_same_objects(semester.courses, [stored_course])


def test_student_delete_course_rejects_foreign_semester():
    student = make_student()
    stored_semester = student.add_semester("Fall 2026")
    foreign_semester = Semester(name="Fall 2026")
    stored_course = make_course(code="CS101")
    foreign_course = make_course(code="CS102")
    student.add_course(stored_semester, stored_course)
    foreign_semester.courses.append(foreign_course)

    semesters_before = list(student.semesters)
    stored_courses_before = list(stored_semester.courses)
    foreign_courses_before = list(foreign_semester.courses)

    with pytest.raises(ValidationError, match="not found"):
        student.delete_course(foreign_semester, foreign_course)

    assert_same_objects(student.semesters, semesters_before)
    assert_same_objects(stored_semester.courses, stored_courses_before)
    assert_same_objects(foreign_semester.courses, foreign_courses_before)


# ===========================================================================
# J. Initial data validation
# ===========================================================================

def test_student_accepts_initial_semesters():
    first = Semester(name="Fall 2026")
    second = Semester(name="Spring 2027")
    third = Semester(name="Summer 2027")

    student = Student(
        name="Amer Lardhi",
        scale="4.0",
        system="plus_only",
        semesters=[first, second, third],
    )

    assert_same_objects(student.semesters, [first, second, third])


def test_student_rejects_invalid_initial_semester():
    valid_semester = Semester(name="Fall 2026")

    with pytest.raises(ValidationError, match="semester"):
        Student(
            name="Amer Lardhi",
            scale="4.0",
            system="plus_only",
            semesters=[valid_semester, "not a semester"],
        )


@pytest.mark.parametrize(
    "duplicate_name",
    [
        "fall 2026",
        "FALL 2026",
        " Fall   2026 ",
        "Fall\t\n2026",
    ],
)
def test_student_rejects_duplicate_initial_semester_names(duplicate_name):
    first = Semester(name="Fall 2026")
    duplicate = Semester(name=duplicate_name)

    with pytest.raises(ValidationError, match="duplicate"):
        Student(
            name="Amer Lardhi",
            scale="4.0",
            system="plus_only",
            semesters=[first, duplicate],
        )


def test_student_accepts_initial_courses():
    first_course = make_course(code="CS101")
    second_course = make_course(code="CS102", name="Data Structures")
    third_course = make_course(code="CS103", name="Database Systems")
    semester = Semester(name="Fall 2026")
    semester.courses.extend([first_course, second_course, third_course])

    student = Student(
        name="Amer Lardhi",
        scale="4.0",
        system="plus_only",
        semesters=[semester],
    )

    assert student.semesters[0] is semester
    assert_same_objects(
        student.semesters[0].courses,
        [first_course, second_course, third_course],
    )


def test_student_rejects_invalid_initial_course():
    semester = Semester(name="Fall 2026")
    semester.courses.extend([make_course(code="CS101"), "not a course"])

    with pytest.raises(ValidationError, match="course"):
        Student(
            name="Amer Lardhi",
            scale="4.0",
            system="plus_only",
            semesters=[semester],
        )


@pytest.mark.parametrize(
    "duplicate_code",
    ["cs101", "CS101", " Cs101 "],
)
def test_student_rejects_duplicate_initial_course_codes(duplicate_code):
    first_course = make_course(code="CS101")
    duplicate_course = make_course(
        code=duplicate_code,
        name="Different Course",
    )
    semester = Semester(name="Fall 2026")
    semester.courses.extend([first_course, duplicate_course])

    with pytest.raises(ValidationError, match="duplicate"):
        Student(
            name="Amer Lardhi",
            scale="4.0",
            system="plus_only",
            semesters=[semester],
        )


@pytest.mark.parametrize(
    ("scale", "system", "grade"),
    [
        ("4.0", "plus_only", "A-"),
        ("5.0", "plus_only", "A-"),
        ("4.0", "plus_minus", "Z"),
    ],
)
def test_student_rejects_invalid_initial_course_grades(
    scale,
    system,
    grade,
):
    course = make_course(code="CS101", grade=grade)
    semester = Semester(name="Fall 2026")
    semester.courses.append(course)

    with pytest.raises(ValidationError, match="grade"):
        Student(
            name="Amer Lardhi",
            scale=scale,
            system=system,
            semesters=[semester],
        )


@pytest.mark.parametrize(
    ("scale", "system", "grade"),
    [
        ("4.0", "plus_only", "A+"),
        ("4.0", "plus_minus", "A-"),
    ],
)
def test_student_accepts_valid_initial_course_grades(
    scale,
    system,
    grade,
):
    course = make_course(code="CS101", grade=grade)
    semester = Semester(name="Fall 2026")
    semester.courses.append(course)

    student = Student(
        name="Amer Lardhi",
        scale=scale,
        system=system,
        semesters=[semester],
    )

    assert student.semesters[0] is semester
    assert_same_objects(semester.courses, [course])
