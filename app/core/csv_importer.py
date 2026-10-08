"""
EduPulse AI - Adaptive CSV Importer
Module 5: File Handling & Advanced Data Ingestion

Provides intelligent, schema-agnostic ingestion for student records:
1. Adaptive Header Detection: Fuzzy maps arbitrary column headers from diverse LMS/Excel sources.
2. Robust Sanitization: Cleans percentages, commas, missing IDs, emails, and phone numbers.
3. Automated AI Inference: Predicts GPA, grade, and risk tier on each row.
4. Batch Upserting: Safely updates or creates records without SQL constraint conflicts.
"""
import io
import re
import csv
from typing import Dict, Any, List, Tuple, Optional
from ..core.validator import RE_EMAIL, RE_STUDENT_ID
from ..core.exceptions import ValidationError

class AdaptiveCSVImporter:
    """
    Intelligently maps arbitrary CSV columns into standard student schema
    and orchestrates batch AI predictions & database upserts.
    """

    # Canonical internal fields mapped to lists of regex patterns/synonyms
    HEADER_ALIASES: Dict[str, List[str]] = {
        "student_id": [
            r"^student[\s_-]?id$", r"^roll[\s_-]?(?:no|num|number)?$",
            r"^prn$", r"^uid$", r"^seat[\s_-]?no$", r"^id$", r"^reg[\s_-]?(?:no|num)?$"
        ],
        "name": [
            r"^student[\s_-]?name$", r"^(?:full[\s_-]?)?name$", r"^candidate[\s_-]?name$",
            r"^student$"
        ],
        "email": [
            r"^(?:student[\s_-]?)?email(?:[\s_-]?address)?$", r"^mail$", r"^email[\s_-]?id$"
        ],
        "phone": [
            r"^(?:phone|mobile|contact)(?:[\s_-]?(?:no|num|number))?$", r"^cell$"
        ],
        "department": [
            r"^department$", r"^dept$", r"^branch$", r"^course$", r"^stream$"
        ],
        "semester": [
            r"^semester$", r"^sem$", r"^term$", r"^year$"
        ],
        "attendance": [
            r"^attendance(?:\s*\(?%?\)?)?$", r"^attnd?$", r"^attnd?_pct$",
            r"^attendance[\s_-]?rate$", r"^present(?:\s*\(?%?\)?)?$"
        ],
        "study_hours_weekly": [
            r"^study[\s_-]?hours(?:[\s_-]?weekly)?$", r"^weekly[\s_-]?study[\s_-]?hours$",
            r"^study[\s_-]?time$", r"^study[\s_-]?hrs$", r"^hours$"
        ],
        "midterm_score": [
            r"^midterm(?:[\s_-]?score)?$", r"^mid[\s_-]?term$", r"^internal[\s_-]?(?:exam|test|score)?$",
            r"^ise$", r"^ia[\s_-]?1$", r"^test[\s_-]?1$", r"^exam[\s_-]?score$", r"^theory$"
        ],
        "assignment_score": [
            r"^assignment(?:[\s_-]?score)?$", r"^assignments?$", r"^ia[\s_-]?2$",
            r"^continuous[\s_-]?eval(?:uation)?$", r"^quiz(?:[\s_-]?score)?$", r"^homework$"
        ],
        "lab_score": [
            r"^lab(?:[\s_-]?(?:score|work))?$", r"^labs?$", r"^practical(?:[\s_-]?(?:score|work))?$",
            r"^tw$", r"^term[\s_-]?work$", r"^experiments?$"
        ]
    }

    @classmethod
    def normalize_header_name(cls, header: str) -> str:
        """Strips special characters, spaces, and lowercase for robust comparison."""
        cleaned = header.strip().lower()
        cleaned = re.sub(r"[\(\)\[\]%]", "", cleaned)
        cleaned = re.sub(r"[\s\-_]+", "_", cleaned).strip("_")
        return cleaned

    @classmethod
    def match_column(cls, raw_header: str) -> Optional[str]:
        """Matches a raw CSV column header to a canonical field name."""
        cleaned = cls.normalize_header_name(raw_header)
        for canonical, patterns in cls.HEADER_ALIASES.items():
            for pat in patterns:
                if re.match(pat, cleaned, re.IGNORECASE) or re.match(pat, raw_header.strip(), re.IGNORECASE):
                    return canonical
        return None

    @classmethod
    def build_header_mapping(cls, raw_headers: List[str]) -> Tuple[Dict[str, str], List[str]]:
        """
        Maps raw CSV headers to canonical fields.
        Returns (mapping: dict[canonical -> raw_header], unmapped: list[str])
        """
        mapping: Dict[str, str] = {}
        unmapped: List[str] = []
        used_canonicals = set()

        for raw in raw_headers:
            canonical = cls.match_column(raw)
            if canonical and canonical not in used_canonicals:
                mapping[canonical] = raw
                used_canonicals.add(canonical)
            else:
                unmapped.append(raw)

        return mapping, unmapped

    @classmethod
    def _clean_numeric(cls, value: Any, default: float, min_val: float, max_val: float) -> float:
        """Parses float values, handling percentage signs, empty strings, and ranges."""
        if value is None:
            return default
        s = str(value).strip().replace("%", "").replace(",", "")
        if not s:
            return default
        try:
            num = float(s)
            return max(min_val, min(max_val, round(num, 2)))
        except (ValueError, TypeError):
            return default

    @classmethod
    def sanitize_and_adapt_row(
        cls,
        row_dict: Dict[str, Any],
        mapping: Dict[str, str],
        index: int,
        existing_ids: set
    ) -> Dict[str, Any]:
        """
        Adapts a single CSV row into a complete, valid student dictionary.
        Imputes missing identifiers and standardizes text formats.
        """
        def get_val(canonical: str, fallback: str = "") -> str:
            raw_col = mapping.get(canonical)
            if raw_col and raw_col in row_dict and row_dict[raw_col] is not None:
                return str(row_dict[raw_col]).strip()
            return fallback

        # 1. Student ID handling: use if valid, otherwise auto-format or auto-generate
        raw_id = get_val("student_id")
        if raw_id:
            if re.match(r"^TCET-[A-Z0-9]{2,6}-\d{3,6}$", raw_id, re.IGNORECASE):
                student_id = raw_id.upper()
            else:
                clean_seq = re.sub(r"\D", "", raw_id)
                if not clean_seq:
                    clean_seq = str(1000 + index)
                student_id = f"TCET-AIML-{clean_seq.zfill(4)}"
        else:
            student_id = f"TCET-AIML-{str(1100 + index).zfill(4)}"

        # 2. Name handling
        raw_name = get_val("name")
        if raw_name:
            cleaned_name = re.sub(r"[^A-Za-z\s.]", "", raw_name).strip()
            name = cleaned_name if len(cleaned_name) >= 2 else f"Student {student_id.split('-')[-1]}"
        else:
            name = f"Student {student_id.split('-')[-1]}"

        # 3. Email handling
        raw_email = get_val("email")
        if raw_email and RE_EMAIL.match(raw_email):
            email = raw_email.lower()
        else:
            slug = re.sub(r"[^a-z0-9]", "", name.lower().replace(" ", "."))
            if not slug:
                slug = student_id.lower().replace("-", "")
            email = f"{slug}@tcetmumbai.in"

        # 4. Phone handling
        raw_phone = get_val("phone", "9876543210")
        clean_phone = re.sub(r"\D", "", raw_phone)
        if len(clean_phone) >= 10:
            phone = clean_phone[-10:]
        else:
            phone = f"98765{str(index).zfill(5)}"

        # 5. Department & Semester
        dept_candidate = get_val("department", "AIML").upper()
        department = dept_candidate if dept_candidate in ["AIML", "AIDS", "COMP", "IT", "EXTC", "MECH", "CIVIL"] else "AIML"
        
        sem_val = get_val("semester", "3")
        try:
            semester = max(1, min(8, int(re.sub(r"\D", "", sem_val) or 3)))
        except ValueError:
            semester = 3

        # 6. Academic Metrics
        attendance = cls._clean_numeric(get_val("attendance"), default=75.0, min_val=0.0, max_val=100.0)
        study_hours = cls._clean_numeric(get_val("study_hours_weekly"), default=12.0, min_val=0.0, max_val=70.0)
        midterm = cls._clean_numeric(get_val("midterm_score"), default=65.0, min_val=0.0, max_val=100.0)
        assignment = cls._clean_numeric(get_val("assignment_score"), default=70.0, min_val=0.0, max_val=100.0)
        lab = cls._clean_numeric(get_val("lab_score"), default=75.0, min_val=0.0, max_val=100.0)

        return {
            "student_id": student_id,
            "name": name,
            "email": email,
            "phone": phone,
            "department": department,
            "semester": semester,
            "attendance": attendance,
            "study_hours_weekly": study_hours,
            "midterm_score": midterm,
            "assignment_score": assignment,
            "lab_score": lab
        }

    @classmethod
    def process_csv_content(
        cls,
        csv_text: str,
        db_manager,
        predictor,
        adapt_model: bool = False
    ) -> Dict[str, Any]:
        """
        Parses CSV string, applies adaptive mapping, generates AI predictions,
        and saves records to the database.
        """
        stream = io.StringIO(csv_text.strip())
        reader = csv.DictReader(stream)

        if not reader.fieldnames:
            raise ValidationError("The uploaded CSV file is empty or missing headers.")

        mapping, unmapped = cls.build_header_mapping(reader.fieldnames)

        existing_students = db_manager.get_all_students(limit=5000)
        existing_ids = {s["student_id"] for s in existing_students}

        adapted_records = []
        errors = []

        for idx, row in enumerate(reader, start=1):
            try:
                adapted = cls.sanitize_and_adapt_row(row, mapping, idx, existing_ids)
                
                # Run AI Prediction
                pred = predictor.predict({
                    "attendance": adapted["attendance"],
                    "study_hours_weekly": adapted["study_hours_weekly"],
                    "midterm_score": adapted["midterm_score"],
                    "assignment_score": adapted["assignment_score"],
                    "lab_score": adapted["lab_score"]
                })

                adapted["predicted_grade"] = pred["predicted_grade"]
                adapted["predicted_gpa"] = pred["predicted_gpa"]
                adapted["risk_level"] = pred["risk_level"]

                adapted_records.append(adapted)
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")

        if not adapted_records:
            raise ValidationError(f"No valid student rows could be parsed from the CSV. Errors: {'; '.join(errors[:3])}")

        # Batch upsert into database
        upsert_stats = db_manager.batch_upsert_students(adapted_records)

        # Optional Adaptive Model Retraining
        model_retrained = False
        retrain_stats = None
        if adapt_model:
            from ..ml.train import retrain_from_database
            retrain_stats = retrain_from_database(db_manager)
            predictor.reload_model()
            model_retrained = True

        return {
            "total_rows": len(adapted_records),
            "inserted": upsert_stats.get("inserted", 0),
            "updated": upsert_stats.get("updated", 0),
            "errors": errors,
            "mapped_columns": mapping,
            "unmapped_columns": unmapped,
            "model_retrained": model_retrained,
            "retrain_stats": retrain_stats
        }
