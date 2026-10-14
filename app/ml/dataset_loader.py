"""
Dataset Loading and Exploratory Data Analysis (EDA) Module.
Handles CSV dataset ingestion, schema validation, cleaning, duplicate detection,
and statistical analysis of the legal corpus.
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from collections import Counter
from app.ml.preprocessor import legal_tokenizer, clean_legal_text

REQUIRED_COLUMNS = ["document_id", "text", "category"]


class DatasetValidationReport:
    def __init__(self):
        self.is_valid: bool = True
        self.total_rows: int = 0
        self.valid_rows: int = 0
        self.missing_columns: list = []
        self.missing_text_count: int = 0
        self.missing_category_count: int = 0
        self.duplicate_count: int = 0
        self.unique_categories: int = 0
        self.category_distribution: Dict[str, int] = {}
        self.min_class_count: int = 0
        self.errors: list = []
        self.warnings: list = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "missing_columns": self.missing_columns,
            "missing_text_count": self.missing_text_count,
            "missing_category_count": self.missing_category_count,
            "duplicate_count": self.duplicate_count,
            "unique_categories": self.unique_categories,
            "category_distribution": self.category_distribution,
            "min_class_count": self.min_class_count,
            "errors": self.errors,
            "warnings": self.warnings
        }


def validate_and_load_dataset(filepath_or_buffer) -> Tuple[pd.DataFrame, DatasetValidationReport]:
    """
    Validates CSV structure and loads data into a cleaned DataFrame.
    Returns (cleaned_df, validation_report).
    """
    report = DatasetValidationReport()
    
    try:
        if isinstance(filepath_or_buffer, (str, os.PathLike)):
            if not os.path.exists(filepath_or_buffer):
                report.is_valid = False
                report.errors.append(f"Dataset file not found: {filepath_or_buffer}")
                return pd.DataFrame(), report
            df = pd.read_csv(filepath_or_buffer, encoding="utf-8", on_bad_lines="skip")
        else:
            df = pd.read_csv(filepath_or_buffer, encoding="utf-8", on_bad_lines="skip")
    except Exception as e:
        report.is_valid = False
        report.errors.append(f"Failed to read CSV dataset: {str(e)}")
        return pd.DataFrame(), report

    report.total_rows = len(df)
    
    # 1. Column header validation
    existing_cols = [c.strip().lower() for c in df.columns]
    column_mapping = {}
    for req in REQUIRED_COLUMNS:
        match = [orig for orig in df.columns if orig.strip().lower() == req]
        if match:
            column_mapping[match[0]] = req
        else:
            report.missing_columns.append(req)

    if report.missing_columns:
        report.is_valid = False
        report.errors.append(f"Missing mandatory columns: {', '.join(report.missing_columns)}")
        return pd.DataFrame(), report

    # Rename columns to standard names
    df = df.rename(columns=column_mapping)
    df = df[REQUIRED_COLUMNS].copy()

    # 2. Check missing values
    missing_text_mask = df["text"].isna() | (df["text"].astype(str).str.strip() == "")
    report.missing_text_count = int(missing_text_mask.sum())

    missing_cat_mask = df["category"].isna() | (df["category"].astype(str).str.strip() == "")
    report.missing_category_count = int(missing_cat_mask.sum())

    # Filter out empty or unusable records
    df = df[~missing_text_mask & ~missing_cat_mask].copy()
    df["text"] = df["text"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["document_id"] = df["document_id"].astype(str).str.strip()

    # 3. Check duplicate documents
    duplicates_mask = df.duplicated(subset=["text"], keep="first")
    report.duplicate_count = int(duplicates_mask.sum())
    if report.duplicate_count > 0:
        report.warnings.append(f"Removed {report.duplicate_count} duplicate text documents.")
        df = df[~duplicates_mask].copy()

    report.valid_rows = len(df)

    if report.valid_rows < 10:
        report.is_valid = False
        report.errors.append(f"Dataset has only {report.valid_rows} valid records. Minimum 10 required for training.")
        return df, report

    # 4. Class distribution analysis
    distribution = df["category"].value_counts().to_dict()
    report.category_distribution = {str(k): int(v) for k, v in distribution.items()}
    report.unique_categories = len(distribution)
    report.min_class_count = int(min(distribution.values())) if distribution else 0

    if report.unique_categories < 2:
        report.is_valid = False
        report.errors.append("Dataset must contain at least 2 distinct legal categories for classification.")

    if report.min_class_count < 2:
        report.warnings.append(
            f"Some categories have fewer than 2 examples (min count: {report.min_class_count}). "
            "Stratified train/test split will require at least 2 examples per category."
        )

    return df, report


def compute_eda_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes Exploratory Data Analysis metrics on the cleaned dataframe.
    """
    if df.empty or "text" not in df.columns:
        return {}

    # Document length statistics
    char_lengths = df["text"].str.len()
    word_lengths = df["text"].apply(lambda t: len(t.split()))

    # Global top terms using legal tokenizer
    all_tokens = []
    for text in df["text"].head(200):  # Sample for speed if large
        all_tokens.extend(legal_tokenizer(text))
    top_terms = Counter(all_tokens).most_common(20)

    # Category breakdown
    class_counts = df["category"].value_counts()
    class_stats = []
    for cat, count in class_counts.items():
        cat_texts = df[df["category"] == cat]["text"]
        cat_word_lens = cat_texts.apply(lambda t: len(t.split()))
        class_stats.append({
            "category": str(cat),
            "count": int(count),
            "percentage": round(float(count / len(df) * 100), 1),
            "avg_words": round(float(cat_word_lens.mean()), 1)
        })

    return {
        "total_documents": int(len(df)),
        "unique_categories": int(df["category"].nunique()),
        "doc_length_chars": {
            "mean": round(float(char_lengths.mean()), 1),
            "median": round(float(char_lengths.median()), 1),
            "min": int(char_lengths.min()),
            "max": int(char_lengths.max()),
            "std": round(float(char_lengths.std()), 1)
        },
        "doc_length_words": {
            "mean": round(float(word_lengths.mean()), 1),
            "median": round(float(word_lengths.median()), 1),
            "min": int(word_lengths.min()),
            "max": int(word_lengths.max()),
            "std": round(float(word_lengths.std()), 1)
        },
        "top_corpus_terms": [{"term": t[0], "count": int(t[1])} for t in top_terms],
        "class_breakdown": class_stats
    }
