import pandas as pd
from datazen.data_manager import (
    correlation_tab
)

def test_correlation_tab():
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6],
        "C": [7, 8, 9],
        "D": ["x", "y", "z"]
    })
    corr_df = correlation_tab(df)
    
    assert isinstance(corr_df, pd.DataFrame)
    assert "Colonne" in corr_df.columns
    assert corr_df.shape == (3, 4)
    assert corr_df.iloc[0, 1] == 1.0
