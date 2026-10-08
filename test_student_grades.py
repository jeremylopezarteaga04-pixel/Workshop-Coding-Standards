"""Unit tests for the Student Grade Management System.

Run them with: python -m unittest -v
"""

import unittest

from student_grades import (
    GradeNotFoundError,
    InvalidInputError,
    Student,
    letter_for_average,
)


class StudentCreationTest(unittest.TestCase):
    """Requirement 1 and 6: create students with a valid name and ID."""

    def test_creates_student_with_id_and_name(self):
        """A student keeps the given ID and name."""
        student = Student("202301234", "Ana Torres")
        self.assertEqual(student.student_id, "202301234")
        self.assertEqual(student.name, "Ana Torres")
        self.assertEqual(student.grades, ())

    def test_strips_surrounding_spaces(self):
        """Spaces around the ID and the name are removed."""
        student = Student("  202301234 ", "  Ana Torres ")
        self.assertEqual(student.student_id, "202301234")
        self.assertEqual(student.name, "Ana Torres")

    def test_rejects_empty_name(self):
        """An empty or blank name is rejected."""
        for name in ("", "   ", None):
            with self.subTest(name=name):
                with self.assertRaises(InvalidInputError):
                    Student("202301234", name)

    def test_rejects_empty_id(self):
        """An empty or blank ID is rejected."""
        for student_id in ("", "   ", None):
            with self.subTest(student_id=student_id):
                with self.assertRaises(InvalidInputError):
                    Student(student_id, "Ana Torres")


class GradeValidationTest(unittest.TestCase):
    """Requirements 2 and 6: only numeric grades in 0-100 are accepted."""

    def setUp(self):
        """Create a fresh student for every test."""
        self.student = Student("202301234", "Ana Torres")

    def test_accepts_numeric_grades_in_range(self):
        """Integers and floats between 0 and 100 are stored as floats."""
        for grade in (0, 72.5, 95.0, 100):
            self.student.add_grade(grade)
        self.assertEqual(self.student.grades, (0.0, 72.5, 95.0, 100.0))

    def test_rejects_non_numeric_grades(self):
        """Text, None, booleans and NaN are not valid grades."""
        for grade in ("Fifty", "95", None, True, float("nan")):
            with self.subTest(grade=grade):
                with self.assertRaises(InvalidInputError):
                    self.student.add_grade(grade)
        self.assertEqual(self.student.grades, ())

    def test_rejects_out_of_range_grades(self):
        """Grades below 0 or above 100 are rejected."""
        for grade in (-0.1, -3, 100.5, 105):
            with self.subTest(grade=grade):
                with self.assertRaises(InvalidInputError):
                    self.student.add_grade(grade)
        self.assertEqual(self.student.grades, ())


class AverageAndStatusTest(unittest.TestCase):
    """Requirements 3, 4, 5 and 7: average, letter, pass/fail, honor."""

    @staticmethod
    def student_with(*grades):
        """Return a student that already has the given grades."""
        student = Student("202301234", "Ana Torres")
        for grade in grades:
            student.add_grade(grade)
        return student

    def test_average_of_grades(self):
        """The average is the sum of the grades divided by their count."""
        student = self.student_with(95.0, 88.5, 92.0)
        self.assertAlmostEqual(student.calculate_average(), 91.8333, 3)

    def test_average_without_grades_is_zero(self):
        """A student with no grades has an average of 0."""
        self.assertEqual(self.student_with().calculate_average(), 0.0)

    def test_letter_grade_boundaries(self):
        """Each average maps to the letter defined in the requirements."""
        expected = {
            100: "A", 90: "A", 89.99: "B", 80: "B", 79.99: "C",
            70: "C", 69.99: "D", 60: "D", 59.99: "F", 0: "F",
        }
        for average, letter in expected.items():
            with self.subTest(average=average):
                self.assertEqual(letter_for_average(average), letter)

    def test_letter_grade_of_student(self):
        """The student's letter grade uses the current average."""
        self.assertEqual(self.student_with(85.0, 78.0).letter_grade, "B")

    def test_pass_fail_boundary(self):
        """An average of 60 or more passes; anything lower fails."""
        self.assertEqual(self.student_with(60.0).pass_status, "Passed")
        self.assertEqual(self.student_with(59.9).pass_status, "Failed")

    def test_honor_roll_is_boolean(self):
        """The honor roll flag is True from an average of 90 upwards."""
        self.assertIs(self.student_with(90.0).is_honor_roll, True)
        self.assertIs(self.student_with(89.9).is_honor_roll, False)


class RemoveGradeTest(unittest.TestCase):
    """Requirement 8: remove grades by value or by index."""

    def setUp(self):
        """Create a student with three grades."""
        self.student = Student("202301234", "Ana Torres")
        for grade in (95.0, 72.5, 88.0):
            self.student.add_grade(grade)

    def test_remove_by_value(self):
        """Removing an existing value deletes it from the list."""
        self.assertEqual(self.student.remove_grade_by_value(95.0), 95.0)
        self.assertEqual(self.student.grades, (72.5, 88.0))

    def test_remove_missing_value_raises(self):
        """Removing a value that does not exist raises a clear error."""
        with self.assertRaises(GradeNotFoundError):
            self.student.remove_grade_by_value(50.0)
        self.assertEqual(len(self.student.grades), 3)

    def test_remove_by_index(self):
        """Index 1 removes the second grade."""
        self.assertEqual(self.student.remove_grade_by_index(1), 72.5)
        self.assertEqual(self.student.grades, (95.0, 88.0))

    def test_remove_out_of_bounds_index_raises(self):
        """Indexes outside the list, including negative ones, fail."""
        for index in (3, 5, -1):
            with self.subTest(index=index):
                with self.assertRaises(GradeNotFoundError):
                    self.student.remove_grade_by_index(index)
        self.assertEqual(len(self.student.grades), 3)

    def test_remove_non_integer_index_raises(self):
        """An index that is not an integer is invalid input."""
        with self.assertRaises(InvalidInputError):
            self.student.remove_grade_by_index("1")


class SummaryReportTest(unittest.TestCase):
    """Requirement 9: formatted summary report with every field."""

    def test_report_contains_every_field(self):
        """The report shows ID, name, count, average, letter, status."""
        student = Student("202301234", "Ana Torres")
        for grade in (95.0, 88.5, 92.0):
            student.add_grade(grade)
        report = student.summary_report()
        expected_lines = (
            "Student ID        : 202301234",
            "Student Name      : Ana Torres",
            "Number of Grades  : 3",
            "Average Grade     : 91.83",
            "Letter Grade      : A",
            "Status            : Passed",
            "Honor Roll        : Yes",
        )
        for line in expected_lines:
            with self.subTest(line=line):
                self.assertIn(line, report)


if __name__ == "__main__":
    unittest.main()
