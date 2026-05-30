import os
import json
import glob
import pandas as pd
import requests
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw" / "ghibli"
FILMS_FILE = os.path.join(DATA_DIR, "films.json")


# =========================================================
# LOAD FILMS METADATA
# =========================================================
def load_films_metadata():
    with open(FILMS_FILE, "r", encoding="utf-8") as f:
        films = json.load(f)

    meta = {}

    for film in films:
        if not isinstance(film, dict):
            continue

        title = film.get("title", "").lower().strip()

        meta[title] = {
            "director": film.get("director"),
            "producer": film.get("producer"),
            "description": film.get("description"),
            "people": film.get("people", [])
        }

    return meta


import requests

def load_people_lookup():
    api_url = "https://ghibliapi.vercel.app/people"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        people = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}

    lookup = {}

    for person in people:
        if not isinstance(person, dict):
            continue

        person_url = person.get("url")
        name = person.get("name")

        if person_url and name:
            lookup[person_url.rstrip("/")] = name

    return lookup


# =========================================================
# LOAD FILM URL LOOKUP
# =========================================================
def load_url_lookup():
    with open(FILMS_FILE, "r", encoding="utf-8") as f:
        films = json.load(f)

    return {
        f.get("url"): f.get("title", "").lower().strip()
        for f in films
        if isinstance(f, dict) and f.get("url")
    }


# =========================================================
# PROCESS ENTITY FILES (UNCHANGED LOGIC)
# =========================================================
def process_entity_file(file_path, url_to_title):

    film_map = defaultdict(lambda: {
        "locations": set(),
        "species": set(),
        "vehicles": set()
    })

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return film_map

    for item in data:
        if not isinstance(item, dict):
            continue

        name = item.get("name") or item.get("title") or item.get("id")
        films = item.get("films", [])

        if isinstance(films, str):
            films = [films]

        for film_url in films:
            title = url_to_title.get(film_url)
            if not title:
                continue

            if "locations" in file_path:
                film_map[title]["locations"].add(name)
            elif "species" in file_path:
                film_map[title]["species"].add(name)
            elif "vehicles" in file_path:
                film_map[title]["vehicles"].add(name)

    return film_map


# =========================================================
# BUILD DATASET
# =========================================================
def build_dataset():

    url_to_title = load_url_lookup()
    people_lookup = load_people_lookup()
    meta = load_films_metadata()

    final = defaultdict(lambda: {
        "director": None,
        "producer": None,
        "description": None,
        "people": [],
        "locations": set(),
        "species": set(),
        "vehicles": set()
    })

    # -------------------------
    # attach metadata
    # -------------------------
    for title, m in meta.items():
        final[title]["director"] = m["director"]
        final[title]["producer"] = m["producer"]
        final[title]["description"] = m["description"]

        resolved_people = []

        for p in m.get("people", []):

            # CASE 1: already a name
            if isinstance(p, str) and not p.startswith("http"):
                resolved_people.append(p)
                continue

            # CASE 2: valid URL
            if isinstance(p, str) and p.startswith("http"):
                p_clean = p.rstrip("/")

                # skip broken endpoint
                if p_clean.endswith("/people"):
                    continue

                # resolve via lookup
                if p_clean in people_lookup:
                    resolved_people.append(people_lookup[p_clean])
                else:
                    # fallback: keep last segment (safe, not blank)
                    resolved_people.append(p_clean.split("/")[-1])

                continue

            # CASE 3: embedded object
            if isinstance(p, dict):
                name = p.get("name")
                if name:
                    resolved_people.append(name)

        final[title]["people"] = resolved_people

    # -------------------------
    # process entity files
    # -------------------------
    for file_path in glob.glob(os.path.join(DATA_DIR, "*.json")):
        if "films.json" in file_path:
            continue

        if any(x in file_path.lower() for x in ["locations", "species", "vehicles"]):
            film_map = process_entity_file(file_path, url_to_title)

            for film, data in film_map.items():
                final[film]["locations"].update(data["locations"])
                final[film]["species"].update(data["species"])
                final[film]["vehicles"].update(data["vehicles"])

    # -------------------------
    # dataframe
    # -------------------------
    rows = []

    for film, data in final.items():
        rows.append({
            "film": film,
            "director": data["director"],
            "producer": data["producer"],
            "description": data["description"],
            "people": list(data["people"]),
            "locations": list(data["locations"]),
            "species": list(data["species"]),
            "vehicles": list(data["vehicles"])
        })

    return pd.DataFrame(rows)

#=========================================================
# RUN + SAVE
# =========================================================
if __name__ == "__main__":
    df = build_dataset()
    df = df.sort_values("film")
    output_dir = os.path.join("../data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ghibli_entities.csv")
    df.to_csv(output_path, index=False)
    print("Saved:", output_path)
    print(df.head())