import os
import json
import pandas as pd
from typing import List, Dict


# =========================================================
# LOAD JSON FOLDER (TMDB)
# =========================================================
def load_json_folder(folder: str) -> List[Dict]:
    data = []

    for file in os.listdir(folder):
        if not file.endswith(".json"):
            continue

        path = os.path.join(folder, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                obj = json.load(f)

                if isinstance(obj, dict):
                    data.append(obj)
                elif isinstance(obj, list):
                    data.extend(obj)

        except Exception as e:
            print(f"Skipping {file}: {e}")
            continue

    return data


# =========================================================
# LOAD GHIBLI CSV
# =========================================================
def load_ghibli_csv(path: str) -> List[Dict]:
    df = pd.read_csv(path).fillna("")
    return df.to_dict(orient="records")


# =========================================================
# MERGER
# =========================================================
class GhibliTMDBMerger:

    def __init__(self):
        self.aliases = {
            "grave of the fireflies": "grave of fireflies",
            "my neighbour totoro": "my neighbor totoro",
            "the wind rises": "wind rises",
            "the cat returns": "cat returns",
            "earwig and the witch": "earwig and witch",
        }

    def normalize(self, title: str) -> str:
        return title.lower().strip() if title else ""

    def apply_alias(self, title: str) -> str:
        return self.aliases.get(title, title)

    def clean_title(self, title: str) -> str:
        return self.apply_alias(self.normalize(title))


# =========================================================
# MERGE DATA
# =========================================================
def merge_data(tmdb_data: List[Dict], ghibli_data: List[Dict]) -> pd.DataFrame:

    merger = GhibliTMDBMerger()

    # ---------------- TMDB INDEX ----------------
    tmdb_index = {}
    for t in tmdb_data:
        title = merger.clean_title(t.get("title"))
        if title:
            tmdb_index[title] = t

    # ---------------- GHIBLI INDEX ----------------
    ghibli_index = {}
    for g in ghibli_data:
        title = merger.clean_title(g.get("film") or g.get("title"))
        if title:
            ghibli_index[title] = g

    # ---------------- MERGE ----------------
    merged = []

    for title, t in tmdb_index.items():

        if title not in ghibli_index:
            continue

        g = ghibli_index[title]

        merged.append({
            # TMDB
            "title": t.get("title"),
            "release_date": t.get("release_date"),
            "runtime": t.get("runtime"),
            "genres": t.get("genres"),
            "tmdb_rating": t.get("rating"),
            "vote_count": t.get("vote_count"),
            "budget": t.get("budget"),
            "revenue": t.get("revenue"),
            "cast": t.get("cast", []),
            "crew": t.get("crew", []),
            "language": t.get("language"),

            # GHIBLI
            "director": g.get("director"),
            "producer": g.get("producer"),
            "description": g.get("description"),
            "people": g.get("people"),
            "locations": g.get("locations"),
            "species": g.get("species"),
            "vehicles": g.get("vehicles"),
        })

    return pd.DataFrame(merged)


# =========================================================
# CLEAN
# =========================================================
def clean_data(df: pd.DataFrame) -> pd.DataFrame:

    if df.empty:
        return df

    df = df.copy()

    for col in ["tmdb_rating", "budget", "revenue"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates(subset=["title"])

    return df


# =========================================================
# SAVE OUTPUT (FIXED PATH)
# =========================================================
def save_processed(df: pd.DataFrame):

    output_dir = os.path.join("../data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "ghibli_tmdb_merged.csv")
    json_path = os.path.join(output_dir, "ghibli_tmdb_merged.json")

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)

    print(f"Saved CSV → {csv_path}")
    print(f"Saved JSON → {json_path}")


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    tmdb_folder = os.path.join("../data", "raw", "tmdb")
    ghibli_csv = os.path.join("../data", "processed", "ghibli_entities.csv")

    tmdb_data = load_json_folder(tmdb_folder)
    ghibli_data = load_ghibli_csv(ghibli_csv)

    print(f"TMDB loaded: {len(tmdb_data)}")
    print(f"Ghibli loaded: {len(ghibli_data)}")

    merged = merge_data(tmdb_data, ghibli_data)
    cleaned = clean_data(merged)

    save_processed(cleaned)