import pandas as pd
import joblib
import ast
import os
import random
import matplotlib.pyplot as plt
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "final_dataset.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "film_model.pkl"


# =========================
# CLEAN FEATURE
# =========================
def clean_feature(text):
    return str(text).strip().lower().replace("_", " ")


# =========================
# BUILD MODEL
# =========================
def train_model():
    os.makedirs("../models", exist_ok=True)
    df = pd.read_csv(CSV_PATH)

    def combine_features(row):
        features = []
        for col in ["genres", "labels", "species"]:
            if col in df.columns and pd.notna(row[col]):
                try:
                    parsed = ast.literal_eval(row[col])
                    if isinstance(parsed, list):
                        features.extend(parsed)
                except:
                    pass
        return set(clean_feature(f) for f in features)

    feature_matrix = dict(zip(df["title"], df.apply(combine_features, axis=1)))

    joblib.dump(feature_matrix, MODEL_PATH)

    print("Model saved.")
    return feature_matrix


# =========================
# MONTE CARLO CHART (REPORT)
# =========================
def generate_jaccard_distribution_analysis(feature_matrix, n_simulations=1000, top_k=5):

    all_features = list(set().union(*feature_matrix.values()))

    all_top_scores = []
    all_pairwise_scores = []

    for _ in range(n_simulations):

        sample_size = random.randint(1, 4)
        selected = random.sample(all_features, sample_size)
        user_set = set(clean_feature(f) for f in selected)

        # top-k simulation
        scores = []
        for title, feats in feature_matrix.items():
            union = user_set | feats
            inter = user_set & feats
            score = len(inter) / len(union) if union else 0
            scores.append(score)

        scores.sort(reverse=True)
        all_top_scores.extend(scores[:top_k])

        # full matrix sparsity
        for feats in feature_matrix.values():
            union = user_set | feats
            inter = user_set & feats
            all_pairwise_scores.append(len(inter) / len(union) if union else 0)

    # =========================
    # PLOTS
    # =========================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.hist(all_pairwise_scores, bins=20, color="steelblue")
    ax1.set_title("Global Jaccard Sparsity")
    ax1.set_xlabel("Similarity")
    ax1.set_ylabel("Count")

    ax2.hist(all_top_scores, bins=20, color="orange")
    ax2.set_title("Top-K Recommendation Quality")
    ax2.set_xlabel("Score")
    ax2.set_ylabel("Count")

    plt.tight_layout()
    plt.savefig("jaccard_report.png", dpi=300)

    print("Chart saved: jaccard_report.png")


# =========================
# RUN EVERYTHING FOR REPORT
# =========================
if __name__ == "__main__":
    matrix = train_model()
    generate_jaccard_distribution_analysis(matrix)