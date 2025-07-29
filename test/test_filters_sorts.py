import pytest
import pandas as pd
import numpy as np
from datazen.data_manager import (
    filter_in_text,
    filter_comparaison,
    filter_types_columns,
    filter_keep_columns,
    filter_na,
    apply_filters,
    sort_abc,
    sort_123,
    apply_sort
)

@pytest.fixture
def df():
    return pd.DataFrame({
        "A": ["apple", "banana", "cherry", None],
        "B": [1, 2, 3, np.nan],
        "C": [1, 0, 1, None]
    })

def test_filter_in_text(df):
    result = filter_in_text(df, "A", "an")
    assert len(result) == 1
    assert "banana" in result["A"].values

def test_filter_comparaison_gt(df):
    result = filter_comparaison(df, "B", 1, "plus grand que")
    assert all(result["B"] > 1)

def test_filter_types_columns_text(df):
    result = filter_types_columns(df, "text")
    assert list(result.columns) == ["A"]

def test_filter_types_columns_numeric(df):
    result = filter_types_columns(df, "numeric")
    assert list(result.columns) == ["B", "C"]

def test_filter_types_columns_boolean(df):
    result = filter_types_columns(df, "boolean")
    assert list(result.columns) == []

def test_filter_keep_columns(df):
    result = filter_keep_columns(df, ["A", "B"])
    assert list(result.columns) == ["A", "B"]

def test_filter_na_drop(df):
    result = filter_na(df, "A", "drop")
    assert result.shape[0] == 3

def test_filter_na_mean(df):
    result = filter_na(df, "B", "mean")
    assert result["B"].isna().sum() == 0

def test_filter_na_median(df):
    result = filter_na(df, "B", "median")
    assert result["B"].isna().sum() == 0

def test_filter_na_zero(df):
    result = filter_na(df, "B", "zero")
    assert result["B"].isna().sum() == 0

def test_apply_filters_combined():
    df = pd.DataFrame({"A": ["apple", "banana", "cherry"], "B": [1, 2, 3]})
    filters = {
        "f1": {"type": "in_text", "col": "A", "value": "an"},
        "f2": {"type": "comparaison", "col": "B", "value": 1, "operator": "plus grand que"}
    }
    result = apply_filters(df, filters)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["A"] == "banana"


def test_sort_abc():
    df = pd.DataFrame({"A": ["banana", "apple", "cherry"], "B": [1, 2, 3]})
    result = sort_abc(df, "A", "asc")
    assert result.iloc[0]["A"] == "apple"

def test_sort_123():
    df = pd.DataFrame({"A": [3, 1, 2], "B": [5, 6, 7]})
    result = sort_123(df, "A", "asc")
    assert list(result["A"]) == [1, 2, 3]

def test_apply_sort():
    df = pd.DataFrame({"A": ["banana", "apple", "cherry"], "B": [2, 1, 3]})
    sort_info = [
        {"column_id": "A", "direction": "asc"},
        {"column_id": "B", "direction": "desc"}
    ]
    result = apply_sort(df, sort_info)

    assert isinstance(result, pd.DataFrame)

    expected = df.sort_values(by="A", ascending=True)
    expected = expected.sort_values(by="B", ascending=False)

    assert result.reset_index(drop=True).equals(expected.reset_index(drop=True))

