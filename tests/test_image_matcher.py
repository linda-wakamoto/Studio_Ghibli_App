from pathlib import Path
from data_processors.ghibli_image_matcher import CSV_PATH

def test_csv_path_exists():
    assert isinstance(CSV_PATH, Path)
    assert str(CSV_PATH).endswith("final_dataset.csv")