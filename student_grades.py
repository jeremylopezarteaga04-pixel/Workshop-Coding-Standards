"""Student Grade Management System.

This module lets you create student records, register numeric grades,
compute the average, the letter grade, the pass/fail status and the
honor roll flag, remove grades by value or by index, and print a
formatted summary report for every student.

Invalid input never crashes the program: the domain classes raise
descriptive exceptions and the presentation layer (``main``) catches
them and shows a clear error message to the user.
"""

import math

MIN_GRADE = 0.0
MAX_GRADE = 100.0
PASSING_AVERAGE = 60.0
HONOR_ROLL_AVERAGE = 90.0

# Minimum average required for each letter, from highest to lowest.
LETTER_GRADE_THRESHOLDS = (
    (90.0, "A"),
    (80.0, "B"),
    (70.0, "C"),
    (60.0, "D"),
)
FAILING_LETTER = "F"

PASSED_STATUS = "Passed"
FAILED_STATUS = "Failed"

REPORT_WIDTH = 40
LABEL_WIDTH = 18


class GradeBookError(Exception):
    """Base class for every error raised by the grade management system."""


class InvalidInputError(GradeBookError):
    """Raised when a name, an ID or a grade does not pass validation."""


class GradeNotFoundError(GradeBookError):
    """Raised when a grade to remove does not exist."""


def validate_text(value, field_name):
    """Return ``value`` without surrounding spaces if it is a non-empty text.

    Raises:
        InvalidInputError: if ``value`` is not a string or is empty.
    """
    if not isinstance(value, str) or not value.strip():
        raise InvalidInputError(f"{field_name} must be a non-empty text.")
    return value.strip()


def validate_grade(grade):
    """Return ``grade`` as a float if it is a number between 0 and 100.

    Raises:
        InvalidInputError: if ``grade`` is not numeric or is out of range.
    """
    is_number = isinstance(grade, (int, float)) and not isinstance(grade, bool)
    if not is_number or not math.isfinite(grade):
        raise InvalidInputError(f"Grade {grade!r} is not a valid number.")
    if not MIN_GRADE <= grade <= MAX_GRADE:
        raise InvalidInputError(
            f"Grade {grade} is out of range "
            f"({MIN_GRADE:g}-{MAX_GRADE:g})."
        )
    return float(grade)


def letter_for_average(average):
    """Return the letter grade (A, B, C, D or F) for a given average."""
    for minimum_average, letter in LETTER_GRADE_THRESHOLDS:
        if average >= minimum_average:
            return letter
    return FAILING_LETTER


class Student:
    """A student record with an ID, a name and a list of numeric grades."""

    def __init__(self, student_id, name):
        """Create a student after validating that ID and name are not empty.

        Raises:
            InvalidInputError: if the ID or the name is empty.
        """
        self.student_id = validate_text(student_id, "Student ID")
        self.name = validate_text(name, "Student name")
        self._grades = []

    @property
    def grades(self):
        """Return a read-only copy of the student's grades."""
        return tuple(self._grades)

    def add_grade(self, grade):
        """Validate and store a new grade; return the stored value.

        Raises:
            InvalidInputError: if the grade is not a number in 0-100.
        """
        valid_grade = validate_grade(grade)
        self._grades.append(valid_grade)
        return valid_grade

    def remove_grade_by_value(self, value):
        """Remove the first grade equal to ``value``; return it.

        Raises:
            InvalidInputError: if ``value`` is not a valid grade.
            GradeNotFoundError: if the student has no such grade.
        """
        target = validate_grade(value)
        for position, grade in enumerate(self._grades):
            if math.isclose(grade, target):
                return self._grades.pop(position)
        raise GradeNotFoundError(
            f"Grade {target:g} was not found for {self.name}."
        )

    def remove_grade_by_index(self, index):
        """Remove the grade at zero-based position ``index``; return it.

        Raises:
            InvalidInputError: if ``index`` is not an integer.
            GradeNotFoundError: if ``index`` is out of bounds.
        """
        if not isinstance(index, int) or isinstance(index, bool):
            raise InvalidInputError(f"Index {index!r} must be an integer.")
        if not 0 <= index < len(self._grades):
            raise GradeNotFoundError(
                f"Index {index} is out of bounds: {self.name} has "
                f"{len(self._grades)} grade(s)."
            )
        return self._grades.pop(index)

    def calculate_average(self):
        """Return the average of all grades, or 0.0 if there are none."""
        if not self._grades:
            return 0.0
        return sum(self._grades) / len(self._grades)

    @property
    def letter_grade(self):
        """Return the letter grade that matches the current average."""
        return letter_for_average(self.calculate_average())

    @property
    def has_passed(self):
        """Return True if the average is at least the passing average."""
        return self.calculate_average() >= PASSING_AVERAGE

    @property
    def pass_status(self):
        """Return "Passed" or "Failed" according to the average."""
        return PASSED_STATUS if self.has_passed else FAILED_STATUS

    @property
    def is_honor_roll(self):
        """Return True if the average is at least the honor roll average."""
        return self.calculate_average() >= HONOR_ROLL_AVERAGE

    def summary_report(self):
        """Return a formatted, multi-line summary report of the student."""
        rows = (
            ("Student ID", self.student_id),
            ("Student Name", self.name),
            ("Number of Grades", len(self._grades)),
            ("Average Grade", f"{self.calculate_average():.2f}"),
            ("Letter Grade", self.letter_grade),
            ("Status", self.pass_status),
            ("Honor Roll", "Yes" if self.is_honor_roll else "No"),
        )
        separator = "=" * REPORT_WIDTH
        lines = [separator, "STUDENT SUMMARY REPORT".center(REPORT_WIDTH),
                 separator]
        lines.extend(f"{label:<{LABEL_WIDTH}}: {value}"
                     for label, value in rows)
        lines.append(separator)
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Presentation layer: every call that can fail is wrapped here so that
# invalid input shows a clear message instead of crashing the program.
# ----------------------------------------------------------------------

