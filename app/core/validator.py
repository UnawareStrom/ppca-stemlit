"""
Module 6: Regular Expressions & Input Validation
Uses Python's built-in `re` library to validate academic credentials,
patterns, contact details, and input ranges before database insertion.
"""
import re
from typing import Dict, Any, Tuple, List
from .exceptions import ValidationError

# Compiled Regular Expression Patterns
RE_STUDENT_ID = re.compile(r"^TCET-[A-Z0-9]{2,6}-\d{1,6}$", re.IGNORECASE)
RE_NAME = re.compile(r"^[A-Za-z\s.]{2,60}$")
RE_EMAIL = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
RE_PHONE = re.compile(r"^(\+91[\-\s]?)?[6789]\d{9}$")
RE_DEPARTMENT = re.compile(r"^(AIML|AIDS|COMP|IT|EXTC|MECH|CIVIL)$", re.IGNORECASE)

def validate_regex(pattern: re.Pattern, value: str, field_name: str) -> None:
    """Helper to match regular expression using re.match(). Raises ValidationError on failure."""
    if not value or not pattern.match(str(value).strip()):
        raise ValidationError(f"Invalid format for '{field_name}'. Failed regex pattern '{pattern.pattern}'.")

def validate_range(value: float, min_val: float, max_val: float, field_name: str) -> float:
    """Validates that a numeric value falls within an expected range."""
    try:
        val = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Field '{field_name}' must be a valid number.")
    if not (min_val <= val <= max_val):
        raise ValidationError(f"Field '{field_name}' ({val}) must be between {min_val} and {max_val}.")
    return val

def validate_student_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validator for student record creation and updates.
    Ensures data consistency and security before executing SQL queries.
    """
    errors: List[str] = []

    # 1. Student ID Regex
    student_id = str(data.get("student_id", "")).strip().upper().strip("'\"")
    if not RE_STUDENT_ID.match(student_id):
        errors.append("Student ID must follow format: 'TCET-AIML-15', 'TCET-AIML-101' or 'TCET-AIML-202601'.")

    # 2. Name Regex
    name = str(data.get("name", "")).strip()
    if not RE_NAME.match(name):
        errors.append("Name must contain only alphabets, dots, and spaces (2 to 60 characters).")

    # 3. Email Regex
    email = str(data.get("email", "")).strip().lower()
    if not RE_EMAIL.match(email):
        errors.append("Invalid email address format.")

    # 4. Phone Regex
    phone = str(data.get("phone", "")).strip()
    if phone and not RE_PHONE.match(phone):
        errors.append("Invalid Indian phone number (must be 10 digits starting with 6, 7, 8, or 9).")

    # 5. Department Regex
    department = str(data.get("department", "AIML")).strip().upper()
    if not RE_DEPARTMENT.match(department):
        errors.append("Department must be one of: AIML, AIDS, COMP, IT, EXTC, MECH, CIVIL.")

    # 6. Numeric Field Range Validation
    clean_data = {
        "student_id": student_id,
        "name": name,
        "email": email,
        "phone": phone if phone else "N/A",
        "department": department,
        "semester": int(data.get("semester", 3)),
    }

    try:
        clean_data["attendance"] = validate_range(data.get("attendance", 75.0), 0.0, 100.0, "attendance")
        clean_data["study_hours_weekly"] = validate_range(data.get("study_hours_weekly", 12.0), 0.0, 70.0, "study_hours_weekly")
        clean_data["midterm_score"] = validate_range(data.get("midterm_score", 65.0), 0.0, 100.0, "midterm_score")
        clean_data["assignment_score"] = validate_range(data.get("assignment_score", 70.0), 0.0, 100.0, "assignment_score")
        clean_data["lab_score"] = validate_range(data.get("lab_score", 75.0), 0.0, 100.0, "lab_score")
    except ValidationError as ve:
        errors.append(str(ve))

    if errors:
        raise ValidationError(" | ".join(errors))

    return clean_data
