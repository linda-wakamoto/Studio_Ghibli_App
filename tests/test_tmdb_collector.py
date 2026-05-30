from unittest.mock import patch, MagicMock
from data_collectors.tmdb_api_collector import TMDBCollector


@patch("requests.Session.get")
def test_tmdb_make_request(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "results": [{"id": 123, "title": "Totoro"}]
    }

    mock_get.return_value = mock_response

    collector = TMDBCollector()

    result = collector._make_request("search/movie", {"query": "Totoro"})

    assert "results" in result
    assert result["results"][0]["title"] == "Totoro"


def test_normalize():
    collector = TMDBCollector()

    assert collector._normalize("The Cat Returns") == "cat returns"
    assert collector._normalize("Spirited-Away") == "spiritedaway"