# Demo data: (student ID, name, grades). Some entries are invalid on
# purpose to show that the system reports the error and keeps running.
DEMO_RECORDS = (
    ("202301234", "Ana Torres", (95.0, 88.5, 92.0)),
    ("202304321", "Sofia Ramirez", (85.0, 78.0, 82.5)),
    ("202305678", "Luis Mendoza", (72.5, 65, 58.0, 100)),
    ("202309012", "Maria Lopez", (45.0, 55.5, "Fifty", 105, -3)),
    ("x", "", (100,)),
    ("", "Pedro Vera", (80,)),
)


def show_error(error):
    """Print an error message in a consistent format."""
    print(f"  [ERROR] {error}")


def create_student(student_id, name):
    """Create and return a student, or return None if the data is invalid."""
    try:
        return Student(student_id, name)
    except InvalidInputError as error:
        show_error(f"Could not create student: {error}")
        return None


def add_grades(student, grades):
    """Try to add every grade in ``grades``, reporting each result."""
    for grade in grades:
        try:
            stored_grade = student.add_grade(grade)
        except InvalidInputError as error:
            show_error(error)
        else:
            print(f"  [OK] Grade {stored_grade:g} added to {student.name}.")


def remove_by_value(student, value):
    """Try to remove a grade by value, reporting the result."""
    try:
        removed = student.remove_grade_by_value(value)
    except GradeBookError as error:
        show_error(error)
    else:
        print(f"  [OK] Grade {removed:g} removed from {student.name}.")


def remove_by_index(student, index):
    """Try to remove a grade by index, reporting the result."""
    try:
        removed = student.remove_grade_by_index(index)
    except GradeBookError as error:
        show_error(error)
    else:
        print(f"  [OK] Grade {removed:g} at index {index} removed "
              f"from {student.name}.")


def register_students(records):
    """Create the students in ``records`` and add their grades.

    ``records`` is a sequence of ``(student_id, name, grades)`` tuples.
    Returns a dictionary of the valid students indexed by their ID.
    """
    students = {}
    for student_id, name, grades in records:
        student = create_student(student_id, name)
        if student is None:
            continue
        if student.student_id in students:
            show_error(f"Student ID {student.student_id} already exists.")
            continue
        students[student.student_id] = student
        print(f"  [OK] Student {student.name} ({student.student_id}) "
              "registered.")
        add_grades(student, grades)
    return students


def main():
    """Run a demonstration that covers every functional requirement."""
    print("1) Creating students and adding grades")
    students = register_students(DEMO_RECORDS)

    print("\n2) Removing grades by value and by index")
    luis = students["202305678"]
    remove_by_value(luis, 100)
    remove_by_value(luis, 99.0)
    remove_by_index(luis, 5)
    remove_by_index(students["202309012"], 1)

    print("\n3) Summary reports")
    for student in students.values():
        print()
        print(student.summary_report())


if __name__ == "__main__":
    main()
