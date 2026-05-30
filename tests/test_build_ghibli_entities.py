import json
import tempfile
from data_processors.build_ghibli_entities import process_entity_file


def test_process_entity_file_basic():

    fake_data = [
        {
            "name": "Forest",
            "films": ["http://ghibliapi.vercel.app/films/1"]
        }
    ]

    url_map = {
        "http://ghibliapi.vercel.app/films/1": "spirited away"
    }

    # create temp file safely
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmp:
        json.dump(fake_data, tmp)
        tmp_path = tmp.name

    result = process_entity_file(
        file_path=tmp_path,
        url_to_title=url_map
    )

    assert isinstance(result, dict)