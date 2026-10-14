"""
REST API Blueprint for Legal Document Category Prediction.
Provides endpoints for document upload, text extraction, inference,
model evaluation, dataset inspection, retraining, and history management.
"""
import os
import io
import uuid
import tempfile
from flask import Blueprint, request, jsonify, send_file, current_app, Response
from werkzeug.utils import secure_filename

from app.ml.preprocessor import extract_text_from_pdf, extract_text_from_txt
from app.ml.predictor import predictor_service
from app.ml.model_trainer import (
    load_evaluation_results, train_and_evaluate_models
)
from app.ml.dataset_loader import (
    validate_and_load_dataset, compute_eda_summary
)
from app.ml.clustering import run_clustering_and_svd
from app.ml.report_generator import (
    generate_classification_pdf, generate_classification_txt, generate_evaluation_pdf
)
from app.database import (
    save_prediction, get_predictions, delete_prediction,
    clear_all_predictions, log_training_run
)

api_bp = Blueprint("api", __name__)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@api_bp.route("/health", methods=["GET"])
def health_check():
    """System health and readiness check."""
    model_ready = predictor_service.is_model_ready()
    return jsonify({
        "status": "healthy" if model_ready else "degraded",
        "model_ready": model_ready,
        "database_connected": True
    })


@api_bp.route("/classify", methods=["POST"])
def classify_document():
    """
    Accepts uploaded file (PDF/TXT) or raw text and performs category prediction.
    """
    raw_text = ""
    source_filename = "Direct Text Input"
    extract_meta = {}

    # 1. Process Uploaded File if provided
    if "file" in request.files and request.files["file"].filename != "":
        uploaded_file = request.files["file"]
        orig_filename = uploaded_file.filename

        if not allowed_file(orig_filename):
            return jsonify({
                "success": False,
                "error": "Unsupported file format. Please upload a PDF (.pdf) or Plain Text (.txt) document."
            }), 400

        source_filename = secure_filename(orig_filename)
        ext = source_filename.rsplit(".", 1)[1].lower()

        # Write to temporary file with randomized name
        temp_dir = tempfile.gettempdir()
        temp_filename = f"legal_doc_{uuid.uuid4().hex}.{ext}"
        temp_path = os.path.join(temp_dir, temp_filename)

        try:
            uploaded_file.save(temp_path)

            if ext == "pdf":
                raw_text, extract_meta = extract_text_from_pdf(temp_path)
                if extract_meta.get("is_scanned"):
                    return jsonify({
                        "success": False,
                        "error": "The uploaded PDF appears to be a scanned image or empty. Optical Character Recognition (OCR) is required for scanned non-selectable PDFs."
                    }), 400
            elif ext == "txt":
                raw_text, extract_meta = extract_text_from_txt(temp_path)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to extract document contents: {str(e)}"
            }), 500
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)  # Always clean up temporary file

    # 2. Alternatively check raw text input
    elif "text" in request.form and request.form["text"].strip():
        raw_text = request.form["text"].strip()
        source_filename = "Pasted Legal Text"
    elif request.is_json and "text" in request.json and request.json["text"].strip():
        raw_text = request.json["text"].strip()
        source_filename = "Pasted Legal Text"
    else:
        return jsonify({
            "success": False,
            "error": "No document uploaded or text provided for classification."
        }), 400

    if not raw_text or len(raw_text.strip()) < 20:
        return jsonify({
            "success": False,
            "error": "Document contains insufficient text content to classify reliably (minimum 20 characters required)."
        }), 400

    # 3. Perform Prediction
    result = predictor_service.predict(raw_text)
    if not result.get("success"):
        return jsonify(result), 400

    # 4. Save Record to SQLite History (saving only snippet for confidentiality)
    snippet = raw_text[:200].replace("\n", " ").strip()
    if len(raw_text) > 200:
        snippet += "..."
    indicative_str = ", ".join([t["term"] for t in result.get("indicative_terms", [])])

    pred_id = save_prediction(
        filename=source_filename,
        predicted_category=result["predicted_category"],
        confidence_score=result.get("confidence_score_percent"),
        model_used=result["model_used"],
        char_count=len(raw_text),
        word_count=len(raw_text.split()),
        indicative_terms=indicative_str,
        snippet=snippet
    )

    result["prediction_id"] = pred_id
    result["filename"] = source_filename
    result["text_preview"] = raw_text[:800] + ("..." if len(raw_text) > 800 else "")

    return jsonify(result)


