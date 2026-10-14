"""
Unit Tests for SQLite Database Storage Layer.
"""
import pytest
from app.database import (
    init_db, save_prediction, get_predictions,
    delete_prediction, clear_all_predictions, log_training_run
)


def test_database_crud_operations():
    init_db()
    # Clear any previous test artifacts
    clear_all_predictions()

    # Insert a prediction
    pred_id = save_prediction(
        filename="test_nda.pdf",
        predicted_category="Non-Disclosure Agreement (NDA)",
        confidence_score=88.5,
        model_used="Linear Support Vector Machine",
        char_count=450,
        word_count=70,
        indicative_terms="confidential, proprietary",
        snippet="This Agreement governs confidential materials..."
    )
    assert pred_id > 0

    # Retrieve predictions
    rows, total = get_predictions(limit=10)
    assert total >= 1
    assert rows[0]["filename"] == "test_nda.pdf"
    assert rows[0]["predicted_category"] == "Non-Disclosure Agreement (NDA)"

    # Test search query
    search_rows, s_total = get_predictions(search="proprietary")
    assert s_total >= 1

    # Delete single prediction
    assert delete_prediction(pred_id) is True
    rows_after, total_after = get_predictions()
    assert total_after == 0

    # Test log training run
    run_id = log_training_run(
        dataset_rows=80,
        best_model="Linear Support Vector Machine",
        macro_f1=0.95,
        accuracy=0.95
    )
    assert run_id > 0
