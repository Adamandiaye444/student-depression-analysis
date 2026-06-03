# Analyse de la dépression étudiante — Flask + MongoDB + Machine Learning

Application web pour **rechercher**, **analyser** et **prédire** le risque de dépression chez les étudiants.  
Données hébergées sur **MongoDB Atlas**, interface **Flask**, modèles **scikit-learn** et recherche sémantique **SentenceTransformers**.

**Dépôt GitHub :** https://github.com/Adamandiaye444/student-depression-analysis

---

## En bref

| Élément | Détail |
|--------|--------|
| URL locale | http://localhost:5001 |
| Base MongoDB | `student_depression_db` |
| Collection | `students` (~10 000 documents) |
| Cluster Atlas | `cluster0.9uaz8kt.mongodb.net` |
| Python | 3.13+ recommandé |

---

## Ce que fait l'application

1. **Recherche classique** — filtre par mot-clé ou `champ:valeur` (ex. `age:22`, `city:Mumbai`)
2. **Recherche vectorielle (ML)** — requêtes en langage naturel + prédictions automatiques
3. **Analyse statistique (EDF)** — tests de normalité, histogrammes, Q-Q plots
4. **CRUD** — créer, lire, modifier et supprimer des fiches étudiants

### Modèles ML (recherche vectorielle)

- **Random Forest** — dépression oui/non + confiance
- **Régression linéaire** — score de risque (0–10)
- **K-Means** — regroupement par profils similaires

---

## Démarrage rapide (5 minutes)

### 1. Cloner le projet

```bash
git clone https://github.com/Adamandiaye444/student-depression-analysis.git
cd student-depression-analysis
```

### 2. Environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate    # macOS / Linux
```

> **Important :** utilisez toujours `venv/bin/python3`, pas le `python3` système.

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
pip install -r requirements_ml.txt
```

### 4. Configurer MongoDB (fichier `.env`)

```bash
cp .env.example .env
```

Ouvrez `.env` et remplacez `VOTRE_MOT_DE_PASSE` par le mot de passe MongoDB Atlas :

```env
MONGODB_URI=mongodb+srv://mamyadama123_db_user:VOTRE_MOT_DE_PASSE@cluster0.9uaz8kt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=student_depression_db
COLLECTION_NAME=students
```

Vérifiez la connexion :

```bash
venv/bin/python3 diagnose.py
```

Vous devez voir : `✓ MongoDB OK`.

### 5. Lancer l'application

**Option A — script automatique**

```bash
chmod +x run.sh
./run.sh
```

**Option B — commande directe**

```bash
export PYTHONUNBUFFERED=1
venv/bin/python3 app.py
```

Ouvrez le navigateur : **http://localhost:5001**

---

## Guide d'utilisation

### Recherche classique

- Tapez un terme : `Ahmedabad`, `25`, `Male`
- Ou une recherche ciblée : `age:25`, `city:Mumbai`, `stress:5`
- Champ vide + **Espace** → affiche les 10 premiers étudiants

### Recherche vectorielle (ML)

Exemples de requêtes :

- `étudiants stressés avec mauvaises notes`
- `personnes dépressives dormant peu`
- `jeunes avec forte pression académique`

> Au **premier** lancement, le modèle peut mettre **1 à 2 minutes** à charger (SentenceTransformer + embeddings).

### Analyse statistique (EDF)

1. Choisir une variable (`age`, `depression`, etc.)
2. Choisir une distribution (normale ou exponentielle)
3. Cliquer sur **Analyser**
4. Lire la statistique KS : plus la valeur est basse, meilleur est l'ajustement

### Interprétation des scores ML

| Modèle | Résultat | Signification |
|--------|----------|---------------|
| Random Forest | Confiance % | Probabilité de la classe prédite |
| Régression | 0–3 / 4–6 / 7–10 | Risque faible / modéré / élevé |
| K-Means | Cluster 0 ou 1 | Deux profils d'étudiants similaires |

---

## Structure du projet

```
student-depression-analysis/
├── app.py                    # Application Flask principale
├── config.py                 # Charge .env (MongoDB)
├── student_vector_ml.py      # Recherche vectorielle + ML
├── statistical_analysis.py   # Analyses EDF
├── diagnose.py               # Test MongoDB + chargement app
├── .env.example              # Modèle de configuration (à copier)
├── requirements.txt          # Dépendances Flask / MongoDB
├── requirements_ml.txt       # Dépendances Machine Learning
├── run.sh                    # Lancement automatique
├── templates/index.html      # Interface web
└── static/                   # CSS, JS, graphiques générés
```

---

## Dépannage

### `ModuleNotFoundError: No module named 'flask'`

Vous utilisez le mauvais Python. Lancez :

```bash
venv/bin/python3 app.py
```

### Erreur `MONGODB_URI manquant`

Créez le fichier `.env` à partir de `.env.example` (voir étape 4).

### Erreur matplotlib / fichiers `._*` (clé USB Mac)

Sur un disque externe, supprimez les métadonnées macOS :

```bash
dot_clean -m venv
```

### Port 5001 déjà utilisé

```bash
pkill -f "python.*app.py"
venv/bin/python3 app.py
```

### Recherche vectorielle sans résultat

- Attendre la fin du premier chargement ML
- Vérifier : `pip install -r requirements_ml.txt`
- Console navigateur (F12) pour les erreurs JavaScript

---

## Sécurité

- Le fichier **`.env`** contient le mot de passe MongoDB : il est **ignoré par Git** (ne jamais le committer).
- Utilisez **`.env.example`** comme modèle sans mot de passe réel.
- Révoquez ou changez le mot de passe Atlas si il a été exposé publiquement.

---

## Technologies

- **Backend :** Flask, PyMongo, Pandas, NumPy
- **ML :** scikit-learn, sentence-transformers, SciPy
- **Stats / graphiques :** Matplotlib, Seaborn
- **Frontend :** HTML, CSS, JavaScript

---

## Auteur

**Adama Ndiaye** — Projet SDD1003  
GitHub : [Adamandiaye444](https://github.com/Adamandiaye444)

Projet à des fins **académiques**.
