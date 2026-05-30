import pandas as pd
import joblib
import ast
import os
import numpy as np
import random
import matplotlib.pyplot as plt

# --- FastAPI Web Infrastructure Imports ---
from fastapi import FastAPI, Query
from typing import List
import uvicorn

# =========================
# PATHS
# =========================
CSV_PATH = "../data/processed/final_dataset.csv"
MODEL_PATH = "../models/film_model.pkl"

# --- Initialize FastAPI Microservice Instance ---
app = FastAPI(
    title="Studio Ghibli Recommendation API",
    description="Decoupled Jaccard Similarity inference engine for STAT 418.",
    version="1.0.0"
)


# =========================
# CLEANING HELPER
# =========================
def clean_feature(text):
    return str(text).strip().lower().replace("_", " ")


# =========================
# TRAIN MODEL
# =========================
def train_model():
    os.makedirs("../models", exist_ok=True)
    df = pd.read_csv(CSV_PATH)

    def combine_features(row):
        features = []
        for col in ["genres", "labels", "species"]:
            if col in df.columns and pd.notna(row[col]):
                value = row[col]
                try:
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, list):
                        features.extend(parsed)
                except (ValueError, SyntaxError):
                    pass
        return [clean_feature(f) for f in features]

    df["features"] = df.apply(combine_features, axis=1)

    # Save a clean mapping dictionary of Title -> Set of Features
    feature_matrix = dict(zip(df["title"], df["features"].apply(set)))

    joblib.dump(feature_matrix, MODEL_PATH)
    print("Content feature matrix compiled and saved successfully!")
    return feature_matrix


# =========================
# PREDICT FILMS (Optimized File Loading)
# =========================
def predict_films(selected_features, top_k=5, feature_matrix=None, exclude_title=None):
    # Only load from disk if matrix isn't explicitly passed (prevents I/O thrashing)
    if feature_matrix is None:
        if os.path.exists(MODEL_PATH):
            feature_matrix = joblib.load(MODEL_PATH)
        else:
            raise FileNotFoundError(f"Model matrix not found at {MODEL_PATH}. Please train model first.")

    user_features = set(clean_feature(f) for f in selected_features)

    if not user_features:
        titles = [t for t in feature_matrix.keys() if t != exclude_title][:top_k]
        return pd.DataFrame({"title": titles, "score": [0.0] * len(titles)})

    scores = []
    for title, movie_features in feature_matrix.items():
        if title == exclude_title:
            continue  # Filter out seed movie during evaluations

        intersection = user_features.intersection(movie_features)
        union = user_features.union(movie_features)

        jaccard_score = len(intersection) / len(union) if union else 0.0
        scores.append({"title": title, "score": jaccard_score})

    results = pd.DataFrame(scores)
    results = results[results["score"] > 0.0]
    return results.sort_values(by="score", ascending=False).head(top_k)


# =========================
# MICROSERVICE ENDPOINT ROUTE
# =========================
@app.get("/recommend")
def get_recommendations(features: List[str] = Query(None), top_k: int = 5):
    """
    Exposes recommendation matrix logic over an HTTP GET network request.
    Streamlit UI calls this endpoint passing user selections.
    """
    if not features:
        return {"recommendations": []}

    # Run the core prediction logic
    results_df = predict_films(features, top_k=top_k)

    # Format pandas DataFrame entries into a clean JSON dictionary payload
    return {"recommendations": results_df.to_dict(orient="records")}


# =========================
# MODEL EVALUATION METRICS
# =========================
def evaluate_recommender(feature_matrix):
    """
    Simulates user profiles based on actual movie features to calculate Hit Rate and MRR,
    ensuring a movie does not self-recommend.
    """
    df = pd.read_csv(CSV_PATH)

    hits_at_5 = 0
    reciprocal_ranks = []
    total_tests = 0

    for _, row in df.iterrows():
        target_title = row['title']
        movie_features = feature_matrix.get(target_title, set())

        if len(movie_features) < 2:
            continue

        # Simulate user input: Take a subset of 2 features belonging to this film
        user_input_features = list(movie_features)[:2]

        # Fetch recommendations while explicitly blocking the source movie from matching itself
        recommendations = predict_films(user_input_features, top_k=5, feature_matrix=feature_matrix,
                                        exclude_title=target_title)
        recommended_titles = recommendations['title'].tolist()

        if target_title in recommended_titles:
            hits_at_5 += 1
            rank = recommended_titles.index(target_title) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

        total_tests += 1

    hit_rate_at_5 = hits_at_5 / total_tests if total_tests > 0 else 0
    mrr = np.mean(reciprocal_ranks) if reciprocal_ranks else 0

    print("\n=== MODEL EVALUATION METRICS ===")
    print(f"Total Test Profiles Simulated: {total_tests}")
    print(f"Hit Rate @ 5 (Unbiased):       {hit_rate_at_5:.2%}")
    print(f"Mean Reciprocal Rank (MRR):    {mrr:.4f}")


