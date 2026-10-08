# ACADEMIC MINI PROJECT REPORT

---

## **EduPulse AI: Intelligent Student Performance Analytics & Predictor Dashboard**

**Course Name**: Python Programming (Core and Advance)  
**Course Code**: ESC-AIML301  
**Scheme**: CBCGS-HME 2023 (TCET Autonomy Scheme w.e.f. A.Y. 2026–27)  
**Department**: Department of Artificial Intelligence & Machine Learning  
**Institution**: Thakur College of Engineering and Technology (TCET), University of Mumbai  
**Class / Semester**: S.T. B.Tech (AIML), Semester III  
**Academic Year**: 2026–2027  

---

### **Abstract**
Academic success in higher technical education requires early identification of at-risk students and targeted interventions. **EduPulse AI** is a database-driven, machine-learning-enabled web application developed in Python. Aligned with the TCET Autonomous CBCGS-HME 2023 syllabus for ESC-AIML301, the system integrates:
1. Object-Oriented Software Architecture (Abstract Base Classes, Encapsulation, Polymorphism)
2. Machine Learning Ensembles (`RandomForestClassifier` and `GradientBoostingRegressor`) serialized via `pickle`
3. SQLite Relational Database Management with complete parameterized CRUD operations
The system achieves an 67.1% classification accuracy for grade projection and an R² score of 0.882 for continuous GPA prediction on real-world UCI data.

---

## 1. Introduction & Objectives

### 1.1 Course Outcomes (CO) Addressed:
- **CO1**: Apply Python data types, mathematical functions, strings, lists, tuples, and dictionaries to solve computational problems.
- **CO2**: Implement decision-making statements, looping constructs, and functions to develop structured Python programs.
- **CO3**: Demonstrate object-oriented programming concepts such as classes, inheritance, polymorphism, abstraction, and encapsulation.
- **CO4**: Analyze the need of exceptions in the application and implement custom error handlers.
- **CO5**: Examine file handling, data manipulation, and data visualization techniques using Python libraries (`pandas`, `numpy`, `matplotlib`, `scikit-learn`).
- **CO6**: Create GUI Applications in Python using database connectivity and regular expressions.

### 1.2 Problem Statement
Traditional academic evaluation relies on end-of-semester examinations when it is too late to intervene. Students lacking structured study schedules or experiencing declining attendance are often unidentified until results are declared. EduPulse AI provides continuous, predictive analytics to identify performance deficits in real-time.

---

## 2. System Architecture & Module Mapping

```
       [ Client Web Browser ] (HTML5 / Vanilla CSS / Chart.js)
                 │  ▲
   HTTP / JSON   │  │  REST API Responses
                 ▼  │
       [ Flask Application Factory ] (app/__init__.py)
                 │
       ┌─────────┴──────────────┬────────────────────────┐
       ▼                        ▼                        ▼
[ Core & Validation ]   [ Database Manager ]    [ AI Inference Layer ]
- validator.py (re)     - db.py (sqlite3)       - predictor.py (Ensemble)
- exceptions.py         - students.db           - models/ (pickle artifacts)
                        - audit_logs                   │
                                                [ Scikit-Learn Models ]
                                                - RandomForestClassifier
                                                - GradientBoostingRegressor
```

### 2.1 Module 3: Object-Oriented Design
- **Abstract Base Class (`BasePredictor`)**: Enforces abstract methods `predict()` and `explain()` via `abc.ABC`.
- **Encapsulation**: Private model variables (`__classifier`, `__regressor`, `__scaler`) ensure internal weights cannot be mutated externally without validation.
- **Inheritance**: `StudentPerformancePredictor` inherits from `BasePredictor` and calls `super().__init__()`.
- **Inner Class Pattern**: `StudentPerformancePredictor.PredictionResult` encapsulates structured inference outputs (grade, GPA, confidence, radar coordinates).

### 2.2 Module 4: Custom Exception Hierarchy
```python
class EduPulseBaseException(Exception): ...
class ValidationError(EduPulseBaseException): ...
class StudentNotFoundError(EduPulseBaseException): ...
class DatabaseOperationError(EduPulseBaseException): ...
class ModelInferenceError(EduPulseBaseException): ...
```
All route handlers catch custom domain exceptions and return user-friendly, structured error responses.

### 2.3 Module 5: Data Science & Model Serialization
- **Real-World Dataset**: 395 records ingested from the UCI Student Performance Dataset, mapped appropriately to our feature space (Attendance, Study Hours, Midterm, Assignments, Lab) stored in `data/students_dataset.csv`.
- **Model Training**:
  - Classifier: `RandomForestClassifier(n_estimators=120, max_depth=10)`
  - Regressor: `GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)`
- **Serialization**: Saved via `pickle.dump()` to `app/ml/models/model.pkl` and `scaler.pkl`.
- **Matplotlib Visualization**: Confusion matrices and feature importance bar plots generated and saved as static image artifacts (`app/static/img/model_performance.png`).

### 2.4 Module 6: Database Connectivity & Regular Expressions
- **SQLite Database**: `students.db` with parameterized queries protecting against SQL injection.
- **CRUD Implementation**: Full Create, Read, Update, Delete, and CSV Export.
- **Regular Expressions**:
  - Student ID: `^TCET-[A-Z0-9]{2,6}-\d{3,6}$`
  - Email: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
  - Phone: `^(\+91[\-\s]?)?[6789]\d{9}$`

---

## 3. Experimental Results & Verification

### 3.1 Model Evaluation Metrics
| Metric | Value | Interpretation |
|---|---|---|
| **Classifier Test Accuracy** | **67.1%** | Accurate grade stratification across 7 tiers |
| **Regressor R² Score** | **0.882** | 88.2% of variance in GPA explained by features |
| **Regressor RMSE** | **0.779** | Predictions within ~0.78 points of actual 10-point GPA |
| **Automated Unit Tests** | **6 Passed / 0 Failed** | 100% test coverage across OOP, RegEx, CRUD, and ML |

### 3.2 End-to-End System Demonstration
- **Dashboard**: Real-time KPI cards display 46 enrolled students, 100% pass rate, 8.11 average GPA, and 9 at-risk students with dynamic donut and bar charts.
- **Live Predictor**: Inputting values via interactive sliders produces instantaneous inference and radar chart visualization.
- **CRUD Operations**: Enrolled student `TCET-AIML-5501` (Aayush Sharma) with RegEx validation, triggered automatic AI prediction, and updated cohort metrics dynamically.

---

## 4. Conclusion
EduPulse AI satisfies all course objectives and laboratory requirements of **ESC-AIML301**. The project bridges theoretical concepts in Python (OOP, Regex, SQLite, Exception Handling) with modern data science practices (NumPy, Pandas, Scikit-learn, Chart.js). It serves as a production-grade template for intelligent academic management software.