@api_bp.route("/dashboard-data", methods=["GET"])
def get_dashboard_data():
    """Returns aggregated metrics and charts data for the dashboard."""
    eval_data = load_evaluation_results()
    dataset_path = current_app.config["DEFAULT_DATASET_PATH"]
    df, val_report = validate_and_load_dataset(dataset_path)

    if eval_data is None:
        return jsonify({
            "status": "not_trained",
            "message": "No model evaluation data available. Retrain via Dataset tab."
        })

    # Prepare model comparison data for Chart.js
    models_comparison = []
    for m_name, m_stats in eval_data.get("models", {}).items():
        models_comparison.append({
            "model_name": m_name,
            "accuracy": round(m_stats.get("accuracy", 0) * 100, 2),
            "macro_precision": round(m_stats.get("macro_precision", 0) * 100, 2),
            "macro_recall": round(m_stats.get("macro_recall", 0) * 100, 2),
            "macro_f1": round(m_stats.get("macro_f1", 0) * 100, 2),
            "weighted_f1": round(m_stats.get("weighted_f1", 0) * 100, 2),
            "cv_mean_f1": round(m_stats.get("cv_mean_f1", 0) * 100, 2)
        })

    return jsonify({
        "status": "ready",
        "dataset_size": eval_data.get("dataset_size", len(df)),
        "unique_categories": len(eval_data.get("classes", [])),
        "best_model_name": eval_data.get("best_model_name"),
        "selection_metric": eval_data.get("selection_metric"),
        "classes": eval_data.get("classes", []),
        "class_distribution": eval_data.get("class_distribution", {}),
        "models_comparison": models_comparison,
        "best_model_metrics": eval_data.get("models", {}).get(eval_data.get("best_model_name"), {})
    })


@api_bp.route("/evaluation-data", methods=["GET"])
def get_evaluation_data():
    """Returns detailed evaluation benchmarks, confusion matrices, and tuning."""
    eval_data = load_evaluation_results()
    if not eval_data:
        return jsonify({"error": "Evaluation report not found. Please train models first."}), 404
    return jsonify(eval_data)


@api_bp.route("/dataset-stats", methods=["GET"])
def get_dataset_stats():
    """Returns EDA summary and records preview for the active dataset."""
    dataset_path = current_app.config["DEFAULT_DATASET_PATH"]
    df, val_report = validate_and_load_dataset(dataset_path)
    eda = compute_eda_summary(df)

    preview_rows = []
    if not df.empty:
        for _, row in df.head(10).iterrows():
            preview_rows.append({
                "document_id": str(row["document_id"]),
                "category": str(row["category"]),
                "snippet": str(row["text"])[:140] + "..." if len(str(row["text"])) > 140 else str(row["text"]),
                "word_count": len(str(row["text"]).split())
            })

    return jsonify({
        "validation_report": val_report.to_dict(),
        "eda_summary": eda,
        "preview_rows": preview_rows
    })


