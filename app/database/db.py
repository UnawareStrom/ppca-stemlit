"""
Module 6: Database Connectivity with Python
Encapsulated SQLite Database Manager providing CRUD operations,
transactions, aggregations, and audit logging.
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from ..config import DATABASE_PATH
from ..core.exceptions import DatabaseOperationError, StudentNotFoundError

from contextlib import contextmanager

class DatabaseManager:
    """Encapsulates all SQLite database interactions with parameterization and safety."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DATABASE_PATH)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Establishes SQLite connection with Row factory enabled, safely closing upon exit."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initializes tables and indexes from schema.sql."""
        schema_file = Path(__file__).resolve().parent / "schema.sql"
        if not schema_file.exists():
            return
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()

    # --- CRUD: INSERT Operation ---
    def insert_student(self, data: Dict[str, Any]) -> int:
        """Inserts a new student record into the database."""
        sql = """
            INSERT INTO students (
                student_id, name, email, phone, department, semester,
                attendance, study_hours_weekly, midterm_score, assignment_score,
                lab_score, predicted_grade, predicted_gpa, risk_level
            ) VALUES (
                :student_id, :name, :email, :phone, :department, :semester,
                :attendance, :study_hours_weekly, :midterm_score, :assignment_score,
                :lab_score, :predicted_grade, :predicted_gpa, :risk_level
            )
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, data)
                conn.commit()
                row_id = cursor.lastrowid
                self.log_audit("INSERT_STUDENT", f"Added student {data['student_id']} ({data['name']})")
                return row_id
        except sqlite3.IntegrityError as e:
            raise DatabaseOperationError(f"Duplicate entry: Student ID or Email already exists ({str(e)}).")
        except Exception as e:
            raise DatabaseOperationError(f"Insert failed: {str(e)}")

    # --- CRUD: READ Operations ---
    def get_student_by_id(self, student_id: str) -> Dict[str, Any]:
        """Fetches a single student by unique student_id."""
        sql = "SELECT * FROM students WHERE student_id = ? OR id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (student_id, student_id))
            row = cursor.fetchone()
            if not row:
                raise StudentNotFoundError(student_id)
            return dict(row)

    def get_all_students(
        self,
        search: Optional[str] = None,
        risk_filter: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieves filtered and paginated list of students."""
        query = "SELECT * FROM students WHERE 1=1"
        params: List[Any] = []

        if search:
            query += " AND (student_id LIKE ? OR name LIKE ? OR email LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term])

        if risk_filter and risk_filter != "ALL":
            query += " AND risk_level = ?"
            params.append(risk_filter)

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    # --- CRUD: UPDATE Operation ---
    def update_student(self, student_id: str, data: Dict[str, Any]) -> bool:
        """Updates academic metrics and predictions of an existing student."""
        # Ensure student exists first
        self.get_student_by_id(student_id)

        sql = """
            UPDATE students SET
                name = :name,
                email = :email,
                phone = :phone,
                department = :department,
                semester = :semester,
                attendance = :attendance,
                study_hours_weekly = :study_hours_weekly,
                midterm_score = :midterm_score,
                assignment_score = :assignment_score,
                lab_score = :lab_score,
                predicted_grade = :predicted_grade,
                predicted_gpa = :predicted_gpa,
                risk_level = :risk_level,
                updated_at = CURRENT_TIMESTAMP
            WHERE student_id = :student_id
        """
        payload = {**data, "student_id": student_id}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, payload)
                conn.commit()
                self.log_audit("UPDATE_STUDENT", f"Updated student {student_id}")
                return cursor.rowcount > 0
        except Exception as e:
            raise DatabaseOperationError(f"Update failed: {str(e)}")

    # --- CRUD: DELETE Operation ---
    def delete_student(self, student_id: str) -> bool:
        """Deletes a student record by student_id."""
        self.get_student_by_id(student_id)
        sql = "DELETE FROM students WHERE student_id = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (student_id,))
                conn.commit()
                self.log_audit("DELETE_STUDENT", f"Deleted student {student_id}")
                return cursor.rowcount > 0
        except Exception as e:
            raise DatabaseOperationError(f"Delete failed: {str(e)}")

    # --- Audit & Prediction Logging ---
    def log_audit(self, action: str, details: str) -> None:
        """Records an administrative or data action into audit_logs."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO audit_logs (action, details) VALUES (?, ?)", (action, details))
                conn.commit()
        except Exception:
            pass

    def log_prediction(
        self,
        student_id: Optional[str],
        grade: str,
        gpa: float,
        risk: str,
        confidence: float,
        features: Dict[str, Any]
    ) -> None:
        """Logs an AI inference event."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO predictions_log (
                        student_id, predicted_grade, predicted_gpa, risk_level, confidence, feature_payload
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (student_id or "ANONYMOUS", grade, gpa, risk, confidence, json.dumps(features)))
                conn.commit()
        except Exception:
            pass

    # --- Analytics & Dashboard Aggregations ---
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Calculates cohort-level aggregations and KPIs for the dashboard."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total count
            cursor.execute("SELECT COUNT(*) as total FROM students")
            total = cursor.fetchone()["total"]

            if total == 0:
                return {
                    "total_students": 0,
                    "avg_attendance": 0,
                    "avg_study_hours": 0,
                    "avg_gpa": 0,
                    "pass_rate": 0,
                    "high_risk_count": 0,
                    "risk_distribution": {"Low Risk": 0, "Moderate Risk": 0, "High Risk": 0},
                    "grade_distribution": {"O": 0, "A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "F": 0},
                    "recent_students": []
                }

            # Averages
            cursor.execute("""
                SELECT
                    ROUND(AVG(attendance), 1) as avg_attendance,
                    ROUND(AVG(study_hours_weekly), 1) as avg_study_hours,
                    ROUND(AVG(predicted_gpa), 2) as avg_gpa
                FROM students
            """)
            avg_row = cursor.fetchone()

            # Risk breakdown
            cursor.execute("SELECT risk_level, COUNT(*) as cnt FROM students GROUP BY risk_level")
            risk_dist = {"Low Risk": 0, "Moderate Risk": 0, "High Risk": 0}
            for r in cursor.fetchall():
                if r["risk_level"] in risk_dist:
                    risk_dist[r["risk_level"]] = r["cnt"]

            # Grade breakdown
            cursor.execute("SELECT predicted_grade, COUNT(*) as cnt FROM students GROUP BY predicted_grade")
            grade_dist = {"O": 0, "A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "F": 0}
            for r in cursor.fetchall():
                if r["predicted_grade"] in grade_dist:
                    grade_dist[r["predicted_grade"]] = r["cnt"]

            # Pass rate calculation (Grade != 'F')
            failing = grade_dist.get("F", 0)
            pass_rate = round(((total - failing) / total) * 100, 1)

            # Recent 5 students
            cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5")
            recent = [dict(r) for r in cursor.fetchall()]

            return {
                "total_students": total,
                "avg_attendance": avg_row["avg_attendance"] or 0,
                "avg_study_hours": avg_row["avg_study_hours"] or 0,
                "avg_gpa": avg_row["avg_gpa"] or 0,
                "pass_rate": pass_rate,
                "high_risk_count": risk_dist.get("High Risk", 0),
                "risk_distribution": risk_dist,
                "grade_distribution": grade_dist,
                "recent_students": recent
            }
