import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


class TMDBCollector:
    def __init__(self):
        # -----------------------------
        # CONFIG
        # -----------------------------
        self.api_key = os.getenv("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"

        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found in environment variables")

        # -----------------------------
        # PATHS (DOCKER + LOCAL SAFE)
        # -----------------------------
        self.project_root = Path(__file__).resolve().parent.parent

        self.log_dir = self.project_root / "logs"
        self.raw_dir = self.project_root / "data" / "raw" / "tmdb"

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        # -----------------------------
        # LOGGING (FILE + CONSOLE SAFE)
        # -----------------------------
        self.logger = logging.getLogger("tmdb_collector")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            file_handler = logging.FileHandler(
                self.log_dir / "api_collector.log"
            )
            file_handler.setFormatter(formatter)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        # -----------------------------
        # SESSION + RATE LIMIT
        # -----------------------------
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 0.25

    # -----------------------------
    # RATE LIMITING
    # -----------------------------
    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    # -----------------------------
    # REQUEST HANDLER
    # -----------------------------
    def _make_request(self, endpoint: str, params: Dict = None, retries: int = 3):
        if params is None:
            params = {}

        params["api_key"] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(retries):
            try:
                self._rate_limit()

                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()

                self.logger.info(f"Fetched {endpoint}")
                return response.json()

            except requests.RequestException as e:
                self.logger.error(
                    f"Attempt {attempt+1} failed for {endpoint}: {e}"
                )

                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

        raise RuntimeError("Request retry loop failed unexpectedly")

    # -----------------------------
    # NORMALIZATION
    # -----------------------------
    def _normalize(self, text: str) -> str:
        if not text:
            return ""

        return (
            text.lower()
            .strip()
            .replace("the ", "")
            .replace("a ", "")
            .replace("an ", "")
            .replace("'", "")
            .replace("-", "")
            .replace(":", "")
        )

    # -----------------------------
    # CLEAN DATA BUILDER
    # -----------------------------
    def _build_clean_item(self, mid: int, details: Dict, credits: Dict) -> Dict:
        return {
            "tmdb_id": mid,
            "title": details.get("title"),
            "release_date": details.get("release_date"),
            "runtime": details.get("runtime"),
            "genres": [g["name"] for g in details.get("genres", [])],
            "rating": details.get("vote_average"),
            "vote_count": details.get("vote_count"),
            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            "language": details.get("original_language"),
            "production_companies": [
                c["name"] for c in details.get("production_companies", [])
            ][:5],
            "cast": [c["name"] for c in credits.get("cast", [])][:5],
            "crew": [c["name"] for c in credits.get("crew", [])][:5],
        }

    # -----------------------------
    # MAIN COLLECTOR
    # -----------------------------
    def collect_ghibli_movies(self) -> List[Dict]:

        ghibli_titles = [
            "Castle in the Sky",
            "Grave of the Fireflies",
            "My Neighbor Totoro",
            "Kiki's Delivery Service",
            "Only Yesterday",
            "Porco Rosso",
            "Pom Poko",
            "Whisper of the Heart",
            "Princess Mononoke",
            "My Neighbors the Yamadas",
            "Spirited Away",
            "The Cat Returns",
            "Howl's Moving Castle",
            "Tales from Earthsea",
            "Ponyo",
            "Arrietty",
            "From Up on Poppy Hill",
            "The Wind Rises",
            "The Tale of the Princess Kaguya",
            "When Marnie Was There",
            "Earwig and the Witch",
            "The Red Turtle"
        ]

        results = []

        for title in ghibli_titles:
            try:
                search = self._make_request(
                    "search/movie",
                    {
                        "query": title,
                        "include_adult": False,
                        "language": "en-US",
                    },
                )

                matches = search.get("results", [])

                if not matches:
                    self.logger.warning(f"No results for {title}")
                    continue

                target = self._normalize(title)
                movie_id = None

                for m in matches:
                    if self._normalize(m.get("title")) == target:
                        movie_id = m["id"]
                        break

                if movie_id is None:
                    self.logger.warning(
                        f"No exact match for {title}, using top result"
                    )
                    movie_id = matches[0]["id"]

                details = self._make_request(f"movie/{movie_id}")
                credits = self._make_request(f"movie/{movie_id}/credits")

                clean_item = self._build_clean_item(
                    movie_id, details, credits
                )

                clean_item["title"] = title

                results.append(clean_item)

                # SAVE FILE SAFELY
                output_file = self.raw_dir / f"{movie_id}.json"

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(clean_item, f, indent=2)

                self.logger.info(f"Saved {title}")

            except Exception as e:
                self.logger.error(f"Failed {title}: {e}")

        return results


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    collector = TMDBCollector()
    data = collector.collect_ghibli_movies()

    print(f"Collected {len(data)} Ghibli movies")