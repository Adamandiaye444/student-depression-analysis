"""
Module de Recherche Vectorielle avec Machine Learning
======================================================
Ce module implémente la classe StudentVectorML pour la recherche vectorielle
avancée avec des modèles ML (Random Forest, Linear Regression, K-Means).
Adapté pour MongoDB Atlas (au lieu de CSV).
"""

# ----------------------------
# 1. Importer les librairies
# ----------------------------
import os
import pandas as pd
#rom sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour générer des images
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
from pymongo import MongoClient
# Import conditionnel - chargé seulement si la classe est utilisée
SentenceTransformer = None

def _lazy_import_sentence_transformer():
    """Import SentenceTransformer seulement quand nécessaire."""
    global SentenceTransformer
    if SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer as ST
        SentenceTransformer = ST
    return SentenceTransformer

# ----------------------------
# 2. Classe unique : StudentVectorML
# ----------------------------
class StudentVectorML:
    """
    Classe pour la recherche vectorielle avec Machine Learning.
    Utilise MongoDB Atlas comme source de données.
    """
    
    def __init__(self, mongodb_uri, model_name='all-MiniLM-L6-v2', limit=2000):
        """
        Initialiser le système ML avec MongoDB Atlas.
        
        Paramètres:
            mongodb_uri (str): URI de connexion MongoDB Atlas
            model_name (str): Nom du modèle SentenceTransformer (défaut: 'all-MiniLM-L6-v2')
            limit (int): Nombre maximum de documents à charger (défaut: 2000)
        """
        print("🔧 Initialisation du système ML...")
        
        # Connexion MongoDB
        print("📡 Connexion à MongoDB Atlas...")
        self.client = MongoClient(mongodb_uri)
        self.db = self.client["student_depression_db"]
        self.collection = self.db["students"]
        
        # Charger le dataset depuis MongoDB
        self._load_from_mongodb(limit)
        
        # Détecter automatiquement les noms de colonnes réels dans MongoDB
        self._detect_feature_columns()
        
        # Convertir en numérique et gérer les valeurs non numériques
        for feat in self.features:
            if feat in self.df.columns:
                self.df[feat] = pd.to_numeric(self.df[feat], errors='coerce').fillna(0)
        
        # Gérer la colonne Depression
        depression_cols = ['Depression', 'depression']
        for col in depression_cols:
            if col in self.df.columns:
                self.df['Depression'] = pd.to_numeric(self.df[col], errors='coerce').fillna(0).astype(int)
                break
        
        # Créer description textuelle complète
        self._create_full_description()
        
        # Charger le modèle de embeddings
        print("🤖 Chargement du modèle et génération des embeddings...")
        ST = _lazy_import_sentence_transformer()
        self.model = ST(model_name)
        self._ensure_embeddings()
        print("✅ Embeddings générés !")
        
        # Initialiser les modèles ML
        self.clf = RandomForestClassifier(n_estimators=50, random_state=42)
        self.linreg = LinearRegression()
        self.kmeans = None  # sera défini après clustering
        
        # Dossier pour les images (dans static pour être servi par Flask)
        self.images_dir = 'static/ml_images'
        os.makedirs(self.images_dir, exist_ok=True)
        
        # Stocker les dernières visualisations générées
        self.last_visualizations = {}
        self.last_query_id = None
        
        print(" Système ML initialisé !")
    
    def _load_from_mongodb(self, limit=2000):
        """Charger les données depuis MongoDB Atlas"""
        print(f" Chargement des données depuis MongoDB Atlas (limite: {limit})...")
        
        # Récupérer les documents
        cursor = self.collection.find({}).limit(limit)
        documents = list(cursor)
        
        if not documents:
            raise ValueError("Aucune donnée trouvée dans MongoDB")
        
        # Convertir en DataFrame
        self.df = pd.DataFrame(documents)
        print(f" {len(self.df)} documents chargés depuis MongoDB")
        print(f" Colonnes disponibles: {list(self.df.columns)[:10]}...")  # Afficher les 10 premières colonnes
    
    def _detect_feature_columns(self):
        """Détecter automatiquement les noms de colonnes réels dans MongoDB"""
        print("🔍 Détection des colonnes pour ML...")
        
        # Mapping des noms possibles pour chaque feature
        feature_mappings = {
            'Academic Pressure': ['Academic Pressure', 'academicPressure', 'academic_pressure', 'AcademicPressure'],
            'Work Pressure': ['Work Pressure', 'workPressure', 'work_pressure', 'WorkPressure'],
            'CGPA': ['CGPA', 'cgpa', 'Cgpa'],
            'Study Satisfaction': ['Study Satisfaction', 'studySatisfaction', 'study_satisfaction', 'StudySatisfaction'],
            'Job Satisfaction': ['Job Satisfaction', 'jobSatisfaction', 'job_satisfaction', 'JobSatisfaction'],
            'Work Study Hours': ['Work Study Hours', 'Work/Study Hours', 'workStudyHours', 'work_study_hours', 'WorkStudyHours'],
            'Financial Stress': ['Financial Stress', 'financialStress', 'financial_stress', 'FinancialStress']
        }
        
        # Détecter les colonnes réelles
        self.features = []
        self.feature_mapping = {}  # Mapping nom standard -> nom réel dans MongoDB
        
        for standard_name, possible_names in feature_mappings.items():
            found = False
            for possible_name in possible_names:
                if possible_name in self.df.columns:
                    self.features.append(possible_name)
                    self.feature_mapping[standard_name] = possible_name
                    print(f"   ✓ '{standard_name}' → '{possible_name}'")
                    found = True
                    break
            
            if not found:
                print(f"    '{standard_name}' non trouvé (variations: {possible_names})")
        
        if len(self.features) == 0:
            print(" Aucune colonne de feature trouvée !")
            print(f"   Colonnes disponibles: {list(self.df.columns)}")
            raise ValueError("Aucune colonne de feature ML trouvée dans MongoDB")
        
        print(f" {len(self.features)} colonnes détectées pour ML")
    
    def _create_full_description(self):
        """Créer une description textuelle complète pour chaque étudiant"""
        print(" Création des descriptions textuelles...")
        
        descriptions = []
        for idx, row in self.df.iterrows():
            desc_parts = []
            
            # Mapper les colonnes possibles (gérer les variations de noms)
            mappings = {
                'Gender': ['gender', 'Gender'],
                'Age': ['age', 'Age'],
                'City': ['city', 'City'],
                'Profession': ['profession', 'Profession'],
                'Academic Pressure': ['Academic Pressure', 'academicPressure', 'academic_pressure', 'AcademicPressure'],
                'Work Pressure': ['Work Pressure', 'workPressure', 'work_pressure', 'WorkPressure'],
                'CGPA': ['CGPA', 'cgpa', 'Cgpa'],
                'Study Satisfaction': ['Study Satisfaction', 'studySatisfaction', 'study_satisfaction', 'StudySatisfaction'],
                'Job Satisfaction': ['Job Satisfaction', 'jobSatisfaction', 'job_satisfaction', 'JobSatisfaction'],
                'Sleep Duration': ['sleepDuration', 'Sleep Duration', 'sleep_duration', 'SleepDuration'],
                'Dietary Habits': ['dietaryHabits', 'Dietary Habits', 'dietary_habits', 'DietaryHabits'],
                'Degree': ['degree', 'Degree'],
                'Suicidal Thoughts': ['suicidalThoughts', 'Suicidal Thoughts', 'Have you ever had suicidal thoughts ?', 'suicidal_thoughts'],
                'Work Study Hours': ['Work Study Hours', 'workStudyHours', 'work_study_hours', 'Work/Study Hours', 'WorkStudyHours'],
                'Financial Stress': ['Financial Stress', 'financialStress', 'financial_stress', 'FinancialStress'],
                'Family History': ['familyHistoryMentalIllness', 'Family History Mental Illness', 'Family History of Mental Illness', 'family_history_mental_illness'],
                'Depression': ['Depression', 'depression']
            }
            
            for key, possible_cols in mappings.items():
                for col in possible_cols:
                    if col in self.df.columns:
                        value = row[col]
                        if pd.notna(value) and value != '':
                            desc_parts.append(f"{key}: {value}")
                            break
            
            descriptions.append(", ".join(desc_parts))
        
        self.df['full_description'] = descriptions
        print(" Descriptions créées !")
    
    def _ensure_embeddings(self):
        """Vérifier et générer les embeddings si nécessaire"""
        # Vérifier si les embeddings existent déjà dans MongoDB
        sample_doc = self.collection.find_one({})
        if sample_doc and 'embedding_ml' in sample_doc and isinstance(sample_doc['embedding_ml'], list):
            print(" Chargement des embeddings depuis MongoDB...")
            # Charger les embeddings depuis MongoDB
            embeddings_list = []
            for doc in self.collection.find({}).limit(len(self.df)):
                if 'embedding_ml' in doc and isinstance(doc['embedding_ml'], list):
                    embeddings_list.append(doc['embedding_ml'])
                else:
                    # Si un embedding manque, on doit tous les régénérer
                    embeddings_list = None
                    break
            
            if embeddings_list and len(embeddings_list) == len(self.df):
                self.embeddings = np.array(embeddings_list, dtype=np.float32)
                print(f" {len(embeddings_list)} embeddings chargés depuis MongoDB")
                return
        
        # Générer les embeddings
        print("Génération des embeddings...")
        descriptions = self.df['full_description'].tolist()
        embeddings = self.model.encode(descriptions, show_progress_bar=True)
        self.embeddings = np.array(embeddings, dtype=np.float32)
        
        # Sauvegarder dans MongoDB
        print(" Sauvegarde des embeddings dans MongoDB...")
        model_name = getattr(self.model, 'get_sentence_embedding_dimension', lambda: 'all-MiniLM-L6-v2')()
        for idx, (doc_id, embedding) in enumerate(zip(self.df['_id'], embeddings)):
            self.collection.update_one(
                {'_id': doc_id},
                {
                    '$set': {
                        'embedding_ml': embedding.tolist(),
                        'embedding_model': 'all-MiniLM-L6-v2',
                        'embedding_updated_at': datetime.utcnow()
                    }
                }
            )
        
        print(f" {len(embeddings)} embeddings générés et sauvegardés")
    
    # ----------------------------
    # Recherche vectorielle
    # ----------------------------
    def search(self, query, top_k=5):
        """
        Effectuer une recherche vectorielle.
        
        Paramètres:
            query (str): Requête textuelle
            top_k (int): Nombre de résultats à retourner
            
        Retourne:
            DataFrame: Top résultats avec similarité
        """
        print(f"🔍 Recherche: '{query}' (top_k={top_k})")
        
        # Encoder la requête
        query_vec = self.model.encode([query])
        
        # Calculer la similarité cosinus
        sims = cosine_similarity(query_vec, self.embeddings)[0]
        
        # Ajouter la similarité au DataFrame
        self.df['similarity'] = sims
        
        # Trier et retourner les top résultats
        top_results = self.df.sort_values(by='similarity', ascending=False).head(top_k).copy()
        
        print(f" {len(top_results)} résultats trouvés")
        return top_results
    
    # ----------------------------
    # Appliquer ML sur les top résultats
    # ----------------------------
    def apply_ml(self, top_results):
        """
        Appliquer les trois algorithmes ML sur les résultats :
        1. Random Forest : Classification de la dépression
        2. Linear Regression : Score de risque
        3. K-Means : Clustering
        
        Paramètres:
            top_results (DataFrame): Résultats de la recherche vectorielle
            
        Retourne:
            DataFrame: Résultats avec les prédictions ML
        """
        print("🤖 Application des modèles ML...")
        
        # Vérifier que les features sont disponibles
        available_features = [f for f in self.features if f in self.df.columns]
        if len(available_features) < 2:
            print(f"  Pas assez de features disponibles ({len(available_features)} trouvées)")
            print(f"   Features recherchées: {self.features}")
            print(f"   Colonnes disponibles: {list(self.df.columns)[:20]}")
            # Ajouter des valeurs par défaut
            top_results['predicted_depression'] = 0
            top_results['prob_depression'] = 0.5
            top_results['predicted_category'] = 'Unknown'
            top_results['category_confidence'] = 0.5
            top_results['risk_score'] = 0.5
            top_results['relevance_score'] = 0.5
            top_results['cluster'] = 0
            return top_results
        
        # Préparer les données d'entraînement (utiliser toutes les données)
        X_full = self.df[available_features].fillna(0)
        y_full = self.df['Depression'] if 'Depression' in self.df.columns else pd.Series([0] * len(self.df))
        
        X_top = top_results[available_features].fillna(0)
        
        # Random Forest : classification
        print("🌲 Entraînement Random Forest...")
        self.clf.fit(X_full, y_full)
        top_results['predicted_depression'] = self.clf.predict(X_top)
        top_results['prob_depression'] = self.clf.predict_proba(X_top)[:, 1]
        
        # Pour compatibilité avec app.py : ajouter predicted_category et category_confidence
        top_results['predicted_category'] = ['Avec Dépression' if p == 1 else 'Sans Dépression' 
                                             for p in top_results['predicted_depression']]
        top_results['category_confidence'] = top_results['prob_depression']
        print("✅ Random Forest entraîné")
        
        # Linear Regression : score de risque
        print("📈 Entraînement Régression Linéaire...")
        self.linreg.fit(X_full, y_full)
        top_results['risk_score'] = self.linreg.predict(X_top)
        
        # Pour compatibilité avec app.py : ajouter relevance_score (normalisé entre 0 et 1)
        risk_scores = top_results['risk_score']
        min_risk, max_risk = risk_scores.min(), risk_scores.max()
        if max_risk != min_risk:
            top_results['relevance_score'] = (risk_scores - min_risk) / (max_risk - min_risk)
        else:
            top_results['relevance_score'] = 0.5
        print("✅ Régression Linéaire entraînée")
        
        # K-Means : clustering
        print("🎯 Clustering K-Means...")
        self.kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        top_results['cluster'] = self.kmeans.fit_predict(X_top)
        print("✅ K-Means entraîné")
        
        print("✅ Tous les modèles ML appliqués !")
        return top_results
    
    # ----------------------------
    # Visualisations
    # ----------------------------
    def visualize(self, top_results, query_id=None):
        """
        Générer et sauvegarder les visualisations.
        
        Paramètres:
            top_results (DataFrame): Résultats avec prédictions ML
            query_id (str): ID unique pour les fichiers d'images
            
        Retourne:
            dict: Chemins des images générées
        """
        print("📊 Génération des visualisations...")
        
        if query_id is None:
            query_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        images = {}
        
        # 1. Probabilité de dépression (Random Forest)
        plt.figure(figsize=(10, 6))
        if 'prob_depression' in top_results.columns or 'category_confidence' in top_results.columns:
            y_col = 'prob_depression' if 'prob_depression' in top_results.columns else 'category_confidence'
            sns.barplot(x=top_results.index, y=y_col, data=top_results, palette='viridis')
            plt.title(f'Probabilité de dépression (Random Forest)\n({len(top_results)} étudiants trouvés)', 
                     fontsize=14, fontweight='bold')
            plt.ylabel('Probabilité', fontsize=12)
            plt.xlabel('Étudiants', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'Données non disponibles', ha='center', va='center', transform=plt.gca().transAxes)
        
        plt.tight_layout()
        rf_path = os.path.join(self.images_dir, f'1_random_forest_probability_{query_id}.png')
        plt.savefig(rf_path, dpi=200, bbox_inches='tight')
        plt.close()
        images['random_forest'] = rf_path
        print(f"   ✓ Graphique Random Forest sauvegardé")
        
        # 2. Score de risque (Linear Regression)
        plt.figure(figsize=(10, 6))
        if 'risk_score' in top_results.columns or 'relevance_score' in top_results.columns:
            y_col = 'relevance_score' if 'relevance_score' in top_results.columns else 'risk_score'
            sns.barplot(x=top_results.index, y=y_col, data=top_results, palette='coolwarm')
            plt.title(f'Score de risque (Linear Regression)\n({len(top_results)} étudiants trouvés)', 
                     fontsize=14, fontweight='bold')
            plt.ylabel('Score', fontsize=12)
            plt.xlabel('Étudiants', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'Données non disponibles', ha='center', va='center', transform=plt.gca().transAxes)
        
        plt.tight_layout()
        lr_path = os.path.join(self.images_dir, f'2_linear_regression_risk_{query_id}.png')
        plt.savefig(lr_path, dpi=200, bbox_inches='tight')
        plt.close()
        images['linear_regression'] = lr_path
        print(f"   ✓ Graphique Régression Linéaire sauvegardé")
        
        # 3. Clustering K-Means
        plt.figure(figsize=(10, 7))
        # Utiliser les noms de colonnes réels détectés
        academic_pressure_col = self.feature_mapping.get('Academic Pressure', 'Academic Pressure')
        work_pressure_col = self.feature_mapping.get('Work Pressure', 'Work Pressure')
        
        if 'cluster' in top_results.columns and academic_pressure_col in top_results.columns and work_pressure_col in top_results.columns:
            sns.scatterplot(x=academic_pressure_col, y=work_pressure_col, hue='cluster', 
                          data=top_results, s=100, palette='viridis', edgecolor='black')
            plt.title(f'Clustering K-Means : Profil étudiant\n({len(top_results)} étudiants trouvés)', 
                     fontsize=14, fontweight='bold')
            plt.xlabel('Academic Pressure', fontsize=12)
            plt.ylabel('Work Pressure', fontsize=12)
            plt.legend(title='Cluster', fontsize=10)
            plt.grid(alpha=0.3)
        else:
            plt.text(0.5, 0.5, 'Données de clustering non disponibles', 
                    ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
        
        plt.tight_layout()
        kmeans_path = os.path.join(self.images_dir, f'3_kmeans_clustering_{query_id}.png')
        plt.savefig(kmeans_path, dpi=200, bbox_inches='tight')
        plt.close()
        images['kmeans'] = kmeans_path
        print(f"   ✓ Graphique K-Means sauvegardé")
        
        print(f"✅ Toutes les visualisations sauvegardées dans {self.images_dir}")
        return images
    
    # ----------------------------
    # Pipeline complet
    # ----------------------------
    def pipeline(self, query, top_k=5):
        """
        Pipeline complet : recherche + ML + visualisations.
        
        Paramètres:
            query (str): Requête textuelle pour la recherche
            top_k (int): Nombre de résultats à retourner
            
        Retourne:
            DataFrame: Résultats finaux avec prédictions ML
        """
        print(f"\n🚀 Pipeline ML complet pour: '{query}'")
        print("   Algorithmes: Random Forest + Linear Regression + K-Means")
        
        # Recherche vectorielle
        top_results = self.search(query, top_k)
        
        # Application ML
        top_results = self.apply_ml(top_results)
        
        # Génération des visualisations
        query_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        images = self.visualize(top_results, query_id)
        
        # Stocker les visualisations dans l'instance pour qu'app.py puisse les récupérer
        self.last_visualizations = images
        self.last_query_id = query_id
        
        # Retourner le DataFrame (app.py s'occupe de la conversion en JSON)
        return top_results
    
    def clear_embeddings(self):
        """Supprime tous les embeddings de MongoDB"""
        print("🗑️  Suppression des embeddings...")
        result = self.collection.update_many(
            {},
            {'$unset': {'embedding_ml': "", 'embedding_model': "", 'embedding_updated_at': ""}}
        )
        print(f"✅ {result.modified_count} embeddings supprimés")
        return {'deleted': result.modified_count}
    
    def regenerate_embeddings(self):
        """Régénère tous les embeddings"""
        print("🔄 Régénération des embeddings...")
        self.clear_embeddings()
        self._ensure_embeddings()
        return {'regenerated': len(self.df)}


# ----------------------------
# Exemple d'utilisation
# ----------------------------
if __name__ == "__main__":
    # Exemple d'utilisation avec MongoDB Atlas
    # Remplacez par votre URI MongoDB
    MONGODB_URI = "mongodb+srv://votre_uri_mongodb_atlas"
    
    ml_system = StudentVectorML(MONGODB_URI)
    
    query = "étudiant avec fort stress académique et peu de sommeil"
    final_results = ml_system.pipeline(query, top_k=5)
    
    print("\n📊 Résultats finaux après post-traitement :")
    print(final_results[['full_description', 'similarity', 'predicted_depression', 
                         'prob_depression', 'risk_score', 'cluster']])
