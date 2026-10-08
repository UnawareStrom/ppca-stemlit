"""
Module 5: Data Handling and Data Science
- NumPy and Pandas: Data manipulation and analysis
- Matplotlib: Data visualization techniques
- Scikit-learn: Basic machine learning algorithms (RandomForestClassifier, GradientBoostingRegressor)
- Pickle: Serialization and Deserialization of trained models
- Database seeding: Populates initial student database for instant dashboard richness.
"""
import os
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import classification_report, mean_squared_error, r2_score

from ..config import DATA_DIR, MODELS_DIR, BASE_DIR
from ..database.db import DatabaseManager

def load_and_transform_uci_dataset() -> pd.DataFrame:
    """Loads the real-world UCI student performance dataset and maps it to EduPulse features."""
    uci_path = Path(DATA_DIR) / "uci_student" / "student-mat.csv"
    if not uci_path.exists():
        raise FileNotFoundError(f"UCI dataset not found at {uci_path}")
        
    uci_df = pd.read_csv(uci_path, sep=";")
    
    # Mapping Logic
    attendance = np.clip(100 - uci_df["absences"], 0, 100)
    study_hours = uci_df["studytime"] * 3.5
    midterm = uci_df["G1"] * 5
    assignments = uci_df["G2"] * 5
    lab = (uci_df["G1"] * 2.5) + (uci_df["G2"] * 2.5)
    gpa = np.clip(uci_df["G3"] / 2.0, 0, 10.0)
    composite_score = (attendance * 0.20 + np.clip(study_hours * 3.2, 0, 100) * 0.15 + midterm * 0.35 + assignments * 0.15 + lab * 0.15)
    
    grades = []
    risk_levels = []
    for g, att in zip(gpa, attendance):
        if g >= 9.0:
            grades.append("O")
        elif g >= 8.0:
            grades.append("A+")
        elif g >= 7.0:
            grades.append("A")
        elif g >= 6.0:
            grades.append("B+")
        elif g >= 5.0:
            grades.append("B")
        elif g >= 4.0:
            grades.append("C")
        else:
            grades.append("F")

        # Risk Classification
        if g < 6.0 or att < 60.0:
            risk_levels.append("High Risk")
        elif g < 7.5 or att < 75.0:
            risk_levels.append("Moderate Risk")
        else:
            risk_levels.append("Low Risk")
            
    df = pd.DataFrame({
        "attendance": np.round(attendance, 1),
        "study_hours_weekly": np.round(study_hours, 1),
        "midterm_score": np.round(midterm, 1),
        "assignment_score": np.round(assignments, 1),
        "lab_score": np.round(lab, 1),
        "final_score": np.round(composite_score, 1),
        "predicted_gpa": np.round(gpa, 2),
        "predicted_grade": grades,
        "risk_level": risk_levels
    })
    return df

