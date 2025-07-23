import pytest
import pandas as pd
from plotly.graph_objs import Figure
from datazen.data_manager import (
    histogram,
    boxplot,
    violin,
    pie_chart,
    bar_chart,
    scatter_2col,
    regression_2col,
    box_2col,
    violin_2col
)

@pytest.fixture
def df():
    return pd.DataFrame({
        'A': [1, 2, 2, 3, 3, 3],
        'B': [5, 3, 6, 2, 4, 1],
        'C': ['cat', 'dog', 'dog', 'cat', 'mouse', 'dog'],
        'D': [10, 20, 10, 20, 30, 40]
    })

def test_histogram(df):
    fig = histogram(df, 'A')
    assert isinstance(fig, Figure)

def test_boxplot(df):
    fig = boxplot(df, 'A')
    assert isinstance(fig, Figure)

def test_violin(df):
    fig = violin(df, 'A')
    assert isinstance(fig, Figure)

def test_pie_chart(df):
    fig = pie_chart(df, 'C')
    assert isinstance(fig, Figure)

def test_bar_chart(df):
    fig = bar_chart(df, 'C')
    assert isinstance(fig, Figure)

def test_scatter_2col(df):
    fig = scatter_2col(df, 'A', 'B')
    assert isinstance(fig, Figure)

def test_regression_2col(df):
    fig = regression_2col(df, 'A', 'B')
    assert isinstance(fig, Figure)

def test_box_2col(df):
    fig = box_2col(df, 'C', 'D')
    assert isinstance(fig, Figure)

def test_violin_2col(df):
    fig = violin_2col(df, 'C', 'D')
    assert isinstance(fig, Figure)
