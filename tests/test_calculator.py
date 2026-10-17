import pytest

import itertools
from decimal import Decimal 
from dataclasses import FrozenInstanceError

from gpa_tracker.calculator import (
    CumulativeStats,
    SemesterStats,
    best_and_lowest,
    cumulative_stats,
    quality_points,
    round_half_up,
    semester_stats,)

from gpa_tracker.models import Course, CourseStatus, Semester, Student


_codes = itertools.count(1)


def course(grade, credits=3):
    status = (
        CourseStatus.IN_PROGRESS if grade is None
        else CourseStatus.COMPLETED)

    return Course(f"C{next(_codes)}", "Course", credits, status, grade)


def semester(name, *specs):
    return Semester(name, [course(grade, credits) for grade, credits in specs])


def student(*semesters, scale="4.0", system="plus_only"):
    return Student("Amer Lardhi", scale, system, list(semesters))


@pytest.mark.parametrize("text, excepted", [
    ("3.125", "3.13"),
    ("2.875", "2.88"),
    ("3.145", "3.15"),
    ("3.124", "3.12"),
    ("3.126", "3.13"),
    ("3.5", "3.50"),
    ("0", "0.00"),
    ("4", "4.00"),
    ("3.1249999", "3.12")])

def test_round_half_up(text, excepted):
    assert str(round_half_up(Decimal(text))) == excepted


@pytest.mark.parametrize("scale, system, grade, credits, excepted", [
    ("4.0", "plus_only", "B+", 3, "10.50"),
    ("4.0", "plus_minus", "B+", 3, "9.99"),
    ("4.0", "plus_only", "A+", 4, "16.00"),
    ("5.0", "plus_only", "A", 4, "19.00"),
    ("5.0", "plus_minus", "D-", 2, "3.50"),
    ("4.0", "plus_only", "F", 3, "0.00"),
    ("5.0", "plus_only", "F", 3, "3.00")])

def test_quality_points_values(scale, system, grade, credits, excepted):
    result = quality_points(course(grade, credits), scale, system)

    assert isinstance(result, Decimal)
    assert result == Decimal(excepted)


def test_quality_points_in_progress_raises_value_error():
    in_progress_course = course(None, 3)

    with pytest.raises(ValueError):
        quality_points(in_progress_course, "4.0", "plus_only")
    

def test_quality_points_invalid_grade_raises_value_error():
    invalid_grade_course = course("A-", 3)

    with pytest.raises(ValueError):
        quality_points(invalid_grade_course, "4.0", "plus_only")


def test_semester_stats_two_courses_and_rounding():
    sem = semester("Test Semester", ("A", 3), ("B", 4))

    stats = semester_stats(sem, "4.0", "plus_only")

    assert stats.quality_points == Decimal("23.25")
    assert stats.graded_credits == 7
    assert stats.completed_credits == 7
    assert stats.gpa == Decimal("23.25") / 7
    assert round_half_up(stats.gpa) == Decimal("3.32")


def test_semester_stats_unrounded_gpa():
    sem = semester("Test Semester", ("A", 4), ("C+", 4))

    stats = semester_stats(sem, "4.0", "plus_only")

    assert stats.quality_points == Decimal("25.00")
    assert stats.graded_credits == 8
    assert stats.completed_credits == 8
    assert stats.gpa == Decimal("25.00") / 8
    assert round_half_up(stats.gpa) == Decimal("3.13")


def test_semester_stats_f_and_a():
    sem = semester("Test Semester", ("F", 3), ("A", 3))

    stats = semester_stats(sem, "5.0", "plus_only")

    assert stats.quality_points == Decimal("17.25")
    assert stats.graded_credits == 6
    assert stats.completed_credits == 3
    assert stats.gpa == Decimal("17.25") / 6
    assert round_half_up(stats.gpa) == Decimal("2.88")


def test_semester_stats_in_progress_excluded():
    sem = semester("Test Semester", ("A", 3), (None, 3))

    stats = semester_stats(sem, "4.0", "plus_only")

    assert stats.quality_points == Decimal("11.25")
    assert stats.graded_credits == 3
    assert stats.completed_credits == 3
    assert stats.gpa == Decimal("11.25") / 3
    assert stats.course_count == 2
    assert stats.in_progress_count == 1


def test_semester_stats_empty_semester():
    sem = semester("Empty Semester")

    stats = semester_stats(sem, "4.0", "plus_only")

    assert stats.gpa is None
    assert stats.quality_points == Decimal("0")
    assert stats.course_count == 0
    assert stats.graded_credits == 0
    assert stats.completed_credits == 0
    assert stats.in_progress_count == 0


