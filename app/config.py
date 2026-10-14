"""
Configuration settings for the Flask application.
"""
import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(24))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB maximum upload
    ALLOWED_EXTENSIONS = {"pdf", "txt"}
    
    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, "legal_classifier.db")
    
    # Dataset and Models
    DEFAULT_DATASET_PATH = os.path.join(BASE_DIR, "data", "sample_legal_dataset.csv")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.joblib")
    EVALUATION_JSON_PATH = os.path.join(MODELS_DIR, "evaluation_results.json")
    
    # Admin demo token for local demonstration
    ADMIN_TOKEN = os.environ.get("ADMIN_DEMO_TOKEN", "academic-demo-2026")
