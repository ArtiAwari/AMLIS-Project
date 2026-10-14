# Legal Document Category Prediction Using Machine Learning
> **An End-to-End Applied Machine Learning and Intelligent Systems (AMLIS) Academic Project**

[![Python Version](https://img.shields.io/badge/Python-3.14%2B-blue.svg)](https://python.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9.0-orange.svg)](https://scikit-learn.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-black.svg)](https://flask.palletsprojects.com)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.28.2-red.svg)](https://pymupdf.readthedocs.io)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-purple.svg)](https://getbootstrap.com)
[![License: Academic](https://img.shields.io/badge/License-Educational%20Use-green.svg)](#)

---

## 📌 Project Overview
**Legal Document Category Prediction** is a comprehensive, production-ready full-stack machine learning web application engineered for college academic evaluation and viva demonstration. 

The application accepts legal agreements, deeds, judicial transcripts, and contracts in **PDF** or **Plain Text (.txt)** formats (or direct text paste), automatically extracts and normalizes the text using NLP, transforms it into sparse **TF-IDF unigram and bigram feature representations**, and classifies the document across **10 legal categories** using calibrated supervised machine learning algorithms.

### ⚖️ Supported Document Categories
1. **Non-Disclosure Agreement (NDA)**
2. **Rental or Lease Agreement**
3. **Employment Contract**
4. **Service Agreement**
5. **Privacy Policy**
6. **Terms and Conditions**
7. **Court Judgment**
8. **Power of Attorney**
9. **Sale or Purchase Agreement**
10. **Other / Unclassified**

---

## 🏛️ System Architecture

```
                       ┌─────────────────────────┐
                       │  Legal Document Ingest  │
                       │  (PDF / TXT / Paste)    │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │  PyMuPDF Text Extractor │
                       │  (Encoding & OCR Check) │
                       └────────────┬────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │             Scikit-Learn Preprocessing Pipeline        │
       │  • Case Normalization & Regex Sanitization             │
       │  • Domain Stopword Filtering (Legal Modal Preservation)│
       │  • Sublinear TF-IDF Vectorization (Unigram + Bigram)   │
       └────────────────────────────┬───────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
    ┌───────────────────────────┐       ┌───────────────────────────┐
    │    Supervised Inference   │       │   Unsupervised Discovery  │
    │  • Multinomial Naive Bayes│       │  • K-Means Clustering     │
    │  • Logistic Regression    │       │  • TruncatedSVD 2D Proj.  │
    │  • Calibrated Linear SVM  │       │    (Latent Pattern Map)   │
    └─────────────┬─────────────┘       └─────────────┬─────────────┘
                  │                                   │
                  ▼                                   ▼
    ┌───────────────────────────┐       ┌───────────────────────────┐
    │     Explainable Output    │       │     Interactive Visual    │
    │  • Predicted Class & Prob │       │  • Centroid Keywords      │
    │  • Indicative Key Terms   │       │  • 2D Scatter Chart.js    │
    │  • SQLite Audit Trail     │       │                           │
    │  • Downloadable PDF / TXT │       │                           │
    └───────────────────────────┘       └───────────────────────────┘
```

---

## 🚀 Key Modules & AMLIS Syllabus Concepts

| AMLIS Concept | Implementation in Project | File Reference |
| :--- | :--- | :--- |
| **A. Data Preprocessing** | Dropping empty rows, hashing duplicate text records, regex normalization, preserving legal words (`not`, `shall`, `liable`, `covenant`). | [`app/ml/preprocessor.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/preprocessor.py) |
| **B. Exploratory Data Analysis (EDA)** | Length distributions, vocabulary frequency profiling, class imbalance diagnostics. | [`app/ml/dataset_loader.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/dataset_loader.py) |
| **C. Feature Engineering** | Unigram + bigram TF-IDF sparse matrices with sublinear term-frequency scaling. | [`app/ml/preprocessor.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/preprocessor.py) |
| **D. Supervised Learning** | Benchmarks Multinomial Naive Bayes, Logistic Regression, and Calibrated Linear SVM. | [`app/ml/model_trainer.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/model_trainer.py) |
| **E. Model Validation** | Stratified train/test split, Stratified K-Fold CV, preventing data leakage via `Pipeline`. | [`app/ml/model_trainer.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/model_trainer.py) |
| **F. Performance Metrics** | Accuracy, Precision, Recall, Macro F1, Weighted F1, Confusion Matrix heatmap. | [`app/ml/model_trainer.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/model_trainer.py) |
| **G. Hyperparameter Tuning** | GridSearchCV optimization over Laplace smoothing $\alpha$ and n-gram ranges. | [`app/ml/model_trainer.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/model_trainer.py) |
| **H. Unsupervised Learning** | K-Means document clustering on TF-IDF space with prominent centroid keyword extraction. | [`app/ml/clustering.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/clustering.py) |
| **I. Dimensionality Reduction** | TruncatedSVD sparse matrix decomposition for 2D visual scatter projection. | [`app/ml/clustering.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/clustering.py) |
| **J. Feature Interpretation** | Extracts top indicative terms by inspecting linear classifier coefficients and log-probabilities. | [`app/ml/predictor.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/predictor.py) |
| **K. Model Persistence** | Serializes the complete fitted Pipeline and metadata with `joblib`. | [`app/ml/model_trainer.py`](file:///c:/Users/awari/OneDrive/Desktop/AML%20Project/app/ml/model_trainer.py) |

---

## 🛠️ Technology Stack
- **Backend**: Python 3.14, Flask 3.1
- **Machine Learning**: scikit-learn 1.9, NumPy, pandas
- **PDF Extraction**: PyMuPDF 1.28 (`fitz`)
- **Report Generation**: ReportLab 5.0 (PDF generator)
- **Database**: SQLite 3 (parameterized SQL queries)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6), Bootstrap 5.3, Chart.js 4.4
- **Testing**: pytest 9.1

---

## 💻 Installation & Quickstart

### 1. Clone or Open Project
```powershell
cd "c:\Users\awari\OneDrive\Desktop\AML Project"
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Automated Tests
```powershell
python -m pytest -v
```
*(All 21 unit & integration tests should pass.)*

### 4. Start the Web Application
```powershell
python run.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Quick Demonstration Walkthrough (Viva / Practical Exam)

1. **Document Classification (`/classify`)**:
   - Click one of the quick sample loaders (e.g., **Sample NDA**, **Sample Lease**, **Sample Employment**, or **Sample Judgment**).
   - Alternatively, drag and drop `sample_documents/sample_nda.pdf` or `sample_documents/sample_lease.pdf`.
   - Click **Predict Document Category**.
   - Observe the predicted class badge, calibrated confidence score, and **Top Indicative Lexical Terms** (e.g., *proprietary, confidential, disclosing party*).
   - Click **Download PDF Report** to view the formatted report generated on the fly with ReportLab!
2. **Dashboard (`/dashboard`)**:
   - Inspect live KPI statistics (Total documents, class count, best model, test accuracy).
   - View the **Category Distribution** doughnut chart and **Model Comparison** bar chart.
   - Inspect the interactive **Confusion Matrix** with green true-positive diagonal cells.
3. **Model Evaluation (`/evaluation`)**:
   - Review the benchmarking table comparing Naive Bayes, Logistic Regression, and Linear SVM across Accuracy, Macro Precision, Macro Recall, and Macro F1.
   - Inspect the per-class classification report and the GridSearchCV optimization results.
   - Download the full academic evaluation PDF report.
4. **Dataset Explorer (`/dataset`)**:
   - Search through the training records with live filtering.
   - Click **Retrain Machine Learning Models** to trigger training across all three algorithms with live notifications.
5. **Prediction History (`/history`)**:
   - Inspect the SQLite audit log recording each classified document, confidence, and timestamp.
   - Test search, filtering, and single/all deletion controls.
6. **AMLIS Concepts (`/concepts`)**:
   - Interact with the **2D TruncatedSVD and K-Means Explorer** by dynamically toggling cluster counts ($k=3, 4, 5, 6, 8$) and hovering over data points to explain unsupervised clustering to the external examiner!
   - Review the built-in **Viva Examination Q&A**.

---

## 🎓 Viva Oral Examination Q&A Guide

### Q1: Why is TF-IDF preferred over Bag-of-Words (CountVectorizer) for legal texts?
> **Answer**: Bag-of-Words simply counts raw term frequencies. In legal contracts, boilerplate terms such as *"party"*, *"agreement"*, and *"terms"* occur frequently across all document types and would dominate the feature space without providing discriminative value. **TF-IDF** penalizes terms that appear ubiquitously across the entire corpus using the Inverse Document Frequency (IDF) factor, while amplifying distinctive terms such as *"sublet"* (Leases) or *"severance"* (Employment).

### Q2: Why is Macro F1-Score chosen as the model selection criterion instead of Accuracy?
> **Answer**: Accuracy can be deceptive when class distributions are imbalanced. For instance, in a dataset where 80% of documents belong to two dominant classes, an uncalibrated classifier could achieve 80% accuracy while failing completely on rare contract types. **Macro F1-Score** calculates the F1-score independently for each legal category and averages them unweighted, ensuring every category is evaluated with equal importance.

### Q3: How is Data Leakage prevented in this implementation?
> **Answer**: Data leakage is prevented by encapsulating both the `TfidfVectorizer` and the classifier inside a unified `sklearn.pipeline.Pipeline`. The dataset is split into training and test partitions *prior* to feature extraction. The vectorizer calls `fit_transform()` exclusively on the training partition. The unseen test set is transformed strictly with `transform()`, ensuring terms unique to the test set never contaminate the vocabulary or IDF weights.

### Q4: Why is LinearSVC wrapped inside CalibratedClassifierCV?
> **Answer**: Standard `LinearSVC` minimizes hinge loss and produces signed functional margins (distances to the decision boundary) rather than probabilistic outputs. Wrapping it in `CalibratedClassifierCV` applies sigmoid **Platt Scaling** over cross-validation folds to transform raw decision scores into mathematically valid posterior probabilities that sum to 1.0.

### Q5: What is the difference between Unsupervised K-Means and Supervised Classification?
> **Answer**: Supervised classification learns a mapping from text features to user-defined ground truth labels ($y$) to predict discrete target categories. K-Means is an unsupervised clustering algorithm that ignores labels entirely and groups documents into $k$ clusters solely by minimizing within-cluster inertia in the TF-IDF feature space. Discovered clusters indicate emergent lexical patterns, not legal validity.

---

## 📂 Project Directory Structure

```
AML Project/
├── app/
│   ├── __init__.py               # Flask application factory & error handlers
│   ├── config.py                 # Configuration settings (upload, DB, paths)
│   ├── database.py               # SQLite database access layer (parameterized queries)
│   ├── ml/
│   │   ├── preprocessor.py       # PyMuPDF text extractor, legal stopwords & tokenizer
│   │   ├── dataset_loader.py     # CSV validation, duplicate detection & EDA summary
│   │   ├── model_trainer.py      # Tri-model training, GridSearchCV, metrics & persistence
│   │   ├── predictor.py          # Inference service & indicative term extraction
│   │   ├── clustering.py         # K-Means clustering & TruncatedSVD 2D dimensionality reduction
│   │   └── report_generator.py   # PDF and TXT report generation with ReportLab
│   ├── routes/
│   │   ├── views.py              # HTML page rendering routes
│   │   └── api.py                # REST API endpoints (classify, retrain, stats, reports)
│   ├── static/
│   │   ├── css/style.css         # Modern navy/gold legal-tech design system
│   │   └── js/main.js            # Client-side logic, drag-and-drop & Chart.js visualizers
│   └── templates/
│       ├── base.html             # Base layout with navbar, footer & disclaimers
│       ├── index.html            # Home page & pipeline overview
│       ├── classify.html         # Interactive classification workspace
│       ├── dashboard.html        # Live metrics & Chart.js dashboards
│       ├── evaluation.html       # Tri-algorithm benchmarks & classification reports
│       ├── dataset.html          # Corpus explorer & retraining controls
│       ├── history.html          # SQLite audit trail
│       └── concepts.html         # AMLIS academic curriculum guide & viva prep
├── data/
│   ├── sample_legal_dataset.csv  # 80 illustrative legal records across 10 classes
│   ├── create_sample_dataset.py  # Dataset generation script
│   └── README.md                 # Real-world dataset import instructions (CUAD, LexGLUE)
├── models/
│   ├── best_model.joblib         # Serialized best Pipeline (TfidfVectorizer + Classifier)
│   └── evaluation_results.json   # Full benchmark metrics & confusion matrices
├── sample_documents/             # Pre-generated demonstrative test files
│   ├── sample_nda.pdf
│   ├── sample_lease.pdf
│   ├── sample_employment.txt
│   └── sample_court_judgment.txt
├── tests/                        # 21 comprehensive pytest unit & integration tests
│   ├── test_preprocessor.py
│   ├── test_dataset_loader.py
│   ├── test_models.py
│   ├── test_database.py
│   └── test_api.py
├── run.py                        # Application entry point
├── requirements.txt              # Dependency specifications
└── README.md                     # Comprehensive academic documentation
```

---

## ⚠️ Academic Disclaimer
This software is developed strictly as an educational and academic demonstration project for the **Applied Machine Learning and Intelligent Systems (AMLIS)** curriculum. Predictions generated by this system are based on statistical linguistic correlations and do not constitute legal advice, professional legal consultation, or certification of document enforceability.
