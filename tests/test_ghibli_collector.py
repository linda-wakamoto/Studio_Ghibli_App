import pytest
from unittest.mock import patch
from data_collectors.ghibli_api_collector import GhibliCollector


@patch("requests.get")
def test_make_request(mock_get):
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = [
        {"id": "1", "title": "Totoro"}
    ]

    collector = GhibliCollector()
    result = collector._make_request("films")

    assert isinstance(result, list)
    assert result[0]["title"] == "Totoro"

def test_validate_data():
    collector = GhibliCollector()

    good_data = [{"id": 1, "title": "Totoro"}]

    collector.validate_data(good_data, "films")


def test_validate_data_empty():
    collector = GhibliCollector()

    with pytest.raises(ValueError):
        collector.validate_data([], "films")