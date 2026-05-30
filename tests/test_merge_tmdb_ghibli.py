from data_processors.merge_tmdb_ghibli import GhibliTMDBMerger, clean_data
import pandas as pd


def test_aliasing():
    merger = GhibliTMDBMerger()

    assert merger.clean_title("The Wind Rises") == "wind rises"
    assert merger.clean_title("My Neighbour Totoro") == "my neighbor totoro"


def test_clean_data_numeric_conversion():
    df = pd.DataFrame([
        {"title": "A", "tmdb_rating": "8.5", "budget": "1000", "revenue": "2000"}
    ])

    cleaned = clean_data(df)

    assert cleaned["tmdb_rating"].dtype != object