"""
Unit Tests for Database CRUD & Regular Expressions Validation
Tests Module 6 (SQLite CRUD & re.match validations).
"""
import unittest
import os
import tempfile
from app.database.db import DatabaseManager
from app.core.validator import validate_student_payload, RE_STUDENT_ID, RE_EMAIL, RE_PHONE
from app.core.exceptions import ValidationError, StudentNotFoundError

class TestDatabaseAndRegex(unittest.TestCase):

    def setUp(self):
        # Create an isolated temporary SQLite database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)

    def tearDown(self):
        try:
            if os.path.exists(self.temp_db.name):
                os.unlink(self.temp_db.name)
        except Exception:
            pass

    def test_regex_patterns(self):
        """Module 6: Verify regular expressions for student ID, email, and phone."""
        # Valid cases
        self.assertTrue(bool(RE_STUDENT_ID.match("TCET-AIML-101")))
        self.assertTrue(bool(RE_STUDENT_ID.match("TCET-AIDS-2026")))
        self.assertTrue(bool(RE_EMAIL.match("student.test@tcetmumbai.in")))
        self.assertTrue(bool(RE_PHONE.match("+919876543210")))
        self.assertTrue(bool(RE_PHONE.match("9876543210")))

        # Invalid cases
        self.assertFalse(bool(RE_STUDENT_ID.match("INVALID_ID_123")))
        self.assertFalse(bool(RE_EMAIL.match("bad_email_format.com")))
        self.assertFalse(bool(RE_PHONE.match("12345")))

    def test_database_crud_lifecycle(self):
        """Module 6: Test complete lifecycle: INSERT, READ, UPDATE, DELETE."""
        student_data = {
            "student_id": "TCET-AIML-9999",
            "name": "Test Candidate",
            "email": "candidate@tcetmumbai.in",
            "phone": "+919988776655",
            "department": "AIML",
            "semester": 3,
            "attendance": 85.0,
            "study_hours_weekly": 15.0,
            "midterm_score": 75.0,
            "assignment_score": 80.0,
            "lab_score": 85.0,
            "predicted_grade": "A+",
            "predicted_gpa": 8.75,
            "risk_level": "Low Risk"
        }

        # 1. INSERT
        row_id = self.db.insert_student(student_data)
        self.assertIsNotNone(row_id)

        # 2. READ
        retrieved = self.db.get_student_by_id("TCET-AIML-9999")
        self.assertEqual(retrieved["name"], "Test Candidate")
        self.assertEqual(retrieved["attendance"], 85.0)

        # 3. UPDATE
        student_data["attendance"] = 92.0
        student_data["predicted_gpa"] = 9.20
        updated = self.db.update_student("TCET-AIML-9999", student_data)
        self.assertTrue(updated)

        updated_student = self.db.get_student_by_id("TCET-AIML-9999")
        self.assertEqual(updated_student["attendance"], 92.0)
        self.assertEqual(updated_student["predicted_gpa"], 9.20)

        # 4. DELETE
        deleted = self.db.delete_student("TCET-AIML-9999")
        self.assertTrue(deleted)

        # Verify not found
        with self.assertRaises(StudentNotFoundError):
            self.db.get_student_by_id("TCET-AIML-9999")

if __name__ == "__main__":
    unittest.main()