def train_and_export():
    """Trains the ML models, evaluates, serializes with pickle, and plots performance."""
    print("-> Loading and transforming real UCI student performance dataset...")
    df = load_and_transform_uci_dataset()

    data_dir = Path(DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_path = data_dir / "students_dataset.csv"
    df.to_csv(csv_path, index=False)
    print(f"-> Saved dataset with {len(df)} records to: {csv_path}")

    # Feature matrix and targets
    features = [
        "attendance",
        "study_hours_weekly",
        "midterm_score",
        "assignment_score",
        "lab_score"
    ]
    X = df[features]
    y_class = df["predicted_grade"]
    y_reg = df["predicted_gpa"]

    X_train, X_test, y_train_cls, y_test_cls, y_train_reg, y_test_reg = train_test_split(
        X, y_class, y_reg, test_size=0.2, random_state=42, stratify=y_class
    )

    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Classification Model (Random Forest)
    print("-> Training Random Forest Classifier for Grade Prediction...")
    clf = RandomForestClassifier(n_estimators=120, max_depth=10, random_state=42)
    clf.fit(X_train_scaled, y_train_cls)
    cls_acc = clf.score(X_test_scaled, y_test_cls)
    print(f"   Classifier Test Accuracy: {cls_acc * 100:.2f}%")

    # 2. Regression Model (Gradient Boosting Regressor)
    print("-> Training Gradient Boosting Regressor for GPA Prediction...")
    reg = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    reg.fit(X_train_scaled, y_train_reg)
    reg_preds = reg.predict(X_test_scaled)
    r2 = r2_score(y_test_reg, reg_preds)
    rmse = np.sqrt(mean_squared_error(y_test_reg, reg_preds))
    print(f"   Regressor R² Score: {r2:.3f} | RMSE: {rmse:.3f}")

    # Module 5: Pickle in Python - Serialization
    models_dir = Path(MODELS_DIR)
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_artifacts = {
        "classifier": clf,
        "regressor": reg,
        "feature_names": features,
        "metrics": {"classifier_accuracy": cls_acc, "regressor_r2": r2, "rmse": rmse}
    }
    
    with open(models_dir / "model.pkl", "wb") as f:
        pickle.dump(model_artifacts, f)
    with open(models_dir / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    print(f"-> Successfully pickled models to: {models_dir}")

    # Module 5: Matplotlib Plot Generation
    img_dir = Path(BASE_DIR) / "app" / "static" / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    plot_path = img_dir / "model_performance.png"

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: Feature Importances
    importances = clf.feature_importances_
    indices = np.argsort(importances)
    axes[0].barh(range(len(indices)), importances[indices], color="#4f46e5", align="center")
    axes[0].set_yticks(range(len(indices)))
    axes[0].set_yticklabels([features[i] for i in indices])
    axes[0].set_title("Random Forest Feature Importances", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Relative Importance")

    # Plot 2: Actual vs Predicted GPA
    axes[1].scatter(y_test_reg, reg_preds, alpha=0.5, color="#06b6d4", edgecolors="none")
    axes[1].plot([4, 10], [4, 10], "--r", linewidth=2)
    axes[1].set_title(f"GPA Regression (R² = {r2:.2f})", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Actual GPA")
    axes[1].set_ylabel("Predicted GPA")

    plt.tight_layout()
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"-> Generated evaluation plot at: {plot_path}")

    # Seed Database with sample students
    seed_database()

def seed_database():
    """Seeds the SQLite database with 45 realistic student records for live testing."""
    print("-> Seeding database with initial cohort records...")
    db = DatabaseManager()

    # Predefined student roster
    first_names = ["Aarav", "Ananya", "Rohan", "Diya", "Kabir", "Sneha", "Aditya", "Pooja", "Vikram", "Neha", 
                   "Ishaan", "Tanvi", "Siddharth", "Meera", "Arjun", "Rhea", "Dhruv", "Isha", "Karan", "Anjali"]
    last_names = ["Sharma", "Verma", "Patel", "Mehta", "Deshmukh", "Nair", "Kulkarni", "Gupta", "Joshi", "Chopra"]
    
    np.random.seed(101)
    for i in range(1, 46):
        fn = np.random.choice(first_names)
        ln = np.random.choice(last_names)
        s_id = f"TCET-AIML-{1000 + i}"
        email = f"{fn.lower()}.{ln.lower()}{i}@tcetmumbai.in"
        phone = f"+9198{np.random.randint(10000000, 99999999)}"

        att = float(np.random.choice([
            np.random.uniform(45, 64),  # At risk
            np.random.uniform(68, 82),  # Average
            np.random.uniform(85, 98)   # Excellent
        ], p=[0.20, 0.50, 0.30]))
        
        hrs = float(np.random.uniform(4, 35))
        mid = float(np.random.uniform(30, 95))
        assign = float(np.random.uniform(40, 95))
        lab = float(np.random.uniform(45, 98))

        # Approximate Grade & GPA
        comp = att*0.2 + min(100, hrs*3.5)*0.15 + mid*0.35 + assign*0.15 + lab*0.15
        gpa = round(min(10.0, max(4.0, 3.8 + (comp/100)*6.2)), 2)
        
        if gpa >= 9.0:
            grade = "O"
        elif gpa >= 8.0:
            grade = "A+"
        elif gpa >= 7.0:
            grade = "A"
        elif gpa >= 6.0:
            grade = "B+"
        elif gpa >= 5.0:
            grade = "B"
        else:
            grade = "F" if gpa < 4.5 else "C"

        if gpa < 6.0 or att < 65.0:
            risk = "High Risk"
        elif gpa < 7.5 or att < 75.0:
            risk = "Moderate Risk"
        else:
            risk = "Low Risk"

        payload = {
            "student_id": s_id,
            "name": f"{fn} {ln}",
            "email": email,
            "phone": phone,
            "department": "AIML",
            "semester": 3,
            "attendance": round(att, 1),
            "study_hours_weekly": round(hrs, 1),
            "midterm_score": round(mid, 1),
            "assignment_score": round(assign, 1),
            "lab_score": round(lab, 1),
            "predicted_grade": grade,
            "predicted_gpa": gpa,
            "risk_level": risk
        }
        try:
            db.insert_student(payload)
        except Exception:
            pass

    print("-> Initial student records seeded successfully!")

if __name__ == "__main__":
    train_and_export()
