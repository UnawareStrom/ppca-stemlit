import streamlit as st
import pandas as pd
import io
import csv

# Import our existing application logic
from app.database.db import DatabaseManager
from app.ml.predictor import StudentPerformancePredictor
from app.core.csv_importer import AdaptiveCSVImporter
from app.core.validator import validate_student_payload
from app.core.exceptions import ValidationError, StudentNotFoundError
from app.config import Config

st.set_page_config(
    page_title="EduPulse AI Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Initialization ---
@st.cache_resource
def get_predictor():
    return StudentPerformancePredictor()

@st.cache_resource
def get_db():
    return DatabaseManager(Config.DATABASE)

predictor = get_predictor()
db = get_db()

# --- Sidebar Navigation ---
st.sidebar.title("🎓 EduPulse AI")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Students Directory", "Student Form", "AI Predictor Playground", "Batch Data Import"]
)
st.sidebar.markdown("---")
st.sidebar.info("TCET AIML Semester-III Python Programming Mini Project")

# --- Page: Dashboard ---
if page == "Dashboard":
    st.title("📊 Analytics Dashboard")
    st.markdown("Overview of student cohort performance and risk metrics.")
    
    metrics = db.get_dashboard_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", metrics["total_students"])
    with col2:
        st.metric("Average GPA", f"{metrics['avg_gpa']:.2f}")
    with col3:
        st.metric("Pass Rate", f"{metrics['pass_rate']}%")
    with col4:
        st.metric("High Risk Count", metrics["high_risk_count"])
        
    st.markdown("---")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Risk Distribution")
        if sum(metrics["risk_distribution"].values()) > 0:
            risk_df = pd.DataFrame(
                list(metrics["risk_distribution"].items()), 
                columns=["Risk Level", "Count"]
            ).set_index("Risk Level")
            st.bar_chart(risk_df, color="#ff4b4b")
        else:
            st.info("No risk data available.")
            
    with col_chart2:
        st.subheader("Grade Distribution")
        if sum(metrics["grade_distribution"].values()) > 0:
            grade_df = pd.DataFrame(
                list(metrics["grade_distribution"].items()), 
                columns=["Grade", "Count"]
            ).set_index("Grade")
            st.bar_chart(grade_df, color="#4b4bff")
        else:
            st.info("No grade data available.")
            
    st.markdown("---")
    st.subheader("Recent Additions")
    if metrics["recent_students"]:
        recent_df = pd.DataFrame(metrics["recent_students"])
        st.dataframe(
            recent_df[["student_id", "name", "department", "semester", "predicted_grade", "risk_level"]],
            use_container_width=True
        )
    else:
        st.info("No recent students found.")

# --- Page: Students Directory ---
elif page == "Students Directory":
    st.title("👥 Students Directory")
    
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("Search by Name, ID, or Email", "")
    with col_filter:
        risk_filter = st.selectbox("Filter by Risk Level", ["ALL", "Low Risk", "Moderate Risk", "High Risk"])
        
    students = db.get_all_students(
        search=search_query if search_query else None, 
        risk_filter=risk_filter
    )
    
    if students:
        df = pd.DataFrame(students)
        # Reorder and select columns for display
        display_cols = ["student_id", "name", "email", "department", "attendance", "predicted_gpa", "risk_level"]
        st.dataframe(df[display_cols], use_container_width=True)
        
        # Export option
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name="EduPulse_Students_Export.csv",
            mime="text/csv",
        )
    else:
        st.warning("No students found matching the criteria.")
        
