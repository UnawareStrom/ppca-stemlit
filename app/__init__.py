"""
EduPulse AI - Flask Application Factory
Registers blueprints, error handlers, static assets, and initializes database.
"""
from flask import Flask, render_template, jsonify
from .config import Config
from .core.exceptions import EduPulseBaseException, ValidationError, StudentNotFoundError
from .database.db import DatabaseManager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Database tables
    db_mgr = DatabaseManager(app.config["DATABASE"])
    app.db = db_mgr

    # Register Blueprints
    from .routes.main_routes import main_bp
    from .routes.student_routes import student_bp
    from .routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix="/students")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Module 4: Custom Application-wide Exception Handlers
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        if app.config.get("API_REQUEST"):
            return jsonify(err.to_dict()), err.status_code
        return render_template("error.html", error=err, title="Validation Error"), err.status_code

    @app.errorhandler(StudentNotFoundError)
    def handle_not_found(err):
        return render_template("error.html", error=err, title="Not Found"), 404

    @app.errorhandler(EduPulseBaseException)
    def handle_custom_exception(err):
        return render_template("error.html", error=err, title="Application Error"), err.status_code

    @app.errorhandler(404)
    def handle_page_not_found(e):
        return render_template("error.html", error=type("Err", (), {"message": "The requested page was not found."})(), title="404 Not Found"), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return render_template("error.html", error=type("Err", (), {"message": "An internal server error occurred."})(), title="Internal Server Error"), 500

    return app
