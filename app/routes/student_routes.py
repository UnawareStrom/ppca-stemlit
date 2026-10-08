"""
Student Management Routes
Module 6: Database CRUD (Insert, Delete, Update, Select)
Integrates with Regular Expressions validator and ML Predictor.
"""
import io
import csv
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from ..core.validator import validate_student_payload
from ..core.exceptions import ValidationError, StudentNotFoundError
from ..core.csv_importer import AdaptiveCSVImporter
from ..ml.predictor import StudentPerformancePredictor
from ..database.db import DatabaseManager

student_bp = Blueprint("students", __name__)
predictor = StudentPerformancePredictor()

@student_bp.route("/")
def list_students():
    """Displays all students with search and risk filters."""
    db: DatabaseManager = current_app.db
    search = request.args.get("search", "").strip()
    risk = request.args.get("risk", "ALL").strip()
    
    students = db.get_all_students(search=search if search else None, risk_filter=risk, limit=200)
    return render_template(
        "students.html",
        students=students,
        search=search,
        selected_risk=risk,
        active_page="students"
    )

@student_bp.route("/add", methods=["GET", "POST"])
def add_student():
    """Module 6: Form handling & INSERT Operation with RegEx validation and AI inference."""
    db: DatabaseManager = current_app.db
    if request.method == "POST":
        try:
            # 1. RegEx and range validation
            data = validate_student_payload(request.form.to_dict())

            # 2. Run AI Model prediction
            prediction = predictor.predict({
                "attendance": data["attendance"],
                "study_hours_weekly": data["study_hours_weekly"],
                "midterm_score": data["midterm_score"],
                "assignment_score": data["assignment_score"],
                "lab_score": data["lab_score"]
            })

            data["predicted_grade"] = prediction["predicted_grade"]
            data["predicted_gpa"] = prediction["predicted_gpa"]
            data["risk_level"] = prediction["risk_level"]

            # 3. Database INSERT
            db.insert_student(data)
            flash(f"Student {data['student_id']} ({data['name']}) added successfully!", "success")
            return redirect(url_for("students.list_students"))

        except ValidationError as ve:
            flash(str(ve), "danger")
            return render_template("student_form.html", student=request.form, is_edit=False, active_page="students")
        except Exception as e:
            flash(f"Error adding student: {str(e)}", "danger")
            return render_template("student_form.html", student=request.form, is_edit=False, active_page="students")

    return render_template("student_form.html", student={}, is_edit=False, active_page="students")

@student_bp.route("/edit/<student_id>", methods=["GET", "POST"])
def edit_student(student_id: str):
    """Module 6: UPDATE Operation with RegEx validation and re-calculated AI prediction."""
    db: DatabaseManager = current_app.db
    student = db.get_student_by_id(student_id)

    if request.method == "POST":
        try:
            data = validate_student_payload(request.form.to_dict())
            
            # Recalculate AI prediction on updated metrics
            prediction = predictor.predict({
                "attendance": data["attendance"],
                "study_hours_weekly": data["study_hours_weekly"],
                "midterm_score": data["midterm_score"],
                "assignment_score": data["assignment_score"],
                "lab_score": data["lab_score"]
            })

            data["predicted_grade"] = prediction["predicted_grade"]
            data["predicted_gpa"] = prediction["predicted_gpa"]
            data["risk_level"] = prediction["risk_level"]

            db.update_student(student_id, data)
            flash(f"Student {student_id} updated successfully!", "success")
            return redirect(url_for("students.list_students"))

        except ValidationError as ve:
            flash(str(ve), "danger")
            return render_template("student_form.html", student=request.form, is_edit=True, student_id=student_id, active_page="students")
        except Exception as e:
            flash(f"Update failed: {str(e)}", "danger")
            return render_template("student_form.html", student=request.form, is_edit=True, student_id=student_id, active_page="students")

    return render_template("student_form.html", student=student, is_edit=True, student_id=student_id, active_page="students")

@student_bp.route("/delete/<student_id>", methods=["POST"])
def delete_student(student_id: str):
    """Module 6: DELETE Operation."""
    db: DatabaseManager = current_app.db
    try:
        db.delete_student(student_id)
        flash(f"Student {student_id} record deleted successfully.", "info")
    except Exception as e:
        flash(f"Could not delete student: {str(e)}", "danger")
    return redirect(url_for("students.list_students"))

