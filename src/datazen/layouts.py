from dash import html, dcc

external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
]

menudata = html.Div(
    children=[
        html.Div(
            [
                "Datazen",
                html.Button(
                    html.I(className="fa-solid fa-arrow-left"), id="sidebar_button"
                ),
            ],
            id="left_menu_header",
        ),
        html.Div([], id="datastorage"),
        html.Div(
            children=[
                html.I(className="fa-solid fa-arrow-up-from-bracket"),
                " Importer un fichier",
            ],
            id="importbutton",
        ),
        dcc.Store(id="stored-data"),
    ],
    id="menudata",
)


importpopup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"), id="importpopup_close_button"
        ),
        dcc.Upload(
            id="import-data",
            children=html.Button("Sélectionner un fichier", id="importbutton_popup"),
            multiple=False,
        ),
        html.Div(children=[], id="import-error-feedback"),
        dcc.Interval(
            id="import-error-interval", interval=5000, n_intervals=0, disabled=True
        ),
        html.Div(
            children=[
                html.Div(children=[], id="title_importpopup"),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Label("Séparateur :"),
                                dcc.Dropdown(
                                    id="import-separator",
                                    options=[
                                        {"label": "Virgule (,)", "value": ","},
                                        {"label": "Point-virgule (;)", "value": ";"},
                                        {"label": "Tabulation (\\t)", "value": "\t"},
                                    ],
                                    value=",",
                                    clearable=False,
                                ),
                                html.Label("Caractère décimal :"),
                                dcc.Dropdown(
                                    id="import-decimal",
                                    options=[
                                        {"label": "Point (.)", "value": "."},
                                        {"label": "Virgule (,)", "value": ","},
                                    ],
                                    value=".",
                                    clearable=False,
                                ),
                            ],
                            className="import-column",
                        ),
                        html.Div(
                            children=[
                                html.Label("Ligne d’en-tête (index) :"),
                                dcc.Input(
                                    id="import-header",
                                    type="number",
                                    value=0,
                                    min=-1,
                                    step=1,
                                ),
                            ],
                            className="import-column",
                        ),
                    ],
                    className="import-options-container",
                ),
                html.Button(
                    "Importer",
                    className="import-validate-button",
                    id="import-validate-button-csv",
                ),
                html.Div(id="import-feedback-csv"),
            ],
            id="importpopup_content_csv",
        ),
        html.Div(
            children=[
                html.Div(children=[], id="title_importpopup-excel"),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Label("Nom ou index de la feuille :"),
                                dcc.Input(
                                    id="import-sheetname",
                                    type="text",
                                    placeholder='ex : "Feuille1" ou 0',
                                    value="0",
                                ),
                                html.Label("Caractère décimal :"),
                                dcc.Dropdown(
                                    id="import-decimal-excel",
                                    options=[
                                        {"label": "Point (.)", "value": "."},
                                        {"label": "Virgule (,)", "value": ","},
                                    ],
                                    value=".",
                                    clearable=False,
                                ),
                            ],
                            className="import-column",
                        ),
                        html.Div(
                            children=[
                                html.Label("Ligne d’en-tête (index) :"),
                                dcc.Input(
                                    id="import-header-excel",
                                    type="number",
                                    value=0,
                                    min=-1,
                                    step=1,
                                ),
                            ],
                            className="import-column",
                        ),
                    ],
                    className="import-options-container",
                ),
                html.Button(
                    "Importer",
                    className="import-validate-button",
                    id="import-validate-button-excel",
                ),
                html.Div(id="import-feedback-excel"),
            ],
            id="importpopup_content_excel",
        ),
    ],
    id="importpopup",
)


