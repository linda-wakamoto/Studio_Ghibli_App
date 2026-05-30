import pandas as pd
import joblib
import ast
import os

# =========================
# PATHS
# =========================
CSV_PATH = "data/processed/ghibli_interest_labels.csv"
MODEL_PATH = "models/film_model.pkl"
ENCODER_PATH = "models/feature_encoder.pkl"


# =========================
# CLEANING HELPER (Bakes lowercase & underscore removal together)
# =========================
def clean_feature(text):
    return str(text).strip().lower().replace("_", " ")


# =========================
# TRAIN MODEL (Now Pre-computes Feature Sets)
# =========================
def train_model():
    os.makedirs("models", exist_ok=True)
    df = pd.read_csv(CSV_PATH)

    def combine_features(row):
        features = []
        for col in ["genres", "labels", "species"]:
            value = row[col]
            if pd.notna(value):
                try:
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, list):
                        features.extend(parsed)
                except:
                    pass
        # Consistently lowercase and drop underscores
        return [clean_feature(f) for f in features]

    df["features"] = df.apply(combine_features, axis=1)

    # Save a clean mapping dictionary of Title -> Set of Features
    feature_matrix = dict(zip(df["title"], df["features"].apply(set)))

    # Save the feature matrix map instead of a broken Random Forest
    joblib.dump(feature_matrix, MODEL_PATH)
    print("Content feature matrix compiled and saved successfully!")


# =========================
# PREDICT FILMS (Using Exact Match Vectoring)
# =========================
def predict_films(selected_features, top_k=5):
    # Load the compiled feature sets
    feature_matrix = joblib.load(MODEL_PATH)

    # Clean the incoming user selections to perfectly match format
    user_features = set(clean_feature(f) for f in selected_features)

    # If the user hasn't selected anything yet, return the default top movies
    if not user_features:
        return pd.DataFrame({"title": list(feature_matrix.keys())[:top_k], "score": [0.0] * top_k})

    scores = []
    for title, movie_features in feature_matrix.items():
        # Calculate Jaccard Similarity: Intersection / Union
        intersection = user_features.intersection(movie_features)
        union = user_features.union(movie_features)

        jaccard_score = len(intersection) / len(union) if union else 0.0
        scores.append({"title": title, "score": jaccard_score})

    results = pd.DataFrame(scores)

    # Only keep movies where the score is strictly greater than 0
    results = results[results["score"] > 0.0]

    # Sort and return the top matching results
    return results.sort_values(by="score", ascending=False).head(top_k)


import numpy as np


def evaluate_recommender():
    """
    Simulates user profiles based on actual movie features to calculate Hit Rate and MRR.
    """
    # 1. Load the data to get ground truth
    df = pd.read_csv(CSV_PATH)
    feature_matrix = joblib.load(MODEL_PATH)

    hits_at_5 = 0
    reciprocal_ranks = []
    total_tests = 0

    # 2. Simulate a user for every movie in your dataset
    for _, row in df.iterrows():
        target_title = row['title']
        movie_features = feature_matrix.get(target_title, set())

        # Skip if the movie has no features to test with
        if len(movie_features) < 2:
            continue

        # Simulate user input: Take a subset (e.g., 2 features) of this specific movie
        user_input_features = list(movie_features)[:2]

        # Get top 5 recommendations
        recommendations = predict_films(user_input_features, top_k=5)
        recommended_titles = recommendations['title'].tolist()

        # Metric A: Hit Rate @ 5
        if target_title in recommended_titles:
            hits_at_5 += 1
            # Metric B: Reciprocal Rank
            rank = recommended_titles.index(target_title) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

        total_tests += 1

    # 3. Calculate Final Metrics
    hit_rate_at_5 = hits_at_5 / total_tests if total_tests > 0 else 0
    mrr = np.mean(reciprocal_ranks) if reciprocal_ranks else 0

    print("=== MODEL EVALUATION METRICS ===")
    print(f"Total Test Profiles Simulated: {total_tests}")
    print(f"Hit Rate @ 5:                  {hit_rate_at_5:.2%}")
    print(f"Mean Reciprocal Rank (MRR):    {mrr:.4f}")


