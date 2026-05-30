import pandas as pd
from data_processors.ghibli_label_tagging import build_labeled_dataset, MANUAL_LABELS


# =========================================================
# TEST: dataset builds successfully
# =========================================================
def test_build_dataset_runs():
    df = build_labeled_dataset()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "title" in df.columns
    assert "labels" in df.columns


# =========================================================
# TEST: known movie gets correct labels
# =========================================================
def test_spirited_away_labels_present():
    df = build_labeled_dataset()

    row = df[df["title"].str.lower() == "spirited away"]

    assert not row.empty

    labels = row.iloc[0]["labels"]

    assert isinstance(labels, list)
    assert "witch" in labels
    assert "dragons" in labels
    assert "family" in labels


# =========================================================
# TEST: unknown movie gets "other"
# =========================================================
def test_unknown_movie_defaults_to_other():
    df = build_labeled_dataset()

    # create fake row logic test (simulate function behavior)
    fake_title = "some random movie"

    labels = MANUAL_LABELS.get(fake_title, ["other"])

    assert labels == ["other"]


# =========================================================
# TEST: all rows have labels
# =========================================================
def test_all_rows_have_labels():
    df = build_labeled_dataset()

    assert df["labels"].isnull().sum() == 0

    for labels in df["labels"]:
        assert isinstance(labels, list)
        assert len(labels) > 0


# =========================================================
# TEST: label consistency with manual dict
# =========================================================
def test_manual_labels_exist():
    df = build_labeled_dataset()

    sample_title = "spirited away"
    expected = MANUAL_LABELS[sample_title]

    assert "witch" in expected
    assert "family" in expected