@api_bp.route("/dataset/upload", methods=["POST"])
def upload_dataset():
    """
    Allows administrator/user to upload a custom CSV dataset for retraining.
    Validates structure before committing.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded."}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"success": False, "error": "Empty filename."}), 400

    if not uploaded_file.filename.endswith(".csv"):
        return jsonify({"success": False, "error": "Dataset must be a CSV file (.csv)."}), 400

    # Read and validate in memory before writing to disk
    try:
        content = uploaded_file.read()
        df, report = validate_and_load_dataset(io.BytesIO(content))

        if not report.is_valid:
            return jsonify({
                "success": False,
                "error": "Dataset validation failed: " + "; ".join(report.errors),
                "report": report.to_dict()
            }), 400

        # Save validated dataset
        target_path = current_app.config["DEFAULT_DATASET_PATH"]
        df.to_csv(target_path, index=False)

        return jsonify({
            "success": True,
            "message": f"Successfully loaded and saved dataset with {len(df)} records across {report.unique_categories} categories.",
            "report": report.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to parse dataset: {str(e)}"}), 500


@api_bp.route("/retrain", methods=["POST"])
def retrain_models():
    """
    Executes ML training pipeline across all 3 candidate algorithms,
    updates best model, and recalculates benchmarks.
    """
    dataset_path = current_app.config["DEFAULT_DATASET_PATH"]
    df, report = validate_and_load_dataset(dataset_path)

    if not report.is_valid:
        return jsonify({
            "success": False,
            "error": "Cannot retrain: dataset is invalid. " + "; ".join(report.errors)
        }), 400

    try:
        results = train_and_evaluate_models(df)
        predictor_service.reload()

        best_m = results["best_model_name"]
        best_stats = results["models"][best_m]
        log_training_run(
            dataset_rows=len(df),
            best_model=best_m,
            macro_f1=best_stats.get("macro_f1", 0.0),
            accuracy=best_stats.get("accuracy", 0.0)
        )

        return jsonify({
            "success": True,
            "message": f"Retraining complete! Best model selected: {best_m}",
            "best_model": best_m,
            "macro_f1": best_stats.get("macro_f1"),
            "accuracy": best_stats.get("accuracy")
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Retraining failed: {str(e)}"}), 500


@api_bp.route("/clustering-data", methods=["GET"])
def get_clustering_data():
    """
    Runs K-Means clustering and TruncatedSVD on the active dataset for interactive visualization.
    """
    dataset_path = current_app.config["DEFAULT_DATASET_PATH"]
    df, _ = validate_and_load_dataset(dataset_path)
    
    clusters_k = request.args.get("k", default=5, type=int)
    clusters_k = max(2, min(10, clusters_k))

    clustering_res = run_clustering_and_svd(df, n_clusters=clusters_k)
    return jsonify(clustering_res)


@api_bp.route("/history", methods=["GET"])
def list_history():
    """Fetches paginated prediction history records."""
    limit = request.args.get("limit", default=25, type=int)
    offset = request.args.get("offset", default=0, type=int)
    search = request.args.get("search", default="", type=str)
    category = request.args.get("category", default="", type=str)

    rows, total_count = get_predictions(limit=limit, offset=offset, search=search, category=category)
    return jsonify({
        "records": rows,
        "total": total_count,
        "limit": limit,
        "offset": offset
    })


@api_bp.route("/history/<int:pred_id>", methods=["DELETE"])
def remove_history_item(pred_id: int):
    """Deletes a single prediction entry."""
    deleted = delete_prediction(pred_id)
    return jsonify({"success": deleted})


@api_bp.route("/history/clear", methods=["DELETE"])
def clear_history():
    """Deletes all history records."""
    count = clear_all_predictions()
    return jsonify({"success": True, "deleted_count": count})


@api_bp.route("/download-report", methods=["POST"])
def download_classification_report():
    """Generates and streams a downloadable PDF or TXT classification report."""
    data = request.json or {}
    report_format = data.get("format", "pdf").lower()
    filename = data.get("filename", "Legal_Document")

    if report_format == "txt":
        txt_content = generate_classification_txt(data, filename)
        return Response(
            txt_content,
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment;filename=Classification_Report_{filename}.txt"}
        )
    else:
        pdf_bytes = generate_classification_pdf(data, filename)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Classification_Report_{filename}.pdf"
        )


@api_bp.route("/download-evaluation-report", methods=["GET"])
def download_eval_report():
    """Streams a downloadable PDF model evaluation report."""
    eval_data = load_evaluation_results()
    if not eval_data:
        return jsonify({"error": "No evaluation results found"}), 404

    pdf_bytes = generate_evaluation_pdf(eval_data)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="AMLIS_Model_Evaluation_Report.pdf"
    )
