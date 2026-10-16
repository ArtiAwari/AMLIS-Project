"""
Frontend Page Rendering Views Blueprint.
Renders all client-facing pages with navigation context.
"""
from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def home():
    return render_template("index.html", active_page="home")


@views_bp.route("/classify")
def classify():
    return render_template("classify.html", active_page="classify")



@views_bp.route("/evaluation")
def evaluation():
    return render_template("evaluation.html", active_page="evaluation")


@views_bp.route("/dataset")
def dataset():
    return render_template("dataset.html", active_page="dataset")


@views_bp.route("/history")
def history():
    return render_template("history.html", active_page="history")


@views_bp.route("/concepts")
def concepts():
    return render_template("concepts.html", active_page="concepts")
