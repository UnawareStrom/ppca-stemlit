"""
Main Web Routes
Handles dashboard, AI predictor page, and analytics overview.
"""
from flask import Blueprint, render_template, current_app
from ..database.db import DatabaseManager

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def dashboard():
    """Main Analytics & Monitoring Dashboard."""
    db: DatabaseManager = current_app.db
    metrics = db.get_dashboard_metrics()
    return render_template("index.html", metrics=metrics, active_page="dashboard")

@main_bp.route("/predictor")
def predictor_view():
    """Interactive Live AI Performance & Risk Predictor."""
    return render_template("predictor.html", active_page="predictor")

@main_bp.route("/analytics")
def analytics_view():
    """Cohort Deep-Dive Visual Analytics."""
    db: DatabaseManager = current_app.db
    metrics = db.get_dashboard_metrics()
    return render_template("analytics.html", metrics=metrics, active_page="analytics")
