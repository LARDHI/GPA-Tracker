from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from .grading import grade_points, is_passing
from .models import Course, CourseStatus, Semester, Student


@dataclass(frozen=True) 
class SemesterStats:
    course_count: int
    graded_credits: int
    quality_points: Decimal
    gpa: Decimal | None
    completed_credits: int
    in_progress_count: int


@dataclass(frozen=True)
class CumulativeStats:
    semester_count: int
    graded_credits: int
    quality_points: Decimal
    cgpa: Decimal | None
    completed_credits: int


def round_half_up(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def quality_points(course: Course, scale: str, system: str) -> Decimal:
    if course.status == CourseStatus.IN_PROGRESS:
        raise ValueError("Cannot calculate quality points for an in-progress course")

    return Decimal(grade_points(course.grade, scale, system) * course.credits)


def semester_stats(semester: Semester, scale: str, system: str) -> SemesterStats:
    course_count = 0
    in_progress_count = 0
    graded_credits = 0
    completed_credits = 0
    total_quality_points = Decimal("0")

    for course in semester.courses:
        course_count += 1

        if course.status == CourseStatus.IN_PROGRESS:
            in_progress_count += 1
            continue

        total_quality_points += quality_points(course, scale, system)
        graded_credits += course.credits

        if is_passing(course.grade, scale, system):
            completed_credits += course.credits

    gpa = (total_quality_points / graded_credits if graded_credits > 0 else None)

    return SemesterStats(
        course_count=course_count,
        graded_credits=graded_credits,
        quality_points=total_quality_points,
        gpa=gpa,
        completed_credits=completed_credits,
        in_progress_count=in_progress_count,
    )


def cumulative_stats(student: Student) -> CumulativeStats:
    semester_count = len(student.semesters)
    total_quality_points = Decimal("0")
    total_graded_credits = 0
    total_completed_credits = 0

    for semester in student.semesters:
        stats = semester_stats(semester, student.scale, student.system)
        total_quality_points += stats.quality_points
        total_graded_credits += stats.graded_credits
        total_completed_credits += stats.completed_credits

    cgpa = (total_quality_points / total_graded_credits if total_graded_credits > 0 else None)

    return CumulativeStats(
        semester_count=semester_count,
        graded_credits=total_graded_credits,
        quality_points=total_quality_points,
        cgpa=cgpa,
        completed_credits=total_completed_credits,
    )


def best_and_lowest(student: Student) -> tuple[Semester, Semester] | None:
    best_gpa = None
    lowest_gpa = None
    best_semester = None
    lowest_semester = None
    
    for semester in student.semesters:
        stats = semester_stats(semester, student.scale, student.system)

        if stats.gpa is None:
            continue

        if best_gpa is None or stats.gpa > best_gpa:
            best_gpa = stats.gpa
            best_semester = semester

        if lowest_gpa is None or stats.gpa < lowest_gpa:
            lowest_gpa = stats.gpa
            lowest_semester = semester

    if best_semester is None:
        return None

    return best_semester, lowest_semester