def test_semester_stats_only_in_progress_courses():
    sem = semester("Test Semester", (None, 3), (None, 4))

    stats = semester_stats(sem, "4.0", "plus_only")

    assert stats.gpa is None
    assert stats.quality_points == Decimal("0")
    assert stats.completed_credits == 0
    assert stats.in_progress_count == 2
    assert stats.course_count == 2


@pytest.mark.parametrize("scale, excepted", [
    ("4.0", Decimal("0.00")),
    ("5.0", Decimal("1.00"))])

def test_semester_stats_only_f(scale, excepted):
    sem = semester("Test Semester", ("F", 3))

    stats = semester_stats(sem, scale, "plus_only")

    assert stats.gpa == excepted
    assert stats.gpa is not None
    assert stats.completed_credits == 0


def test_semester_stats_plus_minus():
    sem = semester("Test Semester", ("B+", 3))

    stats = semester_stats(sem, "4.0", "plus_minus")

    assert stats.quality_points == Decimal("9.99")
    assert stats.gpa == Decimal("3.33")


def test_semester_stats_types():
    sem = semester("Test Semester", ("A", 3), (None, 2))

    stats = semester_stats(sem, "4.0", "plus_only")

    assert isinstance(stats.quality_points, Decimal)
    assert isinstance(stats.gpa, Decimal)
    assert type(stats.course_count) is int
    assert type(stats.graded_credits) is int
    assert type(stats.completed_credits) is int
    assert type(stats.in_progress_count) is int


def  test_semester_stats_frozen():
    sem = semester("Test Semester", ("A", 3))

    stats = semester_stats(sem, "4.0", "plus_only")

    with pytest.raises(FrozenInstanceError):
        stats.gpa = Decimal("4.00")


def test_semester_stats_does_not_mutate_courses():
    sem = semester("Test Semester", ("A", 3), ("B", 4))
    original_courses = list(sem.courses)

    semester_stats(sem, "4.0", "plus_only")

    assert len(sem.courses) == len(original_courses)
    assert all(actual is original for actual, original in zip(sem.courses, original_courses))


def test_cumulative_stats_weighted_average():
    sem1 = semester("Semester 1", ("A+", 1))
    sem2 = semester("Semester 2", ("B", 5))
    stu = student(sem1, sem2)

    stats = cumulative_stats(stu)

    assert stats.quality_points == Decimal("19.00")
    assert stats.graded_credits == 6
    assert round_half_up(stats.cgpa) == Decimal("3.17")
    assert stats.cgpa != Decimal("3.50")


def test_cumulative_stats_w9_actual():
    sem1 = semester("Semester 1", ("B", 3))
    sem2 = semester("Semester 2", ("A", 3), (None, 3))
    stu = student(sem1, sem2)

    stats = cumulative_stats(stu)

    assert stats.quality_points == Decimal("20.25")
    assert stats.graded_credits == 6
    assert round_half_up(stats.cgpa) == Decimal("3.38")
    assert stats.semester_count == 2


def test_cumulative_stats_no_semesters():
    stu = student()

    stats = cumulative_stats(stu)

    assert stats.quality_points == Decimal("0")
    assert stats.cgpa is None
    assert stats.semester_count == 0


def test_cumulative_stats_no_completed_courses():
    sem1 = semester("Empty semester")
    sem2 = semester("In Progress Semester", (None, 3))
    stu = student(sem1, sem2)

    stats = cumulative_stats(stu)

    assert stats.quality_points == Decimal("0")
    assert stats.cgpa is None
    assert stats.semester_count == 2


def test_cumulative_stats_f_does_not_count_as_completed():
    sem1 = semester("Semester 1", ("F", 3))
    sem2 = semester("Semester 2", ("A", 3))
    stu = student(sem1, sem2, scale="5.0", system="plus_only")

    stats = cumulative_stats(stu)

    assert stats.quality_points == Decimal("17.25")
    assert stats.graded_credits == 6
    assert stats.cgpa == Decimal("2.875")
    assert stats.completed_credits == 3


def test_cumulative_stats_empty_semester_changes_nothing():
    sem1 = semester("Semester 1", ("B", 3))
    sem2 = semester("Empty Semester")
    stu = student(sem1, sem2)

    stats = cumulative_stats(stu)

    assert stats.cgpa == Decimal("3.00")
    assert stats.semester_count == 2


def test_cumulative_stats_plus_minus():
    sem = semester("Semester 1", ("B+", 3))
    stu = student(sem, scale="4.0", system="plus_minus")

    stats = cumulative_stats(stu)

    assert stats.quality_points == Decimal("9.99")
    assert stats.cgpa == Decimal("3.33")


