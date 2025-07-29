import pandas as pd
import base64
import io
import numpy as np
from typing import Literal
import plotly.express as px
import statsmodels.api as sm
from dash import ctx
import json
from flask_caching import Cache
import pickle
import hashlib

cache = Cache()


def set_df_to_cache(file_id: str, df: pd.DataFrame):
    """
    Sérialise un DataFrame et le stocke dans le cache avec un identifiant de fichier.
    Parameters:
    - file_id (str): L'identifiant du fichier pour le cache.
    - df (pd.DataFrame): Le DataFrame à stocker dans le cache.
    Returns:
    - None
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> set_df_to_cache('file_123', df)
    """
    data_pickle = pickle.dumps(df)
    cache.set(file_id, data_pickle, timeout=0)


def get_df_from_cache(file_id: str) -> pd.DataFrame | None:
    """
    Récupère un DataFrame du cache à l'aide de l'identifiant de fichier.
    Parameters:
    - file_id (str): L'identifiant du fichier pour le cache.
    Returns:
    - pd.DataFrame | None: Le DataFrame récupéré du cache, ou None si l'identifiant n'existe pas.
    Exemple d'utilisation:
    >>> df = get_df_from_cache('file_123')
    >>> if df is not None:
    """
    pickled_df = cache.get(file_id)
    if pickled_df is None:
        return None
    return pickle.loads(pickled_df)


def id_hash(contents: str) -> str:
    """
    Calcule un hash SHA-256 pour le contenu d'un fichier.
    Parameters:
    - contents (str): Le contenu du fichier sous forme de chaîne de caractères.
    Returns:
    - str: Le hash SHA-256 du contenu du fichier.
    Exemple d'utilisation:
    >>> contents = "Hello, World!"
    >>> hash_value = id_hash(contents)
    >>> print(hash_value)  # Output: un hash SHA-256
    """
    h = hashlib.sha256()
    h.update(contents.encode("utf-8"))
    return h.hexdigest()


def import_csv(
    contents: str, filename: str, sep: str, decimal: str, header: int
) -> dict:
    """
    Importe un fichier CSV à partir d'une chaîne de caractères encodée en base64.
    Parameters:
    - contents (str): Le contenu du fichier CSV encodé en base64.
    - filename (str): Le nom du fichier CSV.
    - sep (str): Le séparateur de colonnes utilisé dans le fichier CSV.
    - decimal (str): Le séparateur décimal utilisé dans le fichier CSV.
    - header (int): La ligne d'en-tête à utiliser pour le DataFrame.
    Returns:
    - dict: Un dictionnaire contenant le nom du fichier et le DataFrame pandas, ou une erreur.
    Exemple d'utilisation:
    >>> contents = "data:text/csv;base64,SGVsbG8sV29ybGQKMSwyLDMKNCw1LDY="
    >>> filename = "example.csv"
    >>> sep = ","
    >>> decimal = "."
    >>> header = 0
    >>> result = import_csv(contents, filename, sep, decimal, header)
    >>> print(result['filename'])  # Output: example.csv
    >>> print(result['panda_data'])  # Output: DataFrame with the CSV data
    """
    try:
        _, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string).decode("utf-8")
        if filename.endswith(".csv"):
            df = pd.read_csv(
                io.StringIO(decoded), sep=sep, decimal=decimal, header=header
            )
            return {"filename": filename, "panda_data": df}
    except Exception as e:
        return {"filename": filename, "panda_data": None, "error": str(e)}