# --- Page: Student Form (Add / Edit / Delete) ---
elif page == "Student Form":
    st.title("📝 Student Management")
    
    # Simple tabs for mode selection
    mode = st.radio("Mode", ["Add New Student", "Edit/Delete Existing Student"], horizontal=True)
    
    if mode == "Add New Student":
        st.subheader("Add New Student")
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                student_id = st.text_input("Student ID (e.g., TCET-AIML-101)")
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                phone = st.text_input("Phone Number")
                department = st.selectbox("Department", ["AIML", "AIDS", "COMP", "IT", "EXTC", "MECH", "CIVIL"])
                semester = st.number_input("Semester", min_value=1, max_value=8, value=3)
            with col2:
                attendance = st.slider("Attendance (%)", 0.0, 100.0, 75.0)
                study_hours = st.slider("Weekly Study Hours", 0.0, 70.0, 12.0)
                midterm_score = st.slider("Midterm Score (0-100)", 0.0, 100.0, 65.0)
                assignment_score = st.slider("Assignment Score (0-100)", 0.0, 100.0, 70.0)
                lab_score = st.slider("Lab Score (0-100)", 0.0, 100.0, 75.0)
                
            submitted = st.form_submit_button("Add Student")
            
            if submitted:
                raw_data = {
                    "student_id": student_id,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "department": department,
                    "semester": semester,
                    "attendance": attendance,
                    "study_hours_weekly": study_hours,
                    "midterm_score": midterm_score,
                    "assignment_score": assignment_score,
                    "lab_score": lab_score
                }
                try:
                    data = validate_student_payload(raw_data)
                    prediction = predictor.predict({
                        "attendance": data["attendance"],
                        "study_hours_weekly": data["study_hours_weekly"],
                        "midterm_score": data["midterm_score"],
                        "assignment_score": data["assignment_score"],
                        "lab_score": data["lab_score"]
                    })
                    data.update({
                        "predicted_grade": prediction["predicted_grade"],
                        "predicted_gpa": prediction["predicted_gpa"],
                        "risk_level": prediction["risk_level"]
                    })
                    db.insert_student(data)
                    st.success(f"Student {data['student_id']} ({data['name']}) added successfully!")
                except ValidationError as ve:
                    st.error(f"Validation Error: {str(ve)}")
                except Exception as e:
                    st.error(f"Error adding student: {str(e)}")
                    
    else:
        st.subheader("Edit / Delete Existing Student")
        target_id = st.text_input("Enter Student ID to Edit/Delete (e.g., TCET-AIML-101)")
        
        if target_id:
            try:
                student = db.get_student_by_id(target_id)
                st.success(f"Student Found: {student['name']}")
                
                with st.form("edit_student_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Full Name", value=student['name'])
                        email = st.text_input("Email Address", value=student['email'])
                        phone = st.text_input("Phone Number", value=student.get('phone', ''))
                        
                        # Find the index of the current department, default to 0 if not found
                        depts = ["AIML", "AIDS", "COMP", "IT", "EXTC", "MECH", "CIVIL"]
                        try:
                            dept_idx = depts.index(student.get('department', 'AIML').upper())
                        except ValueError:
                            dept_idx = 0
                            
                        department = st.selectbox("Department", depts, index=dept_idx)
                        semester = st.number_input("Semester", min_value=1, max_value=8, value=int(student.get('semester', 3)))
                    with col2:
                        attendance = st.slider("Attendance (%)", 0.0, 100.0, float(student['attendance']))
                        study_hours = st.slider("Weekly Study Hours", 0.0, 70.0, float(student['study_hours_weekly']))
                        midterm_score = st.slider("Midterm Score", 0.0, 100.0, float(student['midterm_score']))
                        assignment_score = st.slider("Assignment Score", 0.0, 100.0, float(student['assignment_score']))
                        lab_score = st.slider("Lab Score", 0.0, 100.0, float(student['lab_score']))
                        
                    col_update, col_delete = st.columns([1, 1])
                    with col_update:
                        update_submitted = st.form_submit_button("Update Student", use_container_width=True)
                    with col_delete:
                        delete_submitted = st.form_submit_button("Delete Student", type="primary", use_container_width=True)
                        
                    if update_submitted:
                        raw_data = {
                            "student_id": target_id,
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "department": department,
                            "semester": semester,
                            "attendance": attendance,
                            "study_hours_weekly": study_hours,
                            "midterm_score": midterm_score,
                            "assignment_score": assignment_score,
                            "lab_score": lab_score
                        }
                        try:
                            data = validate_student_payload(raw_data)
                            prediction = predictor.predict({
                                "attendance": data["attendance"],
                                "study_hours_weekly": data["study_hours_weekly"],
                                "midterm_score": data["midterm_score"],
                                "assignment_score": data["assignment_score"],
                                "lab_score": data["lab_score"]
                            })
                            data.update({
                                "predicted_grade": prediction["predicted_grade"],
                                "predicted_gpa": prediction["predicted_gpa"],
                                "risk_level": prediction["risk_level"]
                            })
                            db.update_student(target_id, data)
                            st.success("Student updated successfully!")
                            st.rerun()
                        except ValidationError as ve:
                            st.error(f"Validation Error: {str(ve)}")
                        except Exception as e:
                            st.error(f"Error updating student: {str(e)}")
                            
                    if delete_submitted:
                        try:
                            db.delete_student(target_id)
                            st.warning(f"Student {target_id} deleted successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting student: {str(e)}")
                            
            except StudentNotFoundError:
                st.error("Student not found.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- Page: AI Predictor Playground ---
elif page == "AI Predictor Playground":
    st.title("🤖 Live AI Predictor Playground")
    st.markdown("Test out the prediction model without saving data to the database.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Input Features")
        attendance = st.slider("Attendance (%)", 0.0, 100.0, 75.0)
        study_hours = st.slider("Weekly Study Hours", 0.0, 70.0, 15.0)
        midterm_score = st.slider("Midterm Score", 0.0, 100.0, 70.0)
        assignment_score = st.slider("Assignment Score", 0.0, 100.0, 80.0)
        lab_score = st.slider("Lab Score", 0.0, 100.0, 75.0)
        
        predict_btn = st.button("Predict Performance", type="primary", use_container_width=True)
        
    with col2:
        st.subheader("AI Prediction Results")
        if predict_btn:
            with st.spinner("Analyzing..."):
                result = predictor.predict({
                    "attendance": attendance,
                    "study_hours_weekly": study_hours,
                    "midterm_score": midterm_score,
                    "assignment_score": assignment_score,
                    "lab_score": lab_score
                })
                
                st.metric("Predicted GPA", f"{result['predicted_gpa']:.2f}")
                st.metric("Predicted Grade", result["predicted_grade"])
                st.metric("Risk Level", result["risk_level"])
                st.metric("Confidence", f"{result['confidence_pct']}%")
                
                if result['risk_level'] == 'High Risk':
                    st.error("This student needs immediate attention.")
                elif result['risk_level'] == 'Moderate Risk':
                    st.warning("This student might need some guidance.")
                else:
                    st.success("This student is on track.")
        else:
            st.info("Adjust the sliders and click 'Predict Performance' to see the AI analysis.")

# --- Page: Batch Data Import ---
elif page == "Batch Data Import":
    st.title("📥 Batch Data Import")
    st.markdown("Upload a CSV file to import multiple student records at once.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    adapt_model = st.checkbox("Adapt/Retrain ML Model with new data", value=False)
    
    if uploaded_file is not None:
        if st.button("Process CSV", type="primary"):
            try:
                # Read file content as string
                raw_content = uploaded_file.getvalue().decode("utf-8-sig", errors="replace")
                with st.spinner("Processing records and running AI predictions..."):
                    stats = AdaptiveCSVImporter.process_csv_content(
                        raw_content=raw_content,
                        db_manager=db,
                        predictor=predictor,
                        adapt_model=adapt_model
                    )
                    
                st.success(
                    f"Successfully processed {stats['total_rows']} rows: "
                    f"{stats['inserted']} added, {stats['updated']} updated."
                )
                
                if stats.get("model_retrained") and stats.get("retrain_stats"):
                    ret = stats["retrain_stats"]
                    st.info(
                        f"ML Model adapted on {ret['total_samples']} samples. "
                        f"Accuracy: {ret['classifier_accuracy']}%, R²: {ret['regressor_r2']}"
                    )
            except ValidationError as ve:
                st.error(f"Validation Error in CSV: {str(ve)}")
            except Exception as e:
                st.error(f"Error processing CSV: {str(e)}")
                
    st.markdown("---")
    st.subheader("Need a template?")
    st.markdown("Download a sample CSV file with the correct headers.")
    
    sample_rows = [
        ["Roll No", "Student Name", "Email", "Department", "Semester", "Attendance %", "Study Hours", "Midterm Score", "Assignment", "Lab Work"],
        ["TCET-AIML-1051", "Aarav Sharma", "aarav.sharma@tcetmumbai.in", "AIML", "3", "88%", "18.5", "82", "88", "85"],
        ["TCET-AIML-1052", "Diya Patel", "diya.patel@tcetmumbai.in", "AIML", "3", "52%", "8.0", "42", "55", "60"]
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(sample_rows)
    
    st.download_button(
        label="Download Sample Template",
        data=output.getvalue().encode('utf-8'),
        file_name="EduPulse_Adaptive_Sample_Template.csv",
        mime="text/csv",
    )
