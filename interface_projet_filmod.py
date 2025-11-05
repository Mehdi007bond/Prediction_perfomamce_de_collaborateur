# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import matplotlib
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta
import io
import base64

from flask import Flask, render_template_string, request

# Force Matplotlib à ne pas utiliser de backend d'interface graphique
matplotlib.use('Agg')

# --- 1. LE TEMPLATE HTML/CSS/JINJA2 (Frontend Amélioré) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prévision RH</title>
    <style>
        :root {
            --bg-color: #f0f2f6;
            --sidebar-bg: #ffffff;
            --card-bg: #ffffff;
            --text-color: #333;
            --text-color-light: #666;
            --primary-color: #0068c9;
            --border-color: #e0e0e0;
            --shadow: 0 4px 12px rgba(0,0,0,0.08);
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        body {
            font-family: var(--font-family);
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            display: grid;
            /* Barre latérale plus large pour les nouveaux filtres */
            grid-template-columns: 320px 1fr;
            min-height: 100vh;
        }
        aside {
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            padding: 2rem;
            display: flex;
            flex-direction: column;
        }
        main {
            padding: 2rem 3rem;
            overflow-y: auto;
        }
        h1, h2, h3, h4 {
            color: var(--text-color);
            font-weight: 600;
        }
        h1 { 
            font-size: 2rem; 
            margin-bottom: 2rem;
            color: var(--primary-color);
        }
        h2 { 
            font-size: 1.5rem; 
            margin-bottom: 1.5rem; 
            border-bottom: 2px solid var(--primary-color); 
            padding-bottom: 0.5rem; 
        }
        h3 { 
            font-size: 1.25rem; 
            margin-bottom: 1rem; 
        }
        
        .card {
            background-color: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border-color);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow);
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }
        .metric-card {
            text-align: center;
        }
        .metric-card h4 {
            font-size: 1rem;
            font-weight: 600;
            color: var(--primary-color);
            margin: 0 0 0.5rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        .metric-card .value {
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--text-color);
            line-height: 1.2;
        }
        
        .plot-container img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1rem;
        }
        th, td {
            padding: 0.75rem 1rem;
            border: 1px solid var(--border-color);
            text-align: left;
        }
        th {
            background-color: #f9f9f9;
            font-weight: 600;
        }
        tbody tr:nth-child(even) {
            background-color: #fdfdfd;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label.group-label {
            display: block;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            padding-bottom: 0.25rem;
            border-bottom: 1px solid var(--border-color);
        }
        input[type="range"] {
            width: 100%;
        }
        .checkbox-group {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            padding: 0.75rem;
            border-radius: 4px;
        }
        .checkbox-group label {
            display: flex;
            align-items: center;
            font-weight: 400;
            margin-bottom: 0.5rem;
        }
        .checkbox-group input {
            margin-right: 0.5rem;
        }
        
        button {
            background-image: linear-gradient(to right, var(--primary-color) 0%, #0056a0 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            transition: opacity 0.2s;
            margin-top: auto; /* Colle le bouton en bas de la sidebar */
        }
        button:hover {
            opacity: 0.9;
        }
        
        .data-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        /* Pour les petits écrans */
        @media (max-width: 1024px) {
            body {
                grid-template-columns: 1fr;
            }
            aside {
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }
            .data-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <aside>
        <form method="GET" action="/">
            <h1>Prévision RH</h1>
            
            <div class="form-group">
                <label for="jours_a_predire" class="group-label">Jours à prédire : {{ jours_a_predire }}</label>
                <input type="range" id="jours_a_predire" name="jours_a_predire" 
                       min="7" max="90" value="{{ jours_a_predire }}">
            </div>
            
            <div class="form-group">
                <label class="group-label">Filtrer par Secteur :</label>
                <div class="checkbox-group">
                    {% for category in all_categories %}
                    <label>
                        <input type="checkbox" name="categories" value="{{ category }}"
                               {% if category in selected_categories %}checked{% endif %}>
                        {{ category }}
                    </label>
                    {% endfor %}
                </div>
            </div>

            <!-- NOUVEAU FILTRE PAR LIGNE -->
            <div class="form-group">
                <label class="group-label">Filtrer par Ligne :</label>
                <div class="checkbox-group">
                    {% for ligne in all_lignes %}
                    <label>
                        <input type="checkbox" name="lignes" value="{{ ligne }}"
                               {% if ligne in selected_lignes %}checked{% endif %}>
                        {{ ligne }}
                    </label>
                    {% endfor %}
                </div>
            </div>
            
            <button type="submit">Actualiser</button>
        </form>
    </aside>
    
    <main>
        <h2>📈 Prévision à {{ jours_a_predire }} jours</h2>
        
        <div class="card metric-grid">
            <div class="metric-card">
                <h4><span style="font-size: 1.5rem;">📊</span>Note Actuelle Moy.</h4>
                <div class="value">{{ note_actuelle }}</div>
            </div>
            <div class="metric-card">
                <h4><span style="font-size: 1.5rem;">🔮</span>Prédiction J+7</h4>
                <div class="value">{{ pred_j7 }}</div>
            </div>
            <div class="metric-card">
                <h4><span style="font-size: 1.5rem;">{{ tendance_emoji }}</span>Tendance</h4>
                <div class="value">{{ "%.4f"|format(tendance_val) }}</div>
            </div>
        </div>
        
        <div class="card plot-container">
            <h3>Graphique de la prévision (Modèle RandomForest)</h3>
            <img src="data:image/png;base64,{{ plot_base64 }}" alt="Graphique de prévision">
        </div>
        
        <!-- NOUVELLE SECTION : KEY INFLUENCERS -->
        <h2>🔑 Analyse des Facteurs Clés</h2>
        <div class="card plot-container">
            <h3>Qu'est-ce qui influence la note ?</h3>
            <p style="color: var(--text-color-light); margin-bottom: 1.5rem;">
                Ce graphique montre l'importance de chaque facteur pour le modèle de prédiction. 
                Un score élevé signifie que le facteur a plus d'influence sur la note finale.
            </p>
            {% if plot_influencers_base64 %}
                <img src="data:image/png;base64,{{ plot_influencers_base64 }}" alt="Graphique des facteurs clés">
            {% else %}
                <p style="color: var(--text-color-light);">Erreur lors de la génération du graphique des facteurs clés.</p>
            {% endif %}
        </div>
        
        <h2>🔎 Exploration des données filtrées</h2>
        
        <div class="data-grid">
            <!-- NOUVEAU GRAPHIQUE PAR SECTEUR -->
            <div class="card plot-container">
                <h3>📊 Moyenne par Secteur</h3>
                {% if plot_cat_base64 %}
                    <img src="data:image/png;base64,{{ plot_cat_base64 }}" alt="Graphique par Secteur">
                {% else %}
                    <p style="color: var(--text-color-light);">Aucune donnée à afficher pour ces filtres.</p>
                {% endif %}
            </div>

            <!-- NOUVEAU GRAPHIQUE PAR LIGNE -->
            <div class="card plot-container">
                <h3>📈 Moyenne par Ligne</h3>
                {% if plot_ligne_base64 %}
                    <img src="data:image/png;base64,{{ plot_ligne_base64 }}" alt="Graphique par Ligne">
                {% else %}
                    <p style="color: var(--text-color-light);">Aucune donnée à afficher pour ces filtres.</p>
                {% endif %}
            </div>
        </div>

        <div class="card">
            <!-- TITRE MIS A JOUR ICI -->
            <h3>📋 Données de la prévision (Prochains {{ jours_a_predire }} jours)</h3>
            {% if predictions %}
                <table>
                    <thead>
                        <!-- CORRECTION DES EN-TÊTES -->
                        <tr>
                            <th>Date</th>
                            <th>Prédiction</th>
                            <th>Limite Basse</th>
                            <th>Limite Haute</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in predictions %}
                        <tr>
                            <td>{{ row.Date.strftime('%Y-%m-%d') }}</td>
                            <!-- CORRECTION DE L'ERREUR : 'row.Prédiction' au lieu de 'row.Note' -->
                            <td>{{ "%.2f"|format(row.Prédiction) }}</td>
                            <td>{{ "%.2f"|format(row.Limite_basse) }}</td>
                            <td>{{ "%.2f"|format(row.Limite_haute) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p style="color: var(--text-color-light);">Aucune donnée de prévision à afficher.</p>
            {% endif %}
        </div>
        
        <!-- CORRECTION DE LA STRUCTURE HTML POUR TOP/BOTTOM 5 -->
        <div class="data-grid">
            <div class="card">
                <h3>🏆 Top 5 Collaborateurs</h3>
                {% if top_5 %}
                    <table>
                        <thead>
                            <tr><th>Collaborateur</th><th>Note Moy.</th></tr>
                        </thead>
                        <tbody>
                            {% for row in top_5 %}
                            <tr>
                                <td>{{ row.Collaborateur }}</td>
                                <td>{{ "%.2f"|format(row.Note) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% else %}
                    <p style="color: var(--text-color-light);">Aucune donnée à afficher.</p>
                {% endif %}
            </div>
            <div class="card">
                <h3>⚠️ À surveiller (5 derniers)</h3>
                 {% if bottom_5 %}
                    <table>
                        <thead>
                            <tr><th>Collaborateur</th><th>Note Moy.</th></tr>
                        </thead>
                        <tbody>
                            {% for row in bottom_5 %}
                            <tr>
                                <td>{{ row.Collaborateur }}</td>
                                <td>{{ "%.2f"|format(row.Note) }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% else %}
                    <p style="color: var(--text-color-light);">Aucune donnée à afficher.</p>
                {% endif %}
            </div>
        </div>
        
    </main>
</body>
</html>
"""


# --- 2. LOGIQUE DE GÉNÉRATION DES DONNÉES (Identique) ---
def charger_et_nettoyer_donnees():
    """Génère, nettoie, et fusionne les données fictives."""
    
    COLLABORATEURS = [
        'Adil', 'Anouar', 'Badr', 'Bahia', 'Fatima', 'Hassan', 'Hicham', 'Houda', 
        'Ilham', 'Ismail', 'Jamila', 'Karim', 'Khadija', 'Laila', 'Malak', 
        'Marouane', 'Mehdi', 'Meryem', 'Mourad', 'Nabil', 'Naima', 'Sara', 'Youssef'
    ]
    LIGNES = ['ligne 1', 'ligne 2', 'ligne 3', 'ligne 4', 'ligne 5', 'ligne 6', 
              'ligne 7', 'ligne 8', 'ligne 9', 'ligne 10', 'ligne 11', 'ligne 12']
    ETATS = ['Collaborateur actif', 'En formation']
    ARTICLES = ['A', 'B', 'C', 'D', 'E']

    COMPETENCES_MAINTENANCE = [
        'Enfilage du fil', 'Démarrage de la machine', 'Signalement des anomalies',
        'Réglage de la tension du fil', 'Entretien préventif de la machine',
        'Résolution des pannes mineures', 'Competences techniques'
    ]
    COMPETENCES_PRODUCTION = [
        'Rapidité d\'exécution', 'Respect des cadences', 'Gestion des interruptions',
        'Optimisation des flux de travail', 'Respect des délais d\'expédition', 
        'Competences techniques'
    ]
    COMPETENCES_QUALITE = [
        'Finition des pièces', 'Précision des coutures', 'Respect des consignes techniques',
        'Contrôle des défauts de surface', 'Uniformité des assemblages',
        'Conformité aux normes d\'étiquetage', 'Competences techniques'
    ]
    COMPETENCES_METHODE = [
        'Respect de l\'ordre des étapes', 'Application correcte des points de couture',
        'Utilisation des outils prescrits', 'Respect des ajustements techniques',
        'Reproduction fidèle des démonstrations', 'Vérification des pièces en cours',
        'Competences techniques'
    ]

    dates_continues = pd.date_range(start='2025-06-01', end='2025-11-05')
    DATES_EVAL = dates_continues.to_list()

    ID_COLS = [
        'Sélectionnez la date de l\'évaluation.', 'Ligne designer', 'Etat du personnel',
        'Article', 'Polyvalence', 'Collaborateur'
    ]

    def generer_donnees_brutes(categorie, liste_competences, nb_evals=150):
        donnees = []
        for _ in range(nb_evals):
            ligne = {
                'Sélectionnez la date de l\'évaluation.': random.choice(DATES_EVAL),
                'Ligne designer': random.choice(LIGNES),
                'Etat du personnel': random.choice(ETATS),
                'Article': random.choice(ARTICLES),
                'Collaborateur': random.choice(COLLABORATEURS),
                'Polyvalence': f"{random.randint(1,3)} taches"
            }
            for comp in liste_competences:
                note_base = random.randint(1, 5)
                jour_semaine = ligne['Sélectionnez la date de l\'évaluation.'].weekday()
                if jour_semaine >= 5: # Weekend
                    note_base = max(1, note_base - random.uniform(0, 1))
                ligne[comp] = note_base
            donnees.append(ligne)
            
        df = pd.DataFrame(donnees)
        return df, categorie

    df_maint_brut, cat_maint = generer_donnees_brutes("Maintenance", COMPETENCES_MAINTENANCE)
    df_prod_brut, cat_prod = generer_donnees_brutes("Production", COMPETENCES_PRODUCTION)
    df_qual_brut, cat_qual = generer_donnees_brutes("Qualité", COMPETENCES_QUALITE)
    df_meth_brut, cat_meth = generer_donnees_brutes("Méthode", COMPETENCES_METHODE)

    def nettoyer_et_depivoter(df_brut, id_cols, categorie):
        df_melted = df_brut.melt(
            id_vars=id_cols,
            var_name="Compétence",
            value_name="Note"
        )
        df_melted['Categorie'] = categorie
        return df_melted

    df_maint_propre = nettoyer_et_depivoter(df_maint_brut, ID_COLS, cat_maint)
    df_prod_propre = nettoyer_et_depivoter(df_prod_brut, ID_COLS, cat_prod)
    df_qual_propre = nettoyer_et_depivoter(df_qual_brut, ID_COLS, cat_qual)
    df_meth_propre = nettoyer_et_depivoter(df_meth_brut, ID_COLS, cat_meth)

    df_complet = pd.concat(
        [df_maint_propre, df_prod_propre, df_qual_propre, df_meth_propre], 
        ignore_index=True
    )
    
    return df_complet

# --- 3. LOGIQUE DU MODÈLE (Identique) ---
def entrainer_modele(df_complet):
    """Prépare les données et entraîne un modèle RandomForestRegressor."""
    colonne_date = "Sélectionnez la date de l'évaluation."
    
    df_complet['Note'] = pd.to_numeric(df_complet['Note'], errors='coerce')
    df_complet[colonne_date] = pd.to_datetime(df_complet[colonne_date], errors='coerce')
    df_complet = df_complet.dropna(subset=['Note', colonne_date])
    
    # --- DÉBUT DE LA MODIFICATION ---
    # Nous devons inclure la composition des catégories comme "feature"
    
    # 1. Calculer la composition des catégories par jour
    df_composition = df_complet.groupby([colonne_date, 'Categorie']).size().unstack(fill_value=0)
    # Normaliser pour obtenir des pourcentages (ex: 0.25, 0.30...)
    df_composition_pct = df_composition.apply(lambda x: x / x.sum(), axis=1)
    df_composition_pct.columns = [f"pct_{col}" for col in df_composition_pct.columns] # Renomme en 'pct_Maintenance', etc.

    # 2. Agréger les notes moyennes par jour (comme avant)
    df_agg = df_complet.groupby(colonne_date)['Note'].mean().reset_index()
    
    # 3. Fusionner les notes moyennes avec la composition
    df_agg = pd.merge(df_agg, df_composition_pct, left_on=colonne_date, right_index=True, how='left')
    df_agg = df_agg.fillna(0) # Remplir les jours sans données (si applicable)
    
    # --- FIN DE LA MODIFICATION ---
    
    df_agg = df_agg.sort_values(colonne_date)
    
    df_agg['jours_total'] = (df_agg[colonne_date] - df_agg[colonne_date].min()).dt.days
    df_agg['jour_de_la_semaine'] = df_agg[colonne_date].dt.dayofweek
    df_agg['jour_du_mois'] = df_agg[colonne_date].dt.day
    df_agg['mois'] = df_agg[colonne_date].dt.month
    df_agg['jour_de_l_annee'] = df_agg[colonne_date].dt.dayofyear
    
    # --- DÉBUT DE LA MODIFICATION : AJOUT DES NOUVELLES FEATURES ---
    temporal_features = ['jours_total', 'jour_de_la_semaine', 'jour_du_mois', 'mois', 'jour_de_l_annee']
    composition_features = [col for col in df_agg.columns if col.startswith('pct_')]
    features = temporal_features + composition_features
    # --- FIN DE LA MODIFICATION ---
    
    X = df_agg[features]
    y = df_agg['Note']
    
    model = RandomForestRegressor(
        n_estimators=100, 
        random_state=42, 
        min_samples_leaf=2, 
        oob_score=True
    )
    model.fit(X, y)
    
    try:
        residus_oob = y - model.oob_prediction_
        std_error = np.std(residus_oob)
    except Exception:
        residus_train = y - model.predict(X)
        std_error = np.std(residus_train)
    
    # NOUVEAU : Retourner également l'importance des features
    importances = model.feature_importances_
    
    return model, df_agg, features, std_error, importances

def predire_rf(model, df_historique, features, std_error, jours_a_predire):
    """Génère les prédictions futures avec un modèle scikit-learn."""
    
    colonne_date = 'Sélectionnez la date de l\'évaluation.'
    
    derniere_date = df_historique[colonne_date].max()
    dernier_jour_total = df_historique['jours_total'].max()
    
    dates_futures = pd.date_range(start=derniere_date + timedelta(days=1), periods=jours_a_predire, freq='D')
    df_futur = pd.DataFrame({'Date': dates_futures})
    
    df_futur['jours_total'] = np.arange(dernier_jour_total + 1, dernier_jour_total + jours_a_predire + 1)
    df_futur['jour_de_la_semaine'] = df_futur['Date'].dt.dayofweek
    df_futur['jour_du_mois'] = df_futur['Date'].dt.day
    df_futur['mois'] = df_futur['Date'].dt.month
    df_futur['jour_de_l_annee'] = df_futur['Date'].dt.dayofyear
    
    # --- DÉBUT DE LA MODIFICATION : GESTION DES NOUVELLES FEATURES ---
    # Pour le futur, nous ne connaissons pas la composition,
    # nous utilisons donc la moyenne de l'historique comme estimation.
    composition_features = [col for col in model.feature_names_in_ if col.startswith('pct_')]
    
    if composition_features: # S'assurer qu'il y a des features de composition
        avg_composition = df_historique[composition_features].mean()
        
        # Appliquer cette composition moyenne aux jours futurs
        for col in composition_features:
            df_futur[col] = avg_composition[col]
            
    # S'assurer que l'ordre des colonnes est le même que celui de l'entraînement
    X_futur = df_futur[features] 
    # --- FIN DE LA MODIFICATION ---
    
    predictions = model.predict(X_futur)
    
    df_pred = pd.DataFrame({
        'Date': dates_futures,
        'Prédiction': predictions,
        'Limite_basse': predictions - 1.96 * std_error,
        'Limite_haute': predictions + 1.96 * std_error
    })
    
    df_hist_plot = df_historique.rename(columns={
        colonne_date: 'Date', 
        'Note': 'Note_hist'
    })
    
    return df_pred, df_hist_plot

# --- NOUVELLE FONCTION : Générateur de graphiques à barres ---
def generer_barplot_base64(data, title, xlabel, ylabel):
    """Crée un graphique à barres Matplotlib et le convertit en Base64."""
    if data.empty:
        return None
    
    fig, ax = plt.subplots(figsize=(10, max(5, len(data) * 0.4)))
    ax.barh(data.index, data.values, color='#0068c9') # Graphique à barres horizontales
    
    # Inverser l'axe y pour que le meilleur soit en haut
    ax.invert_yaxis() 
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(ylabel, fontsize=12)
    ax.set_ylabel(xlabel, fontsize=12)
    ax.grid(True, alpha=0.3, axis='x')
    
    # Ajouter les labels de valeur au bout des barres
    for i, v in enumerate(data.values):
        ax.text(v + 0.02, i, f"{v:.2f}", color='black', va='center')
        
    plt.tight_layout()
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 4. LE SERVEUR FLASK ---
app = Flask(__name__)

# Mise en cache globale des données et du modèle pour la performance
print("Chargement et entraînement du modèle RandomForest au démarrage...")
DF_COMPLET = charger_et_nettoyer_donnees()
# NOUVEAU : Stocker les importances des features
MODELE, DF_HISTORIQUE, FEATURES, STD_ERROR, FEATURE_IMPORTANCES = entrainer_modele(DF_COMPLET)
ALL_CATEGORIES = DF_COMPLET['Categorie'].unique().tolist()
ALL_LIGNES = sorted(DF_COMPLET['Ligne designer'].unique())
print("✅ Modèle prêt !")

@app.route('/')
def index():
    # --- Collecte des paramètres de l'URL (le "request") ---
    jours_a_predire = request.args.get('jours_a_predire', 14, type=int)
    selected_categories = request.args.getlist('categories')
    selected_lignes = request.args.getlist('lignes') # NOUVEAU

    # --- Exécution de la logique ---
    if not selected_categories:
        selected_categories = ALL_CATEGORIES
    if not selected_lignes:
        selected_lignes = ALL_LIGNES
        
    # NOUVEAU : Filtrage combiné
    df_filtre = DF_COMPLET[
        (DF_COMPLET['Categorie'].isin(selected_categories)) &
        (DF_COMPLET['Ligne designer'].isin(selected_lignes))
    ]
    
    # --- Génération des prévisions avec RandomForest ---
    df_pred, df_hist_plot = predire_rf(MODELE, DF_HISTORIQUE, FEATURES, STD_ERROR, jours_a_predire)

    # --- Calcul des KPIs ---
    note_actuelle = f"{DF_HISTORIQUE['Note'].iloc[-1]:.2f}"
    pred_j7 = f"{df_pred['Prédiction'].iloc[min(6, len(df_pred)-1)]:.2f}"
    trend_start = df_pred['Prédiction'].iloc[0]
    trend_end = df_pred['Prédiction'].iloc[-1]
    tendance_val = (trend_end - trend_start) / jours_a_predire
    tendance_emoji = "📈" if tendance_val > 0 else "📉"

    # --- Calcul des graphiques d'exploration ---
    if not df_filtre.empty:
        moyennes_collab = df_filtre.groupby('Collaborateur')['Note'].mean().sort_values(ascending=False)
        top_5 = moyennes_collab.head(5).reset_index().to_dict('records')
        bottom_5 = moyennes_collab.tail(5).reset_index().to_dict('records')
        
        # NOUVEAU : Génération des graphiques
        moyennes_par_categorie = df_filtre.groupby('Categorie')['Note'].mean().sort_values(ascending=False)
        moyennes_par_lignes = df_filtre.groupby('Ligne designer')['Note'].mean().sort_values(ascending=False)
        
        plot_cat_base64 = generer_barplot_base64(moyennes_par_categorie, 'Moyenne par Secteur', 'Secteur', 'Note Moyenne')
        plot_ligne_base64 = generer_barplot_base64(moyennes_par_lignes, 'Moyenne par Ligne', 'Ligne', 'Note Moyenne')

    else:
        top_5, bottom_5 = [], []
        plot_cat_base64, plot_ligne_base64 = None, None

    # --- NOUVEAU : Génération du graphique des Key Influencers ---
    try:
        # Traduction des noms techniques des features
        feature_name_map = {
            'jours_total': 'Tendance (Jours)',
            'jour_de_la_semaine': 'Jour de la semaine',
            'jour_du_mois': 'Jour du mois',
            'mois': 'Mois de l\'année',
            'jour_de_l_annee': 'Jour de l\'année',
            'pct_Maintenance': 'Influence Maintenance', # NOUVEAU
            'pct_Production': 'Influence Production',   # NOUVEAU
            'pct_Qualité': 'Influence Qualité',         # NOUVEAU
            'pct_Méthode': 'Influence Méthode'          # NOUVEAU
        }
        importances_series = pd.Series(FEATURE_IMPORTANCES, index=FEATURES)
        importances_series.index = importances_series.index.map(lambda x: feature_name_map.get(x, x))
        importances_series = importances_series.sort_values(ascending=False)
        
        plot_influencers_base64 = generer_barplot_base64(
            importances_series, 
            'Importance des Facteurs Clés', 
            'Facteur', 
            'Importance (Score)'
        )
    except Exception as e:
        print(f"Erreur lors de la génération du graphique des influenceurs : {e}")
        plot_influencers_base64 = None

    # --- Génération du Graphique de Prévision (Matplotlib) ---
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_hist_plot['Date'], df_hist_plot['Note_hist'], 'o-', label='Données historiques', color='blue', linewidth=2, markersize=4)
    ax.plot(df_pred['Date'], df_pred['Prédiction'], 's-', label='Prédictions', color='red', linewidth=2, markersize=4)
    ax.fill_between(df_pred['Date'], 
                    df_pred['Limite_basse'], 
                    df_pred['Limite_haute'], 
                    alpha=0.2, color='red', label='Intervalle de confiance 95%')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Note moyenne', fontsize=12)
    ax.set_title('Évolution et Prévision des Notes (Modèle RandomForest)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    df_pred_table = df_pred.to_dict('records') # Convertir en dict pour le template

    # --- Rendu de la page ---
    return render_template_string(
        HTML_TEMPLATE,
        jours_a_predire=jours_a_predire,
        all_categories=ALL_CATEGORIES,
        selected_categories=selected_categories,
        all_lignes=ALL_LIGNES, # NOUVEAU
        selected_lignes=selected_lignes, # NOUVEAU
        note_actuelle=note_actuelle,
        pred_j7=pred_j7,
        tendance_val=tendance_val,
        tendance_emoji=tendance_emoji,
        predictions=df_pred_table, # MIS A JOUR
        plot_base64=plot_base64,
        plot_cat_base64=plot_cat_base64, # NOUVEAU
        plot_ligne_base64=plot_ligne_base64, # NOUVEAU
        plot_influencers_base64=plot_influencers_base64, # NOUVEAU
        top_5=top_5,
        bottom_5=bottom_5
    )

# --- 5. Lancement de l'application ---
if __name__ == '__main__':
    print("--- Démarrage du serveur Flask ---")
    print("Ouvrez http://127.0.0.1:5000 dans votre navigateur.")
    app.run(debug=True, port=5000)