def import_excel(
    contents: str, filename: str, sheet_name, header=0, decimal="."
) -> dict:
    """
    Importe un fichier Excel à partir d'une chaîne de caractères encodée en base64.
    Parameters:
    - contents (str): Le contenu du fichier Excel encodé en base64.
    - filename (str): Le nom du fichier Excel.
    - sheet_name (str): Le nom de la feuille à importer.
    - header (int): La ligne d'en-tête à utiliser pour le DataFrame.
    - decimal (str): Le séparateur décimal utilisé dans le fichier Excel.
    Returns:
    - dict: Un dictionnaire contenant le nom du fichier et le DataFrame pandas, ou une erreur.
    Exemple d'utilisation:
    >>> contents = "data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,..."
    >>> filename = "example.xlsx"
    >>> sheet_name = "Sheet1"
    >>> header = 0
    >>> decimal = "."
    >>> result = import_excel(contents, filename, sheet_name, header, decimal)
    >>> print(result['filename'])  # Output: example.xlsx
    >>> print(result['panda_data'])  # Output: DataFrame with the Excel data
    """
    try:
        _, content_string = contents.split(",", 1)
        decoded = base64.b64decode(content_string)
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(
                io.BytesIO(decoded),
                sheet_name=sheet_name,
                header=header,
                decimal=decimal,
            )
            return {"filename": filename, "panda_data": df}
    except ValueError as e:
        if "Worksheet named" in str(e) and "not found" in str(e):
            return {
                "filename": filename,
                "panda_data": None,
                "error": f"Feuille Excel introuvable : '{sheet_name}'",
            }
        return {
            "filename": filename,
            "panda_data": None,
            "error": f"Erreur de valeur : {str(e)}",
        }
    except Exception as e:
        return {"filename": filename, "panda_data": None, "error": str(e)}


def filter_text(df: pd.DataFrame, col: str, val: str) -> pd.DataFrame:
    """
    Filtre les lignes d'un DataFrame en fonction d'une valeur de texte dans une colonne spécifique.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à filtrer.
    - col (str): Le nom de la colonne à filtrer.
    - val (str): La valeur de texte à rechercher dans la colonne.
    Returns:
    - pd.DataFrame: Le DataFrame filtré contenant uniquement les lignes où la colonne spécifiée contient la valeur de texte.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': ['apple', 'banana', 'cherry'], 'B': [1, 2, 3]})
    >>> filter_text(df, 'A', 'banana')
         A     B
    1  banana  2
    """
    val = str(val).strip().lower()
    return df[df[col].astype(str).str.strip().str.lower() == val]


def filter_in_text(df: pd.DataFrame, col: str, val: str) -> pd.DataFrame:
    """
    Filtre les lignes d'un DataFrame en fonction d'une valeur de texte dans une colonne spécifique.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à filtrer.
    - col (str): Le nom de la colonne à filtrer.
    - val (str): La valeur de texte à rechercher dans la colonne.
    Returns:
    - pd.DataFrame: Le DataFrame filtré contenant uniquement les lignes où la colonne spécifiée contient la valeur de texte.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': ['apple pie', 'banana split', 'cherry tart'], 'B': [1, 2, 3]})
    >>> filter_in_text(df, 'A', 'banana')
         A           B
    1  banana split  2
    """
    val = str(val).strip().lower()
    return df[df[col].astype(str).str.strip().str.lower().str.contains(val)]


def filter_comparaison(df: pd.DataFrame, col: str, val: float, x: str) -> pd.DataFrame:
    """
    Filtre les lignes d'un DataFrame en fonction d'une comparaison sur une colonne spécifique.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à filtrer.
    - col (str): Le nom de la colonne à filtrer.
    - val (str, int, float): La valeur à comparer.
    - x (str): Le type de comparaison à effectuer (par exemple, "plus grand que", "plus petit que", etc.).
    Returns:
    - pd.DataFrame: Le DataFrame filtré contenant uniquement les lignes où la colonne spéc
    ifiée satisfait la condition de comparaison.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8]})
    >>> filter_comparaison(df, 'A', 2, 'plus grand que')
    A  B
    2  3  7
    3  4  8
    """
    if x == "plus grand que":
        return df[df[col] > val]
    elif x == "plus grand ou égal à":
        return df[df[col] >= val]
    elif x == "plus petit que":
        return df[df[col] < val]
    elif x == "plus petit ou égal à":
        return df[df[col] <= val]
    elif x == "différent de":
        return df[df[col] != val]
    elif x == "égal à":
        return df[df[col] == val]


