import pandas as pd
from datazen.data_manager import import_csv

def encode_csv_to_base64(csv_str):
    import base64
    b64 = base64.b64encode(csv_str.encode("utf-8")).decode("utf-8")
    return f"data:text/csv;base64,{b64}"

def test_import_csv_valid():
    csv_content = "col1,col2\n1,2\n3,4"
    encoded = encode_csv_to_base64(csv_content)
    
    result = import_csv(encoded, "data.csv", sep=",", decimal=".", header=0)

    assert result["filename"] == "data.csv"
    assert isinstance(result["panda_data"], pd.DataFrame)
    assert result["panda_data"].shape == (2, 2)
    assert list(result["panda_data"].columns) == ["col1", "col2"]
    assert result["panda_data"].iloc[0, 0] == 1

def test_import_csv_invalid_base64():
    bad_encoded = "data:text/csv;base64,this_is_not_base64"
    result = import_csv(bad_encoded, "data.csv", sep=",", decimal=".", header=0)

    assert result["filename"] == "data.csv"
    assert result["panda_data"] is None
    assert "error" in result

def test_import_csv_wrong_extension():
    csv_content = "a;b\n1;2"
    encoded = encode_csv_to_base64(csv_content)
    result = import_csv(encoded, "data.txt", sep=";", decimal=",", header=0)

    assert result is None or result.get("panda_data") is None
