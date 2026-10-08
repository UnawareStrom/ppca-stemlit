"""
Custom Exception Classes for EduPulse AI
Implements Module 4: Exception Handling (User-Defined Exceptions & Hierarchy)
"""

class EduPulseBaseException(Exception):
    """Base exception for all domain-specific EduPulse errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {"error": self.__class__.__name__, "message": self.message, "status_code": self.status_code}


class ValidationError(EduPulseBaseException):
    """Raised when user input fails regular expression or range constraints."""
    def __init__(self, message: str = "Input validation failed."):
        super().__init__(message, status_code=422)


class StudentNotFoundError(EduPulseBaseException):
    """Raised when a requested student record does not exist in the database."""
    def __init__(self, student_id: str):
        super().__init__(f"Student with ID '{student_id}' was not found.", status_code=404)


class DatabaseOperationError(EduPulseBaseException):
    """Raised when an SQL query or database transaction fails."""
    def __init__(self, message: str = "Database operation could not be completed."):
        super().__init__(message, status_code=500)


class ModelInferenceError(EduPulseBaseException):
    """Raised when the AI model fails during feature scaling or prediction."""
    def __init__(self, message: str = "Error occurred during AI model inference."):
        super().__init__(message, status_code=500)
