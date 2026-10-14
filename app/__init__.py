"""
Flask Application Factory for Legal Document Category Prediction.
"""
import os
from flask import Flask, render_template
from app.config import Config
from app.database import init_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["MODELS_DIR"], exist_ok=True)

    # Initialize SQLite database
    init_db()

    # Register Blueprints
    from app.routes.views import views_bp
    from app.routes.api import api_bp

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("base.html", error_message="Page Not Found (404)"), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template("base.html", error_message="Uploaded file is too large (Maximum allowed size: 16 MB)"), 413

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("base.html", error_message="Internal Server Error (500)"), 500

    return app
