import base64
import io
import pandas as pd
from datazen.data_manager import import_excel


def test_import_excel_success():
    df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Sheet1")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode()
    contents = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{encoded}"
    result = import_excel(contents, "test.xlsx", "Sheet1")
    assert result["filename"] == "test.xlsx"
    assert isinstance(result["panda_data"], pd.DataFrame)
    pd.testing.assert_frame_equal(result["panda_data"], df)

def test_import_excel_sheet_not_found():
    df = pd.DataFrame({"A": [1]})
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Sheet1")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode()
    contents = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{encoded}"
    result = import_excel(contents, "test.xlsx", "FeuilleInexistante")
    assert result["filename"] == "test.xlsx"
    assert result["panda_data"] is None
    assert "Feuille Excel introuvable" in result["error"]

def test_import_excel_invalid_file():
    invalid_contents = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,aaaaaaa"
    result = import_excel(invalid_contents, "test.xlsx", "Sheet1")
    assert result["filename"] == "test.xlsx"
    assert result["panda_data"] is None
    assert "Erreur" in result["error"]

def test_import_excel_invalid_contents_format():
    contents = "invalid_content_without_comma"
    result = import_excel(contents, "test.xlsx", "Sheet1")
    assert result["filename"] == "test.xlsx"
    assert result["panda_data"] is None
    assert "Erreur" in result["error"]