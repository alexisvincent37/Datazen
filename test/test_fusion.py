import pytest
import pandas as pd
from datazen.data_manager import concat_dataframes, merge_dataframes

@pytest.fixture
def df1():
    return pd.DataFrame({'A': [1, 2], 'B': [3, 4]})

@pytest.fixture
def df2_same_cols():
    return pd.DataFrame({'A': [5, 6], 'B': [7, 8]})

@pytest.fixture
def df2_diff_cols():
    return pd.DataFrame({'C': [5, 6], 'D': [7, 8]})

@pytest.fixture
def df2_same_len():
    return pd.DataFrame({'C': [9, 10], 'D': [11, 12]})

def test_concat_rows_valid(df1, df2_same_cols):
    result = concat_dataframes(df1, df2_same_cols, axis=0)
    assert result.shape == (4, 2)
    assert set(result.columns) == {"A", "B"}

def test_concat_rows_invalid(df1, df2_diff_cols):
    with pytest.raises(ValueError):
        concat_dataframes(df1, df2_diff_cols, axis=0)

def test_concat_columns_valid(df1, df2_same_len):
    result = concat_dataframes(df1, df2_same_len, axis=1)
    assert result.shape == (2, 4)
    assert list(result.columns) == ["A", "B", "C", "D"]

def test_concat_columns_invalid(df1):
    df_shorter = pd.DataFrame({'X': [1]})
    with pytest.raises(ValueError):
        concat_dataframes(df1, df_shorter, axis=1)

def test_merge_inner(df1):
    df2 = pd.DataFrame({'C': [1, 2], 'D': [5, 6]})
    result = merge_dataframes(df1, df2, 'A', 'C', 'inner')
    assert result.shape == (2, 4)

def test_merge_left(df1):
    df2 = pd.DataFrame({'C': [2], 'D': [9]})
    result = merge_dataframes(df1, df2, 'A', 'C', 'left')
    assert result.shape == (2, 4)

def test_merge_right(df1):
    df2 = pd.DataFrame({'C': [2], 'D': [9]})
    result = merge_dataframes(df1, df2, 'A', 'C', 'right')
    assert result.shape[1] == 4

def test_merge_outer(df1):
    df2 = pd.DataFrame({'C': [2, 3], 'D': [9, 10]})
    result = merge_dataframes(df1, df2, 'A', 'C', 'outer')
    assert result.shape[0] == 3