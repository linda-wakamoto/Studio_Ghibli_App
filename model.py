import pandas as pd
import joblib
import ast
import os

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier

# =========================
# PATHS
# =========================
CSV_PATH = "data/processed/ghibli_interest_labels.csv"

MODEL_PATH = "models/film_model.pkl"
ENCODER_PATH = "models/feature_encoder.pkl"

# =========================
# TRAIN MODEL
# =========================
def train_model():

    os.makedirs("models", exist_ok=True)

    df = pd.read_csv(CSV_PATH)

    # -------------------------
    # COMBINE FEATURES
    # -------------------------
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

        return [f.strip().lower() for f in features]

    df["features"] = df.apply(
        combine_features,
        axis=1
    )

    # -------------------------
    # ENCODE FEATURES
    # -------------------------
    mlb = MultiLabelBinarizer()

    X = mlb.fit_transform(df["features"])

    y = df["title"]

    # -------------------------
    # TRAIN RANDOM FOREST
    # -------------------------
    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42
    )

    model.fit(X, y)

    # -------------------------
    # SAVE
    # -------------------------
    joblib.dump(model, MODEL_PATH)
    joblib.dump(mlb, ENCODER_PATH)

    print("Model trained and saved")


# =========================
# LOAD MODEL
# =========================
def load_model():

    model = joblib.load(MODEL_PATH)
    mlb = joblib.load(ENCODER_PATH)

    return model, mlb


# =========================
# PREDICT FILMS
# =========================
def predict_films(selected_features, top_k=5):

    model, mlb = load_model()

    # lowercase consistency
    selected_features = [
        f.strip().lower()
        for f in selected_features
    ]

    x = mlb.transform([selected_features])

    probs = model.predict_proba(x)[0]

    results = pd.DataFrame({
        "title": model.classes_,
        "score": probs
    })

    return results.sort_values(
        by="score",
        ascending=False
    ).head(top_k)


# =========================
# TRAIN
# =========================
if __name__ == "__main__":
    train_model()