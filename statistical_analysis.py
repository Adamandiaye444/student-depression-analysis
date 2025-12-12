"""
Module d'Analyse Statistique avec Fonction de Distribution Empirique (EDF)
===========================================================================
Ce module implémente le calcul et la visualisation de l'EDF (Empirical Distribution Function)
pour des variables quantitatives de la base de données MongoDB.

EDF Formula: F_n(x) = (1/n) * Σ_{i=1}^{n} 1_{X_i ≤ x}
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pymongo import MongoClient
import os
from datetime import datetime


class StatisticalAnalyzer:
    """Classe pour l'analyse statistique avec EDF"""
    
    def __init__(self, mongodb_uri, database_name="student_depression_db", collection_name="students"):
        """
        Initialise l'analyseur statistique.
        
        Paramètres:
            mongodb_uri (str): URI de connexion MongoDB
            database_name (str): Nom de la base de données
            collection_name (str): Nom de la collection
        """
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.df = None
        
        # Connexion à MongoDB
        self._connect()
        
        # Dossier pour les visualisations
        self.images_dir = 'static/statistical_analysis'
        os.makedirs(self.images_dir, exist_ok=True)
    
    def _connect(self):
        """Établit la connexion à MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print(f"✓ Connecté à MongoDB: {self.database_name}.{self.collection_name}")
        except Exception as e:
            print(f"✗ Erreur de connexion MongoDB: {e}")
            raise
    
    def load_data(self, limit=10000):
        """
        Charge les données depuis MongoDB.
        
        Paramètres:
            limit (int): Nombre maximum de documents à charger
        """
        print(f"📥 Chargement des données (limite: {limit})...")
        cursor = self.collection.find({}).limit(limit)
        documents = list(cursor)
        
        if not documents:
            raise ValueError("Aucune donnée trouvée dans MongoDB")
        
        self.df = pd.DataFrame(documents)
        print(f"✓ {len(self.df)} documents chargés")
        
        return self.df
    
    def get_quantitative_variables(self):
        """
        Retourne la liste des variables quantitatives disponibles.
        
        Retourne:
            list: Liste des noms de colonnes numériques
        """
        if self.df is None:
            self.load_data()
        
        # Colonnes numériques possibles
        numeric_cols = []
        possible_vars = [
            'age', 'Age',
            'CGPA', 'cgpa',
            'Academic Pressure', 'academicPressure', 'academic_pressure',
            'Study Satisfaction', 'studySatisfaction', 'study_satisfaction',
            'Financial Stress', 'financialStress', 'financial_stress',
            'Work Pressure', 'workPressure', 'work_pressure',
            'Work Study Hours', 'workStudyHours', 'work_study_hours',
            'Depression', 'depression'
        ]
        
        for var in possible_vars:
            if var in self.df.columns:
                # Vérifier que c'est bien numérique
                try:
                    pd.to_numeric(self.df[var], errors='coerce')
                    numeric_cols.append(var)
                except:
                    pass
        
        return numeric_cols
    
    def calculate_edf(self, variable_name):
        """
        Calcule la fonction de distribution empirique (EDF).
        
        EDF Formula: F_n(x) = (1/n) * Σ_{i=1}^{n} 1_{X_i ≤ x}
        
        Paramètres:
            variable_name (str): Nom de la variable quantitative
            
        Retourne:
            tuple: (x_values, edf_values, n) où:
                - x_values: valeurs triées de la variable
                - edf_values: valeurs de l'EDF correspondantes
                - n: nombre total d'observations
        """
        if self.df is None:
            self.load_data()
        
        if variable_name not in self.df.columns:
            raise ValueError(f"Variable '{variable_name}' non trouvée dans les données")
        
        # Extraire la variable et nettoyer
        data = pd.to_numeric(self.df[variable_name], errors='coerce')
        data = data.dropna()
        
        if len(data) == 0:
            raise ValueError(f"Aucune valeur numérique valide pour '{variable_name}'")
        
        n = len(data)
        print(f"📊 Calcul de l'EDF pour '{variable_name}' (n={n})")
        
        # Trier les valeurs
        x_sorted = np.sort(data.values)
        
        # Calculer l'EDF: F_n(x) = (1/n) * Σ 1_{X_i ≤ x}
        # Pour chaque valeur x, compter combien de X_i ≤ x
        edf_values = np.arange(1, n + 1) / n
        
        return x_sorted, edf_values, n
    
    def fit_theoretical_distribution(self, data, distribution='norm'):
        """
        Ajuste une distribution théorique aux données.
        
        Paramètres:
            data (array): Données observées
            distribution (str): Type de distribution ('norm', 'expon', etc.)
            
        Retourne:
            tuple: (fitted_params, distribution_object)
        """
        data_clean = data[~np.isnan(data)]
        
        if distribution == 'norm':
            # Distribution normale
            mu, sigma = stats.norm.fit(data_clean)
            dist = stats.norm(loc=mu, scale=sigma)
            params = {'mu': mu, 'sigma': sigma}
        elif distribution == 'expon':
            # Distribution exponentielle
            loc, scale = stats.expon.fit(data_clean)
            dist = stats.expon(loc=loc, scale=scale)
            params = {'loc': loc, 'scale': scale}
        else:
            # Par défaut, normale
            mu, sigma = stats.norm.fit(data_clean)
            dist = stats.norm(loc=mu, scale=sigma)
            params = {'mu': mu, 'sigma': sigma}
        
        return params, dist
    
    def visualize_edf_cdf(self, variable_name, distribution='norm', save_path=None):
        """
        Visualise l'EDF et la CDF théorique pour une variable.
        
        Paramètres:
            variable_name (str): Nom de la variable
            distribution (str): Type de distribution théorique
            save_path (str): Chemin pour sauvegarder l'image
            
        Retourne:
            str: Chemin du fichier sauvegardé
        """
        # Calculer l'EDF
        x_edf, y_edf, n = self.calculate_edf(variable_name)
        
        # Extraire les données pour la CDF théorique
        data = pd.to_numeric(self.df[variable_name], errors='coerce').dropna()
        
        # Ajuster la distribution théorique
        params, dist = self.fit_theoretical_distribution(data.values, distribution)
        
        # Créer un range pour la CDF théorique
        x_min, x_max = data.min(), data.max()
        x_range = np.linspace(x_min, x_max, 1000)
        y_cdf = dist.cdf(x_range)
        
        # Créer la figure
        plt.figure(figsize=(14, 8))
        
        # Sous-graphique 1: EDF et CDF superposées
        plt.subplot(2, 2, 1)
        plt.step(x_edf, y_edf, where='post', label=f'EDF (n={n})', linewidth=2, color='#667eea')
        plt.plot(x_range, y_cdf, label=f'CDF théorique ({distribution})', linewidth=2, 
                linestyle='--', color='#f59e0b', alpha=0.8)
        plt.xlabel(f'{variable_name}', fontsize=12, fontweight='bold')
        plt.ylabel('Probabilité cumulée', fontsize=12, fontweight='bold')
        plt.title(f'Fonction de Distribution Empirique (EDF) vs CDF théorique\nVariable: {variable_name}', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Sous-graphique 2: Histogramme avec densité théorique
        plt.subplot(2, 2, 2)
        plt.hist(data.values, bins=50, density=True, alpha=0.7, color='#667eea', 
                edgecolor='black', linewidth=0.5, label='Données observées')
        plt.plot(x_range, dist.pdf(x_range), 'r-', linewidth=2, 
                label=f'Densité théorique ({distribution})', color='#f59e0b')
        plt.xlabel(f'{variable_name}', fontsize=12, fontweight='bold')
        plt.ylabel('Densité', fontsize=12, fontweight='bold')
        plt.title(f'Histogramme et Densité théorique\nVariable: {variable_name}', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Sous-graphique 3: Q-Q Plot pour vérifier l'ajustement
        plt.subplot(2, 2, 3)
        stats.probplot(data.values, dist=dist, plot=plt)
        plt.title(f'Q-Q Plot: {variable_name} vs {distribution}', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Sous-graphique 4: Statistiques descriptives
        plt.subplot(2, 2, 4)
        plt.axis('off')
        stats_text = f"""
        STATISTIQUES DESCRIPTIVES
        
        Variable: {variable_name}
        Nombre d'observations: {n}
        
        Statistiques observées:
        • Moyenne: {data.mean():.2f}
        • Médiane: {data.median():.2f}
        • Écart-type: {data.std():.2f}
        • Min: {data.min():.2f}
        • Max: {data.max():.2f}
        
        Paramètres ajustés ({distribution}):
        """
        if distribution == 'norm':
            stats_text += f"""
        • μ (moyenne): {params['mu']:.2f}
        • σ (écart-type): {params['sigma']:.2f}
        """
        else:
            stats_text += f"\n{params}"
        
        # Test de Kolmogorov-Smirnov
        ks_stat, ks_pvalue = stats.kstest(data.values, dist.cdf)
        stats_text += f"""
        
        Test de Kolmogorov-Smirnov:
        • Statistique KS: {ks_stat:.4f}
        • p-value: {ks_pvalue:.4f}
        """
        
        plt.text(0.1, 0.5, stats_text, fontsize=11, family='monospace',
                verticalalignment='center', bbox=dict(boxstyle='round', 
                facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Sauvegarder la figure
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.images_dir, f'edf_analysis_{variable_name}_{timestamp}.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Visualisation sauvegardée: {save_path}")
        
        return save_path
    
    def get_statistics_summary(self, variable_name):
        """
        Retourne un résumé statistique pour une variable.
        
        Paramètres:
            variable_name (str): Nom de la variable
            
        Retourne:
            dict: Dictionnaire avec les statistiques
        """
        if self.df is None:
            self.load_data()
        
        data = pd.to_numeric(self.df[variable_name], errors='coerce').dropna()
        
        summary = {
            'variable': variable_name,
            'count': len(data),
            'mean': float(data.mean()),
            'median': float(data.median()),
            'std': float(data.std()),
            'min': float(data.min()),
            'max': float(data.max()),
            'q25': float(data.quantile(0.25)),
            'q75': float(data.quantile(0.75))
        }
        
        return summary











