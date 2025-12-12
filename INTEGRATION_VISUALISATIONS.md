# 📊 Documentation : Intégration des Visualisations ML

## Vue d'ensemble

Les visualisations (graphiques) sont intégrées dans l'application en **3 étapes principales** :

1. **Génération** (Backend Python) → Création des images PNG
2. **Transmission** (API Flask) → Envoi des URLs au frontend
3. **Affichage** (Frontend JavaScript) → Rendu dans le navigateur

---

## 🔧 Étape 1 : Génération des Graphiques (Backend)

### Fichier : `student_vector_ml.py`

**Méthode : `visualize()`** (lignes 346-433)

```python
def visualize(self, top_results, query_id=None):
    """Génère 3 graphiques PNG et les sauvegarde"""
    
    # 1. Random Forest - Probabilité de dépression
    plt.figure(figsize=(10, 6))
    sns.barplot(...)
    rf_path = os.path.join(self.images_dir, f'1_random_forest_probability_{query_id}.png')
    plt.savefig(rf_path, dpi=200, bbox_inches='tight')
    images['random_forest'] = rf_path
    
    # 2. Linear Regression - Score de risque
    # ... (même processus)
    images['linear_regression'] = lr_path
    
    # 3. K-Means - Clustering
    # ... (même processus)
    images['kmeans'] = kmeans_path
    
    return images
```

**Dossier de sauvegarde :**
- `static/ml_images/` (accessible via Flask static files)

**Format des fichiers :**
- `1_random_forest_probability_20241209_123456_789012.png`
- `2_linear_regression_risk_20241209_123456_789012.png`
- `3_kmeans_clustering_20241209_123456_789012.png`

**Stockage dans l'instance :**
```python
self.last_visualizations = images  # Dict avec les chemins
self.last_query_id = query_id      # ID unique pour cette recherche
```

---

## 🌐 Étape 2 : Transmission via API (Flask)

### Fichier : `app.py`

**Route : `/api/vector-search`** (lignes 873-1010)

```python
@app.route('/api/vector-search', methods=['POST'])
def vector_search_ml():
    # 1. Exécuter le pipeline ML
    results_df = system.pipeline(query, top_k=top_k)
    
    # 2. Récupérer les chemins des visualisations
    visualization_images = getattr(system, 'last_visualizations', {})
    query_id = getattr(system, 'last_query_id', '')
    
    # 3. Construire les URLs avec cache-busting
    visualization_urls = []
    if visualization_images:
        cache_buster = int(time.time() * 1000)  # Évite le cache navigateur
        for key in ['random_forest', 'linear_regression', 'kmeans']:
            if key in visualization_images:
                img_path = visualization_images[key]
                filename = os.path.basename(img_path)
                # URL accessible via Flask static files
                visualization_urls.append(f'/static/ml_images/{filename}?v={cache_buster}')
    
    # 4. Retourner dans la réponse JSON
    return jsonify({
        'success': True,
        'results': results_list,
        'visualizations': visualization_urls,  # ← URLs des graphiques
        'count': len(results_list)
    })
```

**Cache-busting :**
- Paramètre `?v=timestamp` ajouté à chaque URL
- Force le rechargement des images à chaque nouvelle recherche
- Évite l'affichage d'anciennes images mises en cache

---

## 🎨 Étape 3 : Affichage dans le Frontend (JavaScript)

### Fichier : `static/js/search.js`

**Fonction : `performVectorSearch()`** (lignes 920-980)

```javascript
async function performVectorSearch() {
    const response = await fetch('/api/vector-search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: query, top_k: 10})
    });
    
    const data = await response.json();
    
    if (data.visualizations && data.visualizations.length > 0) {
        const labels = [
            '🌲 Random Forest (Classification)', 
            '📈 Régression Linéaire (Pertinence)', 
            '🎯 K-Means (Clustering)'
        ];
        
        // 1. Créer des liens cliquables
        vizLinksHtml = data.visualizations.map((vizUrl, index) => {
            return `<a href="${vizUrl}" target="_blank" class="viz-link">
                ${icons[index]} ${labels[index]}
            </a>`;
        }).join('');
        
        // 2. Afficher les images directement
        vizImagesHtml = '<div style="display: grid; ...">' +
            data.visualizations.map(vizUrl => {
                return `<div>
                    <img src="${vizUrl}" 
                         alt="Visualisation ML" 
                         style="width: 100%; height: auto;"
                         onclick="window.open('${vizUrl}', '_blank')">
                </div>`;
            }).join('') +
            '</div>';
    }
    
    // Insérer dans le DOM
    headerDiv.innerHTML = `
        <h2>🧠 Résultats de la Recherche Vectorielle ML</h2>
        <div>${vizLinksHtml}</div>
        ${vizImagesHtml}
    `;
    resultsContainer.appendChild(headerDiv);
}
```

