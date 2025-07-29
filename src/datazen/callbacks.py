from dash import *
from datazen.data_manager import *
import dash
import uuid
import json
import pandas as pd
import plotly.express as px
import pickle


@callback(
    Output("menudata", "className"),
    Input("sidebar_button", "n_clicks"),
    State("menudata", "className"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks, active_class):
    if n_clicks is None:
        return no_update

    current_class = active_class if active_class else ""

    if "closed" in current_class:
        return current_class.replace("closed", "").strip()
    else:
        return current_class + " closed"


@callback(
    Output("importpopup", "className"),
    Output("import-feedback-csv", "children"),
    Output("import-feedback-excel", "children"),
    Input("importbutton", "n_clicks"),
    Input("importpopup_close_button", "n_clicks"),
    Input("import-validate-button-csv", "n_clicks"),
    Input("import-validate-button-excel", "n_clicks"),
    State("importpopup", "className"),
    State("import-data", "contents"),
    State("import-data", "filename"),
    State("import-separator", "value"),
    State("import-decimal", "value"),
    State("import-header", "value"),
    State("import-sheetname", "value"),
    State("import-decimal-excel", "value"),
    State("import-header-excel", "value"),
    prevent_initial_call=True,
)
def toggle_import_popup(
    openclick,
    closeclick,
    importvalidation_csv,
    importvalidation_excel,
    active_class,
    contents,
    filename,
    sep,
    decimal_csv,
    header_csv,
    sheet_name,
    decimal_excel,
    header_excel,
):
    current_class = active_class or ""

    if ctx.triggered_id == "importbutton":
        if "open" not in current_class:
            new_class = (current_class + " open").strip()
            return new_class, "", ""
        return current_class, "", ""

    elif ctx.triggered_id == "importpopup_close_button":
        new_class = current_class.replace("open", "").strip()
        return new_class, "", ""

    elif ctx.triggered_id == "import-validate-button-csv":
        result = import_csv(contents, filename, sep, decimal_csv, header_csv)
        error = result.get("error")
        if error is None:
            new_class = current_class.replace("open", "").strip()
            return new_class, "", ""
        return current_class, error or "Une erreur inconnue est survenue.", ""

    elif ctx.triggered_id == "import-validate-button-excel":
        result = import_excel(
            contents, filename, sheet_name, header=header_excel, decimal=decimal_excel
        )
        error = result.get("error")
        data = result.get("data")
        if error is None and data is not None:
            new_class = current_class.replace("open", "").strip()
            return new_class, "", ""
        return current_class, "", error

    return no_update, no_update, no_update


@callback(
    Output("importbutton_popup", "className"),
    Output("import-error-feedback", "children", allow_duplicate=True),
    Output("import-data", "filename"),
    Output("import-error-interval", "disabled"),
    Input("import-data", "filename"),
    Input("importpopup_close_button", "n_clicks"),
    Input("import-validate-button-csv", "n_clicks"),
    Input("import-validate-button-excel", "n_clicks"),
    State("importbutton_popup", "className"),
    prevent_initial_call=True,
)
def toggle_button_and_type_error_import(
    filename, closeclick, importvalidation, importexcelvalidation, active_class
):
    if not ctx.triggered:
        return no_update, "", no_update, True

    triggered_id = ctx.triggered_id

    if not active_class:
        active_class = ""

    try:
        if not (
            filename.endswith(".csv")
            or filename.endswith(".xlsx")
            or filename.endswith(".xls")
        ):
            if "closed" not in active_class:
                new_class = (active_class + " closed").strip()
            return new_class, "Veuillez importer un fichier CSV ou Excel.", None, False
    except Exception:
        return no_update, "", no_update, True

    if triggered_id == "importpopup_close_button":
        new_class = active_class.replace("closed", "").strip()
        return new_class, "", None, True

    if triggered_id == "import-validate-button-csv":
        new_class = active_class
        if "closed" not in active_class:
            new_class = (active_class + " closed").strip()
        return new_class, "", no_update, True

    if triggered_id == "import-validate-button-excel":
        new_class = active_class
        if "closed" not in active_class:
            new_class = (active_class + " closed").strip()
        return new_class, "", no_update, True

    if triggered_id == "import-data" and filename is not None:
        new_class = active_class
        if "closed" not in active_class:
            new_class = (active_class + " closed").strip()
        return new_class, "", no_update, True

    return no_update, "", no_update, True


@callback(
    Output("importbutton_popup", "className", allow_duplicate=True),
    Output("import-error-feedback", "children", allow_duplicate=True),
    Input("import-error-interval", "n_intervals"),
    Input("importpopup_close_button", "n_clicks"),
    State("importbutton_popup", "className"),
    prevent_initial_call=True,
)
def reset_button_after_interval(n_intervals, closeclick, current_class):

    triggered_id = ctx.triggered_id

    if n_intervals == 0:
        raise dash.exceptions.PreventUpdate

    if triggered_id == "importpopup_close_button":
        return "importbutton_popup", ""

    new_class = current_class.replace("closed", "").strip()
    return new_class, ""


@callback(
    Output("importpopup_content_csv", "className"),
    Input("import-data", "filename"),
    Input("importpopup_close_button", "n_clicks"),
    State("importpopup_content_csv", "className"),
    prevent_initial_call=True,
)
def update_import_content_class_csv(filename, closeclick, current_class):

    if not ctx.triggered:
        return no_update
    triggered_id = ctx.triggered_id

    if triggered_id == "importpopup_close_button":

        return "importpopup_content_csv"

    if (
        triggered_id == "import-data"
        and filename is not None
        and filename.endswith(".csv")
    ):

        return "importpopup_content_csv open"

    return current_class or "importpopup_content_csv"


@callback(
    Output("title_importpopup-excel", "className"),
    Output("title_importpopup-excel", "children"),
    Input("import-data", "filename"),
    Input("importpopup_close_button", "n_clicks"),
    prevent_initial_call=True,
)
def update_import_title_excel(filename, closeclick):
    if not ctx.triggered:
        return no_update, no_update

    triggered_id = ctx.triggered_id

    if triggered_id == "importpopup_close_button":
        return "title_importpopup-excel", ""

    if triggered_id == "import-data" and filename is not None:
        if len(filename) > 20:
            filename = filename[:20] + "..."
        return "title_importpopup-excel open", f"{filename}"

    return "title_importpopup-excel", ""


@callback(
    Output("importpopup_content_excel", "className"),
    Input("import-data", "filename"),
    Input("import-data", "contents"),
    Input("importpopup_close_button", "n_clicks"),
    Input("import-validate-button-excel", "n_clicks"),
    State("importpopup_content_excel", "className"),
    State("import-sheetname", "value"),
    State("import-decimal-excel", "value"),
    State("import-header-excel", "value"),
    prevent_initial_call=True,
)
def update_import_content_class_excel(
    filename,
    content,
    closeclick,
    validateclick,
    current_class,
    sheet_name,
    decimal,
    header,
):
    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered_id
    current_class = current_class or "importpopup_content_excel"

    if triggered_id == "importpopup_close_button":
        return "importpopup_content_excel"

    if (
        triggered_id == "import-data"
        and filename
        and (filename.endswith(".xlsx") or filename.endswith(".xls"))
    ):
        return "importpopup_content_excel open"

    if triggered_id == "import-validate-button-excel":
        try:
            result = import_excel(
                content,
                filename,
                sheet_name,
                header,
                decimal,
            )
            if result.get("error") is None:
                return current_class.replace("open", "").strip()
        except Exception:
            pass

    return current_class


@callback(
    Output("title_importpopup", "children"),
    Input("import-data", "filename"),
    Input("importpopup_close_button", "n_clicks"),
    prevent_initial_call=True,
)
def update_import_title(filename, closeclick):

    if isinstance(filename, str) and len(filename) > 20:
        filename = filename[:20] + "..."

    if not ctx.triggered:
        return no_update
    triggered_id = ctx.triggered_id

    if triggered_id == "importpopup_close_button":
        return ""

    if triggered_id == "import-data" and filename is not None:
        return f"{filename}"

    return no_update


@callback(
    Output("stored-data", "data"),
    Output("import-separator", "value"),
    Output("import-decimal", "value"),
    Output("import-header", "value"),
    Output("import-decimal-excel", "value"),
    Output("import-header-excel", "value"),
    Output("import-sheetname", "value"),
    Input("import-validate-button-csv", "n_clicks"),
    Input("import-validate-button-excel", "n_clicks"),
    State("import-separator", "value"),
    State("import-decimal", "value"),
    State("import-header", "value"),
    State("import-decimal-excel", "value"),
    State("import-header-excel", "value"),
    State("import-sheetname", "value"),
    State("import-data", "contents"),
    State("import-data", "filename"),
    State("stored-data", "data"),
    prevent_initial_call=True,
)
def store_imported_data(
    n_clicks_csv,
    n_clicks_excel,
    sep,
    decimal_csv,
    header_csv,
    decimal_excel,
    header_excel,
    sheetname,
    contents,
    filename,
    stored_data,
):
    if not contents or not filename:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    result = None

    if filename.lower().endswith(".csv"):
        result = import_csv(
            contents, filename, sep=sep, decimal=decimal_csv, header=header_csv
        )
    elif filename.lower().endswith((".xls", ".xlsx")):
        try:
            header_excel = int(header_excel)
        except Exception:
            header_excel = 0
        result = import_excel(
            contents,
            filename,
            sheet_name=sheetname if sheetname else 0,
            header=header_excel,
            decimal=decimal_excel,
        )
    else:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    if result and result.get("error") is None:
        df = result.get("panda_data")
        file_id = id_hash(contents)

        if stored_data is None:
            stored_data = {"files": []}

        if not any(f["id"] == file_id for f in stored_data["files"]):
            stored_data["files"].append(
                {
                    "name": filename[:20] + "..." if len(filename) > 20 else filename,
                    "id": file_id,
                }
            )

        set_df_to_cache(file_id, df)

        return stored_data, ",", ".", 0, ".", 0, "0"

    return no_update, no_update, no_update, no_update, no_update, no_update, no_update


@callback(
    Output("datastorage", "children"),
    Output("stored-data", "data", allow_duplicate=True),
    Output("importpopup_content_csv", "className", allow_duplicate=True),
    Output("importbutton_popup", "className", allow_duplicate=True),
    Output("import-data", "contents", allow_duplicate=True),
    Output("import-data", "filename", allow_duplicate=True),
    Output("table_container", "children", allow_duplicate=True),
    Output("active_table", "data", allow_duplicate=True),
    Input({"type": "data_remove", "index": ALL}, "n_clicks"),
    Input("stored-data", "data"),
    State("stored-data", "data"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def manage_files(remove_clicks, stored_data, stored_data_state, active_table_id):
    if not stored_data or "files" not in stored_data or not stored_data["files"]:
        return (
            [],
            {"files": []},
            "importpopup_content_csv",
            "importbutton_popup",
            None,
            None,
            html.Div(),
            None,
        )

    file_id_to_remove = None
    if (
        ctx.triggered_id
        and isinstance(ctx.triggered_id, dict)
        and ctx.triggered_id.get("type") == "data_remove"
    ):
        file_id_to_remove = ctx.triggered_id["index"]

    if file_id_to_remove:
        filtered_files = [
            f for f in stored_data["files"] if f["id"] != file_id_to_remove
        ]
    else:
        filtered_files = stored_data["files"]

    buttons = []
    for f in filtered_files:
        file_block = html.Div(
            [
                html.Button(
                    f["name"],
                    className="data_added",
                    id={"type": "data_added", "index": f["id"]},
                ),
                html.Button(
                    html.I(className="fa-solid fa-xmark"),
                    className="data_remove",
                    id={"type": "data_remove", "index": f["id"]},
                ),
            ],
            className="data-row",
        )
        buttons.append(file_block)

    if (
        file_id_to_remove
        and active_table_id
        and file_id_to_remove == active_table_id.get("id")
    ):
        clear_table = html.Div()
        reset_active = None
    else:
        clear_table = dash.no_update
        reset_active = dash.no_update

    return (
        html.Div(buttons),
        {"files": filtered_files},
        "importpopup_content_csv",
        "importbutton_popup",
        None,
        None,
        clear_table,
        reset_active,
    )


@callback(
    Output("filter_sort_history", "className"),
    Input("filter_sort_history_button", "n_clicks"),
    State("filter_sort_history", "className"),
    prevent_initial_call=True,
)
def toggle_filter_sort_history(n_clicks, activeclass):
    if n_clicks is None:
        return no_update
    current_class = activeclass or ""
    if "open" in current_class:
        return current_class.replace("open", "").strip()
    else:
        return (current_class + " open").strip() if current_class else "open"


@callback(
    Output("table_container", "children", allow_duplicate=True),
    Output("active_table", "data", allow_duplicate=True),
    Input({"type": "data_added", "index": ALL}, "n_clicks"),
    State("stored-data", "data"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def display_table(n_clicks, stored_data, active_table):

    if not stored_data or "files" not in stored_data or not stored_data["files"]:
        return no_update, no_update

    triggered_id = ctx.triggered_id
    if not triggered_id:
        return no_update, no_update

    file_id = triggered_id.get("index")

    if active_table and file_id == active_table.get("id"):
        return no_update, no_update

    try:
        index_in_all = [i["id"]["index"] for i in ctx.inputs_list[0]].index(file_id)
    except Exception:
        return no_update, no_update

    if not n_clicks or n_clicks[index_in_all] is None or n_clicks[index_in_all] == 0:
        return no_update, no_update

    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return "Cache expiré, recharge le fichier.", no_update

    df = pickle.loads(pickled_df)
    if df is None:
        return "Erreur: df vide après chargement du cache.", no_update

    table = dash_table.DataTable()
    return table, {"id": file_id, "filters": {}, "sort": []}


@callback(
    Output("table_container_wrapper", "className"),
    Input("rezize_table_button", "n_clicks"),
    State("table_container_wrapper", "className"),
    prevent_initial_call=True,
)
def toggle_table_container(n_clicks, current_class):
    if not ctx.triggered:
        return no_update

    if current_class and "closed" in current_class:
        return current_class.replace("closed", "").strip()
    else:
        return (current_class + " closed").strip() if current_class else "closed"


@callback(
    Output("visualization_container", "style"),
    Input("table_container_wrapper", "className"),
)
def update_visualization_visibility(table_class):
    if "closed" in (table_class or ""):
        return {
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "width": "100vw",
            "height": "100vh",
        }
    return {"display": "none"}


@callback(
    Output("savebutton", "className"),
    Output("filter_button", "className"),
    Output("tri_button", "className"),
    Output("savebutton", "children"),
    Output("df_fusion_button", "className"),
    Output("exportbutton", "className"),
    Output("reset-interval", "disabled"),
    Output("reset-interval", "n_intervals"),
    Input("savebutton", "n_clicks"),
    Input("table_container", "children"),
    Input("reset-interval", "n_intervals"),
    Input("active_table", "data"),
    State("savebutton", "className"),
    State("filter_button", "className"),
    State("tri_button", "className"),
    prevent_initial_call=True,
)
def toggle_btns(
    n_clicks, table, n_interv, active_table_data, cls_save, cls_filter, cls_tri
):
    triggered_id = ctx.triggered_id
    base_cls = (
        "savebutton",
        "filter_button",
        "tri_button",
        "df_fusion_button",
        "exportbutton",
    )
    open_cls = [c + " open" if table else c for c in base_cls]

    if not active_table_data or not active_table_data.get("id"):
        open_cls = [c.replace(" open", "") for c in open_cls]

    if triggered_id in ["reset-interval", "table_container"]:
        return (
            open_cls[0],
            open_cls[1],
            open_cls[2],
            html.I(className="fa-solid fa-floppy-disk"),
            open_cls[3],
            open_cls[4],
            True,
            0,
        )

    if triggered_id == "savebutton" and n_clicks:
        return (
            open_cls[0] + " active",
            open_cls[1],
            open_cls[2],
            html.I(className="fa-solid fa-check animated-icon"),
            open_cls[3],
            open_cls[4],
            False,
            0,
        )

    return (
        open_cls[0],
        open_cls[1],
        open_cls[2],
        html.I(className="fa-solid fa-floppy-disk"),
        open_cls[3],
        open_cls[4],
        True,
        0,
    )


@callback(
    Output("stored-data", "data", allow_duplicate=True),
    Input("savebutton", "n_clicks"),
    State({"type": "data_viewer", "index": ALL}, "data"),
    State({"type": "data_viewer", "index": ALL}, "id"),
    State("stored-data", "data"),
    prevent_initial_call=True,
)
def save_table_data(n_clicks, data_list, id_list, stored_data):
    """
    Sauvegarde les données modifiées dans le cache à partir des tableaux éditables.
    """
    if not stored_data or "files" not in stored_data:
        return dash.no_update

    for row_list, df_id in zip(data_list, id_list):
        if not row_list:
            continue

        file_id = df_id["index"]

        try:
            old_df_pickled = cache.get(file_id)
            if old_df_pickled is None:
                continue
            old_df = pickle.loads(old_df_pickled)

            new_df = pd.DataFrame(row_list, columns=old_df.columns)

            set_df_to_cache(file_id, new_df)

        except Exception as e:
            print(f"Erreur lors de la sauvegarde du fichier {file_id} : {e}")
            continue

    return stored_data


@callback(
    Output("table_container", "children", allow_duplicate=True),
    Output("active_table", "data", allow_duplicate=True),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_table_with_filters_and_sort(active_table):
    if not active_table:
        return no_update, no_update

    file_id = active_table.get("id")
    filters = active_table.get("filters", {})
    sort_info = active_table.get("sort", [])

    if file_id is None:
        return no_update, no_update

    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return "fichier introuvable, recharge le fichier.", no_update

    df = pickle.loads(pickled_df)

    df_filtered = apply_filters(df, filters)

    df_sorted = apply_sort(df_filtered, sort_info)

    sorted_data = df_sorted.to_dict("records")

    table = dash_table.DataTable(
        id={"type": "data_viewer", "index": file_id},
        data=sorted_data,
        columns=[{"name": col, "id": col} for col in df_sorted.columns],
        page_size=26,
        editable=True,
        style_table={
            "margin-top": "2.5vh",
            "overflowX": "auto",
            "borderRadius": "10px",
            "boxShadow": "0 4px 10px rgba(0, 0, 0, 0.1)",
            "border": "1px solid #374151",
            "height": "90vh",
            "maxWidth": "70vw",
        },
        style_header={
            "backgroundColor": "#1f2937",
            "color": "white",
            "fontWeight": "bold",
            "fontSize": "16px",
            "borderBottom": "2px solid #374151",
            "textAlign": "center",
            "position": "sticky",
            "top": 0,
            "zIndex": 1000,
            "minWidth": "150px",
        },
        style_cell={
            "color": "white",
            "padding": "6px",
            "textAlign": "center",
            "fontFamily": "Segoe UI, sans-serif",
            "fontSize": "12px",
            "backgroundColor": "transparent",
            "whiteSpace": "normal",
            "overflow": "visible",
            "textOverflow": "unset",
            "minWidth": "150px",
        },
    )

    return table, active_table


@callback(
    Output("filter_list", "children"),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_filter_list(active_table):
    if not active_table:
        return []

    filters = active_table.get("filters", {})
    if not isinstance(filters, dict):
        return []

    items = []
    for filter_id, f in filters.items():
        f_type = f.get("type", "")
        label = ""

        if f_type == "text":
            label = f"{f.get('col', '')} recherche '{f.get('value', '')}'"

        elif f_type == "in_text":
            label = f"{f.get('col', '')} contient '{f.get('value', '')}'"

        elif f_type == "comparaison":
            op_map = {
                "greater_than": ">",
                "less_than": "<",
                "equal_to": "=",
                "different_than": "≠",
            }
            op = op_map.get(f.get("operator", ""), f.get("operator", ""))
            label = f"{f.get('col', '')} {op} {f.get('value', '')}"

        elif f_type == "types_columns":
            label = f"Type colonne : {f.get('col_type', '')}"

        elif f_type == "keep_columns":
            cols = f.get("columns", [])
            label = (
                f"Garder colonnes : {', '.join(cols)}"
                if isinstance(cols, list)
                else str(cols)
            )

        elif f_type == "na":
            action_map = {
                "drop": "Supprimer les lignes",
                "mean": "Remplacer par la moyenne",
                "median": "Remplacer par la médiane",
                "zero": "Remplacer par zéro",
            }
            action_label = action_map.get(f.get("action", ""), f.get("action", ""))
            label = f"{action_label} si NA dans '{f.get('col', '')}'"
        elif f_type == "outlier":
            label = f"Détection des valeurs aberrantes dans '{f.get('col', '')}' avec la méthode '{f.get('method', '')}'"
        items.append(
            html.Li(
                [
                    html.Span(label, style={"marginRight": "10px"}),
                    html.I(
                        className="fa-solid fa-xmark",
                        style={"cursor": "pointer", "color": "red"},
                        id={"type": "remove_filter", "filter_id": filter_id},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                },
            )
        )

    return items


@callback(
    Output("sort_list", "children"),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_sort_list(active_table):
    if not active_table:
        return []

    sort_info = active_table.get("sort", [])
    if not isinstance(sort_info, list):
        return []

    items = []
    for sort in sort_info:
        col = sort.get("column_id", "?")
        order = sort.get("direction", "asc")
        tri_type = sort.get("type", "")

        direction = "A → Z" if order == "asc" else "Z → A"
        type_str = (
            "(texte)"
            if tri_type == "abc"
            else "(numérique)" if tri_type == "123" else ""
        )

        label = f"{col} {direction} {type_str}"

        items.append(
            html.Li(
                [
                    html.Span(label, style={"marginRight": "10px"}),
                    html.I(
                        className="fa-solid fa-xmark",
                        style={"cursor": "pointer", "color": "red"},
                        id={"type": "remove_sort", "col": col},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                },
            )
        )

    return items


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input({"type": "remove_filter", "filter_id": ALL}, "n_clicks"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def remove_filter(n_clicks, active_table):
    if not n_clicks or not active_table:
        return no_update

    for click, filter_obj in zip(n_clicks, ctx.inputs_list[0]):
        if click:
            filter_id = filter_obj["id"]["filter_id"]
            filters = active_table.get("filters", {})
            if filter_id in filters:
                del filters[filter_id]
                active_table["filters"] = filters
                break

    return active_table


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input({"type": "remove_sort", "col": ALL}, "n_clicks"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def remove_sort(n_clicks, active_table):
    if not n_clicks or not active_table:
        return no_update

    for click, col_obj in zip(n_clicks, ctx.inputs_list[0]):
        if click:
            col_name = col_obj["id"]["col"]
            sort_list = active_table.get("sort", [])
            if not isinstance(sort_list, list):
                return no_update
            sort_list = [s for s in sort_list if s.get("column_id") != col_name]
            active_table["sort"] = sort_list
            break

    return active_table


@callback(
    Output("text_filter_popup", "className"),
    Output("text_filter_column_dropdown", "value"),
    Output("text_filter_input", "value"),
    Input("filter_text", "n_clicks"),
    Input("text_filter_popup_close_button", "n_clicks"),
    Input("import-validate-button-text-filter", "n_clicks"),
    State("text_filter_popup", "className"),
    prevent_initial_call=True,
)
def toggle_text_filter_popup(open_clicks, close_clicks, validate_clicks, current_class):
    if not ctx.triggered:
        return no_update, no_update, no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "filter_text":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip(), no_update, no_update
        else:
            return (
                ((current_class + " open").strip() if current_class else "open"),
                no_update,
                no_update,
            )

    elif triggered_id in [
        "text_filter_popup_close_button",
        "import-validate-button-text-filter",
    ]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None, ""

    return no_update, no_update, no_update


@callback(
    Output("text_filter_column_dropdown", "options"),
    Input("active_table", "data"),
)
def update_dropdown_columns_text(active_table_data):
    if not active_table_data or "id" not in active_table_data:
        return []

    file_id = active_table_data["id"]
    pickled_df = cache.get(file_id)

    if pickled_df is None:
        return []

    df = pickle.loads(pickled_df)
    cols = df.columns.tolist()
    return [{"label": c, "value": c} for c in cols]


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-text-filter", "n_clicks"),
    State("active_table", "data"),
    State("text_filter_column_dropdown", "value"),
    State("text_filter_input", "value"),
    prevent_initial_call=True,
)
def store_text_filter(n_clicks, active_table, col_name, search_text):
    if not n_clicks or not active_table or not col_name or search_text is None:
        return no_update

    filters = active_table.get("filters", {})
    if not isinstance(filters, dict):
        filters = {}

    filters = {
        k: v
        for k, v in filters.items()
        if not (v.get("type") == "text" and v.get("col") == col_name)
    }

    new_id = str(uuid.uuid4())
    filters[new_id] = {"type": "text", "col": col_name, "value": search_text}
    active_table["filters"] = filters

    return active_table


@callback(
    Output("in_text_filter_popup", "className"),
    Output("in_text_filter_column_dropdown", "value"),
    Output("in_text_filter_input", "value"),
    Input("filter_in_text", "n_clicks"),
    Input("in_text_filter_popup_close_button", "n_clicks"),
    Input("import-validate-button-in-text-filter", "n_clicks"),
    State("in_text_filter_popup", "className"),
    prevent_initial_call=True,
)
def toggle_in_text_filter_popup(
    open_clicks, close_clicks, validate_clicks, current_class
):
    if not ctx.triggered:
        return no_update, no_update, no_update

    triggered_id = ctx.triggered_id

    if triggered_id == "filter_in_text":
        if current_class and "open" in current_class:
            new_class = current_class.replace("open", "").strip()
            return new_class, no_update, no_update
        else:
            new_class = (current_class + " open").strip() if current_class else "open"
            return new_class, no_update, no_update

    elif triggered_id in [
        "in_text_filter_popup_close_button",
        "import-validate-button-in-text-filter",
    ]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None, ""

    return no_update, no_update, no_update


@callback(
    Output("in_text_filter_column_dropdown", "options"),
    Input("active_table", "data"),
)
def update_dropdown_columns_in_text(active_table_data):
    if not active_table_data or "id" not in active_table_data:
        return []

    file_id = active_table_data["id"]
    pickled_df = cache.get(file_id)

    if pickled_df is None:
        return []

    df = pickle.loads(pickled_df)
    cols = df.columns.tolist()
    return [{"label": c, "value": c} for c in cols]


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-in-text-filter", "n_clicks"),
    State("active_table", "data"),
    State("in_text_filter_column_dropdown", "value"),
    State("in_text_filter_input", "value"),
    prevent_initial_call=True,
)
def store_in_text_filter(n_clicks, active_table, col_name, search_text):
    if not n_clicks or not active_table or not col_name or search_text is None:
        return no_update

    filters = active_table.get("filters", {})
    if not isinstance(filters, dict):
        filters = {}

    filters = {
        k: v
        for k, v in filters.items()
        if not (v.get("type") == "in_text" and v.get("col") == col_name)
    }

    new_id = str(uuid.uuid4())
    filters[new_id] = {"type": "in_text", "col": col_name, "value": search_text}
    active_table["filters"] = filters

    return active_table


@callback(
    Output("comparaison_filter_popup", "className"),
    Output("comparaison_filter_column_dropdown", "value"),
    Output("comparaison_filter_value_input", "value"),
    Output("comparaison_filter_operator_dropdown", "value"),
    Input("filter_comparaison", "n_clicks"),
    Input("comparaison_filter_popup_close_button", "n_clicks"),
    Input("import-validate-button-comparaison-filter", "n_clicks"),
    State("comparaison_filter_popup", "className"),
    prevent_initial_call=True,
)
def toggle_comparaison_filter_popup(
    open_clicks, close_clicks, validate_clicks, current_class
):
    if not ctx.triggered:
        return no_update, no_update, no_update, no_update
    triggered_id = ctx.triggered_id
    if triggered_id == "filter_comparaison":
        if current_class and "open" in current_class:
            return (
                current_class.replace("open", "").strip(),
                no_update,
                no_update,
                no_update,
            )
        else:
            return (
                ((current_class + " open").strip() if current_class else "open"),
                no_update,
                no_update,
                no_update,
            )
    elif triggered_id in [
        "comparaison_filter_popup_close_button",
        "import-validate-button-comparaison-filter",
    ]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None, None, None
    return no_update, no_update, no_update, no_update


@callback(
    Output("comparaison_filter_column_dropdown", "options"),
    Input("active_table", "data"),
)
def update_dropdown_columns_comparaison_filter(active_table_data):
    if not active_table_data or "id" not in active_table_data:
        return []
    file_id = active_table_data["id"]
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return []
    df = pickle.loads(pickled_df)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    return [{"label": c, "value": c} for c in numeric_cols]


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-comparaison-filter", "n_clicks"),
    State("active_table", "data"),
    State("comparaison_filter_column_dropdown", "value"),
    State("comparaison_filter_value_input", "value"),
    State("comparaison_filter_operator_dropdown", "value"),
    prevent_initial_call=True,
)
def store_comparaison_filter(n_clicks, active_table, col_name, value, operator):
    if not n_clicks:
        return dash.no_update
    filters = active_table.get("filters", {})
    if not isinstance(filters, dict):
        filters = {}
    new_id = str(uuid.uuid4())
    filters[new_id] = {
        "type": "comparaison",
        "col": col_name,
        "value": value,
        "operator": operator,
    }
    active_table["filters"] = filters
    return active_table


@callback(
    Output("types_columns_popup", "className"),
    Output("types_columns_dropdown", "value"),
    Input("filter_types_columns", "n_clicks"),
    Input("types_columns_popup_close_button", "n_clicks"),
    Input("import-validate-button-types-columns", "n_clicks"),
    State("types_columns_popup", "className"),
    prevent_initial_call=True,
)
def toggle_types_columns_popup(
    open_clicks, close_clicks, validate_clicks, current_class
):
    if not ctx.triggered:
        return no_update, no_update
    triggered_id = ctx.triggered_id
    if triggered_id == "filter_types_columns":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip(), no_update
        else:
            return (
                (current_class + " open").strip() if current_class else "open"
            ), no_update
    elif triggered_id in [
        "types_columns_popup_close_button",
        "import-validate-button-types-columns",
    ]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None
    return no_update, no_update


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-types-columns", "n_clicks"),
    State("active_table", "data"),
    State("types_columns_dropdown", "value"),
    prevent_initial_call=True,
)
def store_types_columns_filter(n_clicks, active_table, col_type):
    if not n_clicks:
        return dash.no_update
    filters = active_table.get("filters", {})
    if not isinstance(filters, dict):
        filters = {}
    filters = {k: v for k, v in filters.items() if v.get("type") != "types_columns"}
    new_id = str(uuid.uuid4())
    filters[new_id] = {"type": "types_columns", "col_type": col_type}
    active_table["filters"] = filters
    return active_table


@callback(
    Output("keep_columns_popup", "className"),
    Output("keep_columns_dropdown", "value"),
    Input("filter_keep_columns", "n_clicks"),
    Input("keep_columns_popup_close_button", "n_clicks"),
    Input("import-validate-button-keep-columns", "n_clicks"),
    State("keep_columns_popup", "className"),
    prevent_initial_call=True,
)
def toggle_keep_columns_popup(
    open_clicks, close_clicks, validate_clicks, current_class
):
    if not ctx.triggered:
        return no_update, no_update
    triggered_id = ctx.triggered_id
    if triggered_id == "filter_keep_columns":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip(), no_update
        else:
            return (
                (current_class + " open").strip() if current_class else "open"
            ), no_update
    elif triggered_id in [
        "keep_columns_popup_close_button",
        "import-validate-button-keep-columns",
    ]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None
    return no_update, no_update


@callback(
    Output("keep_columns_dropdown", "options"),
    Input("active_table", "data"),
)
def update_keep_columns_dropdown(active_table_data):
    if not active_table_data or "id" not in active_table_data:
        return []
    file_id = active_table_data["id"]
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return []
    df = pickle.loads(pickled_df)
    cols = df.columns.tolist()
    return [{"label": c, "value": c} for c in cols]


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-keep-columns", "n_clicks"),
    State("active_table", "data"),
    State("keep_columns_dropdown", "value"),
    prevent_initial_call=True,
)
def store_keep_columns_filter(n_clicks, active_table, selected_columns):
    if not n_clicks:
        return dash.no_update
    filters = active_table.get("filters", {})
    if not isinstance(filters, dict):
        filters = {}
    filters = {k: v for k, v in filters.items() if v.get("type") != "keep_columns"}
    new_id = str(uuid.uuid4())
    filters[new_id] = {"type": "keep_columns", "columns": selected_columns}
    active_table["filters"] = filters
    return active_table


@callback(
    Output("Na_popup", "className"),
    Output("Na_column_dropdown", "value"),
    Input("filter_NA", "n_clicks"),
    Input("Na_popup_close_button", "n_clicks"),
    Input("import-validate-button-Na", "n_clicks"),
    State("Na_popup", "className"),
    prevent_initial_call=True,
)
def toggle_na_popup(open_clicks, close_clicks, validate_clicks, current_class):
    if not ctx.triggered:
        return no_update, no_update
    triggered_id = ctx.triggered_id
    if triggered_id == "filter_NA":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip(), no_update
        else:
            return (
                (current_class + " open").strip() if current_class else "open"
            ), no_update
    elif triggered_id in ["Na_popup_close_button", "import-validate-button-Na"]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None
    return no_update, no_update


@callback(
    Output("Na_column_dropdown", "options"),
    Input("active_table", "data"),
)
def update_na_column_dropdown(active_table_data):
    if not active_table_data or "id" not in active_table_data:
        return []
    file_id = active_table_data["id"]
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return []
    df = pickle.loads(pickled_df)
    cols = df.columns.tolist()
    return [{"label": c, "value": c} for c in cols]


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-Na", "n_clicks"),
    State("active_table", "data"),
    State("Na_column_dropdown", "value"),
    State("Na_action_dropdown", "value"),
    prevent_initial_call=True,
)
def store_na_filter(n_clicks, active_table, col_name, action):
    if not n_clicks:
        return dash.no_update
    filters = active_table.get("filters", {})
    if not isinstance(filters, dict):
        filters = {}
    filters = {k: v for k, v in filters.items() if v.get("type") != "na"}
    new_id = str(uuid.uuid4())
    filters[new_id] = {"type": "na", "col": col_name, "action": action}
    active_table["filters"] = filters
    return active_table


@callback(
    Output("outlier_popup", "className"),
    Output("outlier_column_dropdown", "value"),
    Input("filter_outlier", "n_clicks"),
    Input("outlier_popup_close_button", "n_clicks"),
    Input("import-validate-button-outlier", "n_clicks"),
    State("outlier_popup", "className"),
    prevent_initial_call=True,
)
def toggle_outlier_popup(open_clicks, close_clicks, validate_clicks, current_class):
    if not ctx.triggered:
        return no_update, no_update

    triggered_id = ctx.triggered_id

    if triggered_id == "filter_outlier":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip(), no_update
        else:
            return (
                (current_class + " open").strip() if current_class else "open"
            ), no_update

    elif triggered_id in [
        "outlier_popup_close_button",
        "import-validate-button-outlier",
    ]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None

    return no_update, no_update


@callback(
    Output("outlier_column_dropdown", "options"),
    Input("active_table", "data"),
)
def update_outlier_column_dropdown(active_table_data):
    if not active_table_data or "id" not in active_table_data:
        return []

    file_id = active_table_data["id"]
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return []

    df = pickle.loads(pickled_df)
    quali_cols = df.select_dtypes(include=["number"]).columns.tolist()

    return [{"label": c, "value": c} for c in quali_cols]


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-outlier", "n_clicks"),
    State("active_table", "data"),
    State("outlier_column_dropdown", "value"),
    State("outlier_action_dropdown", "value"),
    prevent_initial_call=True,
)
def store_outlier_filter(n_clicks, active_table, col_name, action):
    if not n_clicks:
        return dash.no_update

    filters = active_table.get("filters", {})
    if not isinstance(filters, dict):
        filters = {}

    filters = {k: v for k, v in filters.items() if v.get("type") != "outlier"}

    new_id = str(uuid.uuid4())
    filters[new_id] = {
        "type": "outlier",
        "col": col_name,
        "action": action if action else "drop",
    }
    active_table["filters"] = filters
    return active_table


@callback(
    Output("sort_abc_popup", "className"),
    Output("sort_abc_column_dropdown", "value"),
    Input("sort_abc", "n_clicks"),
    Input("sort_abc_popup_close_button", "n_clicks"),
    Input("import-validate-button-sort-abc", "n_clicks"),
    State("sort_abc_popup", "className"),
    prevent_initial_call=True,
)
def toggle_sort_abc_popup(open_clicks, close_clicks, validate_clicks, current_class):
    if not ctx.triggered:
        return no_update, no_update

    triggered_id = ctx.triggered_id

    if triggered_id == "sort_abc":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip(), no_update
        else:
            return (
                (current_class + " open").strip() if current_class else "open"
            ), no_update

    elif triggered_id in [
        "sort_abc_popup_close_button",
        "import-validate-button-sort-abc",
    ]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None

    return no_update, no_update


@callback(
    Output("sort_abc_column_dropdown", "options"),
    Input("active_table", "data"),
)
def update_sort_abc_column_dropdown(active_table_data):
    if not active_table_data or "id" not in active_table_data:
        return []

    file_id = active_table_data["id"]
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return []

    df = pickle.loads(pickled_df)
    text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    return [{"label": c, "value": c} for c in text_cols]


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-sort-abc", "n_clicks"),
    State("active_table", "data"),
    State("sort_abc_column_dropdown", "value"),
    State("sort_abc_order_dropdown", "value"),
    prevent_initial_call=True,
)
def store_sort_abc(n_clicks, active_table, col_name, order):
    if not n_clicks or not active_table or not col_name or not order:
        return no_update

    sort_info = active_table.get("sort", [])
    if not isinstance(sort_info, list):
        sort_info = []

    sort_info = [s for s in sort_info if s.get("column_id") != col_name]

    sort_info.append({"column_id": col_name, "direction": order})

    active_table["sort"] = sort_info

    return active_table


@callback(
    Output("sort_123_popup", "className"),
    Output("sort_123_column_dropdown", "value"),
    Input("sort_123", "n_clicks"),
    Input("sort_123_popup_close_button", "n_clicks"),
    Input("import-validate-button-sort-123", "n_clicks"),
    State("sort_123_popup", "className"),
    prevent_initial_call=True,
)
def toggle_sort_123_popup(open_clicks, close_clicks, validate_clicks, current_class):
    if not ctx.triggered:
        return no_update, no_update

    triggered_id = ctx.triggered_id

    if triggered_id == "sort_123":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip(), no_update
        else:
            return (
                (current_class + " open").strip() if current_class else "open"
            ), no_update

    elif triggered_id in [
        "sort_123_popup_close_button",
        "import-validate-button-sort-123",
    ]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class, None

    return no_update, no_update


@callback(
    Output("sort_123_column_dropdown", "options"),
    Input("active_table", "data"),
)
def update_sort_123_column_dropdown(active_table_data):
    if not active_table_data or "id" not in active_table_data:
        return []

    file_id = active_table_data["id"]
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return []

    try:
        df = pickle.loads(pickled_df)
        num_bool_cols = [
            col
            for col in df.columns
            if pd.api.types.is_numeric_dtype(df[col])
            or pd.api.types.is_bool_dtype(df[col])
        ]
        return [{"label": c, "value": c} for c in num_bool_cols]
    except Exception:
        return []


@callback(
    Output("active_table", "data", allow_duplicate=True),
    Input("import-validate-button-sort-123", "n_clicks"),
    State("active_table", "data"),
    State("sort_123_column_dropdown", "value"),
    State("sort_123_order_dropdown", "value"),
    prevent_initial_call=True,
)
def store_sort_abc(n_clicks, active_table, col_name, order):
    if not n_clicks or not active_table or not col_name or not order:
        return no_update

    sort_info = active_table.get("sort", [])
    if not isinstance(sort_info, list):
        sort_info = []

    sort_info = [s for s in sort_info if s.get("column_id") != col_name]

    sort_info.append({"type": "abc", "column_id": col_name, "direction": order})

    active_table["sort"] = sort_info

    return active_table


@callback(
    Output("concatenate_popup", "className"),
    Input("fusion_concat", "n_clicks"),
    Input("concatenate_popup_close_button", "n_clicks"),
    State("concatenate_popup", "className"),
    prevent_initial_call=True,
)
def toggle_concatenate_popup(open_clicks, close_clicks, current_class):
    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered_id

    if triggered_id == "fusion_concat":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip()
        else:
            return (current_class + " open").strip() if current_class else "open"

    elif triggered_id in ["concatenate_popup_close_button"]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class

    return no_update


@callback(
    Output("concatenate_data_dropdown", "options"),
    Output("concatenate_data_dropdown", "value"),
    Input("fusion_concat", "n_clicks"),
    Input("stored-data", "data"),
    State("active_table", "data"),
    State("concatenate_data_dropdown", "value"),
    prevent_initial_call=True,
)
def update_concatenate_data_dropdown(
    fusion_clicks, stored_data, active_table, current_value
):
    if not stored_data or "files" not in stored_data:
        return [], None

    if active_table and "id" in active_table:
        options = [
            {"label": f["name"], "value": f["id"]}
            for f in stored_data["files"]
            if f["id"] != active_table["id"]
        ]
    else:
        options = [{"label": f["name"], "value": f["id"]} for f in stored_data["files"]]

    triggered_id = ctx.triggered_id

    if triggered_id == "fusion_concat":
        return options, None
    elif triggered_id == "stored-data":

        return options, current_value
    else:
        return options, current_value


@callback(
    Output("stored-data", "data", allow_duplicate=True),
    Output("datastorage", "children", allow_duplicate=True),
    Output("concatenate_feedback", "children"),
    Output("concatenate_popup", "className", allow_duplicate=True),
    Input("import-validate-button-concatenate", "n_clicks"),
    State("concatenate_data_dropdown", "value"),
    State("concatenate_axis_dropdown", "value"),
    State("stored-data", "data"),
    State("active_table", "data"),
    State("concatenate_popup", "className"),
    prevent_initial_call=True,
)
def concat_add_file(
    n_clicks, selected_id, axis, stored_data, active_table, popup_class
):
    if not n_clicks or not selected_id or axis is None:
        raise no_update

    try:
        id_main = active_table["id"]
        df_main = pickle.loads(cache.get(id_main))
        df_other = pickle.loads(cache.get(selected_id))

        df_concat = concat_dataframes(df_main, df_other, axis)

        new_id = str(uuid.uuid4())
        new_name = f"concat_{id_main[:4]}_{selected_id[:4]}"
        cache.set(new_id, pickle.dumps(df_concat))

        new_file = {"id": new_id, "name": new_name}
        new_stored_data = {"files": stored_data["files"] + [new_file]}

        file_buttons = [
            html.Div(
                [
                    html.Button(
                        f["name"],
                        className="data_added",
                        id={"type": "data_added", "index": f["id"]},
                    ),
                    html.Button(
                        html.I(className="fa-solid fa-xmark"),
                        className="data_remove",
                        id={"type": "data_remove", "index": f["id"]},
                    ),
                ],
                className="data-row",
            )
            for f in new_stored_data["files"]
        ]

        popup_class = popup_class.replace("open", "").strip()
        return new_stored_data, html.Div(file_buttons), "", popup_class

    except Exception as e:
        return no_update, no_update, str(e), popup_class


@callback(
    Output("merge_popup", "className"),
    Input("fusion_merge", "n_clicks"),
    Input("merge_popup_close_button", "n_clicks"),
    State("merge_popup", "className"),
    prevent_initial_call=True,
)
def toggle_merge_popup(open_clicks, close_clicks, current_class):
    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered_id

    if triggered_id == "fusion_merge":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip()
        else:
            return (current_class + " open").strip() if current_class else "open"

    elif triggered_id in ["merge_popup_close_button"]:
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class

    return no_update


@callback(
    Output("merge_data_dropdown", "options"),
    Output("merge_data_dropdown", "value"),
    Input("fusion_merge", "n_clicks"),
    Input("import-validate-button-merge", "n_clicks"),
    Input("stored-data", "data"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def update_merge_data_dropdown(
    fusion_clicks, validate_clicks, stored_data, active_table
):
    if (
        not stored_data
        or "files" not in stored_data
        or not active_table
        or "id" not in active_table
    ):
        return [], None

    files = stored_data["files"]
    active_id = active_table["id"]

    options = [
        {"label": f["name"], "value": f["id"]} for f in files if f["id"] != active_id
    ]

    triggered_id = ctx.triggered_id

    if triggered_id == "import-validate-button-merge":
        return options, None
    else:
        return options, dash.no_update


@callback(
    Output("merge_column_left", "options"),
    Output("merge_column_left", "value"),
    Input("merge_data_dropdown", "value"),
    Input("import-validate-button-merge", "n_clicks"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def update_merge_column_left(selected_file_id, validate_clicks, active_table):
    if not active_table or "id" not in active_table:
        return [], None

    active_id = active_table["id"]
    df = pickle.loads(cache.get(active_id))
    cols = [{"label": col, "value": col} for col in df.columns]

    triggered_id = ctx.triggered_id
    if triggered_id == "import-validate-button-merge":
        return cols, None
    return cols, dash.no_update


@callback(
    Output("merge_column_right", "options"),
    Output("merge_column_right", "value"),
    Input("merge_data_dropdown", "value"),
    Input("import-validate-button-merge", "n_clicks"),
    prevent_initial_call=True,
)
def update_merge_column_right(selected_file_id, validate_clicks):
    if not selected_file_id:
        return [], None

    df = pickle.loads(cache.get(selected_file_id))
    cols = [{"label": col, "value": col} for col in df.columns]

    triggered_id = ctx.triggered_id
    if triggered_id == "import-validate-button-merge":
        return cols, None
    return cols, dash.no_update


@callback(
    Output("stored-data", "data", allow_duplicate=True),
    Output("datastorage", "children", allow_duplicate=True),
    Output("merge_feedback", "children"),
    Output("merge_popup", "className", allow_duplicate=True),
    Input("import-validate-button-merge", "n_clicks"),
    State("merge_data_dropdown", "value"),
    State("merge_column_left", "value"),
    State("merge_column_right", "value"),
    State("merge_how_dropdown", "value"),
    State("active_table", "data"),
    State("stored-data", "data"),
    State("merge_popup", "className"),
    prevent_initial_call=True,
)
def merge_add_file(
    n_clicks,
    selected_file_id,
    left_key,
    right_key,
    how,
    active_table,
    stored_data,
    popup_class,
):
    if (
        not n_clicks
        or not selected_file_id
        or not left_key
        or not right_key
        or not how
        or not active_table
        or not stored_data
    ):
        return (
            no_update,
            no_update,
            "Erreur : Tous les champs doivent être remplis.",
            popup_class,
        )

    try:
        active_id = active_table["id"]

        df_main = pickle.loads(cache.get(active_id))
        df_other = pickle.loads(cache.get(selected_file_id))

        df_merged = merge_dataframes(df_main, df_other, left_key, right_key, how)

        new_id = str(uuid.uuid4())
        new_name = f"merged_{active_id[:4]}_{selected_file_id[:4]}"
        new_file = {"id": new_id, "name": new_name}

        cache.set(new_id, pickle.dumps(df_merged))

        new_stored_data = {
            "files": stored_data["files"] + [new_file],
        }

        file_buttons = [
            html.Div(
                [
                    html.Button(
                        f["name"],
                        className="data_added",
                        id={"type": "data_added", "index": f["id"]},
                    ),
                    html.Button(
                        html.I(className="fa-solid fa-xmark"),
                        className="data_remove",
                        id={"type": "data_remove", "index": f["id"]},
                    ),
                ],
                className="data-row",
            )
            for f in new_stored_data["files"]
        ]

        popup_class = popup_class.replace("open", "").strip()

        return new_stored_data, html.Div(file_buttons), "", popup_class

    except Exception as e:
        return no_update, no_update, f"{str(e)}", popup_class


@callback(
    Output("export_popup", "className"),
    Input("exportbutton", "n_clicks"),
    Input("export_popup_close_button", "n_clicks"),
    State("export_popup", "className"),
    prevent_initial_call=True,
)
def toggle_export_popup(open_clicks, close_clicks, current_class):
    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered_id

    if triggered_id == "exportbutton":
        if current_class and "open" in current_class:
            return current_class.replace("open", "").strip()
        else:
            return (current_class + " open").strip() if current_class else "open"

    elif triggered_id == "export_popup_close_button":
        new_class = (
            current_class.replace("open", "").strip()
            if current_class and "open" in current_class
            else (current_class or "")
        )
        return new_class

    return no_update


@callback(
    Output("export", "data"),
    Input("import-validate-button-export", "n_clicks"),
    State("active_table", "data"),
    State("export_format_dropdown", "value"),
    prevent_initial_call=True,
)
def export_file(n, store_data, file_format):
    if not store_data or "id" not in store_data or not file_format:
        return dash.no_update

    data_id = store_data["id"]
    df = pickle.loads(cache.get(data_id))
    filename = f"export_{data_id}"

    if file_format == "csv":
        return dcc.send_data_frame(df.to_csv, f"{filename}.csv", index=False)
    elif file_format == "excel":
        return dcc.send_data_frame(df.to_excel, f"{filename}.xlsx", index=False)

    return dash.no_update


@callback(
    Output("valuebox_quantitative_count", "children"),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_valuebox_quantitative_count(active_table):
    if not active_table or "id" not in active_table:
        return "0"
    file_id = active_table["id"]

    pickled_df = cache.get(file_id)
    if not pickled_df:
        return "0"

    df = pickle.loads(pickled_df)

    filters = active_table.get("filters", {})

    df_filtered = apply_filters(df, filters)

    count = count_quantitative(df_filtered)

    return str(count)


@callback(
    Output("valuebox_qualitative_count", "children"),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_valuebox_qualitative_count(active_table):
    if not active_table or "id" not in active_table:
        return "0"
    file_id = active_table["id"]

    pickled_df = cache.get(file_id)
    if not pickled_df:
        return "0"

    df = pickle.loads(pickled_df)

    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    count = count_qualitative(df_filtered)
    return str(count)


@callback(
    Output("valuebox_nrow_data_count", "children"),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_nrow(active_table):
    if not active_table or "id" not in active_table:
        return "0"
    file_id = active_table["id"]

    pickled_df = cache.get(file_id)
    if not pickled_df:
        return "0"

    df = pickle.loads(pickled_df)

    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    return str(len(df_filtered))


@callback(
    Output("valuebox_missing_count", "children"),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_missing_count(active_table):
    if not active_table or "id" not in active_table:
        return "0"
    file_id = active_table["id"]

    pickled_df = cache.get(file_id)
    if not pickled_df:
        return "0"

    df = pickle.loads(pickled_df)

    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    return str(nas(df_filtered))


@callback(
    Output("dropdown_quanti", "options"),
    Output("dropdown_quali", "options"),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_dropdowns(active_table):
    if not active_table or "id" not in active_table:
        return [], []

    file_id = active_table["id"]
    pickled_df = cache.get(file_id)
    if not pickled_df:
        return [], []

    df = pickle.loads(pickled_df)

    filters = active_table.get("filters", {})

    df_filtered = apply_filters(df, filters)

    quanti_columns = df_filtered.select_dtypes(include=["number"]).columns.tolist()
    quali_columns = df_filtered.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    quanti_options = [{"label": col, "value": col} for col in quanti_columns]
    quali_options = [{"label": col, "value": col} for col in quali_columns]

    return quanti_options, quali_options


@callback(
    Output("quantitative_table_graph", "children"),
    Input("btn_table_quanti", "n_clicks"),
    Input("active_table", "data"),
    State("dropdown_quanti", "value"),
    prevent_initial_call=True,
)
def update_quantitative_tables(n_clicks, active_table, selected_col):
    if not n_clicks or not active_table or "id" not in active_table or not selected_col:
        return html.Div()

    file_id = active_table["id"]
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return html.Div("fichier introuvable.")

    df = pickle.loads(pickled_df)

    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    if selected_col not in df_filtered.columns:
        return html.Div(
            f"Colonne '{selected_col}' introuvable dans les données filtrées."
        )

    desc = df_filtered[selected_col].describe().to_frame().T.reset_index(drop=True)
    desc.insert(0, "Colonne", selected_col)
    desc["NA"] = df_filtered[selected_col].isna().sum()

    desc.rename(
        columns={
            "count": "Nombre",
            "mean": "Moyenne",
            "std": "Écart-type",
            "min": "Min",
            "25%": "1er quartile (Q1)",
            "50%": "Médiane (Q2)",
            "75%": "3e quartile (Q3)",
            "max": "Max",
        },
        inplace=True,
    )

    for col in desc.columns[1:]:
        if pd.api.types.is_numeric_dtype(desc[col]):
            desc[col] = desc[col].round(3)

    desc_table = dash_table.DataTable(
        data=desc.to_dict("records"),
        columns=[{"name": c, "id": c} for c in desc.columns],
        page_size=1,
        style_table={
            "overflowX": "auto",
            "marginTop": "1.5vh",
            "borderRadius": "8px",
            "boxShadow": "0 3px 8px rgba(0, 0, 0, 0.3)",
            "border": "1px solid #374151",
            "backgroundColor": "#111827",
            "tableLayout": "fixed",
            "wordBreak": "break-word",
        },
        style_header={
            "backgroundColor": "#1f2937",
            "color": "#e0e0e0",
            "fontWeight": "bold",
            "fontSize": "14px",
            "borderBottom": "2px solid #374151",
            "textAlign": "center",
            "position": "sticky",
            "top": 0,
            "zIndex": 1000,
            "minWidth": "120px",
            "boxShadow": "inset 0 -1px 0 #374151",
            "whiteSpace": "normal",
        },
        style_cell={
            "color": "#d1d5db",
            "padding": "6px",
            "textAlign": "center",
            "fontFamily": "Segoe UI, sans-serif",
            "fontSize": "13px",
            "backgroundColor": "transparent",
            "whiteSpace": "normal",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "minWidth": "90px",
            "borderBottom": "1px solid #374151",
        },
        id="describe_table",
    )

    corr = correlation_tab(df_filtered)

    corr_table = dash_table.DataTable(
        data=corr.to_dict("records"),
        columns=[{"name": c, "id": c} for c in corr.columns],
        page_size=10,
        style_table={
            "overflowX": "auto",
            "marginTop": "25px",
            "borderRadius": "8px",
            "boxShadow": "0 3px 8px rgba(0, 0, 0, 0.3)",
            "border": "1px solid #374151",
            "backgroundColor": "#111827",
            "tableLayout": "fixed",
            "wordBreak": "break-word",
            "maxHeight": "20vh",
        },
        style_header={
            "backgroundColor": "#1f2937",
            "color": "#e0e0e0",
            "fontWeight": "bold",
            "fontSize": "14px",
            "borderBottom": "2px solid #374151",
            "textAlign": "center",
            "position": "sticky",
            "top": 0,
            "zIndex": 1000,
            "minWidth": "120px",
            "boxShadow": "inset 0 -1px 0 #374151",
            "whiteSpace": "normal",
        },
        style_cell={
            "color": "#d1d5db",
            "padding": "6px",
            "textAlign": "center",
            "fontFamily": "Segoe UI, sans-serif",
            "fontSize": "13px",
            "backgroundColor": "transparent",
            "whiteSpace": "normal",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "minWidth": "90px",
            "borderBottom": "1px solid #374151",
        },
        id="corr_table",
    )

    return html.Div(
        [
            html.H3(
                "Statistiques descriptives",
                style={"color": "#e0e0e0", "marginBottom": "10px"},
            ),
            desc_table,
            html.H3(
                "Matrice de corrélation",
                style={"color": "#e0e0e0", "marginTop": "30px", "marginBottom": "10px"},
            ),
            corr_table,
        ],
        id="tables_container",
    )


@callback(
    Output("qualitative_table_graph", "children"),
    Input("btn_table_quali", "n_clicks"),
    Input("active_table", "data"),
    State("dropdown_quali", "value"),
    prevent_initial_call=True,
)
def update_qualitative_tables(n_clicks, active_table, selected_col):
    if not n_clicks or not active_table or "id" not in active_table or not selected_col:
        return html.Div()

    file_id = active_table["id"]
    pickled_df = cache.get(file_id)
    if not pickled_df:
        return html.Div("fichier introuvable.", style={"color": "red"})

    df = pickle.loads(pickled_df)

    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    if selected_col not in df_filtered.columns:
        return html.Div(f"Colonne {selected_col} non trouvée", style={"color": "red"})

    series = df_filtered[selected_col].fillna("NA").replace("", "NA")

    freq_table = (
        series.value_counts(dropna=False)
        .rename_axis("Modalité")
        .reset_index(name="Nombre")
    )
    freq_table["Pourcentage"] = (
        freq_table["Nombre"] / freq_table["Nombre"].sum() * 100
    ).round(2)

    table = dash_table.DataTable(
        data=freq_table.to_dict("records"),
        columns=[{"name": col, "id": col} for col in freq_table.columns],
        page_size=10,
        style_table={
            "marginTop": "1.5vh",
            "borderRadius": "8px",
            "boxShadow": "0 3px 8px rgba(0, 0, 0, 0.3)",
            "border": "1px solid #374151",
            "backgroundColor": "#111827",
            "tableLayout": "fixed",
            "wordBreak": "break-word",
            "Height": "20vh",
            "z-index": 0,
        },
        style_header={
            "backgroundColor": "#1f2937",
            "color": "#e0e0e0",
            "fontWeight": "bold",
            "fontSize": "14px",
            "borderBottom": "2px solid #374151",
            "textAlign": "center",
            "position": "sticky",
            "top": 0,
            "zIndex": 1000,
            "minWidth": "120px",
            "boxShadow": "inset 0 -1px 0 #374151",
            "whiteSpace": "normal",
        },
        style_cell={
            "color": "#d1d5db",
            "padding": "6px",
            "textAlign": "center",
            "fontFamily": "Segoe UI, sans-serif",
            "fontSize": "13px",
            "backgroundColor": "transparent",
            "whiteSpace": "normal",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
            "minWidth": "90px",
            "borderBottom": "1px solid #374151",
        },
        id="freq_table",
    )

    return html.Div(
        [
            html.H3(
                "Tableau des fréquences",
                style={"color": "#e0e0e0", "marginBottom": "10px"},
            ),
            table,
        ],
        id="qualitative_table_container",
    )


@callback(
    Output("quantitative_table_graph", "children", allow_duplicate=True),
    Input("btn_graph_quanti", "n_clicks"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def show_quanti_graph_dropdown_section(n_clicks, active_table):
    if not active_table or not isinstance(active_table, dict):
        return html.Div("Aucune table active")

    return html.Div(
        [
            dcc.Dropdown(
                id="dropdown_quanti_graph_type",
                options=[
                    {"label": "Histogramme", "value": "hist"},
                    {"label": "Boxplot", "value": "box"},
                    {"label": "Violin plot", "value": "violin"},
                ],
                placeholder="Sélectionnez un type de graphique",
                style={
                    "backgroundColor": "#2A2D3A",
                    "border": "1px solid #2A2D3A",
                    "color": "#000000",
                    "width": "200px",
                },
            ),
            html.Div(id="quanti_graph_container"),
        ]
    )


@callback(
    Output("quanti_graph_container", "children"),
    Input("dropdown_quanti_graph_type", "value"),
    State("dropdown_quanti", "value"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def update_quanti_graph(graph_type, selected_col, active_table):
    if (
        not active_table
        or not isinstance(active_table, dict)
        or "id" not in active_table
    ):
        return html.Div("Aucune table active", style={"color": "red"})

    file_id = active_table["id"]
    pickled_df = cache.get(file_id)
    if not pickled_df:
        return html.Div("fichier introuvable.", style={"color": "red"})

    df = pickle.loads(pickled_df)
    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    if selected_col not in df_filtered.columns:
        return html.Div(f"Colonne '{selected_col}' non trouvée", style={"color": "red"})

    if graph_type == "hist":
        fig = histogram(df_filtered, selected_col)
    elif graph_type == "box":
        fig = boxplot(df_filtered, selected_col)
    elif graph_type == "violin":
        fig = violin(df_filtered, selected_col)
    else:
        return html.Div("Type de graphique non supporté", style={"color": "red"})

    fig.update_layout(
        plot_bgcolor="#1F2430",
        paper_bgcolor="#1F2430",
        font_color="#FFFFFF",
        xaxis=dict(color="#FFFFFF"),
        yaxis=dict(color="#FFFFFF"),
    )

    return dcc.Graph(figure=fig)


@callback(
    Output("qualitative_table_graph", "children", allow_duplicate=True),
    Input("btn_graph_quali", "n_clicks"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def show_quali_graph_dropdown_section(n_clicks, active_table):
    if not active_table or not isinstance(active_table, dict):
        return html.Div("Aucune table active")

    return html.Div(
        [
            dcc.Dropdown(
                id="dropdown_quali_graph_type",
                options=[
                    {"label": "Camembert", "value": "pie"},
                    {"label": "Bar chart", "value": "bar"},
                ],
                placeholder="Sélectionnez un type de graphique",
                style={
                    "backgroundColor": "#2A2D3A",
                    "border": "1px solid #2A2D3A",
                    "color": "#000000",
                    "width": "200px",
                },
            ),
            html.Div(id="quali_graph_container"),
        ]
    )


@callback(
    Output("quali_graph_container", "children"),
    Input("dropdown_quali_graph_type", "value"),
    State("dropdown_quali", "value"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def update_quali_graph(graph_type, selected_col, active_table):
    if (
        not active_table
        or not isinstance(active_table, dict)
        or "id" not in active_table
    ):
        return html.Div("Aucune table active", style={"color": "red"})

    file_id = active_table["id"]
    pickled_df = cache.get(file_id)
    if not pickled_df:
        return html.Div("fichier introuvable.", style={"color": "red"})

    df = pickle.loads(pickled_df)
    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    if selected_col not in df_filtered.columns:
        return html.Div(f"Colonne '{selected_col}' non trouvée", style={"color": "red"})

    if graph_type == "pie":
        fig = pie_chart(df_filtered, selected_col)
    elif graph_type == "bar":
        fig = bar_chart(df_filtered, selected_col)
    else:
        return html.Div("Type de graphique non supporté", style={"color": "red"})

    return dcc.Graph(figure=fig)


@callback(
    Output("advanced_graphs", "className"),
    Output("advanced_graphs_button", "children"),
    Input("advanced_graphs_button", "n_clicks"),
    State("advanced_graphs", "className"),
    prevent_initial_call=True,
)
def toggle_advanced_graphs_button(n_clicks, current_class):
    if current_class and "open" in current_class:
        new_class = current_class.replace("open", "").strip()
        new_children = "Graphiques avancés"
    else:
        new_class = (current_class + " open").strip() if current_class else "open"
        new_children = html.I(className="fas fa-arrow-down")

    return new_class, new_children


@callback(
    Output("col_x_dropdown", "options"),
    Output("col_y_dropdown", "options"),
    Input("active_table", "data"),
    prevent_initial_call=True,
)
def update_graph_dropdowns(active_table):
    if (
        not active_table
        or not isinstance(active_table, dict)
        or "id" not in active_table
    ):
        return [], []

    file_id = active_table["id"]
    pickled_df = cache.get(file_id)
    if not pickled_df:
        return [], []

    df = pickle.loads(pickled_df)
    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    col_options = [
        {"label": col, "value": col} for col in df_filtered.columns if col != "index"
    ]

    return col_options, col_options


@callback(
    Output("graph_container", "children"),
    Input("col_x_dropdown", "value"),
    Input("col_y_dropdown", "value"),
    Input("graph_type_dropdown", "value"),
    State("active_table", "data"),
    prevent_initial_call=True,
)
def update_advanced_graph(col_x, col_y, graph_type, active_table):
    if (
        col_x is None
        or col_y is None
        or graph_type is None
        or not active_table
        or "id" not in active_table
    ):
        return html.Div(
            "Choisis les colonnes X, Y et le type de graphique.",
            style={"color": "white"},
        )

    file_id = active_table["id"]
    pickled_df = cache.get(file_id)
    if not pickled_df:
        return html.Div("fichier introuvable.", style={"color": "red"})

    df = pickle.loads(pickled_df)
    filters = active_table.get("filters", {})
    df_filtered = apply_filters(df, filters)

    if col_x not in df_filtered.columns or col_y not in df_filtered.columns:
        return html.Div(
            "Colonne X ou Y non trouvée dans les données filtrées.",
            style={"color": "red"},
        )

    try:
        if graph_type == "scatter":
            fig = scatter_2col(df_filtered, col_x, col_y)
        elif graph_type == "line":
            fig = regression_2col(df_filtered, col_x, col_y)
        elif graph_type == "box":
            fig = box_2col(df_filtered, col_x, col_y)
        elif graph_type == "violin":
            fig = violin_2col(df_filtered, col_x, col_y)
        else:
            return html.Div("Type de graphique non supporté.", style={"color": "red"})
    except Exception as e:
        if graph_type == "line":
            fig = scatter_2col(df_filtered, col_x, col_y)
        else:
            return html.Div(
                f"Erreur lors de la création du graphique: {str(e)}",
                style={"color": "red"},
            )

    return dcc.Graph(figure=fig, style={"height": "70vh", "width": "80vw"})
