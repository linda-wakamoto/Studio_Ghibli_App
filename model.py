# import pandas as pd
# import joblib
# import ast
# import os
#
# from sklearn.preprocessing import MultiLabelBinarizer
# from sklearn.ensemble import RandomForestClassifier
#
# # =========================
# # PATHS
# # =========================
# CSV_PATH = "data/processed/ghibli_interest_labels.csv"
#
# MODEL_PATH = "models/film_model.pkl"
# ENCODER_PATH = "models/feature_encoder.pkl"
#
# # =========================
# # TRAIN MODEL
# # =========================
# def train_model():
#
#     os.makedirs("models", exist_ok=True)
#
#     df = pd.read_csv(CSV_PATH)
#
#     # -------------------------
#     # COMBINE FEATURES
#     # -------------------------
#     def combine_features(row):
#
#         features = []
#
#         for col in ["genres", "labels", "species"]:
#
#             value = row[col]
#
#             if pd.notna(value):
#
#                 try:
#                     parsed = ast.literal_eval(value)
#
#                     if isinstance(parsed, list):
#                         features.extend(parsed)
#
#                 except:
#                     pass
#
#         return [f.strip().lower() for f in features]
#
#     df["features"] = df.apply(
#         combine_features,
#         axis=1
#     )
#
#     # -------------------------
#     # ENCODE FEATURES
#     # -------------------------
#     mlb = MultiLabelBinarizer()
#
#     X = mlb.fit_transform(df["features"])
#
#     y = df["title"]
#
#     # -------------------------
#     # TRAIN RANDOM FOREST
#     # -------------------------
#     model = RandomForestClassifier(
#         n_estimators=300,
#         random_state=42
#     )
#
#     model.fit(X, y)
#
#     # -------------------------
#     # SAVE
#     # -------------------------
#     joblib.dump(model, MODEL_PATH)
#     joblib.dump(mlb, ENCODER_PATH)
#
#     print("Model trained and saved")
#
#
# # =========================
# # LOAD MODEL
# # =========================
# def load_model():
#
#     model = joblib.load(MODEL_PATH)
#     mlb = joblib.load(ENCODER_PATH)
#
#     return model, mlb
#
#
# # =========================
# # PREDICT FILMS
# # =========================
# def predict_films(selected_features, top_k=5):
#
#     model, mlb = load_model()
#
#     # lowercase consistency
#     selected_features = [
#         f.strip().lower()
#         for f in selected_features
#     ]
#
#     x = mlb.transform([selected_features])
#
#     probs = model.predict_proba(x)[0]
#
#     results = pd.DataFrame({
#         "title": model.classes_,
#         "score": probs
#     })
#
#     return results.sort_values(
#         by="score",
#         ascending=False
#     ).head(top_k)
#
#
# # =========================
# # TRAIN
# # =========================
# if __name__ == "__main__":
#     train_model()

import pandas as pd
import joblib
import ast
import os

from sklearn.preprocessing import MultiLabelBinarizer

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


if __name__ == "__main__":
    train_model()