"""
Unit Tests for Model Training, Evaluation, and Predictor Service.
"""
import os
import pytest
from app.ml.dataset_loader import validate_and_load_dataset
from app.ml.model_trainer import (
    train_and_evaluate_models, load_best_model_artifact, load_evaluation_results
)
from app.ml.predictor import predictor_service
from app.ml.clustering import run_clustering_and_svd

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_legal_dataset.csv")


def test_model_training_and_artifacts():
    df, report = validate_and_load_dataset(DATASET_PATH)
    results = train_and_evaluate_models(df)

    assert "best_model_name" in results
    assert "models" in results
    assert len(results["models"]) == 3

    for model_name, stats in results["models"].items():
        assert 0.0 <= stats["accuracy"] <= 1.0
        assert 0.0 <= stats["macro_f1"] <= 1.0
        assert "confusion_matrix" in stats
        assert "classification_report" in stats

    # Verify saved artifact
    artifact = load_best_model_artifact()
    assert artifact is not None
    assert "pipeline" in artifact
    assert len(artifact["classes"]) == 10


def test_predictor_service_inference():
    predictor_service.reload()
    assert predictor_service.is_model_ready() is True

    # Test NDA inference
    nda_text = (
        "MUTUAL NON-DISCLOSURE AGREEMENT. The Receiving Party agrees to protect "
        "and maintain all trade secrets, proprietary algorithms, and confidential materials "
        "disclosed by the Disclosing Party in strictest confidence for a term of five years."
    )
    res = predictor_service.predict(nda_text)
    assert res["success"] is True
    assert res["predicted_category"] == "Non-Disclosure Agreement (NDA)"
    assert res["confidence_available"] is True
    assert res["confidence_score_percent"] > 50.0
    assert len(res["indicative_terms"]) > 0

    # Test input too short
    short_res = predictor_service.predict("Too short")
    assert short_res["success"] is False
    assert "too short" in short_res["error"]


def test_clustering_and_svd():
    df, _ = validate_and_load_dataset(DATASET_PATH)
    cluster_res = run_clustering_and_svd(df, n_clusters=4)
    assert "n_clusters" in cluster_res
    assert cluster_res["n_clusters"] == 4
    assert len(cluster_res["clusters"]) == 4
    assert len(cluster_res["points"]) == len(df)
    assert "explained_variance_ratio_percent" in cluster_res
