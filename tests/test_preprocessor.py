"""
Unit Tests for Text Preprocessor and Extraction Modules.
"""
import os
import pytest
from app.ml.preprocessor import (
    clean_legal_text, legal_tokenizer,
    extract_text_from_pdf, extract_text_from_txt,
    LEGAL_PRESERVED_WORDS
)

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents")


def test_clean_legal_text():
    raw = "THIS is a NON-DISCLOSURE AGREEMENT — § 4.1... Under Delaware Law!"
    cleaned = clean_legal_text(raw)
    assert "this is a non disclosure agreement" in cleaned
    assert "delaware law" in cleaned
    assert "—" not in cleaned
    assert "!" not in cleaned


def test_legal_tokenizer_preserves_legal_words():
    # Words like 'shall', 'not', 'liable' must be preserved despite being stopword-like
    text = "The employee shall not be liable under this contract"
    tokens = legal_tokenizer(text)
    assert "employee" in tokens
    assert "contract" in tokens
    assert "shall" in tokens
    assert "not" in tokens
    assert "liable" in tokens
    # Common stopwords like 'the', 'be', 'under', 'this' should be removed
    assert "the" not in tokens
    assert "under" not in tokens


def test_extract_text_from_pdf():
    pdf_path = os.path.join(SAMPLE_DIR, "sample_nda.pdf")
    assert os.path.exists(pdf_path)
    text, meta = extract_text_from_pdf(pdf_path)
    assert meta["error"] is None
    assert meta["page_count"] >= 1
    assert "NON-DISCLOSURE" in text or "CONFIDENTIAL" in text
    assert meta["is_scanned"] is False


def test_extract_text_from_txt():
    txt_path = os.path.join(SAMPLE_DIR, "sample_employment.txt")
    assert os.path.exists(txt_path)
    text, meta = extract_text_from_txt(txt_path)
    assert meta["error"] is None
    assert "EXECUTIVE EMPLOYMENT AGREEMENT" in text
    assert len(text) > 100
