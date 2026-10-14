"""
Unsupervised Learning and Dimensionality Reduction Module.
Implements K-Means clustering on TF-IDF sparse feature matrices and
TruncatedSVD 2D dimensionality reduction for interactive exploratory visualization.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD

from app.ml.preprocessor import clean_legal_text, legal_tokenizer


def run_clustering_and_svd(df: pd.DataFrame, n_clusters: int = 5) -> Dict[str, Any]:
    """
    Executes K-Means document clustering and TruncatedSVD 2D projection.
    Returns cluster profiles, top keywords per cluster, and 2D coordinates for plotting.
    """
    if df.empty or len(df) < n_clusters:
        return {
            "error": "Dataset too small for clustering demonstration (requires more documents than clusters)."
        }

    texts = df["text"].values
    categories = df["category"].values
    doc_ids = df["document_id"].values

    # 1. Feature Engineering: Sparse TF-IDF Representation
    vectorizer = TfidfVectorizer(
        preprocessor=clean_legal_text,
        tokenizer=legal_tokenizer,
        token_pattern=None,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = np.array(vectorizer.get_feature_names_out())

    # 2. Unsupervised Clustering: K-Means
    actual_clusters = min(n_clusters, len(df))
    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(tfidf_matrix)

    # Extract top keywords per cluster centroid
    centroids = kmeans.cluster_centers_
    cluster_terms = []
    for c_idx, centroid in enumerate(centroids):
        top_indices = centroid.argsort()[-6:][::-1]
        top_words = feature_names[top_indices].tolist()
        cluster_terms.append({
            "cluster_id": int(c_idx),
            "label": f"Cluster {c_idx + 1}",
            "top_terms": top_words,
            "document_count": int(np.sum(cluster_labels == c_idx))
        })

    # 3. Dimensionality Reduction: TruncatedSVD (2 Components)
    svd = TruncatedSVD(n_components=2, random_state=42)
    coords_2d = svd.fit_transform(tfidf_matrix)
    explained_variance = [round(float(v) * 100, 2) for v in svd.explained_variance_ratio_]

    # Structure plot points
    plot_points = []
    for i in range(len(df)):
        plot_points.append({
            "document_id": str(doc_ids[i]),
            "x": round(float(coords_2d[i, 0]), 4),
            "y": round(float(coords_2d[i, 1]), 4),
            "cluster_id": int(cluster_labels[i]),
            "category": str(categories[i]),
            "snippet": str(texts[i][:120]) + ("..." if len(texts[i]) > 120 else "")
        })

    return {
        "n_clusters": actual_clusters,
        "n_documents": len(df),
        "explained_variance_ratio_percent": explained_variance,
        "clusters": cluster_terms,
        "points": plot_points,
        "academic_note": (
            "K-Means discovers latent clusters based on TF-IDF cosine distance in an unsupervised manner. "
            "TruncatedSVD projects high-dimensional sparse text vectors into 2 dimensions for human inspection. "
            "Clusters represent statistical lexical patterns and do not strictly dictate legal validity."
        )
    }