def test_cumulative_stats_types_and_no_mutation():
    sem1 = semester("Semester 1", ("A", 3))
    sem2 = semester("Semester 2", ("B", 4))
    stu = student(sem1, sem2)
    original_semesters = list(stu.semesters)

    stats = cumulative_stats(stu)

    assert isinstance(stats.quality_points, Decimal)
    assert isinstance(stats.cgpa, Decimal)
    assert type(stats.semester_count) is int
    assert type(stats.graded_credits) is int
    assert type(stats.completed_credits) is int
    assert all(
        actual is original
        for actual, original in zip(stu.semesters, original_semesters)
    )


def test_best_and_lowest_three_semesters():
    sem1 = semester("Semester 1", ("B", 3))
    sem2 = semester("Semester 2", ("A+", 3))
    sem3 = semester("Semester 3", ("C", 3))
    stu = student(sem1, sem2, sem3)

    best, lowest = best_and_lowest(stu)

    assert best is sem2
    assert lowest is sem3


def test_best_and_lowest_w10_tie():
    sem1 = semester("Semester 1", ("A", 3))
    sem2 = semester("Semester 2", ("A", 1))
    stu = student(sem1, sem2)

    best, lowest = best_and_lowest(stu)

    assert best is sem1
    assert lowest is sem1


def test_best_and_lowest_tied_best():
    sem1 = semester("Semester 1", ("B", 3))
    sem2 = semester("Semester 2", ("A+", 3))
    sem3 = semester("Semester 3", ("A+", 1))
    stu = student(sem1, sem2, sem3)

    best, lowest = best_and_lowest(stu)

    assert best is sem2
    assert lowest is sem1


def test_best_and_lowest_tied_lowest():
    sem1 = semester("Semester 1", ("A+", 3))
    sem2 = semester("Semester 2", ("C", 3))
    sem3 = semester("Semester 3", ("C", 1))
    stu = student(sem1, sem2, sem3)

    best, lowest = best_and_lowest(stu)

    assert best is sem1
    assert lowest is sem2


def test_best_and_lowest_unrounded_gpa():
    sem_x = semester("Semester X", ("A+", 3), ("A", 4), ("A", 3))
    sem_y = semester("Semester Y", ("A+", 4), ("B+", 1), ("B", 1))
    stu = student(sem_x, sem_y)

    best, lowest = best_and_lowest(stu)

    assert best is sem_x
    assert lowest is sem_y


def test_best_and_lowest_unrounded_gpa_reversed():
    sem_y = semester("Semester Y", ("A+", 4), ("B+", 1), ("B", 1))
    sem_x = semester( "Semester X", ("A+", 3), ("A", 4), ("A", 3))
    stu = student(sem_y, sem_x)

    best, lowest = best_and_lowest(stu)

    assert best is sem_x
    assert lowest is sem_y


def test_best_and_lowest_skips_unrankable_semesters():
    sem1 = semester("Empty Semester")
    sem2 = semester("Graded Semester", ("B", 3))
    sem3 = semester("In Progress Semester", (None, 3))
    stu = student(sem1, sem2, sem3)

    best, lowest = best_and_lowest(stu)

    assert best is sem2
    assert lowest is sem2


def test_best_and_lowest_includes_f_only_semester():
    sem1 = semester("Semester 1", ("B", 3))
    sem2 = semester("Semester 2", ("F", 3))
    stu = student(sem1, sem2)

    best, lowest = best_and_lowest(stu)

    assert best is sem1
    assert lowest is sem2


def test_best_and_lowest_no_semesters():
    stu = student()

    assert best_and_lowest(stu) is None


def test_best_and_lowest_no_rankable_semesters():
    sem1 = semester("Empty Semester")
    sem2 = semester("In Progress Semester", (None, 3))
    stu = student(sem1, sem2)

    assert best_and_lowest(stu) is None


def test_best_and_lowest_single_semester():
    sem1 = semester("Only Semester", ("A", 3))
    stu = student(sem1)

    best, lowest = best_and_lowest(stu)

    assert best is sem1
    assert lowest is sem1


def test_best_and_lowest_does_not_reorder_semesters():
    sem1 = semester("Semester 1", ("B", 3))
    sem2 = semester("Semester 2", ("A+", 3))
    sem3 = semester("Semester 3", ("C", 3))
    stu = student(sem1, sem2, sem3)
    original_order = list(stu.semesters)

    best_and_lowest(stu)

    assert all(
        actual is original
        for actual, original in zip(stu.semesters, original_order)
    )