table_container = html.Div(
    children=[
        html.Div(
            id="filter_sort_history",
            children=[
                html.Button(
                    html.I(className="fa-solid fa-arrow-down"),
                    id="filter_sort_history_button",
                ),
                html.Div("Historique", id="filter_sort_history_title"),
                html.Div(
                    id="filter_sort_history_content",
                    children=[
                        html.Div(
                            children=[
                                html.H1("Filtres actifs"),
                                html.Ul(id="filter_list"),
                            ],
                            id="filter_list_container",
                        ),
                        html.Div(
                            children=[
                                html.H1("Tri actif"),
                                html.Ul(id="sort_list"),
                            ],
                            id="sort_list_container",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            children=[],
            id="table_container",
        ),
        dcc.Store(id="active_table"),
        dcc.Store(id="savebutton-last-click", data=None),
        dcc.Interval(id="reset-interval", interval=2000, n_intervals=0, disabled=True),
        html.Div(
            children=[html.I(className="fa-solid fa-floppy-disk")], id="savebutton"
        ),
        html.Div(
            children=[
                html.I(className="fa-solid fa-filter"),
                html.Span("Filtres", id="filter-title"),
                html.Div(
                    className="filter-menu",
                    children=[
                        html.Button("Recherche exacte", id="filter_text"),
                        html.Button("Recherche (in)", id="filter_in_text"),
                        html.Button("Comparaison", id="filter_comparaison"),
                        html.Button("Types colonnes", id="filter_types_columns"),
                        html.Button("Colonnes gardées", id="filter_keep_columns"),
                        html.Button("Valeurs manquantes", id="filter_NA"),
                        html.Button("Valeur aberrante", id="filter_outlier"),
                    ],
                ),
            ],
            id="filter_button",
        ),
        html.Div(
            children=[
                html.I(className="fa-solid fa-sort"),
                html.Span("Tri", id="tri-title"),
                html.Div(
                    children=[
                        html.Button("Tri alphabétique", id="sort_abc"),
                        html.Button("Tri numérique", id="sort_123"),
                    ]
                ),
            ],
            id="tri_button",
        ),
        html.Div(
            children=[
                html.I(className="fa-solid fa-layer-group"),
                html.Span("Fusion", id="fusion-title"),
                html.Div(
                    children=[
                        html.Button("Concaténer", id="fusion_concat"),
                        html.Button("Merge", id="fusion_merge"),
                    ]
                ),
            ],
            id="df_fusion_button",
        ),
        html.Div(
            children=[html.I(className="fa-solid fa-file-export")], id="exportbutton"
        ),
        html.Button(
            html.I(className="fa-solid fa-arrow-left"), id="rezize_table_button"
        ),
    ],
    id="table_container_wrapper",
)

text_filter_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="text_filter_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Filtre texte (recherche exacte)", id="text_filter_popup_title"),
        dcc.Dropdown(
            id="text_filter_column_dropdown",
            placeholder="Choisir une colonne...",
            style={
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "backgroundColor": "#2A2D3A",
            },
        ),
        dcc.Input(
            id="text_filter_input",
            type="text",
            placeholder="Texte à rechercher...",
            debounce=True,
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-text-filter",
        ),
    ],
    id="text_filter_popup",
)

in_text_filter_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="in_text_filter_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Filtre de texte (in)", id="in_text_filter_popup_title"),
        dcc.Dropdown(
            id="in_text_filter_column_dropdown",
            placeholder="Choisir une colonne...",
            style={
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "backgroundColor": "#2A2D3A",
            },
        ),
        dcc.Input(
            id="in_text_filter_input",
            type="text",
            placeholder="Texte à rechercher...",
            debounce=True,
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-in-text-filter",
        ),
    ],
    id="in_text_filter_popup",
)

comparaison_filter_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="comparaison_filter_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Filtre de comparaison", id="comparaison_filter_popup_title"),
        dcc.Dropdown(
            id="comparaison_filter_column_dropdown",
            placeholder="Choisir une colonne...",
            style={
                "border": "1px solid #2A2D3A",
                "color": "#2B2B2B",
                "backgroundColor": "#2A2D3A",
            },
        ),
        dcc.Input(
            id="comparaison_filter_value_input",
            type="number",
            placeholder="Valeur numérique...",
            debounce=True,
        ),
        dcc.Dropdown(
            id="comparaison_filter_operator_dropdown",
            options=[
                {"label": ">", "value": "plus grand que"},
                {"label": "≥", "value": "plus grand ou égal à"},
                {"label": "<", "value": "plus petit que"},
                {"label": "≤", "value": "plus petit ou égal à"},
                {"label": "=", "value": "égal à"},
                {"label": "≠", "value": "différent de"},
            ],
            placeholder="Choisir un opérateur...",
            style={
                "border": "1px solid #2A2D3A",
                "color": "#444444",
                "backgroundColor": "#2A2D3A",
                "marginTop": "10px",
                "width": "200px",
            },
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-comparaison-filter",
        ),
    ],
    id="comparaison_filter_popup",
)


types_columns_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="types_columns_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Types de colonnes", id="types_columns_popup_title"),
        dcc.Dropdown(
            id="types_columns_dropdown",
            options=[
                {"label": "Quanti", "value": "numeric"},
                {"label": "Quali", "value": "text"},
                {"label": "Booléen", "value": "boolean"},
            ],
            placeholder="Choisir un type...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-types-columns",
        ),
    ],
    id="types_columns_popup",
)


