# Datazen

**Datazen** est une application de gestion et de visualisation de données tabulaires, conçue pour les débutants en codage ou pour ceux qui souhaitent gagner du temps dans le traitement des données.

Développée entièrement avec [Dash](https://dash.plotly.com/), elle permet :

- d'importer des fichiers **CSV** et **Excel (.xlsx)** ;
- d'appliquer des opérations simples : **filtres**, **tris**, **recherches** ;
- de visualiser les données via :
  - des **graphiques interactifs** (Plotly),
  - des **tableaux statiques**.

**Aucune connaissance en Python n’est nécessaire pour utiliser l’application.**
---

## Installation rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/alexisvincent37/Datazen
```

### 2. Se placer dans le répertoire cloné

```bash
cd "votre_chemin/Datazen"
```

### 3. Initialiser l'environnement virtuel (recommandé)

```bash
python -m venv .venv
```

#### Puis activer l’environnement :

- **Windows** :

```bash
.venv\Scripts\activate
```

- **Linux / macOS** :

```bash
source .venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install coverage dash dash-design-kit flask-caching openpyxl pandas plotly pytest pytest-cov statsmodels xlsxwriter
```

---

## Lancement de l'application

### **Méthode 1** : Exécuter le script Python

PowerShell
```bash
$env:PYTHONPATH="src"; python app.py
```

Linux/macOS
```bash
PYTHONPATH=src python app.py
```

> L'application sera disponible à l'adresse : `http://localhost:8050` (serveur Dash en développement)

Vous pouvez également la lancer en mode **production** avec Gunicorn :

```bash
PYTHONPATH=src gunicorn app:server --workers 7 --bind 0.0.0.0:8050
```

> *(Adaptez le nombre de workers selon votre machine)*

---

### **Méthode 2** : Utiliser l’exécutable

Un exécutable `app.exe` est disponible à la racine.  
Il a été généré via `auto-py-to-exe`.

- Il lance l'application en mode Dash/Flask avec `debug=False`
- Recommandé pour une **utilisation quotidienne sans installation Python**

---

## Fonctionnalités

### Importation de données

Il est possible d'importer des fichiers CSV et Excel (.xlsx et .xls) directement dans l'application. Les données sont ensuite chargées dans un DataFrame Pandas et stockées en cache sur le disque pour une utilisation plus fluide.

Il suffit de cliquer sur **"Importer un fichier"**, un popup vous permet de sélectionner le fichier à charger.

### Affichage des données

Après importation, cliquez sur le nom du fichier dans le menu latéral gauche. Les données apparaissent sous forme de tableau interactif :

- **Filtrer** selon des critères choisis
- **Trier** les colonnes
- **Rechercher** dans les colonnes

### Opérations sur les données

Filtres disponibles :
- Recherche exacte
- Recherche "contient"
- Comparaison (>, <, >=, <=, ==, !=)
- Garder certaines colonnes selon leur type (quanti, quali, booléen)
- Gestion des valeurs manquantes (suppression ou remplacement)
- Suppression ou traitement des outliers

Tris disponibles :
- Alphabétique
- Numérique

Chaque opération est historisée et peut être retirée via le menu déroulant en haut.

### Fusion de données

Il est possible de fusionner deux fichiers importés via :
- Concaténation (lignes ou colonnes)
- Merge (inner, outer, left, right)

### Sauvegarde des données

Le bouton "disquette" sauvegarde l’état actuel du tableau (trié/filtré) en remplaçant les données dans le cache.  
À utiliser avec précaution.

Les modifications directes dans les cellules doivent être sauvegardées manuellement.  
Conseil : faire les modifications **avant** d’appliquer des filtres ou tris.

### Export des données

Les données peuvent être exportées en `.csv` ou `.xlsx` via le bouton d’export (dans le navigateur).

### Visualisation des données

Pour afficher les graphiques, cachez la section de gestion à gauche. Une fois une table active sélectionnée :

- Sélectionner une colonne quantitative ou qualitative
- Cliquer sur l’icône de tableau → stats descriptives
- Cliquer sur l’icône de graphique → graphique interactif

#### Tableaux :

- **Quantitatives** : stats descriptives + matrice de corrélation
- **Qualitatives** : tableau de fréquence

#### Graphiques :

- **Quantitatives** :
  - Histogramme
  - Boxplot
  - Violinplot

- **Qualitatives** :
  - Barplot
  - Pie chart

### Graphiques avancés

Dans l’onglet “Graphiques avancés”, on peut afficher des relations entre 2 variables avec :

- Nuage de points (scatter plot)
- Droite de régression
- Boxplot
- Violinplot

Tous les graphiques sont interactifs et exportables (Plotly).

---

## Documentation

Ce projet a été réalisé dans le cadre d’un mémoire de Master 1.  
Une documentation détaillée sera prochainement disponible dans le dossier `docs`.
