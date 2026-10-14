# Dataset Documentation & Real-World Import Guide

## Academic Context & Educational Scope
This dataset is an **illustrative academic dataset** compiled for demonstration and examination of the **Legal Document Category Prediction** project. 

### Why is an Illustrative Dataset Provided?
1. **Reproducibility**: Small, self-contained dataset runnable locally without requiring multi-gigabyte downloads or high-memory servers.
2. **Class Coverage**: Covers 10 distinct legal document classes with standard legal clauses, nomenclature, and terminology:
   - Non-Disclosure Agreement (NDA)
   - Rental or Lease Agreement
   - Employment Contract
   - Service Agreement
   - Privacy Policy
   - Terms and Conditions
   - Court Judgment
   - Power of Attorney
   - Sale or Purchase Agreement
   - Other / Unclassified
3. **Transparency**: All records are explicitly identified as educational samples. No claims of production-grade accuracy on synthetic records are made.

---

## Schema Requirements
The application expects a CSV file containing at least the following 3 columns:
- `document_id`: Unique identifier for each record (e.g., `DOC_001`).
- `text`: Full raw text content of the legal document.
- `category`: Ground truth category/label string.

Optional columns (e.g. `file_path`, `source_year`) are safely ignored by the ingestion pipeline.

---

## How to Import a Real-World Dataset

To train the model on real legal corpora:
1. **Public Legal Benchmark Datasets**:
   - **CUAD (Contract Understanding Atticus Dataset)**: 500+ commercial contracts curated by The Atticus Project ([Law.Stanford.edu](https://www.atticusprojectai.org/cuad)).
   - **LexGLUE (Legal General Language Understanding Evaluation)**: Benchmark covering ECtHR judgments, SCOTUS opinions, and EURLEX legislation ([Hugging Face LexGLUE](https://huggingface.co/datasets/lex_glue)).
   - **Kaggle Legal Text Classification**: Datasets with labeled legal agreements and judicial orders.
2. **Formatting**:
   Format your exported data into a CSV matching `document_id, text, category`.
3. **Uploading**:
   Navigate to the **Dataset Explorer** tab (`/dataset`) in the web interface and upload your CSV. The application validates column headers, cleans empty/duplicate rows, computes updated class distributions, and allows the administrator to trigger one-click retraining!
