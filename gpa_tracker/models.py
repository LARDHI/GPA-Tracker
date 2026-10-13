"""Dataclasses, CourseStatus, validation and ValidationError. (T2)

Skeleton only: the shapes are here, the rules are not. Every method marked
TODO is yours to write; the rule it must enforce is named in its docstring
(spec section 3). Nothing in this module may call input() or print().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ValidationError(ValueError):
    """Raised when data breaks a rule from spec section 3.

    Subclasses ValueError so callers (and tests) can catch either.
    Messages must be specific: say which field and which rule.
    """


class CourseStatus(Enum):
    """A course is either finished with a known grade, or still running."""

    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"


@dataclass
class Course:
    """One course. Checks here need nothing but the course's own fields.

    Rules (spec section 3):
    - code: text, non-empty after trimming; stored trimmed
    - name: text, non-empty after trimming, at most 100 characters
      (measured after trimming); stored trimmed
    - credits: a real int from 1 to 9 (bool, 3.0, 3.5 and "3" are invalid)
    - status: must be a CourseStatus
    - COMPLETED needs a grade; IN_PROGRESS must have grade None
      (so "" is not a valid grade for either status)
    - grade, when present: must be text; stored normalized with
      grading.normalize_grade (" b+ " -> "B+"). Turn its ValueError into a
      ValidationError so every failure from Course has one type.
    Whether the grade is a letter in the ACTIVE table needs the student's
    scale and system, so Student checks that, not Course.
    """

    code: str
    name: str
    credits: int
    status: CourseStatus
    grade: str | None = None

    def __post_init__(self) -> None:
        # TODO (you): validate every rule above; raise ValidationError.
        raise NotImplementedError


@dataclass
class Semester:
    """A named list of courses, in order of addition.

    Rule: name non-empty after trimming, at most 50 characters.
    Uniqueness across semesters is checked by Student, which sees them all.
    """

    name: str
    courses: list[Course] = field(default_factory=list)

    def __post_init__(self) -> None:
        # TODO (you): validate the name rule above.
        raise NotImplementedError


@dataclass
class Student:
    """The profile: name, scale, grading system, and ordered semesters."""

    name: str
    scale: str  # "4.0" or "5.0"
    system: str  # "plus_only" or "plus_minus"
    semesters: list[Semester] = field(default_factory=list)

    def __post_init__(self) -> None:
        """TODO (you): name non-empty after trimming, at most 100 characters;
        (scale, system) must be one of the four configurations."""
        raise NotImplementedError

    @property
    def has_courses(self) -> bool:
        """True while at least one course exists in any semester."""
        # TODO (you)
        raise NotImplementedError

    def set_name(self, name: str) -> None:
        """Name is editable at any time; same rule as at creation."""
        # TODO (you)
        raise NotImplementedError

    def set_grading(self, scale: str, system: str) -> None:
        """Lock rule: allowed only while NO course exists. Otherwise raise
        ValidationError explaining why it is locked."""
        # TODO (you)
        raise NotImplementedError

    def add_semester(self, name: str) -> Semester:
        """Unique within the profile. Compare after trimming, collapsing runs
        of internal whitespace to one space, and ignoring case (spec section 3):
        " Fall 2026 " == "fall 2026", but "Fall 2026" != "Fall2026".
        Store the cleaned name (trimmed, collapsed) with its capitalization
        kept: " Fall 2026 " is stored as "Fall 2026"."""
        # TODO (you)
        raise NotImplementedError

    def rename_semester(self, semester: Semester, new_name: str) -> None:
        """Same rules as add_semester. Renaming to its own name is fine."""
        # TODO (you)
        raise NotImplementedError

    def delete_semester(self, semester: Semester) -> None:
        """Removes the semester and its courses. (Confirmation is the CLI's job.)"""
        # TODO (you)
        raise NotImplementedError

    def add_course(self, semester: Semester, course: Course) -> None:
        """Code unique within this semester, ignoring case. A COMPLETED
        course's grade must be a letter in the active table."""
        # TODO (you)
        raise NotImplementedError

    def replace_course(
        self, semester: Semester, old: Course, new: Course
    ) -> None:
        """Edit = swap in a new, already-valid Course. Same checks as
        add_course, but `old` must not count as a duplicate of itself."""
        # TODO (you)
        raise NotImplementedError

    def delete_course(self, semester: Semester, course: Course) -> None:
        """Removes one course. Deleting the last course lifts the lock."""
        # TODO (you)
        raise NotImplementedError