def filter_types_columns(df, col_type: Literal["text", "numeric", "boolean"]):
    """
    Filtre les colonnes d'un DataFrame en fonction de leur type.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à filtrer.
    - col_type (str): Le type de colonne à filtrer ('text', 'numeric' 'boolean').
    Returns:
    - pd.DataFrame: Un DataFrame contenant uniquement les colonnes du type spécifié.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': ['apple', 'banana'], 'B':
    [1, 2], 'C': [True, False]})
    >>> filter_types_columns(df, 'text')
    A
    0    apple
    1   banana
    >>> filter_types_columns(df, 'numeric')
    B
    0    1
    1    2
    >>> filter_types_columns(df, 'boolean')
    C
    0     True
    1    False
    """
    if col_type == "text":
        return df.select_dtypes(include=["object", "string"])
    elif col_type == "numeric":
        return df.select_dtypes(include=["number"])
    elif col_type == "boolean":
        return df.select_dtypes(include=["bool"])


def filter_keep_columns(df, columns):
    """
    Filtre les colonnes d'un DataFrame pour ne conserver que celles spécifiées.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à filtrer.
    - columns (list): La liste des noms de colonnes à conserver.
    Returns:
    - pd.DataFrame: Un DataFrame contenant uniquement les colonnes spécifiées.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4], 'C': [5, 6]})
    >>> filter_keep_columns(df, ['A', 'C'])
       A  C
    0  1  5
    1  2  6
    """
    if not columns:
        return df
    return df[columns]


def filter_na(
    df: pd.DataFrame, col: str, action: Literal["drop", "mean", "median", "zero"]
) -> pd.DataFrame:
    """
    Filtre les valeurs manquantes (NA) dans une colonne spécifique d'un DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à filtrer.
    - col (str): Le nom de la colonne à filtrer.
    - action (str): L'action à effectuer sur les valeurs manquantes :
        - "drop": Supprimer les lignes contenant des NA dans la colonne spécifiée.
        - "mean": Remplacer les NA par la moyenne de la colonne (si numérique).
        - "median": Remplacer les NA par la médiane de la colonne (si numérique).
        - "zero": Remplacer les NA par 0 (si numérique) ou par "0" (si chaîne de caractères).
    Returns:
    - pd.DataFrame: Le DataFrame filtré ou modifié en fonction de l'action spécifiée.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, np.nan, 4], 'B': [5, np.nan, 7, 8]})
    >>> filter_na(df, 'A', 'drop')
       A    B
    0  1.0  5.0
    1  2.0  NaN
    3  4.0  8.0
    """

    fake_na_values = {
        "na",
        "n/a",
        "nan",
        "null",
        "none",
        "?",
        "-",
        "--",
        "NA",
        "N/A",
        "NAN",
        "NULL",
        "None",
        "",
        " ",
    }

    if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
        df[col] = df[col].apply(
            lambda x: (
                np.nan
                if isinstance(x, str) and x.strip().lower() in fake_na_values
                else x
            )
        )

    if action == "drop":
        return df.dropna(subset=[col])

    elif action == "mean":
        if pd.api.types.is_numeric_dtype(df[col]):
            return df.assign(**{col: df[col].fillna(df[col].mean())})
        else:
            return df

    elif action == "median":
        if pd.api.types.is_numeric_dtype(df[col]):
            return df.assign(**{col: df[col].fillna(df[col].median())})
        else:
            return df

    elif action == "zero":
        if pd.api.types.is_numeric_dtype(df[col]):
            return df.assign(**{col: df[col].fillna(0)})
        elif pd.api.types.is_string_dtype(df[col]):
            return df.assign(**{col: df[col].fillna("0")})
        elif pd.api.types.is_bool_dtype(df[col]):
            return df.assign(**{col: df[col].fillna(False)})
        else:
            return df

    return df


