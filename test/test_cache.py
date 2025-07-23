
import pandas as pd
import pickle
from datazen.data_manager import set_df_to_cache, get_df_from_cache, id_hash
from unittest.mock import MagicMock
import hashlib

cache = MagicMock()

def set_df_to_cache(file_id: str, df: pd.DataFrame):
    data_pickle = pickle.dumps(df)
    cache.set(file_id, data_pickle, timeout=3600)

def get_df_from_cache(file_id: str) -> pd.DataFrame | None:
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return None
    return pickle.loads(pickled_df)

def test_set_df_to_cache_calls_cache_set():
    df = pd.DataFrame({"A": [1, 2]})
    set_df_to_cache("file_1", df)
    args, kwargs = cache.set.call_args
    assert args[0] == "file_1"
    unpickled = pickle.loads(args[1])
    pd.testing.assert_frame_equal(unpickled, df)
    assert kwargs.get("timeout") == 3600

def test_get_df_from_cache_returns_none_if_missing():
    cache.get.return_value = None
    result = get_df_from_cache("file_2")
    assert result is None

def test_get_df_from_cache_returns_dataframe():
    df = pd.DataFrame({"B": [3, 4]})
    pickled = pickle.dumps(df)
    cache.get.return_value = pickled
    result = get_df_from_cache("file_3")
    pd.testing.assert_frame_equal(result, df)


def test_id_hash_sha256():
    contents = "Hello, World!"
    expected = hashlib.sha256(contents.encode("utf-8")).hexdigest()

    result = id_hash(contents)

    assert result == expected
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result.lower())