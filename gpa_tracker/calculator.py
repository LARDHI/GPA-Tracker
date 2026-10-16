from dataclasses import dataclass
from decimal import Decimal

from .grading import grade_points, is_passing
from .models import Course, CourseStatus, Semester, Student


@dataclass(frozen=True) 
class SemesterStatus:
    course_count: int
    graded_credits: int
    quality_points: Decimal
    gpa: Decimal | None
    completed_credits: int
    in_progress_count: int


@dataclass(frozen=True)
class CumulativeStatus:
    semester_count: int
    graded_credits: int
    quality_points: Decimal
    cgpa: Decimal | None
    completed_credits: int


def round_half_up(value: Decimal) -> Decimal:
    raise NotImplementedError


def quality_points(course: Course, scale: str, system: str) -> Decimal:
    raise NotImplementedError


def semester_status(semester: Semester, scale: str, system: str) -> SemesterStatus:
    raise NotImplementedError


def cumulative_status(student: Student) -> CumulativeStatus:
    raise NotImplementedError


def best_and_lowest(student: Student) -> tuple[semester, semester] | None:
    raise NotImplementedError