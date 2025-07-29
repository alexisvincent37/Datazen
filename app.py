from src.datazen.layouts import *
from src.datazen.data_manager import cache
from src.datazen.callbacks import *
from dash import Dash, html

app = Dash(external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

cache.init_app(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "flask_cache",
        "CACHE_DEFAULT_TIMEOUT": 0,
    },
)

app.layout = html.Div(
    [
        menudata,
        importpopup,
        table_container,
        visualization_container,
        text_filter_popup,
        in_text_filter_popup,
        comparaison_filter_popup,
        types_columns_popup,
        keep_columns_popup,
        Na_popup,
        outlier_popup,
        sort_abc_popup,
        sort_123_popup,
        concatenate_popup,
        merge_popup,
        export_popup,
    ],
    id="app_container",
)

server = app.server

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