def filter_outlier(df: pd.DataFrame, col: str, action: str) -> pd.DataFrame:
    """
    Filtre les outliers dans la colonne `col` selon l'action choisie,
    en détectant les outliers avec la méthode IQR (interquartile range).

    action :
        - "drop" : supprimer les lignes outliers
        - "median" : remplacer les outliers par la médiane
        - "winsorize" : limiter les outliers aux bornes (clipping)
    Parameters:
    - df (pd.DataFrame): Le DataFrame à filtrer.
    - col (str): Le nom de la colonne à filtrer.
    - action (str): L'action à effectuer sur les outliers :
        - "drop": Supprimer les lignes contenant des outliers dans la colonne spécifiée.
        - "median": Remplacer les outliers par la médiane de la colonne.
        - "winsorize": Limiter les valeurs des outliers aux bornes inférieure et supérieure.
    Returns:
    - pd.DataFrame: Le DataFrame filtré ou modifié en fonction de l'action spécifiée.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 3, 100, 5], 'B': [5, 6, 7, 8, 9]})
    >>> filter_outlier(df, 'A', 'drop')
       A  B
    0  1  5
    1  2  6
    2  3  7
    4  5  9

    """
    df = df.copy()
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = (df[col] < lower_bound) | (df[col] > upper_bound)

    if action == "drop":
        df = df.loc[~outliers]
    elif action == "median":
        median_val = df[col].median()
        df.loc[outliers, col] = median_val
    elif action == "winsorize":
        df.loc[df[col] < lower_bound, col] = lower_bound
        df.loc[df[col] > upper_bound, col] = upper_bound

    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Applique une série de filtres à un DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à filtrer.
    - filters (dict): Dictionnaire des filtres à appliquer.
    Returns:
    - pd.DataFrame: DataFrame filtré.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': ['apple', 'banana', 'cherry'], 'B': [1, 2, 3]})
    >>> filters = {
        'f1': {'type': 'text', 'col': 'A', 'value': 'banana'},
        'f2': {'type': 'comparaison', 'col': 'B', 'value': 2, 'operator': 'plus grand que'}
    }
    >>> filtered_df = apply_filters(df, filters)
    >>> print(filtered_df)
         A     B
    2  cherry  3
    """
    for f_id, f in filters.items():
        if f["type"] == "text":
            df = filter_text(df, f["col"], f["value"])
        elif f["type"] == "in_text":
            df = filter_in_text(df, f["col"], f["value"])
        elif f["type"] == "comparaison":
            df = filter_comparaison(df, f["col"], f["value"], f["operator"])
        elif f["type"] == "types_columns":
            df = filter_types_columns(df, f["col_type"])
        elif f["type"] == "keep_columns":
            df = filter_keep_columns(df, f["columns"])
        elif f["type"] == "na":
            df = filter_na(df, f["col"], f["action"])
        elif f["type"] == "outlier":
            df = filter_outlier(df, f["col"], f["action"])
    return df


def sort_abc(df: pd.DataFrame, col: str, order: Literal["asc", "desc"]) -> pd.DataFrame:
    """
    Trie un DataFrame par ordre alphabétique sur une colonne spécifique.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à trier.
    - col (str): Le nom de la colonne sur laquelle trier.
    - order (str): L'ordre de tri ('asc' pour ascendant, 'desc' pour descendant).
    Returns:
    - pd.DataFrame: Le DataFrame trié.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': ['banana', 'apple', 'cherry'], 'B': [1, 2, 3]})
    >>> sort_abc(df, 'A', 'asc')
         A    B
    1  apple  2
    0  banana  1
    2  cherry  3
    """
    if order == "asc":
        return df.sort_values(by=col, ascending=True)
    elif order == "desc":
        return df.sort_values(by=col, ascending=False)


def sort_123(df: pd.DataFrame, col: str, order: Literal["asc", "desc"]) -> pd.DataFrame:
    """
    Trie un DataFrame par ordre numérique sur une colonne spécifique.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à trier.
    - col (str): Le nom de la colonne sur laquelle trier.
    - order (str): L'ordre de tri ('asc' pour ascendant, 'desc' pour descendant).
    Returns:
    - pd.DataFrame: Le DataFrame trié.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [3, 1, 2], 'B': [5, 6, 7]})
    >>> sort_123(df, 'A', 'asc')
       A  B
    1  1  6
    2  2  7
    0  3  5
    """
    if order == "asc":
        return df.sort_values(
            by=col, ascending=True, key=lambda x: pd.to_numeric(x, errors="coerce")
        )
    elif order == "desc":
        return df.sort_values(
            by=col, ascending=False, key=lambda x: pd.to_numeric(x, errors="coerce")
        )


def apply_sort(df: pd.DataFrame, sort_info: list) -> pd.DataFrame:
    """
    Applique un tri à un DataFrame selon la nature des colonnes.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à trier.
    - sort_info (list): Liste de dictionnaires contenant les informations de tri, chaque dictionnaire ayant les clés 'column_id' et 'direction'.
    Returns:
    - pd.DataFrame: Le DataFrame trié.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': ['banana', 'apple', 'cherry'], 'B': [3, 1, 2]})
    >>> sort_info = [{'column_id': 'A', 'direction': 'asc'}, {'column_id': 'B', 'direction': 'desc'}]
    >>> sorted_df = apply_sort(df, sort_info)
    >>> print(sorted_df)
         A     B
    1  apple   1
    2  cherry  2
    0  banana  3
    """
    for sort in sort_info:
        col = sort.get("column_id")
        direction = sort.get("direction")
        if col not in df.columns:
            continue

        if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_bool_dtype(
            df[col]
        ):
            df = sort_123(df, col, direction)
        else:
            df = sort_abc(df, col, direction)

    return df


def concat_dataframes(
    df_main: pd.DataFrame, df_other: pd.DataFrame, axis: int
) -> pd.DataFrame:
    """
    Concatène deux DataFrames le long d'un axe spécifié (0 pour lignes, 1 pour colonnes).
    Parameters:
    - df_main (pd.DataFrame): Le DataFrame principal (tableau de gauche).
    - df_other (pd.DataFrame): Le DataFrame à concaténer (tableau de droite).
    - axis (int): L'axe le long duquel concaténer (0 pour lignes, 1 pour colonnes).
    Returns:
    - pd.DataFrame: Le DataFrame résultant de la concaténation.
    Raises:
    - ValueError: Si les colonnes ne correspondent pas pour une concaténation en lignes ou si le nombre de lignes ne correspond pas pour une concaténation en colonnes.
    Exemple d'utilisation:
    >>> df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
    >>> concat_dataframes(df1, df2, axis=0)
       A  B
    0  1  3
    1  2  4
    2  5  7
    3  6  8
    """
    if axis == 0:
        if set(df_main.columns) != set(df_other.columns):
            raise ValueError(
                "Les colonnes ne correspondent pas pour une concaténation en lignes."
            )
        return pd.concat([df_main, df_other], axis=0, ignore_index=True)

    elif axis == 1:
        if len(df_main) != len(df_other):
            raise ValueError(
                "Le nombre de lignes ne correspond pas pour une concaténation en colonnes."
            )
        return pd.concat(
            [df_main.reset_index(drop=True), df_other.reset_index(drop=True)], axis=1
        )


def merge_dataframes(
    df_main: pd.DataFrame,
    df_other: pd.DataFrame,
    left_key: str,
    right_key: str,
    how: str,
) -> pd.DataFrame:
    """
    Fusionne deux DataFrames en fonction des colonnes spécifiées et du type de merge.

    Parameters:
    - df_main (pd.DataFrame): Le DataFrame principal (tableau de gauche).
    - df_other (pd.DataFrame): Le DataFrame à fusionner (tableau de droite).
    - left_key (str): Nom de la colonne du DataFrame principal à utiliser pour la fusion.
    - right_key (str): Nom de la colonne du DataFrame à fusionner à utiliser pour la fusion.
    - how (str): Type de fusion ('inner', 'left', 'right', 'outer').

    Returns:
    - pd.DataFrame: Le DataFrame résultant de la fusion.

    Raises:
    - ValueError: Si les colonnes spécifiées n'existent pas ou si le type de fusion est invalide.
    Exemple d'utilisation:
    >>> df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    >>> df2 = pd.DataFrame({'C': [1, 2], 'D': [5, 6]})
    >>> merge_dataframes(df1, df2, 'A', 'C', 'inner')
       A  B  C  D
    0  1  3  1  5
    1  2  4  2  6
    """
    return pd.merge(df_main, df_other, left_on=left_key, right_on=right_key, how=how)


def count_quantitative(df: pd.DataFrame) -> int:
    """
    Retourne le nombre de colonnes quantitatives (numériques) dans le DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à analyser.
    Returns:
    - int: Le nombre de colonnes quantitatives dans le DataFrame.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c'], 'C': [4.5, 5.5, 6.5]})
    >>> count_quantitative(df)
    2
    """
    if df.empty:
        return 0
    return df.select_dtypes(include=["number"]).shape[1]


def count_qualitative(df: pd.DataFrame) -> int:
    """
    Retourne le nombre de colonnes qualitatives (texte) dans le DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à analyser.
    Returns:
    - int: Le nombre de colonnes qualitatives dans le DataFrame.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c'], 'C': [4.5, 5.5, 6.5]})
    >>> count_qualitative(df)
    1
    """
    if df.empty:
        return 0
    return df.select_dtypes(include=["object", "string"]).shape[1]


def nrow(df: pd.DataFrame) -> int:
    """
    Retourne le nombre de lignes du DataFrame.

    Parameters:
    - df (pd.DataFrame): Le DataFrame à analyser.

    Returns:
    - int: Le nombre de lignes dans le DataFrame.
    """
    return df.shape[0] if df is not None else 0


def nas(df: pd.DataFrame) -> int:
    """
    Retourne le nombre de valeurs manquantes dans le DataFrame.

    Parameters:
    - df (pd.DataFrame): Le DataFrame à analyser.

    Returns:
    - int: Le nombre de valeurs manquantes dans le DataFrame.
    """
    return df.isna().sum().sum()


def correlation_tab(df):
    """
    Calcule la matrice de corrélation pour les colonnes numériques du DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame à analyser.
    Returns:
    - pd.DataFrame: Un DataFrame contenant la matrice de corrélation arrondie à 3 décimales, avec les colonnes renommées.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
    >>> corr_df = correlation_tab(df)
    >>> print(corr_df)
    Colonne    A    B    C
    0         A  1.0  1.0  1.0
    1         B  1.0  1.0  1.0
    2         C  1.0  1.0  1.0
    """
    corr = df.select_dtypes(include=["number"]).corr(method="pearson")
    corr = corr.round(3)
    corr = corr.reset_index().rename(columns={"index": "Colonne"})
    return corr


def histogram(df: pd.DataFrame, col: str) -> px.histogram:
    """
    Crée un histogramme pour une colonne spécifique du DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col (str): Le nom de la colonne pour laquelle créer l'histogramme.
    Returns:
    - px.histogram: Un objet Plotly Express représentant l'histogramme.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 2, 3, 3, 3]})
    >>> fig = histogram(df, 'A')
    >>> fig.show()
    """
    fig = px.histogram(
        df,
        x=col,
        nbins=20,
        labels={col: col, "count": "Effectif"},
        hover_data={col: True},
        color_discrete_sequence=["aquamarine"],
    )
    fig.update_traces(opacity=0.6)
    fig.update_layout(xaxis_title=col, yaxis_title="Effectif", bargap=0.2)
    return fig


def boxplot(df: pd.DataFrame, col: str) -> px.box:
    """
    Crée un boxplot pour une colonne spécifique du DataFrame.

    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col (str): Le nom de la colonne pour laquelle créer le boxplot.

    Returns:
    - px.box: Un objet Plotly Express représentant le boxplot.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 2, 3, 3, 3]})
    >>> fig = boxplot(df, 'A')
    >>> fig.show()
    """
    fig = px.box(
        df,
        y=col,
        labels={col: col},
        hover_data={col: True},
        color_discrete_sequence=["aquamarine"],
    )
    fig.update_traces(opacity=0.6)
    fig.update_layout(yaxis_title=col)
    return fig


def violin(df: pd.DataFrame, col: str) -> px.violin:
    """
    Crée un violin plot pour une colonne spécifique du DataFrame.

    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col (str): Le nom de la colonne pour laquelle créer le violin plot.

    Returns:
    - px.violin: Un objet Plotly Express représentant le violin plot.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 2, 3, 3, 3]})
    >>> fig = violin(df, 'A')
    >>> fig.show()
    """
    fig = px.violin(
        df,
        y=col,
        labels={col: col},
        hover_data={col: True},
        color_discrete_sequence=["aquamarine"],
    )
    fig.update_traces(opacity=0.6)
    fig.update_layout(yaxis_title=col)
    return fig


def pie_chart(df: pd.DataFrame, col: str) -> px.pie:
    """
    Crée un diagramme circulaire pour une colonne spécifique du DataFrame.

    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col (str): Le nom de la colonne pour laquelle créer le diagramme circulaire.

    Returns:
    - px.pie: Un objet Plotly Express représentant le diagramme circulaire.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 2, 3, 3, 3]})
    >>> fig = pie_chart(df, 'A')
    >>> fig.show()
    """
    fig = px.pie(
        df,
        names=col,
        labels={col: col},
        hover_data=[col],
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        title=f"Répartition de {col}",
        plot_bgcolor="#1F2430",
        paper_bgcolor="#1F2430",
        font_color="#FFFFFF",
    )
    return fig


def bar_chart(df: pd.DataFrame, col: str) -> px.bar:
    """
    Crée un diagramme à barres pour une colonne spécifique du DataFrame.

    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col (str): Le nom de la colonne pour laquelle créer le diagramme à barres.

    Returns:
    - px.bar: Un objet Plotly Express représentant le diagramme à barres.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 2, 3, 3, 3]})
    >>> fig = bar_chart(df, 'A')
    >>> fig.show()
    """
    counts = df[col].value_counts().reset_index()
    counts.columns = [col, "Effectif"]
    fig = px.bar(
        counts,
        x=col,
        y="Effectif",
        labels={col: col, "Effectif": "Effectif"},
        hover_data={col: True, "Effectif": True},
        color_discrete_sequence=["aquamarine"],
    )
    fig.update_traces(opacity=0.6)
    fig.update_layout(
        xaxis_title=col,
        yaxis_title="Effectif",
        plot_bgcolor="#1F2430",
        paper_bgcolor="#1F2430",
        font_color="#FFFFFF",
        xaxis=dict(color="#FFFFFF"),
        yaxis=dict(color="#FFFFFF"),
    )
    return fig


def scatter_2col(df: pd.DataFrame, col_x: str, col_y: str) -> px.scatter:
    """
    Crée un nuage de points pour deux colonnes spécifiques du DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col_x (str): Le nom de la colonne pour l'axe des x.
    - col_y (str): Le nom de la colonne pour l'axe des y.
    Returns:
    - px.scatter: Un objet Plotly Express représentant le nuage de points.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> fig = scatter_2col(df, 'A', 'B')
    >>> fig.show()
    """
    fig = px.scatter(df, x=col_x, y=col_y, color_discrete_sequence=["aquamarine"])
    fig.update_traces(opacity=0.6)
    fig.update_layout(
        title=f"Nuage de points : {col_x} vs {col_y}",
        xaxis_title=col_x,
        yaxis_title=col_y,
        plot_bgcolor="#1F2430",
        paper_bgcolor="#1F2430",
        font_color="#FFFFFF",
    )
    return fig


def regression_2col(df: pd.DataFrame, col_x: str, col_y: str) -> px.line:
    """
    Effectue une régression linéaire entre deux colonnes du DataFrame et crée un graphique de la ligne de régression.
    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col_x (str): Le nom de la colonne pour l'axe des x.
    - col_y (str): Le nom de la colonne pour l'axe des y.
    Returns:
    - px.line: Un objet Plotly Express représentant la ligne de régression.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> fig = regression_2col(df, 'A', 'B')
    >>> fig.show()
    """
    df_clean = df[[col_x, col_y]].dropna()

    X = df_clean[col_x]
    Y = df_clean[col_y]

    X_const = sm.add_constant(X)
    model = sm.OLS(Y, X_const).fit()

    df_clean["y_pred"] = model.predict(X_const)

    fig = px.line(df_clean, x=col_x, y="y_pred", color_discrete_sequence=["aquamarine"])

    fig.update_layout(
        title=f"Régression linéaire entre {col_x} et {col_y}",
        xaxis_title=col_x,
        yaxis_title=col_y,
        plot_bgcolor="#1F2430",
        paper_bgcolor="#1F2430",
        font_color="#FFFFFF",
    )
    return fig


def box_2col(df: pd.DataFrame, col_x: str, col_y: str) -> px.box:
    """
    Crée un boxplot pour deux colonnes spécifiques du DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col_x (str): Le nom de la colonne pour l'axe des x.
    - col_y (str): Le nom de la colonne pour l'axe des y.
    Returns:
    - px.box: Un objet Plotly Express représentant le boxplot.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': ['a', 'b', 'c'], 'B': [1, 2, 3]})
    >>> fig = box_2col(df, 'A', 'B')
    >>> fig.show()
    """
    fig = px.box(df, x=col_x, y=col_y, color_discrete_sequence=["aquamarine"])
    fig.update_traces(opacity=0.6)
    fig.update_layout(
        title=f"Boxplot : {col_x} vs {col_y}",
        xaxis_title=col_x,
        yaxis_title=col_y,
        plot_bgcolor="#1F2430",
        paper_bgcolor="#1F2430",
        font_color="#FFFFFF",
    )
    return fig


def violin_2col(df: pd.DataFrame, col_x: str, col_y: str) -> px.violin:
    """
    Crée un violin plot pour deux colonnes spécifiques du DataFrame.
    Parameters:
    - df (pd.DataFrame): Le DataFrame contenant les données.
    - col_x (str): Le nom de la colonne pour l'axe des x.
    - col_y (str): Le nom de la colonne pour l'axe des y.
    Returns:
    - px.violin: Un objet Plotly Express représentant le violin plot.
    Exemple d'utilisation:
    >>> df = pd.DataFrame({'A': ['a', 'b', 'c'], 'B': [1, 2, 3]})
    >>> fig = violin_2col(df, 'A', 'B')
    >>> fig.show()
    """
    fig = px.violin(df, x=col_x, y=col_y, color_discrete_sequence=["aquamarine"])
    fig.update_traces(opacity=0.6)
    fig.update_layout(
        title=f"Violin plot : {col_x} vs {col_y}",
        xaxis_title=col_x,
        yaxis_title=col_y,
        plot_bgcolor="#1F2430",
        paper_bgcolor="#1F2430",
        font_color="#FFFFFF",
    )
    return fig
