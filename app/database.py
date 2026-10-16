"""
SQLite Database Access Layer with Parameterized Queries.
Manages prediction history, training runs, and auditing records.
Avoids storing sensitive raw legal documents by default, preserving only non-sensitive snippets.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

Tuple_Results = Tuple[List[Dict[str, Any]], int]
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "legal_classifier.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite database tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                predicted_category TEXT NOT NULL,
                confidence_score REAL,
                model_used TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                word_count INTEGER NOT NULL,
                indicative_terms TEXT,
                snippet TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Model training runs history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trained_at TEXT NOT NULL,
                dataset_rows INTEGER NOT NULL,
                best_model TEXT NOT NULL,
                macro_f1 REAL NOT NULL,
                accuracy REAL NOT NULL
            )
        """)
        conn.commit()


def save_prediction(
    filename: str,
    predicted_category: str,
    confidence_score: Optional[float],
    model_used: str,
    char_count: int,
    word_count: int,
    indicative_terms: str,
    snippet: str
) -> int:
    """Inserts prediction record using parameterized query."""
    created_at = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions 
            (filename, predicted_category, confidence_score, model_used, char_count, word_count, indicative_terms, snippet, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename, predicted_category, confidence_score, model_used,
            char_count, word_count, indicative_terms, snippet, created_at
        ))
        conn.commit()
        return cursor.lastrowid


def get_predictions(
    limit: int = 50,
    offset: int = 0,
    search: str = "",
    category: str = ""
) -> Tuple_Results:
    """Retrieves paginated and filtered prediction records."""
    query = "SELECT * FROM predictions WHERE 1=1"
    params = []

    if search:
        query += " AND (filename LIKE ? OR snippet LIKE ? OR indicative_terms LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])

    if category:
        query += " AND predicted_category = ?"
        params.append(category)

    # Count total matching
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Get total count
        cursor.execute(count_query, params[:-2])
        total_count = cursor.fetchone()[0]

        # Get records
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]

    return rows, total_count


def delete_prediction(prediction_id: int) -> bool:
    """Deletes a single prediction record by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_all_predictions() -> int:
    """Deletes all history records from predictions table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions")
        conn.commit()
        return cursor.rowcount


def log_training_run(dataset_rows: int, best_model: str, macro_f1: float, accuracy: float) -> int:
    """Records a model retraining event."""
    trained_at = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO training_runs (trained_at, dataset_rows, best_model, macro_f1, accuracy)
            VALUES (?, ?, ?, ?, ?)
        """, (trained_at, dataset_rows, best_model, macro_f1, accuracy))
        conn.commit()
        return cursor.lastrowid
