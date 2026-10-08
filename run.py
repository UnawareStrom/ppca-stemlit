"""
EduPulse AI - Application Entry Point
Starts the Flask server for local development and demonstration.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app

app = create_app()

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    port = int(os.environ.get("PORT", 5000))
    print("===========================================================")
    print(f"EduPulse AI Server starting on http://127.0.0.1:{port}")
    print("TCET AIML Semester-III Python Programming Mini Project")
    print("===========================================================")
    app.run(host="127.0.0.1", port=port, debug=False)
