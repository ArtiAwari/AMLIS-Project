"""
Text Preprocessing and Extraction Module for Legal Documents.
Handles PDF and TXT text extraction, text normalization, legal-specific stopword filtering,
and tokenization for the scikit-learn pipeline.
"""
import re
import os
from typing import Tuple, List, Optional
import pymupdf  # PyMuPDF


# Standard English stopwords with legal domain terms preserved
# Preserves critical legal modal verbs, negations, and relational words that alter legal meaning
DEFAULT_LEGAL_STOPWORDS = {
    "a", "about", "above", "after", "again", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "both", "by", 
    "can", "did", "do", "does", "doing", "down", "during", "each", "few", "for", 
    "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", 
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", 
    "its", "itself", "just", "me", "more", "most", "my", "myself", "of", "off", "on", 
    "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", 
    "same", "she", "should", "so", "some", "such", "than", "that", "the", "their", 
    "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", 
    "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", 
    "what", "when", "where", "which", "while", "who", "whom", "why", "with", "you", 
    "your", "yours", "yourself", "yourselves"
}

# Explicitly kept legal keywords (even if normally in stopwords lists)
LEGAL_PRESERVED_WORDS = {
    "not", "no", "nor", "against", "without", "between", "shall", "may", 
    "liable", "liability", "party", "parties", "herein", "therein", "whereas",
    "covenant", "warranty", "indemnify", "breach", "remedy", "court", "claim"
}

LEGAL_STOPWORDS = DEFAULT_LEGAL_STOPWORDS - LEGAL_PRESERVED_WORDS


def extract_text_from_pdf(pdf_path_or_bytes) -> Tuple[str, dict]:
    """
    Extracts text from a PDF document using PyMuPDF.
    Returns (extracted_text, metadata).
    """
    metadata = {
        "page_count": 0,
        "is_scanned": False,
        "char_count": 0,
        "error": None
    }
    
    try:
        if isinstance(pdf_path_or_bytes, (str, os.PathLike)):
            doc = pymupdf.open(pdf_path_or_bytes)
        else:
            doc = pymupdf.open(stream=pdf_path_or_bytes, filetype="pdf")
            
        metadata["page_count"] = len(doc)
        text_chunks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text("text")
            if page_text:
                text_chunks.append(page_text)
                
        doc.close()
        full_text = "\n".join(text_chunks).strip()
        metadata["char_count"] = len(full_text)
        
        # Heuristic to detect scanned/image-only PDFs
        if metadata["page_count"] > 0 and len(full_text.strip()) < 30:
            metadata["is_scanned"] = True
            
        return full_text, metadata
        
    except Exception as e:
        metadata["error"] = str(e)
        return "", metadata


def extract_text_from_txt(txt_path_or_bytes) -> Tuple[str, dict]:
    """
    Extracts text from a plain TXT file or byte stream.
    Tries utf-8, then falls back to latin-1.
    """
    metadata = {"char_count": 0, "error": None}
    
    try:
        if isinstance(txt_path_or_bytes, (str, os.PathLike)):
            with open(txt_path_or_bytes, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        else:
            try:
                content = txt_path_or_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = txt_path_or_bytes.decode("latin-1", errors="replace")
                
        content = content.strip()
        metadata["char_count"] = len(content)
        return content, metadata
        
    except Exception as e:
        metadata["error"] = str(e)
        return "", metadata


def clean_legal_text(text: str) -> str:
    """
    Normalizes legal text:
    - Normalizes case to lowercase
    - Replaces bullet points, unusual quotation marks, and unicode dashes
    - Removes non-alphanumeric punctuation while retaining section symbols, numbers, and hyphens
    - Normalizes multi-whitespace and newlines
    """
    if not text or not isinstance(text, str):
        return ""
        
    # Convert to lowercase
    text = text.lower()
    
    # Replace unicode quotes and dashes with standard ASCII
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    text = text.replace("—", " ").replace("–", " ").replace("…", " ")
    
    # Replace non-printable ASCII and control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
    
    # Keep alphanumeric characters, legal section symbol §, and basic spaces
    text = re.sub(r'[^a-z0-9§\s]', ' ', text)
    
    # Normalize multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def legal_tokenizer(text: str) -> List[str]:
    """
    Custom tokenizer for legal text that filters out domain-irrelevant stopwords
    while retaining important legal indicators and tokens of length >= 2.
    """
    cleaned = clean_legal_text(text)
    tokens = cleaned.split()
    filtered_tokens = [
        t for t in tokens 
        if len(t) >= 2 and (t not in LEGAL_STOPWORDS or t in LEGAL_PRESERVED_WORDS)
    ]
    return filtered_tokens