keep_columns_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="keep_columns_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Colonnes à garder", id="keep_columns_popup_title"),
        dcc.Dropdown(
            id="keep_columns_dropdown",
            placeholder="Choisir des colonnes...",
            multi=True,
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-keep-columns",
        ),
    ],
    id="keep_columns_popup",
)

Na_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="Na_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Valeurs manquantes", id="Na_popup_title"),
        dcc.Dropdown(
            id="Na_column_dropdown",
            placeholder="Choisir une colonne...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        dcc.Dropdown(
            id="Na_action_dropdown",
            options=[
                {"label": "Supprimer les lignes", "value": "drop"},
                {"label": "Remplacer par la moyenne", "value": "mean"},
                {"label": "Remplacer par la médiane", "value": "median"},
                {"label": "Remplacer par 0", "value": "zero"},
            ],
            placeholder="Choisir une action...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-Na",
        ),
    ],
    id="Na_popup",
)

outlier_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="outlier_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Valeurs aberrantes", id="outlier_popup_title"),
        dcc.Dropdown(
            id="outlier_column_dropdown",
            placeholder="Choisir une colonne...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        dcc.Dropdown(
            id="outlier_action_dropdown",
            options=[
                {"label": "Supprimer les lignes", "value": "drop"},
                {"label": "Remplacer par la médiane", "value": "median"},
                {"label": "Winsoriser (clipping)", "value": "winsorize"},
            ],
            placeholder="Choisir une action...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-outlier",
        ),
    ],
    id="outlier_popup",
)


sort_abc_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="sort_abc_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Tri alphabétique", id="sort_abc_popup_title"),
        dcc.Dropdown(
            id="sort_abc_column_dropdown",
            placeholder="Choisir une colonne...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        dcc.Dropdown(
            id="sort_abc_order_dropdown",
            options=[
                {"label": "Ordre croissant", "value": "asc"},
                {"label": "Ordre décroissant", "value": "desc"},
            ],
            placeholder="Choisir un ordre...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-sort-abc",
        ),
    ],
    id="sort_abc_popup",
)


sort_123_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="sort_123_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Tri numérique", id="sort_123_popup_title"),
        dcc.Dropdown(
            id="sort_123_column_dropdown",
            placeholder="Choisir une colonne...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        dcc.Dropdown(
            id="sort_123_order_dropdown",
            options=[
                {"label": "Ordre croissant", "value": "asc"},
                {"label": "Ordre décroissant", "value": "desc"},
            ],
            placeholder="Choisir un ordre...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-sort-123",
        ),
    ],
    id="sort_123_popup",
)


concatenate_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="concatenate_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Concaténer des dataframe", id="concatenate_popup_title"),
        dcc.Dropdown(
            id="concatenate_data_dropdown",
            placeholder="Choisir un dataframe...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        dcc.Dropdown(
            id="concatenate_axis_dropdown",
            options=[
                {"label": "Lignes", "value": 0},
                {"label": "Colonnes", "value": 1},
            ],
            placeholder="Choisir un axe...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Div(children=[], className="feedback-popup", id="concatenate_feedback"),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-concatenate",
        ),
    ],
    id="concatenate_popup",
)

merge_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="merge_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Fusionner des DataFrames", id="merge_popup_title"),
        dcc.Dropdown(
            id="merge_data_dropdown",
            placeholder="Choisir un DataFrame à fusionner...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        dcc.Dropdown(
            id="merge_column_left",
            placeholder="Colonne de gauche (table active)...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        dcc.Dropdown(
            id="merge_column_right",
            placeholder="Colonne de droite (table sélectionnée)...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        dcc.Dropdown(
            id="merge_how_dropdown",
            options=[
                {"label": "inner", "value": "inner"},
                {"label": "left", "value": "left"},
                {"label": "right", "value": "right"},
                {"label": "outer", "value": "outer"},
            ],
            placeholder="Type de merge...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Div(children=[], className="feedback-popup", id="merge_feedback"),
        html.Button(
            "Valider",
            className="import-validate-button",
            id="import-validate-button-merge",
        ),
    ],
    id="merge_popup",
)


export_popup = html.Div(
    children=[
        html.Button(
            html.I(className="fa-solid fa-xmark"),
            id="export_popup_close_button",
            className="filter_close_button",
        ),
        html.H2("Exporter le DataFrame", id="export_popup_title"),
        dcc.Dropdown(
            id="export_format_dropdown",
            options=[
                {"label": "CSV", "value": "csv"},
                {"label": "Excel", "value": "excel"},
            ],
            placeholder="Choisir un format...",
            style={
                "backgroundColor": "#2A2D3A",
                "border": "1px solid #2A2D3A",
                "color": "#000000",
                "width": "200px",
            },
        ),
        html.Button(
            "Exporter",
            className="import-validate-button",
            id="import-validate-button-export",
        ),
        dcc.Download(id="export"),
    ],
    id="export_popup",
)


