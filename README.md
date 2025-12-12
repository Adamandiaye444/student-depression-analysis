# Application de Recherche Flask + MongoDB Atlas

## 📋 Description

Application web Flask permettant de rechercher des documents dans une collection MongoDB Atlas avec :
- **Recherche en temps réel** avec autocomplétion
- **Affichage des 10 premiers documents** si la recherche est vide
- **Interface moderne et responsive**

## 🚀 Installation

### Prérequis

- Python 3.7 ou supérieur
- Compte MongoDB Atlas avec une base de données configurée
- pip (gestionnaire de packages Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

2. **Créer un environnement virtuel (recommandé)**
   
   Sur macOS avec Homebrew, il est nécessaire d'utiliser un environnement virtuel :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   **Note** : À chaque nouvelle session terminal, vous devrez réactiver l'environnement virtuel avec :
   ```bash
   source venv/bin/activate
   ```

3. **Installer les dépendances Python**
   ```bash
   pip install -r requirements.txt
   ```
   
   Ou si `pip` n'est pas disponible :
   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. **Configurer la connexion MongoDB**
   
   Le fichier `app.py` contient déjà les informations de connexion :
   ```python
   MONGODB_URI = "mongodb+srv://adamandiaye1_db_user:tCLjHu1rz8xtwtds@cluster0.ugjeorv.mongodb.net/..."
   DATABASE_NAME = "adamandiaye1_db"
   COLLECTION_NAME = "movies"  # À modifier selon votre collection
   ```
   
  
5. **Adapter les champs de recherche**
   
   Dans `app.py`, la fonction `search()` recherche dans les champs :
   - `title`
   - `titre`
   - `name`
   
   Si votre collection utilise d'autres noms de champs, modifiez la fonction `search()` et `autocomplete()`.

6. **Adapter l'affichage des résultats**
   
   Dans `static/js/search.js`, la fonction `displayResults()` extrait les champs suivants :
   - Titre : `title`, `titre`, `name`
   - Année : `year`, `annee`, `annee_sortie`, `release_year`
   - Réalisateur : `director`, `realisateur`, `directeur`
   - Genre : `genre`, `genres`, `type`
   - Résumé : `plot`, `resume`, `description`, `overview`, `synopsis`
   
   Adaptez ces noms selon votre structure de données.

## ▶️ Lancement de l'application

### Méthode 1 : Script automatique (
```bash
./run.sh
```
Ce script active automatiquement l'environnement virtuel et lance l'application.

### Méthode 2 : Lancement manuel
1. **Activer l'environnement virtuel** (si vous utilisez un venv)
   ```bash
   source venv/bin/activate
   ```

2. **Démarrer le serveur Flask**
   ```bash
   python app.py
   ```
   
   Ou si `python` n'est pas disponible :
   ```bash
   python3 app.py
   ```

2. **Ouvrir dans le navigateur**
   ```
   http://localhost:5001
   ```


## 🎯 Fonctionnalités

### 📝 Opérations CRUD Complètes ⭐ NOUVEAU

L'application permet maintenant de **gérer complètement** les étudiants :

- **📖 READ (Lire)** : Recherche et affichage des étudiants
- **✏️ UPDATE (Mettre à jour)** : Modifier les informations d'un étudiant
- **🗑️ DELETE (Supprimer)** : Supprimer un étudiant de la base de données
- **➕ CREATE (Créer)** : API disponible pour créer de nouveaux étudiants

**Voir CRUD_GUIDE.md pour le guide complet**

### 🔍 Deux Modes de Recherche

#### 1. **Recherche Globale** (Simple)
Tapez simplement votre terme : `25`, `Ahmedabad`, `Healthy`
- Cherche dans TOUS les champs
- Rapide et simple

#### 2. **Recherche Ciblée** (Avec Préfixe) ⭐ NOUVEAU
Utilisez la syntaxe `champ:valeur` pour une recherche précise :
- `age:25` → Seulement les étudiants de 25 ans
- `id:166` → Seulement l'étudiant ID 166
- `ville:Ahmedabad` → Seulement les étudiants d'Ahmedabad
- `stress:5` → Seulement stress financier de 5
- `cgpa:7.5` → Seulement moyenne de 7.5


### Cas a) Barre d'espace
- Appuyez sur **Espace** dans un champ vide → Affiche les **10 premiers étudiants**

### Cas b) Autocomplétion
- Pendant la saisie, une **liste de suggestions** apparaît automatiquement
- Format : "ID X - Y ans - Ville - Profession (Degré)"
- Cliquer sur une suggestion lance la recherche

### Affichage des résultats
- Chaque résultat affiche **15 champs** :
  - ID, Genre, Âge, Ville, Profession
  - Degré, Moyenne cumulative, Pression académique
  - Satisfaction des études, Durée du sommeil
  - Habitudes alimentaires, Stress financier
  - Dépression, Pensées suicidaires, Antécédents familiaux

## 📁 Structure du projet

```
final/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── README.md             # Ce fichier
├── templates/
│   └── index.html        # Template HTML principal
└── static/
    ├── css/
    │   └── style.css     # Styles CSS
    └── js/
        └── search.js     # Logique JavaScript de recherche
```

## 🔧 Configuration

### Modifier le nom de la collection

Dans `app.py`, ligne ~30 :
```python
COLLECTION_NAME = "votre_collection"  # Remplacez "movies" par votre nom de collection
```

### Modifier les champs de recherche

Dans `app.py`, fonction `search()`, adaptez les champs selon votre structure :
```python
search_filter = {
    '$or': [
        {'votre_champ_titre': {'$regex': query, '$options': 'i'}},
        # Ajoutez d'autres champs si nécessaire
    ]
}
```

## 🐛 Dépannage

### Erreur de connexion MongoDB
- Vérifiez que votre IP est autorisée dans MongoDB Atlas (Network Access)
- Vérifiez que le nom d'utilisateur et le mot de passe sont corrects
- Vérifiez que le nom de la base de données et de la collection sont corrects

### Aucun résultat affiché
- Vérifiez que votre collection contient des documents
- Vérifiez que les noms de champs dans le code correspondent à votre structure de données

### L'autocomplétion ne fonctionne pas
- Ouvrez la console du navigateur (F12) pour voir les erreurs JavaScript
- Vérifiez que le serveur Flask est bien démarré
- Vérifiez que les routes `/api/autocomplete` et `/api/search` fonctionnent

## 📝 Notes

- Tous les fichiers contiennent des **commentaires détaillés** expliquant chaque section du code.
- Le code est organisé de manière modulaire pour faciliter la maintenance.
- L'interface est **responsive** et fonctionne sur mobile, tablette et desktop.

## 👨‍💻 Auteur

Application créée pour le projet SDD1003.

