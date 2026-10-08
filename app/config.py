"""
Application Configuration
Configures file paths, secret keys, database location, and ML model settings.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = BASE_DIR / "database" / "students.db"
MODELS_DIR = BASE_DIR / "app" / "ml" / "models"

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "edupulse-ai-secret-key-tcet-aiml-2026")
    DATABASE = str(DATABASE_PATH)
    MODELS_DIR = str(MODELS_DIR)
    DATA_DIR = str(DATA_DIR)
    DEBUG = True
