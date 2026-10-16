"""
Integration Tests for Flask Endpoints and REST API.
"""
import io
import os
import pytest
from app import create_app

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents")


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Legal Document Category Prediction" in response.data


def test_views_routes(client):
    routes = ["/classify", "/evaluation", "/dataset", "/history", "/concepts"]
    for route in routes:
        res = client.get(route)
        assert res.status_code == 200


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] in ["healthy", "degraded"]


def test_api_classify_direct_text(client):
    payload = {
        "text": (
            "RESIDENTIAL APARTMENT LEASE AGREEMENT. The Landlord hereby leases the demised apartment "
            "to Tenant for a term of twelve months. Tenant agrees to pay monthly rent of $2,100 on the "
            "first day of each month and furnish a security deposit."
        )
    }
    res = client.post("/api/classify", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["predicted_category"] == "Rental or Lease Agreement"
    assert "indicative_terms" in data


def test_api_classify_uploaded_pdf(client):
    pdf_path = os.path.join(SAMPLE_DIR, "sample_nda.pdf")
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    data = {
        "file": (io.BytesIO(file_bytes), "sample_nda.pdf")
    }
    res = client.post("/api/classify", data=data, content_type="multipart/form-data")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True
    assert json_data["predicted_category"] == "Non-Disclosure Agreement (NDA)"



def test_api_evaluation_data(client):
    res = client.get("/api/evaluation-data")
    assert res.status_code == 200
    data = res.get_json()
    assert "models" in data
    assert "best_model_name" in data


def test_api_clustering_data(client):
    res = client.get("/api/clustering-data?k=4")
    assert res.status_code == 200
    data = res.get_json()
    assert data["n_clusters"] == 4
    assert len(data["clusters"]) == 4


def test_api_reports(client):
    # Test TXT classification report
    payload = {
        "predicted_category": "Non-Disclosure Agreement (NDA)",
        "model_used": "Linear Support Vector Machine",
        "confidence_available": True,
        "confidence_score_percent": 88.5,
        "filename": "sample.pdf",
        "format": "txt"
    }
    res_txt = client.post("/api/download-report", json=payload)
    assert res_txt.status_code == 200
    assert b"LEGAL DOCUMENT CATEGORY PREDICTION" in res_txt.data

    # Test PDF classification report
    payload["format"] = "pdf"
    res_pdf = client.post("/api/download-report", json=payload)
    assert res_pdf.status_code == 200
    assert res_pdf.data.startswith(b"%PDF")

    # Test Model Evaluation PDF report
    res_eval_pdf = client.get("/api/download-evaluation-report")
    assert res_eval_pdf.status_code == 200
    assert res_eval_pdf.data.startswith(b"%PDF")
