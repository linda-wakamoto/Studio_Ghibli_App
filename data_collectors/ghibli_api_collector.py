import requests
import json
import os

class GhibliCollector:
    def __init__(self):
        self.base_url = "https://ghibliapi.vercel.app"
        os.makedirs("../data/raw/ghibli", exist_ok=True)

    def _make_request(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_all_data(self):
        films = self._make_request("films")
        people = self._make_request("people")
        locations = self._make_request("locations")
        species = self._make_request("species")
        vehicles = self._make_request("vehicles")

        return {
            "films": films,
            "people": people,
            "locations": locations,
            "species": species,
            "vehicles": vehicles
        }

    def save_raw(self):
        data = self.get_all_data()

        for key, value in data.items():
            with open(f"data/raw/ghibli/{key}.json", "w", encoding="utf-8") as f:
                json.dump(value, f, indent=2)

        return data

if __name__ == "__main__":
    collector = GhibliCollector()
    data = collector.save_raw()
    print("Saved all Ghibli data successfully.")
