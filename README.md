# EduPulse AI: Intelligent Student Performance Analytics & Career Recommendation System

[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9-orange.svg)](https://scikit-learn.org/)
[![TCET Autonomous](https://img.shields.io/badge/TCET-CBCGS--HME_2023-purple.svg)](https://www.tcetmumbai.in/)

> **Academic Course**: Python Programming (Core and Advance) — Course Code: `ESC-AIML301`  
> **Department**: Artificial Intelligence & Machine Learning (AIML), TCET, University of Mumbai  
> **Semester**: S.T. SEM III  
> **Topic**: Mini Project (Experiment 10) & Case Studies 1 & 3  

---

## 📖 Executive Summary
**EduPulse AI** is an AI-powered academic performance monitoring, risk stratification, and career recommendation platform. It combines machine learning (`scikit-learn`), database connectivity (`sqlite3`), regular expression validation (`re`), asynchronous event-driven REST APIs, and a glassmorphism dashboard (`Chart.js`) to provide educators and students with predictive foresight.

---

## 🎯 Syllabus Alignment Matrix (ESC-AIML301)

| Syllabus Module | Syllabus Concept / Topic | Codebase Location | Implementation Highlights |
|---|---|---|---|
| **Module 1: Basics of Python** | Data types, tuples, lists, dictionaries, sets, math functions | [`app/ml/train.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/ml/train.py) | Data modeling, score weightings, dictionary payloads |
| **Module 2: Decision Making & Functions** | Conditional logic, loops, functions, lambdas, map & filter | `app/ml/predictor.py` | Mathematical rule cutoffs in model inference |
| **Module 3: OOP's Using Python** | Classes, objects, inheritance, `super()`, method overriding, private/protected encapsulation, abstract classes, inner classes | [`app/ml/base.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/ml/base.py), [`app/ml/predictor.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/ml/predictor.py) | `BasePredictor(ABC)`, `StudentPerformancePredictor`, `__classifier` encapsulation, inner class `PredictionResult` |
| **Module 4: Exception Handling & Packages** | Try-except-finally, user-defined custom exceptions, assertions, package modularity | [`app/core/exceptions.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/core/exceptions.py) | `ValidationError`, `StudentNotFoundError`, `ModelInferenceError`, structured package architecture |
| **Module 5: Data Handling & Data Science** | NumPy, Pandas, Scikit-learn, Matplotlib, Pickle serialization & deserialization | [`app/ml/train.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/ml/train.py), [`app/ml/predictor.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/ml/predictor.py) | 1,200 sample dataset generated, `StandardScaler`, `RandomForestClassifier`, `GradientBoostingRegressor`, `pickle.dump/load`, Matplotlib plot generation |
| **Module 6: GUI, Databases & RegEx** | Flask web app, SQLite connectivity (INSERT, UPDATE, DELETE, SELECT), Regular Expressions (`re.match`), Chart.js GUI | [`app/database/db.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/database/db.py), [`app/core/validator.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/core/validator.py), [`app/routes/`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/routes/) | Full parameterized CRUD operations, RegEx validation for `TCET-AIML-XXXX`, Email, and Phone number |
| **Experiment 8: Public API Integration** | Public API fetching with JSON parsing using `requests` | [`app/routes/api_routes.py`](file:///c:/Users/aayus/OneDrive/Attachments/Desktop/IE/ppca/app/routes/api_routes.py) | Real-time educational wisdom API client with resilient local fallback |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed (this project runs on **Python 3.14.2**).

### 2. Activate Virtual Environment
```powershell
# In project root:
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Train Model & Seed Database
```powershell
python -m app.ml.train
```
*Outputs: `data/students_dataset.csv`, `app/ml/models/model.pkl`, `app/ml/models/scaler.pkl`, `app/static/img/model_performance.png`, and seeds 45 student records.*

### 5. Run Web Application
```powershell
python run.py
```
Visit: **`http://127.0.0.1:5000`** in your browser.

### 6. Run Automated Unit Tests
```powershell
python -m unittest discover tests
```

---

## 🏗️ Project Architecture

```
ppca/
├── .venv/                      # Active Virtual Environment (Python 3.14.2)
├── app/
│   ├── __init__.py             # Flask App Factory & Exception Handlers
│   ├── config.py               # Paths, secret keys, constants
│   ├── core/
│   │   ├── exceptions.py       # Module 4: Custom exception hierarchy
│   │   └── validator.py        # Module 6: Regular Expressions & input sanitization
│   ├── database/
│   │   ├── db.py               # Module 6: SQLite DatabaseManager (CRUD + Audit)
│   │   └── schema.sql          # SQLite DDL Schema (students, logs, audit)
│   ├── ml/
│   │   ├── base.py             # Module 3: Abstract Base Classes (OOP Abstraction)
│   │   ├── predictor.py        # Module 3 & 5: Ensemble Predictor & Inner Class

│   │   ├── train.py            # Module 5: Dataset generation, training, pickle, Matplotlib
│   │   └── models/             # Serialized binary models (.pkl)
│   │       ├── model.pkl
│   │       └── scaler.pkl
│   ├── routes/
│   │   ├── main_routes.py      # Dashboard & Analytics views
│   │   ├── student_routes.py   # Student CRUD routes & CSV export
│   │   └── api_routes.py       # REST API endpoints & Public Quote API
│   ├── static/
│   │   ├── css/style.css       # Responsive dark glassmorphic styling
│   │   ├── js/dashboard.js     # Event-driven UI, async fetch, dynamic Chart.js
│   │   └── img/                # Generated analytical figures
│   └── templates/              # Jinja2 HTML Templates
│       ├── base.html           # Master layout
│       ├── index.html          # Main Dashboard with KPI cards & charts
│       ├── predictor.html      # Interactive Live Predictor & Radar Chart
│       ├── students.html       # Student Directory & CRUD management
│       ├── student_form.html   # Add/Edit Student form with RegEx hints
│       ├── analytics.html      # Model performance & syllabus coverage
│       └── error.html          # Friendly error pages
├── data/
│   └── students_dataset.csv    # 1,200 synthetic student records
├── database/
│   └── students.db             # Live SQLite relational database
├── tests/
│   ├── test_model.py           # Unit tests for ML & OOP
│   └── test_db.py              # Unit tests for CRUD & RegEx
├── requirements.txt            # Package dependencies
├── run.py                      # Application launcher
└── README.md                   # Project documentation
```

---

## ❓ Viva Voce Preparation (Questions & Answers)

### Q1: How is Object-Oriented Programming (OOP) utilized in this project?
**Answer**:
- **Abstraction**: `BasePredictor` in `app/ml/base.py` use Python's `abc.ABC` and `@abstractmethod` to define mandatory contracts (`predict`, `explain`).
- **Inheritance & `super()`**: `StudentPerformancePredictor` inherits from `BasePredictor` and calls `super().__init__(model_name="EduPulse-Ensemble-Predictor")`.
- **Encapsulation**: Private attributes `__classifier`, `__regressor`, and `__scaler` are encapsulated using Python's name-mangling syntax and accessed via `@property` getters/setters.
- **Polymorphism / Method Overriding**: Concrete implementation overrides the abstract `predict()` method to provide customized feature extraction, probability estimation, and continuous GPA regression.
- **Inner Classes**: `StudentPerformancePredictor.PredictionResult` encapsulates structured inference outputs cleanly.

### Q2: How did you implement Database Connectivity and CRUD operations?
**Answer**:
In `app/database/db.py`, we created a `DatabaseManager` using Python's native `sqlite3` library:
- **Create (Insert)**: `insert_student()` runs parameterized `INSERT INTO students (...) VALUES (...)`.
- **Read (Select)**: `get_all_students()` supports dynamic parameterized filtering by search substring and risk tier (`Low`, `Moderate`, `High Risk`).
- **Update**: `update_student()` recalculates the student's metrics and runs `UPDATE students SET ... WHERE student_id = ?`.
- **Delete**: `delete_student()` removes the record and writes a log into `audit_logs`.
- Safe transaction handling is enforced using Python's `@contextmanager` to ensure all connections are closed cleanly.

### Q3: How are Regular Expressions applied?
**Answer**:
In `app/core/validator.py`:
- **Student ID**: `r"^TCET-[A-Z0-9]{2,6}-\d{3,6}$"` enforces TCET autonomous institutional ID formats (e.g. `TCET-AIML-1001`).
- **Email**: `r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"` validates RFC-compliant email addresses.
- **Phone**: `r"^(\+91[\-\s]?)?[6789]\d{9}$"` validates 10-digit Indian telephone formats.
- Every form submission and API call is sanitized with `re.match()` before executing SQL transactions.

### Q4: Explain the Machine Learning architecture.
**Answer**:
- **Algorithms**: Ensemble learning utilizing `RandomForestClassifier` (120 estimators) for categorical grade classification (O, A+, A, B+, B, C, F) and `GradientBoostingRegressor` (100 estimators) for continuous GPA prediction (4.0 to 10.0).
- **Preprocessing**: `StandardScaler` fits feature vectors across 5 dimensions: attendance, study hours, midterm, assignments, and lab work.
- **Serialization (Module 5)**: `pickle.dump()` serializes model dictionaries into `model.pkl` and `scaler.pkl`, deserialized at runtime using `pickle.load()`.
- **Metrics**: Random Forest achieved **82.08%** test accuracy; Gradient Boosting achieved **0.972 R²** with an RMSE of **0.173**.