visualization_container = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H2("Nb Quantitatives"),
                        html.H1(children=[], id="valuebox_quantitative_count"),
                    ],
                    id="valuebox_quantitative",
                ),
                html.Div(
                    children=[
                        html.H2("Nb lignes"),
                        html.H1(children=[], id="valuebox_nrow_data_count"),
                    ],
                    id="valuebox_nrow_data",
                ),
                html.Div(
                    children=[
                        html.H2("Nb Qualitatives"),
                        html.H1(children=[], id="valuebox_qualitative_count"),
                    ],
                    id="valuebox_qualitative",
                ),
                html.Div(
                    children=[
                        html.H2("Données manquantes"),
                        html.H1(children=[], id="valuebox_missing_count"),
                    ],
                    id="valuebox_missing",
                ),
            ],
            id="valuebox_container",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children=[], id="quantitative_table_graph"),
                        html.Div(
                            children=[
                                dcc.Dropdown(
                                    id="dropdown_quanti",
                                    options=[],
                                    placeholder="Choisir une variable quantitative",
                                    className="custom-dropdown",
                                ),
                                html.Div(
                                    children=[
                                        html.Button(
                                            html.I(className="fas fa-table"),
                                            id="btn_table_quanti",
                                            title="Afficher tableau",
                                        ),
                                        html.Button(
                                            html.I(className="fas fa-chart-bar"),
                                            id="btn_graph_quanti",
                                            title="Afficher graphique",
                                        ),
                                    ],
                                    className="button-group",
                                    id="quanti_buttons",
                                ),
                            ],
                            className="options-box",
                            id="options_quantitative",
                        ),
                    ],
                    id="quantitative_visualization",
                ),
                html.Div(
                    children=[
                        html.Div(children=[], id="qualitative_table_graph"),
                        html.Div(
                            children=[
                                dcc.Dropdown(
                                    id="dropdown_quali",
                                    options=[],
                                    placeholder="Choisir une variable qualitative",
                                    className="custom-dropdown",
                                ),
                                html.Div(
                                    children=[
                                        html.Button(
                                            html.I(className="fas fa-table"),
                                            id="btn_table_quali",
                                            title="Afficher tableau",
                                        ),
                                        html.Button(
                                            html.I(className="fas fa-chart-pie"),
                                            id="btn_graph_quali",
                                            title="Afficher graphique",
                                        ),
                                    ],
                                    className="button-group",
                                    id="quali_buttons",
                                ),
                            ],
                            className="options-box",
                            id="options_qualitative",
                        ),
                    ],
                    id="qualitative_visualization",
                ),
            ],
            id="visualization_content",
        ),
        html.Div(
            children=[
                html.Button(
                    "Graphiques avancés",
                    id="advanced_graphs_button",
                ),
                html.Div(
                    children=[
                        dcc.Dropdown(
                            id="col_x_dropdown",
                            options=[],
                            placeholder="Choisir une colonne pour l'axe X",
                            style={
                                "border": "1px solid #2A2D3A",
                                "color": "#444444",
                                "backgroundColor": "#2A2D3A",
                                "marginTop": "10px",
                                "width": "300px",
                                "textAlign": "center",
                            },
                        ),
                        dcc.Dropdown(
                            id="col_y_dropdown",
                            options=[],
                            placeholder="Choisir une colonne pour l'axe Y",
                            style={
                                "border": "1px solid #2A2D3A",
                                "color": "#444444",
                                "backgroundColor": "#2A2D3A",
                                "marginTop": "10px",
                                "width": "300px",
                                "textAlign": "center",
                            },
                        ),
                        dcc.Dropdown(
                            id="graph_type_dropdown",
                            options=[
                                {"label": "Nuage de points", "value": "scatter"},
                                {"label": "Courbe", "value": "line"},
                                {"label": "Boxplot", "value": "box"},
                                {"label": "Violin plot", "value": "violin"},
                            ],
                            placeholder="Choisir le type de graphique",
                            style={
                                "border": "1px solid #2A2D3A",
                                "backgroundColor": "#2A2D3A",
                                "marginTop": "10px",
                                "width": "300px",
                                "textAlign": "center",
                            },
                        ),
                    ],
                    id="advanced_graphs_content",
                ),
                html.Div(children=[], id="graph_container"),
            ],
            id="advanced_graphs",
        ),
    ],
    id="visualization_container",
)
