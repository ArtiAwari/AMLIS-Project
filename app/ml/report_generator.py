"""
Report Generation Service for Classification and Model Evaluation.
Generates structured PDF and TXT reports with academic formatting and legal disclaimers.
"""
import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_classification_txt(result: Dict[str, Any], filename: str = "Pasted_Text") -> str:
    """Generates plain text classification report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conf = f"{result.get('confidence_score_percent', 'N/A')}%" if result.get("confidence_available") else "Not Available"
    
    terms = ", ".join([t["term"] for t in result.get("indicative_terms", [])]) or "None extracted"
    
    report = f"""========================================================================
LEGAL DOCUMENT CATEGORY PREDICTION - ACADEMIC CLASSIFICATION REPORT
========================================================================
Project Title     : Legal Document Category Prediction Using Machine Learning
Course            : Applied Machine Learning and Intelligent Systems (AMLIS)
Generated At      : {timestamp}
Document Source   : {filename}
------------------------------------------------------------------------
PREDICTION SUMMARY
------------------------------------------------------------------------
Predicted Category: {result.get('predicted_category', 'Unknown')}
Model Utilized    : {result.get('model_used', 'N/A')}
Confidence Score  : {conf}
Top Terms Ranked  : {terms}
Text Statistics   : {result.get('text_statistics', {}).get('raw_char_count', 0)} characters | {result.get('text_statistics', {}).get('token_count', 0)} tokens

CLASS PROBABILITY DISTRIBUTION:
"""
    for item in result.get("all_class_scores", []):
        report += f"  - {item['category']:<35} : {item['score']}%\n"

    report += f"""
------------------------------------------------------------------------
EDUCATIONAL DISCLAIMER:
{result.get('disclaimer', 'This report is generated for educational evaluation purposes only.')}
========================================================================
"""
    return report


def generate_classification_pdf(result: Dict[str, Any], filename: str = "Pasted_Text") -> bytes:
    """Generates styled PDF classification report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f223d")
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b")
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#6b7280")
    )

    story = []
    
    # Title & Header
    story.append(Paragraph("Legal Document Category Prediction", title_style))
    story.append(Paragraph("Machine Learning & Applied NLP Academic Report", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#d4af37"), spaceAfter=15))

    # Meta Table
    timestamp = datetime.now().strftime("%B %d, %Y - %H:%M:%S")
    conf = f"{result.get('confidence_score_percent', 'N/A')}%" if result.get("confidence_available") else "N/A"
    
    meta_data = [
        [Paragraph("<b>Document Source:</b>", body_style), Paragraph(filename, body_style)],
        [Paragraph("<b>Date & Time:</b>", body_style), Paragraph(timestamp, body_style)],
        [Paragraph("<b>Predicted Category:</b>", body_style), Paragraph(f"<b><font color='#0f223d'>{result.get('predicted_category')}</font></b>", body_style)],
        [Paragraph("<b>Model Architecture:</b>", body_style), Paragraph(result.get("model_used", "N/A"), body_style)],
        [Paragraph("<b>Confidence Score:</b>", body_style), Paragraph(conf, body_style)]
    ]
    t = Table(meta_data, colWidths=[140, 390])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Indicative Terms
    story.append(Paragraph("Indicative Model Terms Contributing to Classification", heading_style))
    terms = [t["term"] for t in result.get("indicative_terms", [])]
    terms_str = ", ".join(terms) if terms else "No specific dominant vocabulary triggers identified."
    story.append(Paragraph(f"<b>Key Contributing Terms:</b> {terms_str}", body_style))
    story.append(Spacer(1, 15))

    # Probability Distribution
    scores = result.get("all_class_scores", [])
    if scores:
        story.append(Paragraph("Probability Distribution Breakdown Across Legal Categories", heading_style))
        table_rows = [["Legal Document Category", "Calibrated Confidence (%)"]]
        for item in scores[:8]:
            table_rows.append([item["category"], f"{item['score']}%"])
        
        score_table = Table(table_rows, colWidths=[380, 150])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f223d")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 15))

    # Disclaimer Box
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
    story.append(Paragraph("<b>Educational Use Disclaimer:</b> " + result.get("disclaimer", ""), disclaimer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_evaluation_pdf(eval_data: Dict[str, Any]) -> bytes:
    """Generates styled PDF model evaluation report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "EvalTitle", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#0f223d")
    )
    heading_style = ParagraphStyle(
        "EvalHeading", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#1e3a8a"), spaceAfter=6
    )
    body_style = ParagraphStyle(
        "EvalBody", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#1e293b")
    )

    story = []
    story.append(Paragraph("AMLIS Model Benchmark & Evaluation Report", title_style))
    story.append(Paragraph("Legal Document Category Classification Experiment Results", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#d4af37"), spaceAfter=12))

    # Summary
    best_model = eval_data.get("best_model_name", "N/A")
    samples = eval_data.get("dataset_size", 0)
    train_s = eval_data.get("train_samples", 0)
    test_s = eval_data.get("test_samples", 0)
    vocab = eval_data.get("vocabulary_size", 0)
    
    summary_text = f"Dataset: {samples} records ({train_s} training, {test_s} test) | Vocabulary Features: {vocab} | Selected Model: <b>{best_model}</b>"
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 12))

    # Comparison Table
    story.append(Paragraph("Comparative Model Performance Metrics (Test Set)", heading_style))
    models_dict = eval_data.get("models", {})
    headers = ["Model Architecture", "Accuracy", "Macro Precision", "Macro Recall", "Macro F1", "Weighted F1"]
    rows = [headers]
    for m_name, m_stats in models_dict.items():
        rows.append([
            m_name,
            f"{m_stats.get('accuracy', 0):.4f}",
            f"{m_stats.get('macro_precision', 0):.4f}",
            f"{m_stats.get('macro_recall', 0):.4f}",
            f"{m_stats.get('macro_f1', 0):.4f}",
            f"{m_stats.get('weighted_f1', 0):.4f}"
        ])

    table = Table(rows, colWidths=[150, 75, 75, 75, 75, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f223d")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    story.append(Spacer(1, 15))

    # Hyperparameter Tuning
    tuning = eval_data.get("hyperparameter_tuning", {})
    if tuning and tuning.get("algorithm"):
        story.append(Paragraph("GridSearchCV Hyperparameter Optimization", heading_style))
        tune_str = f"Algorithm: {tuning.get('algorithm')} | Best Params: {tuning.get('best_params')} | Best CV Macro F1: {tuning.get('best_cv_score')}"
        story.append(Paragraph(tune_str, body_style))
        story.append(Spacer(1, 15))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
