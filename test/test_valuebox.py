import pytest
import pandas as pd
import numpy as np
from datazen.data_manager import (
    count_quantitative,
    count_qualitative,
    nrow,
    nas
)

@pytest.fixture
def df_mixed():
    return pd.DataFrame({
        "num1": [1, 2, 3],
        "num2": [4.5, 5.5, 6.5],
        "text": ["a", "b", "c"],
        "bool": [True, False, True],
        "nan_col": [None, np.nan, 1]
    })

def test_count_quantitative(df_mixed):
    assert count_quantitative(df_mixed) == 3

def test_count_qualitative(df_mixed):
    assert count_qualitative(df_mixed) == 1

def test_nrow(df_mixed):
    assert nrow(df_mixed) == 3

def test_nas(df_mixed):
    assert nas(df_mixed) == 2
