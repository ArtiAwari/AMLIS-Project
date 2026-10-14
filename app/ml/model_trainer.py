"""
Machine Learning Model Training, Comparison, and Evaluation Module.
Trains Multinomial Naive Bayes, Logistic Regression, and Calibrated Linear SVM.
Performs Stratified Cross-Validation, GridSearchCV hyperparameter tuning,
evaluates comprehensive classification metrics, and persists the best model using Joblib.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    classification_report, confusion_matrix
)

from app.ml.preprocessor import clean_legal_text, legal_tokenizer

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.joblib")
EVALUATION_JSON_PATH = os.path.join(MODELS_DIR, "evaluation_results.json")


def build_pipeline(classifier) -> Pipeline:
    """
    Constructs a reproducible scikit-learn Pipeline with TF-IDF Vectorizer
    and the designated classifier.
    """
    vectorizer = TfidfVectorizer(
        preprocessor=clean_legal_text,
        tokenizer=legal_tokenizer,
        token_pattern=None,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )
    return Pipeline([
        ("tfidf", vectorizer),
        ("clf", classifier)
    ])


def train_and_evaluate_models(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Trains all candidate algorithms on the dataset, evaluates performance,
    tunes hyperparameters, compares results, selects the best model, and saves artifacts.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)

    X = df["text"].values
    y = df["category"].values

    classes = sorted(list(set(y)))
    class_counts = df["category"].value_counts().to_dict()
    min_count = min(class_counts.values())

    # Train/Test Split logic
    can_stratify = min_count >= 2
    stratify_target = y if can_stratify else None
    
    # 80/20 train/test split
    test_size = 0.20 if len(df) >= 40 else 0.25
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=stratify_target
    )

    # Cross-validation folds
    cv_folds = max(2, min(5, min_count))
    cv_strategy = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42) if can_stratify else 3

    # Define Candidate Classifiers
    # Note: LinearSVC is wrapped in CalibratedClassifierCV to provide valid posterior probabilities
    candidates = {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(
            C=1.0, max_iter=1000, class_weight="balanced", random_state=42
        ),
        "Linear Support Vector Machine": CalibratedClassifierCV(
            estimator=LinearSVC(C=1.0, class_weight="balanced", random_state=42),
            method="sigmoid",
            cv=3 if can_stratify and min_count >= 3 else 2
        )
    }

    results = {}
    fitted_pipelines = {}

    for name, clf in candidates.items():
        pipeline = build_pipeline(clf)

        # Cross-validation score on training set to prevent data leakage
        try:
            cv_scores = cross_val_score(
                pipeline, X_train, y_train, cv=cv_strategy, scoring="f1_macro"
            )
            cv_mean = float(np.mean(cv_scores))
            cv_std = float(np.std(cv_scores))
        except Exception as e:
            cv_mean = 0.0
            cv_std = 0.0

        # Fit on full training set
        pipeline.fit(X_train, y_train)
        fitted_pipelines[name] = pipeline

        # Evaluate on unseen test set
        y_pred = pipeline.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_test, y_pred, average="macro", zero_division=0
        )
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_test, y_pred, average="weighted", zero_division=0
        )

        cm = confusion_matrix(y_test, y_pred, labels=classes).tolist()
        report_dict = classification_report(
            y_test, y_pred, labels=classes, output_dict=True, zero_division=0
        )

        results[name] = {
            "model_name": name,
            "accuracy": round(acc, 4),
            "macro_precision": round(float(p_macro), 4),
            "macro_recall": round(float(r_macro), 4),
            "macro_f1": round(float(f1_macro), 4),
            "weighted_f1": round(float(f1_weighted), 4),
            "cv_mean_f1": round(cv_mean, 4),
            "cv_std_f1": round(cv_std, 4),
            "confusion_matrix": cm,
            "classification_report": report_dict
        }

    # Hyperparameter Tuning Demonstration using GridSearchCV
    tuning_summary = {}
    try:
        nb_pipeline = build_pipeline(MultinomialNB())
        param_grid = {
            "clf__alpha": [0.01, 0.1, 0.5, 1.0],
            "tfidf__ngram_range": [(1, 1), (1, 2)]
        }
        grid_search = GridSearchCV(
            nb_pipeline, param_grid, cv=cv_strategy, scoring="f1_macro", n_jobs=1
        )
        grid_search.fit(X_train, y_train)
        tuning_summary = {
            "algorithm": "Multinomial Naive Bayes",
            "best_params": {
                "alpha": float(grid_search.best_params_["clf__alpha"]),
                "ngram_range": list(grid_search.best_params_["tfidf__ngram_range"])
            },
            "best_cv_score": round(float(grid_search.best_score_), 4),
            "tested_param_grid": {
                "alpha": [0.01, 0.1, 0.5, 1.0],
                "ngram_range": ["(1,1)", "(1,2)"]
            }
        }
    except Exception as e:
        tuning_summary = {"status": "skipped", "reason": str(e)}

    # Model Selection: Pick model with highest Macro F1-score
    best_name = max(results.keys(), key=lambda k: (results[k]["macro_f1"], results[k]["accuracy"]))
    best_pipeline = fitted_pipelines[best_name]
    best_metrics = results[best_name]

    # Inspect vocabulary size
    vocab_size = len(best_pipeline.named_steps["tfidf"].vocabulary_)

    # Save Best Model Artifact with metadata
    model_artifact = {
        "pipeline": best_pipeline,
        "model_name": best_name,
        "classes": classes,
        "trained_at": datetime.now().isoformat(),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "vocabulary_size": vocab_size,
        "metrics": best_metrics
    }
    joblib.dump(model_artifact, BEST_MODEL_PATH)

    # Save Full Evaluation Report JSON
    full_evaluation = {
        "timestamp": datetime.now().isoformat(),
        "dataset_size": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "classes": classes,
        "class_distribution": class_counts,
        "stratified_split": can_stratify,
        "best_model_name": best_name,
        "selection_metric": "Macro F1-Score (balances multi-class performance equally)",
        "vocabulary_size": vocab_size,
        "models": results,
        "hyperparameter_tuning": tuning_summary
    }

    with open(EVALUATION_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(full_evaluation, f, indent=2)

    return full_evaluation


def load_best_model_artifact() -> Dict[str, Any]:
    """
    Loads saved best model artifact from disk.
    Returns None if file does not exist or fails to load.
    """
    if not os.path.exists(BEST_MODEL_PATH):
        return None
    try:
        artifact = joblib.load(BEST_MODEL_PATH)
        return artifact
    except Exception as e:
        print(f"Error loading model artifact: {e}")
        return None


def load_evaluation_results() -> Dict[str, Any]:
    """
    Loads saved evaluation JSON results.
    """
    if not os.path.exists(EVALUATION_JSON_PATH):
        return None
    try:
        with open(EVALUATION_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading evaluation results: {e}")
        return None
