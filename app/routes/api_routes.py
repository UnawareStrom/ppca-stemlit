"""
Module 6: Web APIs and Event-Driven Services
Experiment 8: Public API Consumption with JSON handling & requests library
"""
from flask import Blueprint, request, jsonify, current_app
from ..ml.predictor import StudentPerformancePredictor
from ..core.validator import validate_range
from ..core.exceptions import ValidationError
from ..database.db import DatabaseManager

api_bp = Blueprint("api", __name__)
predictor = StudentPerformancePredictor()

@api_bp.route("/predict", methods=["POST"])
def predict_performance():
    """
    Live AI Prediction Endpoint.
    Receives student academic parameters and returns grade, GPA, risk tier,
    confidence score, and radar coordinates.
    """
    try:
        data = request.get_json(force=True) if request.is_json else request.form.to_dict()
        
        # Validations
        features = {
            "attendance": validate_range(data.get("attendance", 75), 0, 100, "attendance"),
            "study_hours_weekly": validate_range(data.get("study_hours_weekly", 12), 0, 70, "study_hours_weekly"),
            "midterm_score": validate_range(data.get("midterm_score", 65), 0, 100, "midterm_score"),
            "assignment_score": validate_range(data.get("assignment_score", 70), 0, 100, "assignment_score"),
            "lab_score": validate_range(data.get("lab_score", 75), 0, 100, "lab_score")
        }

        # Model Inference
        result = predictor.predict(features)

        # Log to Database
        db: DatabaseManager = current_app.db
        db.log_prediction(
            student_id=data.get("student_id"),
            grade=result["predicted_grade"],
            gpa=result["predicted_gpa"],
            risk=result["risk_level"],
            confidence=result["confidence_pct"],
            features=features
        )

        return jsonify({
            "status": "success",
            "prediction": result
        })

    except ValidationError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 422
    except Exception as e:
        return jsonify({"status": "error", "message": f"Inference failed: {str(e)}"}), 500

@api_bp.route("/metrics", methods=["GET"])
def get_metrics():
    """Fetches real-time dashboard aggregated metrics for dynamic charts."""
    db: DatabaseManager = current_app.db
    metrics = db.get_dashboard_metrics()
    return jsonify({"status": "success", "data": metrics})
