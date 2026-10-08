"""
Unit Tests for EduPulse AI - Machine Learning & OOP Classes
Tests Module 3 (OOP inheritance, encapsulation), Module 4 (Exceptions),
and Module 5 (Model inference and serialization).
"""
import unittest
from app.ml.predictor import StudentPerformancePredictor
class TestMachineLearningLayer(unittest.TestCase):

    def setUp(self):
        self.predictor = StudentPerformancePredictor()

    def test_oop_properties_and_encapsulation(self):
        """Verify OOP encapsulation and inheritance in StudentPerformancePredictor."""
        self.assertEqual(self.predictor.model_name, "EduPulse-Ensemble-Predictor")
        self.assertIn("2.1", self.predictor.engine_version)
        self.assertTrue(self.predictor.is_trained)

    def test_predictor_valid_inference(self):
        """Verify model returns expected structure, valid grades, and bounded GPA."""
        sample_features = {
            "attendance": 88.5,
            "study_hours_weekly": 20.0,
            "midterm_score": 85.0,
            "assignment_score": 90.0,
            "lab_score": 92.0
        }
        result = self.predictor.predict(sample_features)

        # Check dictionary keys
        self.assertIn("predicted_grade", result)
        self.assertIn("predicted_gpa", result)
        self.assertIn("risk_level", result)
        self.assertIn("confidence_pct", result)
        self.assertIn("radar_scores", result)

        # Value bounds
        self.assertIn(result["predicted_grade"], ["O", "A+", "A", "B+", "B", "C", "F"])
        self.assertGreaterEqual(result["predicted_gpa"], 4.0)
        self.assertLessEqual(result["predicted_gpa"], 10.0)
        self.assertGreaterEqual(result["confidence_pct"], 0.0)
        self.assertLessEqual(result["confidence_pct"], 100.0)

    def test_at_risk_detection(self):
        """Verify that low attendance and poor marks correctly trigger High Risk status."""
        poor_features = {
            "attendance": 45.0,
            "study_hours_weekly": 4.0,
            "midterm_score": 30.0,
            "assignment_score": 40.0,
            "lab_score": 45.0
        }
        result = self.predictor.predict(poor_features)
        self.assertEqual(result["risk_level"], "High Risk")

if __name__ == "__main__":
    unittest.main()
