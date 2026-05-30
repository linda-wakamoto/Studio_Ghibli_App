import json
import logging
from pathlib import Path
import requests

project_root = Path(__file__).resolve().parent.parent

log_file = project_root / "logs" / "api_collector.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ghibli_collector")


class GhibliCollector:
    def __init__(self):
        self.base_url = "https://ghibliapi.vercel.app"

        # Project root directory
        self.project_root = Path(__file__).resolve().parent.parent

        # Data output directory
        self.raw_dir = (
            self.project_root
            / "data"
            / "raw"
            / "ghibli"
        )

        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def _make_request(self, endpoint):
        """
        Make API request and return JSON data.
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            logger.info(f"Fetching {endpoint} data")

            response = requests.get(
                url,
                timeout=10
            )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            logger.error(
                f"Request timed out for endpoint: {endpoint}"
            )
            raise

        except requests.exceptions.RequestException as e:
            logger.error(
                f"API request failed for {endpoint}: {e}"
            )
            raise

    def validate_data(self, data, endpoint):
        """
        Basic data quality checks.
        """
        if not isinstance(data, list):
            raise ValueError(
                f"{endpoint} response is not a list"
            )

        if len(data) == 0:
            raise ValueError(
                f"{endpoint} returned no records"
            )

        logger.info(
            f"{endpoint}: validation passed ({len(data)} records)"
        )

    def get_all_data(self):
        """
        Download all Ghibli API resources.
        """
        endpoints = [
            "films",
            "people",
            "locations",
            "species",
            "vehicles"
        ]

        results = {}

        for endpoint in endpoints:
            data = self._make_request(endpoint)

            self.validate_data(
                data,
                endpoint
            )

            results[endpoint] = data

        return results

    def save_raw(self):
        """
        Save all API responses to JSON files.
        """
        data = self.get_all_data()

        for key, value in data.items():
            output_file = self.raw_dir / f"{key}.json"

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    value,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            logger.info(
                f"Saved {key}.json"
            )

        logger.info(
            "Successfully saved all Ghibli data"
        )

        return data


if __name__ == "__main__":
    collector = GhibliCollector()

    try:
        collector.save_raw()

    except Exception as e:
        logger.exception(
            f"Collector failed: {e}"
        )