@student_bp.route("/export")
def export_csv():
    """Module 5: File Handling - Exports all student records as a downloadable CSV."""
    db: DatabaseManager = current_app.db
    students = db.get_all_students(limit=1000)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    headers = [
        "Student ID", "Name", "Email", "Department", "Semester", "Attendance (%)",
        "Weekly Study Hours", "Midterm Score", "Assignment Score", "Lab Score",
        "Predicted Grade", "Predicted GPA", "Risk Level"
    ]
    writer.writerow(headers)

    for s in students:
        writer.writerow([
            s.get("student_id"), s.get("name"), s.get("email"), s.get("department"),
            s.get("semester"), s.get("attendance"), s.get("study_hours_weekly"),
            s.get("midterm_score"), s.get("assignment_score"), s.get("lab_score"),
            s.get("predicted_grade"), s.get("predicted_gpa"),
            s.get("risk_level")
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=TCET_Students_Performance_Export.csv"}
    )

@student_bp.route("/import", methods=["GET", "POST"])
def import_csv():
    """
    Module 5: File Handling & Advanced CSV Ingestion.
    Accepts arbitrary student CSV uploads, applies adaptive header matching,
    runs automated ML predictions, and performs database batch upsert.
    """
    db: DatabaseManager = current_app.db
    if request.method == "POST":
        if "csv_file" not in request.files:
            flash("No file was uploaded. Please choose a CSV file.", "danger")
            return redirect(url_for("students.import_csv"))

        file = request.files["csv_file"]
        if not file or file.filename == "":
            flash("No file selected. Please select a valid .csv file.", "danger")
            return redirect(url_for("students.import_csv"))

        if not file.filename.lower().endswith(".csv"):
            flash("Invalid file format. Please upload a comma-separated values (.csv) file.", "danger")
            return redirect(url_for("students.import_csv"))

        adapt_model = request.form.get("adapt_model") == "true" or request.form.get("adapt_model") == "on"

        try:
            raw_content = file.read().decode("utf-8-sig", errors="replace")
            stats = AdaptiveCSVImporter.process_csv_content(
                raw_content,
                db_manager=db,
                predictor=predictor,
                adapt_model=adapt_model
            )

            msg = (
                f"Successfully processed {stats['total_rows']} student records: "
                f"{stats['inserted']} added, {stats['updated']} updated."
            )
            if stats.get("model_retrained") and stats.get("retrain_stats"):
                ret = stats["retrain_stats"]
                msg += f" ML Model adapted on {ret['total_samples']} samples (Accuracy: {ret['classifier_accuracy']}%, R²: {ret['regressor_r2']})."

            flash(msg, "success")
            return redirect(url_for("students.list_students"))

        except ValidationError as ve:
            flash(f"Validation Error: {str(ve)}", "danger")
            return redirect(url_for("students.import_csv"))
        except Exception as e:
            flash(f"CSV Ingestion Failed: {str(e)}", "danger")
            return redirect(url_for("students.import_csv"))

    return render_template("import_csv.html", active_page="students")

@student_bp.route("/sample-csv")
def sample_csv():
    """Generates a downloadable sample CSV demonstrating flexible adaptive headers."""
    sample_rows = [
        ["Roll No", "Student Name", "Email", "Department", "Semester", "Attendance %", "Study Hours", "Midterm Score", "Assignment", "Lab Work"],
        ["1051", "Aarav Sharma", "aarav.sharma@tcetmumbai.in", "AIML", "3", "88%", "18.5", "82", "88", "85"],
        ["1052", "Diya Patel", "diya.patel@tcetmumbai.in", "AIML", "3", "52%", "8.0", "42", "55", "60"],
        ["1053", "Rohan Mehta", "rohan.mehta@tcetmumbai.in", "AIML", "3", "94%", "22.0", "91", "94", "90"],
        ["1054", "Sneha Roy", "sneha.roy@tcetmumbai.in", "AIML", "3", "64%", "12.0", "70", "65", "68"],
        ["1055", "Kabir Khan", "", "AIML", "3", "78%", "15.0", "74", "78", "80"]
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(sample_rows)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=EduPulse_Adaptive_Sample_Template.csv"}
    )