**Affichage :**
- **Liens cliquables** : Boutons pour ouvrir les graphiques dans un nouvel onglet
- **Images intégrées** : Graphiques affichés directement dans la page
- **Grid responsive** : Layout adaptatif (3 colonnes sur desktop, 1 sur mobile)

---

## 📁 Structure des Fichiers

```
final/
├── student_vector_ml.py          # Génération des graphiques
│   └── visualize()               # Crée les PNG
│
├── app.py                         # API Flask
│   └── /api/vector-search        # Retourne les URLs
│
├── static/
│   ├── ml_images/                # Dossier des graphiques
│   │   ├── 1_random_forest_*.png
│   │   ├── 2_linear_regression_*.png
│   │   └── 3_kmeans_*.png
│   │
│   └── js/
│       └── search.js             # Affichage frontend
│
└── templates/
    └── index.html                # Page HTML
```

---

## 🔄 Flux Complet

```
1. Utilisateur lance recherche ML
   ↓
2. JavaScript : performVectorSearch()
   ↓
3. Flask : /api/vector-search
   ↓
4. student_vector_ml.py : pipeline()
   ├─→ search()          (recherche vectorielle)
   ├─→ apply_ml()        (Random Forest, Linear Regression, K-Means)
   └─→ visualize()       (génère 3 PNG)
       ├─→ Sauvegarde dans static/ml_images/
       └─→ Stocke chemins dans self.last_visualizations
   ↓
5. Flask : Récupère last_visualizations
   ├─→ Construit URLs : /static/ml_images/filename.png?v=timestamp
   └─→ Retourne JSON avec visualizations: [url1, url2, url3]
   ↓
6. JavaScript : Reçoit data.visualizations
   ├─→ Crée liens cliquables
   └─→ Affiche images dans la page
   ↓
7. Navigateur : Charge les images depuis /static/ml_images/
```

---

## 🎯 Points Clés

### 1. **Unicité des fichiers**
- Chaque recherche génère un `query_id` unique avec microsecondes
- Format : `YYYYMMDD_HHMMSS_microsecondes`
- Évite l'écrasement des fichiers entre recherches

### 2. **Cache-busting**
- Paramètre `?v=timestamp` dans les URLs
- Force le rechargement des images
- Évite l'affichage d'anciennes visualisations

### 3. **Gestion d'erreurs**
```javascript
onerror="this.style.display='none'; console.error('Erreur chargement image:', '${vizUrl}');"
```
- Si une image ne charge pas, elle est masquée
- Erreur loggée dans la console

### 4. **Accessibilité**
- Images cliquables pour ouvrir en grand format
- Liens avec labels descriptifs
- Alt text pour les lecteurs d'écran

---

## 🛠️ Configuration

### Modifier le dossier de sauvegarde

Dans `student_vector_ml.py` :
```python
self.images_dir = 'static/ml_images'  # Modifier ici
```

### Modifier la qualité des images

Dans `student_vector_ml.py`, méthode `visualize()` :
```python
plt.savefig(rf_path, dpi=200, bbox_inches='tight')  # dpi=200 → qualité
```

### Modifier le layout d'affichage

Dans `search.js`, ligne ~952 :
```javascript
'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">'
// Modifier minmax(300px, 1fr) pour changer la taille des colonnes
```

---

## ✅ Résumé

Les visualisations sont intégrées via :
1. **Backend** : Génération PNG avec matplotlib/seaborn → `static/ml_images/`
2. **API** : Transmission des URLs avec cache-busting
3. **Frontend** : Affichage direct des images + liens cliquables

Tout est automatique : l'utilisateur lance une recherche ML et les graphiques s'affichent automatiquement ! 🎉








