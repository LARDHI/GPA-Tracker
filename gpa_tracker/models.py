"""Dataclasses, CourseStatus, validation and ValidationError. (T2)"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from gpa_tracker.grading import GRADING_TABLES, normalize_grade


class ValidationError(ValueError):
    """Raised when data breaks a rule from spec section 3."""


def _key(text: str) -> str:
    """Return a case-insensitive comarison key."""
    return text.casefold()


class CourseStatus(Enum):
    """A course is either finished with a known grade, or still running."""

    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"


@dataclass
class Course:
    """One course. Checks here need nothing but the course's own fields."""

    code: str
    name: str
    credits: int
    status: CourseStatus
    grade: str | None = None

        
    def __post_init__(self) -> None:
        if not isinstance(self.code, str):
            raise ValidationError("Course code must be a string.")

        if not isinstance(self.name, str):
            raise ValidationError("Course name must be a string.")

        code = self.code.strip()
        name = self.name.strip()

        if not code:
            raise ValidationError("Course code cannot be empty.")

        if not name:
            raise ValidationError("Course name cannot be empty.")

        if len(name) > 100:
            raise ValidationError("Course name cannot exceed 100 characters.")

        if isinstance(self.credits, bool) or not isinstance(self.credits, int):
            raise ValidationError("Course credits must be an integer.")

        if not 1 <= self.credits <= 9:
            raise ValidationError("Course credits must be between 1 and 9.")

        if not isinstance(self.status, CourseStatus):
            raise ValidationError("Course status must be COMPLETED or IN_PROGRESS.")

        if self.grade is not None:
            try:
                grade = normalize_grade(self.grade)
            except ValueError as exc:
                raise ValidationError(f"Invalid course grade: {exc}") from exc
        else:
            grade = None

        if self.status == CourseStatus.COMPLETED and grade is None:
            raise ValidationError("A completed course must have a grade.")

        if self.status == CourseStatus.IN_PROGRESS and grade is not None:
            raise ValidationError("An in-progress course cannot have a grade.")

        self.code = code
        self.name = name
        self.grade = grade  


@dataclass
class Semester:
    """A named list of courses, in order of addition."""

    name: str
    courses: list[Course] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise ValidationError("Semester name must be a string.")

        if not isinstance(self.courses, list):
            raise ValidationError("Semester courses must be a list.")

        name = " ".join(self.name.split())

        if not name:
            raise ValidationError("Semester name cannot be empty.")

        if len(name) > 50:
            raise ValidationError("Semester name cannot exceed 50 characters.")

        self.name = name


def _clean_name(name: str) -> str:
    if not isinstance(name, str):
        raise ValidationError("name must be a string.")

    name = name.strip()

    if not name:
        raise ValidationError("name cannot be empty.")

    if len(name) > 100:
        raise ValidationError("name cannot exceed 100 characters.")

    return name


@dataclass
class Student:
    """The profile: name, scale, grading system, and ordered semesters."""

    name: str
    scale: str  # "4.0" or "5.0"
    system: str  # "plus_only" or "plus_minus"
    semesters: list[Semester] = field(default_factory=list)

    def _check_config(self, scale: str, system: str) -> None:
        try:
            valid = (scale, system) in GRADING_TABLES
        except TypeError:
            valid = False

        if not valid:
            raise ValidationError("Invalid grading configuration.")

    def _find_semester(self, semester: Semester) -> Semester:
        for item in self.semesters:
            if item is semester:
                return item

        raise ValidationError("Semester not found.")

    def _find_course_index(self, semester: Semester, course: Course) -> int:
        for index, item in enumerate(semester.courses):
            if item is course:
                return index

        raise ValidationError("Course not found.")


    def _check_course(self, semester: Semester, course: Course, ignore: Course | None = None) -> None:
        if not isinstance(course, Course):
            raise ValidationError("Item is not a course object.")

        if course.status is CourseStatus.COMPLETED:
            table = GRADING_TABLES[(self.scale, self.system)]
            if course.grade not in table:
                raise ValidationError("Course grade is invalid for this grading configuration.")

        course_key = _key(course.code)

        for item in semester.courses:
            if item is ignore:
                continue

            if _key(item.code) == course_key:
                raise ValidationError("Course code is a duplicate.")

    def __post_init__(self) -> None:
        self.name = _clean_name(self.name)
        self._check_config(self.scale, self.system)

        semester_names = set()

        for semester in self.semesters:
            if not isinstance(semester, Semester):
                raise ValidationError("Item is not a semester object.")

            name_key = _key(semester.name)
            if name_key in semester_names:
                raise ValidationError("Semester name is a duplicate.")

            semester_names.add(name_key)

            course_codes = set()
            table = GRADING_TABLES[(self.scale, self.system)]

            for course in semester.courses:
                if not isinstance(course, Course):
                    raise ValidationError("Item is not a course object.")

                if (
                    course.status is CourseStatus.COMPLETED
                    and course.grade not in table):

                    raise ValidationError("Course grade is invalid.")

                code_key = _key(course.code)
                if code_key in course_codes:
                    raise ValidationError("Course code is a duplicate.")

                course_codes.add(code_key)

    @property
    def has_courses(self) -> bool:
        """True while at least one course exists in any semester."""
        return any(semester.courses for semester in self.semesters)

    def set_name(self, name: str) -> None:
        """Name is editable at any time; same rule as at creation."""
        self.name = _clean_name(name)

    def set_grading(self, scale: str, system: str) -> None:
        """Lock rule: allowed only while NO course exists. Otherwise raise
        ValidationError explaining why it is locked."""
        self._check_config(scale, system)

        if self.has_courses:
            raise ValidationError("Grading configuration is locked while courses exist.")

        self.scale = scale
        self.system = system

    def add_semester(self, name: str) -> Semester:
        sem = Semester(name)

        if any(_key(item.name) == _key(sem.name) for item in self.semesters):
            raise ValidationError("Semester name is a duplicate.")

        self.semesters.append(sem)
        return sem

    def rename_semester(self, semester: Semester, new_name: str) -> None:
        """Same rules as add_semester. Renaming to its own name is fine."""
        self._find_semester(semester)
        clean_name = Semester(new_name).name

        for item in self.semesters:
            if item is semester:
                continue

            if _key(item.name) == _key(clean_name):
                raise ValidationError("Semester name is a duplicate.")

        semester.name = clean_name

    def delete_semester(self, semester: Semester) -> None:
        """Removes the semester and its courses. (Confirmation is the CLI's job.)"""
        for index, item in enumerate(self.semesters):
            if item is semester:
                del self.semesters[index]
                return

        raise ValidationError("Semester not found.")
    
    def add_course(self, semester: Semester, course: Course) -> None:
        """Code unique within this semester, ignoring case. A COMPLETED
        course's grade must be a letter in the active table."""
        self._find_semester(semester)
        self._check_course(semester, course)
        semester.courses.append(course)

    def replace_course(
        self, semester: Semester, old: Course, new: Course
    ) -> None:
        """Edit = swap in a new, already-valid Course. Same checks as
        add_course, but `old` must not count as a duplicate of itself."""
        self._find_semester(semester)
        index = self._find_course_index(semester, old)
        self._check_course(semester, new, ignore=old)
        semester.courses[index] = new


    def delete_course(self, semester: Semester, course: Course) -> None:
        """Removes one course. Deleting the last course lifts the lock."""
        self._find_semester(semester)
        index = self._find_course_index(semester, course)
        del semester.courses[index] 
