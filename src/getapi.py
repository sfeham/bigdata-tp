import requests
import json
from datetime import datetime
from pathlib import Path

class VelibAPI:
    URL = (
        "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
        "velib-disponibilite-en-temps-reel/records?limit=1000"
    )

    def fetch_and_save(self, output_dir: str):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = f"{output_dir}/velib_{datetime.now():%Y%m%d_%H%M%S}.json"

        data = requests.get(self.URL).json()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        print(f"Fichier créé : {filename}")
        return filename

if __name__ == "__main__":
    VelibAPI().fetch_and_save("../data/raw")