def print_catalog_metrics():
    feature_matrix = joblib.load(MODEL_PATH)
    total_movies = len(feature_matrix)

    feature_counts = [len(feats) for feats in feature_matrix.values()]
    avg_features = sum(feature_counts) / total_movies
    zero_feature_movies = sum(1 for c in feature_counts if c == 0)

    print("=== DATA & MODEL METRICS ===")
    print(f"Total Movies in Catalog:  {total_movies}")
    print(f"Average Features / Movie: {avg_features:.2f}")
    print(f"Un-recommendable Movies:  {zero_feature_movies} (0 features)")
    print(f"Catalog Coverage:         {((total_movies - zero_feature_movies) / total_movies):.2%}")


import random
import matplotlib.pyplot as plt


def generate_jaccard_distribution_analysis(n_simulations=1000, top_k=5):
    """
    Simulates random user feature selections to evaluate system sparsity
    and the quality of top-K recommendations. Saves a histogram plot.
    """
    # 1. Load the pre-computed feature matrix
    if not os.path.exists(MODEL_PATH):
        print(f"Model file not found at {MODEL_PATH}. Running train_model() first...")
        train_model()

    feature_matrix = joblib.load(MODEL_PATH)

    # 2. Extract every single unique feature available across your Ghibli catalog
    all_features = list(set().union(*feature_matrix.values()))

    if not all_features:
        print("Error: No features found in the loaded model matrix.")
        return

    all_top_scores = []
    all_pairwise_scores = []

    print(f"Simulating {n_simulations} random user queries...")

    for _ in range(n_simulations):
        # Simulate a user choosing between 1 and 4 random features
        num_to_sample = random.randint(1, 4)
        selected_features = random.sample(all_features, min(num_to_sample, len(all_features)))

        # Metric A: Evaluate the exact Top-K results the user would see on screen
        top_recs = predict_films(selected_features, top_k=top_k)
        all_top_scores.extend(top_recs['score'].tolist())

        # Metric B: Evaluate the entire catalog matrix to test global sparsity
        user_features_set = set(clean_feature(f) for f in selected_features)
        for title, movie_features in feature_matrix.items():
            intersection = user_features_set.intersection(movie_features)
            union = user_features_set.union(movie_features)
            jaccard_score = len(intersection) / len(union) if union else 0.0
            all_pairwise_scores.append(jaccard_score)

    # 3. Create a clean, non-overlapping dual visualization panel
    # (Adhering to strict standards: using subplots, tight layout, and savefig)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Left Chart: Sparsity Analysis
    ax1.hist(all_pairwise_scores, bins=20, color='#1f77b4', edgecolor='black', alpha=0.8)
    ax1.set_title("Global Matrix Sparsity\n(All Pairwise Movie Matches)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Jaccard Similarity Score", fontsize=10)
    ax1.set_ylabel("Count of Movie Comparisons", fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    # Right Chart: Recommendation Quality Analysis
    ax2.hist(all_top_scores, bins=15, color='#ff7f0e', edgecolor='black', alpha=0.8)
    ax2.set_title(f"User Experience Quality\n(Scores within Shown Top-{top_k} Results)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Jaccard Similarity Score", fontsize=10)
    ax2.set_ylabel("Count of Returned Recommendations", fontsize=10)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()

    # Save high-resolution PNG for slides
    output_image = "jaccard_score_distribution.png"
    plt.savefig(output_image, dpi=300)
    print(f"\nSuccess! Chart generated and saved to: {output_image}")

    # Calculate brief statistical summaries for slide bullets
    total_zeros = sum(1 for score in all_pairwise_scores if score == 0.0)
    sparsity_pct = (total_zeros / len(all_pairwise_scores)) * 100
    avg_top_score = sum(all_top_scores) / len(all_top_scores) if all_top_scores else 0.0

    print("\n=== TEXT METRICS FOR YOUR SLIDES ===")
    print(f"• Total Cross-Comparisons Simulated: {len(all_pairwise_scores)}")
    print(f"• Global Matrix Sparsity:             {sparsity_pct:.2f}% of overall combinations result in a 0.0 match.")
    print(f"• Average Top-{top_k} Score Displayed:   {avg_top_score:.4f} Jaccard Similarity")

if __name__ == "__main__":
    train_model()
    evaluate_recommender()
    print_catalog_metrics()
    generate_jaccard_distribution_analysis(n_simulations=1000, top_k=5)
