"""
WSGI Entry Point for Production Deployment (Gunicorn / Waitress / Render / Railway).
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Production fallback
    try:
        from waitress import serve
        print(f"Starting Waitress production WSGI server on port {port}...")
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        app.run(host="0.0.0.0", port=port)
