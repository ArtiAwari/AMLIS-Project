"""
Unit Tests for Dataset Loader and Validation Module.
"""
import io
import os
import pytest
import pandas as pd
from app.ml.dataset_loader import validate_and_load_dataset, compute_eda_summary

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_legal_dataset.csv")


def test_validate_and_load_valid_dataset():
    df, report = validate_and_load_dataset(DATASET_PATH)
    assert report.is_valid is True
    assert len(df) >= 10
    assert report.unique_categories == 10
    assert "document_id" in df.columns
    assert "text" in df.columns
    assert "category" in df.columns


def test_validate_missing_columns():
    csv_data = "doc_id,content\n1,some text\n2,more text\n"
    df, report = validate_and_load_dataset(io.StringIO(csv_data))
    assert report.is_valid is False
    assert len(report.missing_columns) > 0


def test_validate_empty_rows_and_duplicates():
    csv_data = (
        "document_id,text,category\n"
        "1,,NDA\n"
        "2,Valid NDA text,NDA\n"
        "3,Valid NDA text,NDA\n"  # Duplicate
        "4,Another valid text,Lease\n"
    )
    df, report = validate_and_load_dataset(io.StringIO(csv_data))
    assert report.missing_text_count == 1
    assert report.duplicate_count == 1


def test_compute_eda_summary():
    df, report = validate_and_load_dataset(DATASET_PATH)
    eda = compute_eda_summary(df)
    assert eda["total_documents"] == len(df)
    assert eda["unique_categories"] == 10
    assert "doc_length_chars" in eda
    assert "doc_length_words" in eda
    assert len(eda["top_corpus_terms"]) > 0
    assert len(eda["class_breakdown"]) == 10
