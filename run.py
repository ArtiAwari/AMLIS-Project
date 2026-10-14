"""
Application Entry Point for Legal Document Category Prediction.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 70)
    print("Starting Legal Document Category Prediction Web Application...")
    print("Access application at: http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host="127.0.0.1", port=5000, debug=True)
