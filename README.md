# Application d'Analyse de Dépression Étudiante avec Machine Learning

Application web Flask avancée permettant la recherche, l'analyse et la prédiction des risques de dépression chez les étudiants à l'aide de Machine Learning et d'analyses statistiques.

---

## Description

Cette application combine plusieurs technologies pour offrir une plateforme complète d'analyse :

- **Recherche classique** : Filtrage par critères multiples
- **Recherche vectorielle ML** : Recherche sémantique utilisant des embeddings
- **Analyse statistique** : Tests de normalité (EDF), distributions, visualisations
- **Prédictions ML** : Random Forest, Régression Linéaire, K-Means Clustering
- **Gestion CRUD complète** : Création, lecture, mise à jour, suppression

---

## Fonctionnalités Principales

### Trois Modes de Recherche

#### 1. Recherche Classique
- Recherche globale dans tous les champs
- Recherche ciblée avec syntaxe `champ:valeur`
  - Exemples : `age:25`, `ville:Ahmedabad`, `stress:5`
- Autocomplétion en temps réel
- Affichage des 10 premiers résultats si recherche vide

#### 2. Recherche Vectorielle ML (NOUVEAU)
- Recherche sémantique basée sur le sens
- Utilise SentenceTransformers (modèle all-MiniLM-L6-v2)
- Exemples de requêtes naturelles :
  - "étudiants stressés avec mauvaises notes"
  - "personnes dépressives dormant peu"
  - "jeunes avec pression académique élevée"

#### 3. Analyse Statistique (EDF) (NOUVEAU)
- Fonction de Distribution Empirique (EDF)
- Tests de normalité (Kolmogorov-Smirnov)
- Comparaison avec distributions théoriques :
  - Distribution normale
  - Distribution exponentielle
- Visualisations :
  - Courbes EDF vs CDF théorique
  - Histogrammes avec densité théorique
  - Q-Q plots

### Machine Learning Intégré

Pour chaque résultat de recherche vectorielle, l'application génère automatiquement :

1. **Random Forest (Classification)**
   - Prédiction : Avec/Sans dépression
   - Confiance : 0-100%

2. **Régression Linéaire**
   - Score de risque : 0-10
   - Plus le score est élevé, plus le risque est important

3. **K-Means Clustering**
   - Cluster 0 ou 1
   - Regroupe les étudiants aux profils similaires

### Visualisations Automatiques

- Graphiques de probabilité de dépression
- Graphiques de score de risque
- Graphiques de clustering
- Analyse EDF avec courbes théoriques
- Q-Q plots pour tests de normalité

### Gestion CRUD Complète

- CREATE : Ajouter de nouveaux étudiants
- READ : Rechercher et consulter les étudiants
- UPDATE : Modifier les informations
- DELETE : Supprimer des étudiants

---

## Installation

### Prérequis
- Python 3.13+
- MongoDB Atlas (déjà configuré)
- pip (gestionnaire de packages Python)

### 1. Cloner le projet
```bash
git clone https://github.com/Adamandiaye444/student-depression-analysis.git
cd student-depression-analysis
```

### 2. Créer un environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
```

Note : À chaque nouvelle session, réactivez l'environnement :
```bash
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
# Dépendances principales
pip install -r requirements.txt

# Dépendances ML (optionnelles mais recommandées)
pip install -r requirements_ml.txt
```

### 4. Configuration MongoDB

L'application est déjà configurée pour se connecter à MongoDB Atlas.
Les identifiants sont inclus dans `app.py` pour faciliter l'évaluation.

**Base de données :** `student_depression_db`  
**Collection :** `students`  
**Nombre d'étudiants :** ~10,000

Note de sécurité : Ces identifiants sont partagés uniquement pour l'évaluation académique.

---

## Lancement de l'Application

### Méthode 1 : Script automatique (recommandé)
```bash
./run.sh
```

Ce script active automatiquement l'environnement virtuel et lance l'application.

### Méthode 2 : Lancement manuel
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Lancer l'application
python3 app.py
```

### 3. Accéder à l'application

Ouvrez votre navigateur : **http://localhost:5001**

---

## Guide d'Utilisation

### Recherche Classique

1. Allez dans l'onglet "Recherche Classique"
2. **Recherche globale** : Tapez simplement un terme (ex: `25`, `Ahmedabad`)
3. **Recherche ciblée** : Utilisez `champ:valeur` (ex: `age:25`, `ville:Mumbai`)
4. Appuyez sur Espace dans un champ vide pour voir les 10 premiers étudiants

### Recherche Vectorielle ML

1. Allez dans "Recherche Vectorielle"
2. Tapez une requête en langage naturel :
   - "étudiants stressés avec mauvaises notes"
   - "personnes dépressives"
   - "étudiants avec problèmes de sommeil"
3. Attendez 1-2 minutes au premier lancement (chargement du modèle ML)
4. Consultez les prédictions ML et visualisations générées

### Analyse Statistique (EDF)

1. Allez dans "Analyse Statistique"
2. Sélectionnez une variable (age, depression, etc.)
3. Choisissez une distribution théorique (normale, exponentielle)
4. Cliquez sur "Analyser"
5. Interprétez les résultats :
   - KS < 0.05 : Excellent fit
   - KS > 0.15 : Mauvais fit

### Gestion CRUD

