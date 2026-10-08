"""
Module 3: OOP's Using Python - Inheritance, Polymorphism & Inner Classes
Module 5: Pickle in Python, Serialization & Deserialization
Implements StudentPerformancePredictor inheriting from BasePredictor.
"""
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BasePredictor
from ..config import MODELS_DIR
from ..core.exceptions import ModelInferenceError

class StudentPerformancePredictor(BasePredictor):
    """
    Concrete Predictor Class.
    Demonstrates:
    - Inheritance using super().__init__()
    - Method Overriding (polymorphic predict and explain implementations)
    - Encapsulation with private models (__classifier, __regressor, __scaler)
    - Inner Class pattern (PredictionResult)
    """

    FEATURE_NAMES = [
        "attendance",
        "study_hours_weekly",
        "midterm_score",
        "assignment_score",
        "lab_score"
    ]

    class PredictionResult:
        """
        Inner Class demonstrating encapsulation of structured inference results.
        Module 3: Inner Classes in Python.
        """
        def __init__(
            self,
            predicted_grade: str,
            predicted_gpa: float,
            risk_level: str,
            confidence: float,
            factor_impacts: Dict[str, float],
            radar_scores: Dict[str, float]
        ):
            self.predicted_grade = predicted_grade
            self.predicted_gpa = round(predicted_gpa, 2)
            self.risk_level = risk_level
            self.confidence = round(confidence * 100, 1)
            self.factor_impacts = factor_impacts
            self.radar_scores = radar_scores

        def to_dict(self) -> Dict[str, Any]:
            """Converts inner result object to clean JSON-serializable dictionary."""
            return {
                "predicted_grade": self.predicted_grade,
                "predicted_gpa": self.predicted_gpa,
                "risk_level": self.risk_level,
                "confidence_pct": self.confidence,
                "factor_impacts": self.factor_impacts,
                "radar_scores": self.radar_scores
            }

    def __init__(self, models_dir: Optional[str] = None):
        # Call base class constructor via super()
        super().__init__(model_name="EduPulse-Ensemble-Predictor")
        
        self.models_dir = Path(models_dir or MODELS_DIR)
        # Private encapsulated ML artifacts
        self.__classifier = None
        self.__regressor = None
        self.__scaler = None

        self.load_models()

    def load_models(self) -> None:
        """Deserializes trained models from disk using Python's pickle module."""
        clf_path = self.models_dir / "model.pkl"
        scaler_path = self.models_dir / "scaler.pkl"

        if clf_path.exists() and scaler_path.exists():
            try:
                with open(clf_path, "rb") as f:
                    artifacts = pickle.load(f)
                    self.__classifier = artifacts.get("classifier")
                    self.__regressor = artifacts.get("regressor")
                with open(scaler_path, "rb") as f:
                    self.__scaler = pickle.load(f)
                self.is_trained = True
            except Exception as e:
                self.is_trained = False
        else:
            self.is_trained = False

    def _extract_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Extracts and orders input features into a 2D numpy array."""
        try:
            vector = [float(features.get(k, 0.0)) for k in self.FEATURE_NAMES]
            return np.array([vector], dtype=np.float64)
        except Exception as e:
            raise ModelInferenceError(f"Feature vector extraction failed: {str(e)}")

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Polymorphic implementation of abstract predict method.
        Predicts Final Grade, Continuous GPA, Risk Level, and Confidence.
        """
        raw_vector = self._extract_feature_vector(features)

        if self.is_trained and self.__classifier and self.__scaler:
            try:
                import pandas as pd
                feature_df = pd.DataFrame(raw_vector, columns=self.FEATURE_NAMES)
                scaled_vector = self.__scaler.transform(feature_df)
                
                # Class prediction & confidence probability
                grade = str(self.__classifier.predict(scaled_vector)[0])
                probs = self.__classifier.predict_proba(scaled_vector)[0]
                confidence = float(np.max(probs))

                # Continuous GPA regression
                if self.__regressor:
                    gpa = float(self.__regressor.predict(scaled_vector)[0])
                    gpa = float(np.clip(gpa, 4.0, 10.0))
                else:
                    gpa = self._grade_to_gpa(grade)

            except Exception as e:
                # Fallback to analytical calculation if inference has exception
                grade, gpa, confidence = self._rule_based_fallback(features)
        else:
            grade, gpa, confidence = self._rule_based_fallback(features)

        # Risk level determination based on predicted GPA & Attendance
        risk_level = self._compute_risk_level(gpa, features.get("attendance", 75.0))
        
        # Explainable impact
        impacts = self.explain(features)["impacts"]
        
        # Subject / Dimension Radar normalized to 100
        radar = {
            "Attendance": float(features.get("attendance", 0)),
            "Study Consistency": min(100.0, float(features.get("study_hours_weekly", 0)) * 3.5),
            "Theory Exam": float(features.get("midterm_score", 0)),
            "Continuous Evaluation": float(features.get("assignment_score", 0)),
            "Practical / Lab": float(features.get("lab_score", 0))
        }

        # Instantiate inner class
        result = self.PredictionResult(
            predicted_grade=grade,
            predicted_gpa=gpa,
            risk_level=risk_level,
            confidence=confidence,
            factor_impacts=impacts,
            radar_scores=radar
        )
        return result.to_dict()

    def explain(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Provides analytical explanation of positive and negative student drivers."""
        att = float(features.get("attendance", 75))
        hrs = float(features.get("study_hours_weekly", 10))
        mid = float(features.get("midterm_score", 60))
        assign = float(features.get("assignment_score", 70))
        lab = float(features.get("lab_score", 70))

        impacts = {
            "Attendance": round((att - 75.0) * 0.4, 1),
            "Study Hours": round((hrs - 15.0) * 0.8, 1),
            "Midterm Exam": round((mid - 60.0) * 0.5, 1),
            "Assignments": round((assign - 65.0) * 0.3, 1),
            "Lab Work": round((lab - 65.0) * 0.3, 1)
        }
        return {"impacts": impacts}

    def _compute_risk_level(self, gpa: float, attendance: float) -> str:
        """Determines academic risk tier."""
        if gpa < 6.0 or attendance < 60.0:
            return "High Risk"
        elif gpa < 7.5 or attendance < 75.0:
            return "Moderate Risk"
        return "Low Risk"

    def _grade_to_gpa(self, grade: str) -> float:
        mapping = {"O": 9.7, "A+": 9.1, "A": 8.3, "B+": 7.5, "B": 6.8, "C": 5.8, "F": 4.0}
        return mapping.get(grade, 7.0)

    def _rule_based_fallback(self, features: Dict[str, float]) -> Tuple[str, float, float]:
        """Module 2: Structured decision-making fallback using mathematical formula."""
        composite = (
            features.get("attendance", 75) * 0.20 +
            min(100.0, features.get("study_hours_weekly", 15) * 3.5) * 0.20 +
            features.get("midterm_score", 60) * 0.30 +
            features.get("assignment_score", 70) * 0.15 +
            features.get("lab_score", 70) * 0.15
        )
        if composite >= 88:
            return "O", min(10.0, 9.0 + (composite - 88) / 12), 0.94
        elif composite >= 78:
            return "A+", 8.0 + (composite - 78) / 10, 0.89
        elif composite >= 68:
            return "A", 7.0 + (composite - 68) / 10, 0.85
        elif composite >= 58:
            return "B+", 6.0 + (composite - 58) / 10, 0.80
        elif composite >= 48:
            return "B", 5.0 + (composite - 48) / 10, 0.75
        elif composite >= 40:
            return "C", 4.0 + (composite - 40) / 10, 0.70
        else:
            return "F", 3.5, 0.92