# =========================
# CATALOG METRICS
# =========================
def print_catalog_metrics(feature_matrix):
    total_movies = len(feature_matrix)
    feature_counts = [len(feats) for feats in feature_matrix.values()]
    avg_features = sum(feature_counts) / total_movies if total_movies > 0 else 0
    zero_feature_movies = sum(1 for c in feature_counts if c == 0)

    print("\n=== DATA & MODEL METRICS ===")
    print(f"Total Movies in Catalog:  {total_movies}")
    print(f"Average Features / Movie: {avg_features:.2f}")
    print(f"Un-recommendable Movies:  {zero_feature_movies} (0 features)")
    print(f"Catalog Coverage:         {((total_movies - zero_feature_movies) / total_movies):.2%}")


# =========================
# MONTE CARLO SIMULATION
# =========================
def generate_jaccard_distribution_analysis(feature_matrix, n_simulations=1000, top_k=5):
    """
    Simulates random user feature selections to evaluate system sparsity
    and the quality of top-K recommendations. Saves a histogram plot.
    """
    all_features = list(set().union(*feature_matrix.values()))

    if not all_features:
        print("Error: No features found in the loaded matrix.")
        return

    all_top_scores = []
    all_pairwise_scores = []

    print(f"\nRunning {n_simulations} Monte Carlo simulation loops...")

    for _ in range(n_simulations):
        num_to_sample = random.randint(1, 4)
        selected_features = random.sample(all_features, min(num_to_sample, len(all_features)))

        top_recs = predict_films(selected_features, top_k=top_k, feature_matrix=feature_matrix)
        all_top_scores.extend(top_recs['score'].tolist())

        user_features_set = set(clean_feature(f) for f in selected_features)
        for title, movie_features in feature_matrix.items():
            intersection = user_features_set.intersection(movie_features)
            union = user_features_set.union(movie_features)
            jaccard_score = len(intersection) / len(union) if union else 0.0
            all_pairwise_scores.append(jaccard_score)

    # Visualization Setup
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    ax1.hist(all_pairwise_scores, bins=20, color='#1f77b4', edgecolor='black', alpha=0.8)
    ax1.set_title("Global Matrix Sparsity\n(All Pairwise Movie Matches)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Jaccard Similarity Score", fontsize=10)
    ax1.set_ylabel("Count of Movie Comparisons", fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    ax2.hist(all_top_scores, bins=15, color='#ff7f0e', edgecolor='black', alpha=0.8)
    ax2.set_title(f"User Experience Quality\n(Scores within Shown Top-{top_k} Results)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Jaccard Similarity Score", fontsize=10)
    ax2.set_ylabel("Count of Returned Recommendations", fontsize=10)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    output_image = "jaccard_score_distribution.png"
    plt.savefig(output_image, dpi=300)
    print(f"Success! Diagnostic chart exported to: {output_image}")

    total_zeros = sum(1 for score in all_pairwise_scores if score == 0.0)
    sparsity_pct = (total_zeros / len(all_pairwise_scores)) * 100
    avg_top_score = sum(all_top_scores) / len(all_top_scores) if all_top_scores else 0.0

    print("\n=== TEXT METRICS FOR YOUR SLIDES ===")
    print(f"• Total Cross-Comparisons Simulated: {len(all_pairwise_scores)}")
    print(f"• Global Matrix Sparsity:             {sparsity_pct:.2f}% zero-match rate.")
    print(f"• Average Top-{top_k} Score Displayed:   {avg_top_score:.4f} Jaccard Similarity")


# =========================================================
# RUN DATA ENGINE & START MICROSERVICE SERVER INTERFACE
# =========================================================
if __name__ == "__main__":
    # 1. Compile matrix dictionary and evaluate performance algorithms
    matrix = train_model()
    evaluate_recommender(matrix)
    print_catalog_metrics(matrix)
    generate_jaccard_distribution_analysis(matrix, n_simulations=1000, top_k=5)

    # 2. Boot up Uvicorn ASGI listener engine inside the container context
    print("\nInitializing Live FastAPI Recommendation Engine Service...")
    # 'model:app' tells uvicorn to look inside model.py for the FastAPI variable named 'app'
    uvicorn.run("model:app", host="0.0.0.0", port=8080, reload=True)