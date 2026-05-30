import pandas as pd
import re
from titlecase import titlecase
from pathlib import Path

# =========================================================
# LOAD DATA
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
CSV_PATH = DATA_DIR / "ghibli_tmdb_merged.csv"

# =========================================================
# MANUAL LABELS
# =========================================================
MANUAL_LABELS = {
    "pom poko": [
        "raccoons",
        "family"
    ],

    "my neighbor totoro": [
        "cats",
        "forests",
        "slice_of_life",
        "family",
        "friendship"
    ],

    "kiki's delivery service": [
        "witch",
        "coming_of_age",
        "family",
        "friendship"
    ],

    "howl's moving castle": [
        "witch",
        "castles",
        "strong_lead",
        "romantic",
        "friendship"
    ],

    "earwig and the witch": [
        "witch",
        "friendship"
    ],

    "spirited away": [
        "witch",
        "dragons",
        "coming_of_age",
        "family",
        "friendship"
    ],

    "the wind rises": [
        "planes",
        "friendship",
        "family",
        "romantic"
    ],

    "porco rosso": [
        "planes",
        "romantic"
    ],

    "princess mononoke": [
        "forests",
        "strong_lead",
        "battles",
        "romantic"
    ],

    "arrietty": [
        "forests",
        "slice_of_life",
        "romantic"
    ],

    "whisper of the heart": [
        "music",
        "slice_of_life",
        "romantic"
    ],

    "grave of the fireflies": [
        "need_a_good_cry",
        "family"
    ],

    "the tale of the princess kaguya": [
        "need_a_good_cry",
        "forests",
        "family",
        "friendship"
    ],

    "ponyo": [
        "ocean",
        "family",
        "friendship"
    ],

    "my neighbors the yamadas": [
        "slice_of_life",
        "family"
    ],

    "only yesterday": [
        "slice_of_life",
        "friendship"
    ],

    "when marnie was there": [
        "slice_of_life",
        "friendship"
    ],

    "castle in the sky": [
        "castles",
        "battles",
        "friendship"
    ],

    "the cat returns": [
        "cats",
        "coming_of_age"
    ],

    "the red turtle": [
        "ocean",
        "forests"
    ],

    "from up on poppy hill": [
        "ocean",
        "romantic",
        "coming_of_age"
    ],

    "tales from earthsea": [
        "battles",
        "friendship"
    ]
}

# =========================================================
# CORE FUNCTION
# =========================================================
def build_labeled_dataset():
    df = pd.read_csv(CSV_PATH)

    df["title"] = df["title"].fillna("").str.lower()

    def assign_labels(row):
        title = row["title"]
        return sorted(MANUAL_LABELS.get(title, ["other"]))

    df["labels"] = df.apply(assign_labels, axis=1)

    df["title"] = df["title"].fillna("").apply(titlecase)

    return df

# =========================================================
# SAVE
# =========================================================
if __name__ == "__main__":
    df = build_labeled_dataset()

    output_path = DATA_DIR / "final_dataset.csv"
    df.to_csv(output_path, index=False)

    print("Saved:", output_path)
