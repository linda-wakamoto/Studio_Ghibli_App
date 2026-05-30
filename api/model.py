import joblib
from fastapi import FastAPI, Query
from typing import List

MODEL_PATH = "models/film_model.pkl"

app = FastAPI()

feature_matrix = {}

def clean_feature(text):
    return str(text).strip().lower().replace("_", " ")


@app.on_event("startup")
def load_model():
    global feature_matrix
    feature_matrix = joblib.load(MODEL_PATH)


def predict(selected_features, top_k=5):
    user_set = set(clean_feature(f) for f in selected_features)

    scores = []

    for title, feats in feature_matrix.items():
        union = user_set | feats
        inter = user_set & feats
        score = len(inter) / len(union) if union else 0

        if score > 0:
            scores.append({"title": title, "score": score})

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:top_k]


@app.get("/recommend")
def recommend(features: List[str] = Query(default_factory=list), top_k: int = 5):

    return {
        "recommendations": predict(features, top_k)
    }


@app.get("/")
def health():
    return {"status": "ok"}