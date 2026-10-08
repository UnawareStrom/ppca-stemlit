-- EduPulse AI SQLite Database Schema
-- Aligned with Module 6: Database Connectivity with Python

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    department TEXT NOT NULL DEFAULT 'AIML',
    semester INTEGER NOT NULL DEFAULT 3,
    attendance REAL NOT NULL,
    study_hours_weekly REAL NOT NULL,
    midterm_score REAL NOT NULL,
    assignment_score REAL NOT NULL,
    lab_score REAL NOT NULL,
    predicted_grade TEXT,
    predicted_gpa REAL,
    risk_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    predicted_grade TEXT,
    predicted_gpa REAL,
    risk_level TEXT,
    confidence REAL,
    feature_payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_risk_level ON students(risk_level);