- **Modifier** : Cliquez sur le bouton d'édition à côté d'un étudiant
- **Supprimer** : Cliquez sur le bouton de suppression (confirmation demandée)
- **Créer** : Utilisez l'API (voir documentation complète)

---

## Interprétation des Résultats ML

### Random Forest
- **Prédiction** : "Avec Dépression" ou "Sans Dépression"
- **Confiance** : 0-100% (attention si 100% = possible surapprentissage)

### Régression Linéaire
- **Score de risque** : 0-10
  - 0-3 : Risque faible
  - 4-6 : Risque modéré
  - 7-10 : Risque élevé

### K-Means Clustering
- **Cluster 0** : Premier groupe de profils similaires
- **Cluster 1** : Deuxième groupe de profils similaires

### Analyse EDF
- **Statistique KS** : Distance entre données réelles et théoriques
  - < 0.05 : Excellent
  - 0.05-0.10 : Bon
  - 0.10-0.20 : Moyen
  - > 0.20 : Mauvais
- **p-value** : Significativité statistique (< 0.05 = rejet de l'hypothèse)

---

## Technologies Utilisées

### Backend
- **Flask** : Framework web Python
- **PyMongo** : Connexion MongoDB
- **Pandas, NumPy** : Manipulation de données

### Machine Learning
- **scikit-learn** : Random Forest, Linear Regression, K-Means
- **sentence-transformers** : Embeddings sémantiques (all-MiniLM-L6-v2)
- **SciPy** : Tests statistiques (Kolmogorov-Smirnov)

### Visualisation
- **Matplotlib** : Graphiques ML
- **Seaborn** : Visualisations statistiques avancées

### Frontend
- HTML5, CSS3, JavaScript
- Design responsive et moderne

---

## Structure du Projet
```
student-depression-analysis/
├── app.py                      # Application Flask principale (1800+ lignes)
├── student_vector_ml.py        # Système de recherche vectorielle ML
├── statistical_analysis.py    # Analyse statistique (EDF, tests)
├── templates/
│   └── index.html             # Interface utilisateur complète
├── static/
│   ├── css/style.css          # Styles modernes
│   ├── js/search.js           # Logique frontend
│   ├── ml_images/             # Visualisations ML générées
│   └── statistical_analysis/  # Graphiques EDF
├── requirements.txt           # Dépendances principales
├── requirements_ml.txt        # Dépendances ML
└── run.sh                     # Script de lancement automatique
```

---

## Dépannage

### L'application démarre lentement (1ère fois)
Normal : Le premier lancement de la recherche vectorielle prend 1-2 minutes.
- Chargement du modèle SentenceTransformer (100+ MB)
- Génération des embeddings pour 10,000 étudiants
- Les lancements suivants sont instantanés (lazy loading)

### Port 5001 déjà utilisé
```bash
pkill -f "python.*app.py"
python3 app.py
```

### Erreur de connexion MongoDB
- Vérifiez votre connexion internet
- L'URI MongoDB Atlas est dans `app.py` ligne ~70

### Aucun résultat dans la recherche vectorielle
- Attendez la fin du chargement initial (1-2 min)
- Vérifiez la console du navigateur (F12) pour les erreurs
- Assurez-vous que `requirements_ml.txt` est installé

### Graphiques EDF ne s'affichent pas
- Vérifiez que Matplotlib est installé : `pip install matplotlib seaborn`
- Les images sont sauvegardées dans `static/statistical_analysis/`

---

## Champs Disponibles pour la Recherche

Chaque étudiant possède 15 champs :

1. **id** : Identifiant unique
2. **gender** : Genre (Male/Female)
3. **age** : Âge (18-50 ans)
4. **city** : Ville de résidence
5. **profession** : Profession actuelle
6. **academic_pressure** : Pression académique (1-5)
7. **cgpa** : Moyenne cumulative (0-10)
8. **study_satisfaction** : Satisfaction des études (1-5)
9. **sleep_duration** : Durée du sommeil (heures)
10. **dietary_habits** : Habitudes alimentaires
11. **degree** : Degré académique
12. **suicidal_thoughts** : Pensées suicidaires (Yes/No)
13. **work_study_hours** : Heures de travail/étude
14. **financial_stress** : Stress financier (1-5)
15. **family_history** : Antécédents familiaux de problèmes mentaux (Yes/No)

---

## Sécurité et Confidentialité

- Les identifiants MongoDB sont inclus uniquement pour l'évaluation
- En production, ils seraient stockés dans des variables d'environnement
- L'accès sera révoqué après l'évaluation du projet
- Les données étudiantes sont anonymisées (pas de noms réels)

---

## Documentation Complémentaire

- **Lazy Loading** : Le système ML ne se charge qu'à la première utilisation pour accélérer le démarrage
- **Tests statistiques** : Kolmogorov-Smirnov pour vérifier la normalité des distributions
- **Embeddings** : Vecteurs de 384 dimensions générés par SentenceTransformer

---

## Auteur

**Adama Ndiaye**  
Projet académique SDD1003 - Analyse de données avec Machine Learning  
GitHub: [Adamandiaye444](https://github.com/Adamandiaye444)

---

## Licence

Ce projet est développé à des fins académiques.

---

## Remerciements

- MongoDB Atlas pour l'hébergement de la base de données
- Sentence-Transformers pour les modèles d'embeddings
- scikit-learn pour les algorithmes de Machine Learning
- La communauté Flask pour le framework web
