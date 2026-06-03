"""
Application Flask avec MongoDB Atlas - Système de recherche
============================================================
Ce script crée une application web Flask qui se connecte à MongoDB Atlas
et permet de rechercher des documents avec autocomplétion.
"""

# ============================================================================
# IMPORTS
# ============================================================================
from flask import Flask, render_template, jsonify, request
# Flask : framework web pour créer l'application
# render_template : pour afficher les templates HTML
# jsonify : pour retourner des données en format JSON (pour l'autocomplétion)
# request : pour récupérer les données des requêtes HTTP

from pymongo import MongoClient
# MongoClient : client MongoDB pour se connecter à la base de données

from bson import ObjectId
# ObjectId : pour gérer les identifiants MongoDB (si nécessaire)

import os
# os : pour gérer les variables d'environnement (optionnel)

import math
# math : pour les calculs mathématiques (similarité cosinus)

import pandas as pd
# pandas : pour la manipulation de DataFrames (recherche vectorielle ML)

# Imports pour la recherche vectorielle ML (optionnels)
# Si non installés, la recherche vectorielle simple restera disponible
try:
    from student_vector_ml import StudentVectorML
    ML_AVAILABLE = True
    print("✓ Module ML disponible : Recherche vectorielle avancée activée")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  Module ML non disponible : Installez requirements_ml.txt pour activer")

# Imports pour l'analyse statistique (EDF)
try:
    from statistical_analysis import StatisticalAnalyzer
    STATS_AVAILABLE = True
    print("✓ Module d'analyse statistique disponible")
except ImportError:
    STATS_AVAILABLE = False
    print("⚠️  Module d'analyse statistique non disponible")

# ============================================================================
# CONFIGURATION DE L'APPLICATION FLASK
# ============================================================================
app = Flask(__name__)
# Création de l'instance Flask
# __name__ permet à Flask de trouver les templates et fichiers statiques

# Configuration pour le mode debug (développement)
app.config['DEBUG'] = True
# En production, mettre à False pour la sécurité

# ============================================================================
# CONFIGURATION DE LA CONNEXION MONGODB
# ============================================================================
from config import MONGODB_URI, DATABASE_NAME, COLLECTION_NAME

# Variable globale pour stocker la connexion MongoDB
db = None
collection = None

# Variable globale pour le système ML (initialisé au premier usage)
ml_system = None


def connect_to_mongodb():
    """
    Établit la connexion à MongoDB Atlas.
    
    Cette fonction crée une connexion à la base de données MongoDB
    et stocke les références dans les variables globales.
    
    Retourne:
        bool: True si la connexion réussit, False sinon
    """
    global db, collection
    
    # #region agent log
    import json
    import time
    log_path = '/Users/adamandiaye/Documents/SDD1003/final/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'app.py:83',
                'message': 'connect_to_mongodb entry',
                'data': {
                    'db_name': DATABASE_NAME,
                    'collection_name': COLLECTION_NAME,
                    'uri_masked': MONGODB_URI[:50] + '...' if len(MONGODB_URI) > 50 else MONGODB_URI
                },
                'timestamp': int(time.time() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    try:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'app.py:97',
                    'message': 'Before MongoClient creation',
                    'data': {'uri_length': len(MONGODB_URI)},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Création du client MongoDB avec la chaîne de connexion
        client = MongoClient(MONGODB_URI)
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'app.py:100',
                    'message': 'MongoClient created successfully',
                    'data': {'client_type': str(type(client))},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Sélection de la base de données
        db = client[DATABASE_NAME]
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B',
                    'location': 'app.py:104',
                    'message': 'Database selected',
                    'data': {'db_name': DATABASE_NAME},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Sélection de la collection
        # Note : Si la collection n'existe pas, MongoDB la créera automatiquement
        collection = db[COLLECTION_NAME]
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'app.py:108',
                    'message': 'Collection selected, before ping',
                    'data': {'collection_name': COLLECTION_NAME},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Test de connexion : ping la base de données
        ping_result = client.admin.command('ping')
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'app.py:112',
                    'message': 'Ping successful',
                    'data': {'ping_result': str(ping_result)},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        print(f"✓ Connexion réussie à MongoDB Atlas")
        print(f"✓ Base de données: {DATABASE_NAME}")
        print(f"✓ Collection: {COLLECTION_NAME}")
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'E',
                    'location': 'app.py:118',
                    'message': 'connect_to_mongodb success',
                    'data': {'return_value': True},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        return True
        
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A,B,C,D,E',
                    'location': 'app.py:122',
                    'message': 'connect_to_mongodb exception',
                    'data': {
                        'exception_type': str(type(e).__name__),
                        'exception_message': str(e),
                        'exception_args': str(e.args) if hasattr(e, 'args') else 'N/A'
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Gestion des erreurs de connexion
        print(f"✗ Erreur de connexion à MongoDB: {e}")
        import traceback
        print(f"✗ Traceback complet: {traceback.format_exc()}")
        return False


def get_collection():
    """
    Récupère la collection MongoDB, en établissant la connexion si nécessaire.
    
    Cette fonction garantit que la collection est toujours disponible,
    même si la connexion a été perdue ou n'a pas encore été établie.
    
    Retourne:
        Collection MongoDB ou None en cas d'erreur
    """
    global collection
    
    # Si la collection n'est pas initialisée, établir la connexion
    if collection is None:
        connect_to_mongodb()
    
    return collection


# ============================================================================
# FONCTIONS POUR LA RECHERCHE VECTORIELLE
# ============================================================================

def create_simple_embedding(student):
    """
    Crée un embedding (vecteur) simple basé sur les champs numériques.
    
    Un embedding est une représentation vectorielle d'un étudiant.
    Chaque dimension du vecteur représente une caractéristique normalisée (0-1).
    
    Paramètres:
        student (dict): Le document étudiant MongoDB
        
    Retourne:
        list: Vecteur de 10 dimensions normalisées entre 0 et 1
        
    Dimensions du vecteur:
        [0] Âge normalisé (18-50 → 0-1)
        [1] Pression académique (0-5 → 0-1)
        [2] Satisfaction des études (0-5 → 0-1)
        [3] Stress financier (0-5 → 0-1)
        [4] Dépression (0 ou 1)
        [5] CGPA - Moyenne (0-10 → 0-1)
        [6] Genre (Male=1, Female=0)
        [7] Pensées suicidaires (Yes=1, No=0)
        [8] Pression au travail (0-5 → 0-1)
        [9] Heures d'étude (0-24 → 0-1)
    """
    def normalize(value, min_val, max_val):
        """Normalise une valeur entre 0 et 1."""
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)
    
    # Création du vecteur avec 10 dimensions
    return [
        normalize(student.get('age', 25), 18, 50),           # Âge normalisé
        student.get('academicPressure', 0) / 5.0,            # Pression académique
        student.get('studySatisfaction', 0) / 5.0,           # Satisfaction
        student.get('financialStress', 0) / 5.0,             # Stress financier
        float(student.get('depression', 0)),                 # Dépression
        student.get('cgpa', 5.0) / 10.0,                     # CGPA normalisé
        1.0 if student.get('gender') == 'Male' else 0.0,    # Genre
        1.0 if student.get('suicidalThoughts') == 'Yes' else 0.0,  # Pensées
        student.get('workPressure', 0) / 5.0,                # Pression travail
        normalize(student.get('studyHours', 8), 0, 24)       # Heures d'étude
    ]


def cosine_similarity(vec1, vec2):
    """
    Calcule la similarité cosinus entre deux vecteurs.
    
    La similarité cosinus mesure l'angle entre deux vecteurs.
    Plus l'angle est petit, plus les vecteurs sont similaires.
    
    Paramètres:
        vec1 (list): Premier vecteur
        vec2 (list): Deuxième vecteur
        
    Retourne:
        float: Score de similarité entre 0 (différent) et 1 (identique)
        
    Formule:
        cos(θ) = (A · B) / (||A|| × ||B||)
        où · est le produit scalaire et || || est la magnitude
    """
    # Produit scalaire : somme de (a1*b1 + a2*b2 + ... + an*bn)
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Magnitude (norme) de chaque vecteur : √(a1² + a2² + ... + an²)
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    # Éviter la division par zéro
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    
    # Calcul de la similarité cosinus
    return dot_product / (magnitude1 * magnitude2)


# ============================================================================
# ROUTES FLASK
# ============================================================================

@app.route('/')
def index():
    """
    Route principale - Affiche la page d'accueil avec la zone de recherche.
    
    Cette fonction rend le template HTML principal qui contient
    l'interface utilisateur pour la recherche.
    
    Retourne:
        HTML: Le template index.html
    """
    # #region agent log
    import json
    import time
    log_path = '/Users/adamandiaye/Documents/SDD1003/final/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'app.py:227',
                'message': 'index route entry',
                'data': {},
                'timestamp': int(time.time() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    # Vérification de la connexion MongoDB
    connection_status = connect_to_mongodb()
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A',
                'location': 'app.py:243',
                'message': 'index route after connect_to_mongodb',
                'data': {'connection_status': connection_status},
                'timestamp': int(time.time() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    # Passage du statut de connexion au template
    # Le template pourra afficher un message de succès ou d'erreur
    return render_template('index.html', 
                         connected=connection_status,
                         db_name=DATABASE_NAME,
                         collection_name=COLLECTION_NAME)


@app.route('/debug')
def debug():
    """
    Page de debug pour tester la barre de recherche.
    """
    return render_template('debug.html')


# ============================================================================
# ROUTES CRUD CREATION, LECTURE, MISE A JOUR, SUPPRESSION
# ============================================================================

@app.route('/api/student/<student_id>', methods=['GET'])
def get_student(student_id):
    """
    Récupère un étudiant spécifique par son ID MongoDB.
    
    Paramètres:
        student_id (str): L'ID MongoDB de l'étudiant (_id)
        
    Retourne:
        JSON: Les informations de l'étudiant
    """
    # #region agent log
    import json
    import time
    log_path = '/Users/adamandiaye/Documents/SDD1003/final/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'A,B',
                'location': 'app.py:427',
                'message': 'get_student entry',
                'data': {'student_id': student_id, 'student_id_type': type(student_id).__name__},
                'timestamp': int(time.time() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    try:
        from bson import ObjectId
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B',
                    'location': 'app.py:442',
                    'message': 'Before ObjectId conversion',
                    'data': {'student_id': student_id},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Récupérer la collection
        coll = get_collection()
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'app.py:449',
                    'message': 'After get_collection',
                    'data': {'collection_is_none': coll is None},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if coll is None:
            return jsonify({
                'success': False,
                'error': 'Impossible de se connecter à MongoDB'
            }), 500
        
        # #region agent log
        try:
            object_id = ObjectId(student_id)
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B',
                    'location': 'app.py:450',
                    'message': 'ObjectId created successfully',
                    'data': {'object_id_str': str(object_id)},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except Exception as obj_err:
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'B',
                        'location': 'app.py:450',
                        'message': 'ObjectId conversion failed',
                        'data': {'error': str(obj_err), 'student_id': student_id},
                        'timestamp': int(time.time() * 1000)
                    }) + '\n')
            except: pass
        # #endregion
        
        # Rechercher l'étudiant par _id
        student = coll.find_one({'_id': ObjectId(student_id)})
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'app.py:451',
                    'message': 'After find_one',
                    'data': {'student_found': student is not None},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if student:
            # Convertir ObjectId en string pour JSON
            student['_id'] = str(student['_id'])
            return jsonify({
                'success': True,
                'student': student
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Étudiant non trouvé'
            }), 404
            
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A,B,C,D,E',
                    'location': 'app.py:465',
                    'message': 'get_student exception',
                    'data': {
                        'exception_type': type(e).__name__,
                        'exception_message': str(e),
                        'student_id': student_id
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/student/<student_id>', methods=['PUT'])
def update_student(student_id):
    """
    Met à jour un étudiant existant.
    
    Paramètres:
        student_id (str): L'ID MongoDB de l'étudiant (_id)
        
    Body (JSON): Les champs à mettre à jour
        
    Retourne:
        JSON: Confirmation de la mise à jour
    """
    # #region agent log
    import json
    import time
    log_path = '/Users/adamandiaye/Documents/SDD1003/final/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C,D',
                'location': 'app.py:472',
                'message': 'update_student entry',
                'data': {'student_id': student_id},
                'timestamp': int(time.time() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    try:
        from bson import ObjectId
        
        # Récupérer la collection
        coll = get_collection()
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'app.py:489',
                    'message': 'update_student after get_collection',
                    'data': {'collection_is_none': coll is None},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if coll is None:
            return jsonify({
                'success': False,
                'error': 'Impossible de se connecter à MongoDB'
            }), 500
        
        # Récupérer les données à mettre à jour depuis le body de la requête
        update_data = request.json
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'app.py:497',
                    'message': 'update_student request.json received',
                    'data': {
                        'update_data_is_none': update_data is None,
                        'update_data_keys': list(update_data.keys()) if update_data else []
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if update_data is None:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400
        
        # Supprimer les champs qui ne doivent pas être modifiés
        update_data.pop('_id', None)  # Ne pas modifier l'_id
        update_data.pop('createdAt', None)  # Ne pas modifier la date de création
        
        # Mettre à jour la date de modification
        from datetime import datetime
        update_data['updatedAt'] = datetime.utcnow()
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B',
                    'location': 'app.py:508',
                    'message': 'update_student before update_one',
                    'data': {'student_id': student_id, 'update_keys': list(update_data.keys())},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Mettre à jour le document
        result = coll.update_one(
            {'_id': ObjectId(student_id)},
            {'$set': update_data}
        )
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'app.py:511',
                    'message': 'update_student after update_one',
                    'data': {
                        'modified_count': result.modified_count,
                        'matched_count': result.matched_count
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if result.modified_count > 0:
            # Récupérer le document mis à jour
            updated_student = coll.find_one({'_id': ObjectId(student_id)})
            updated_student['_id'] = str(updated_student['_id'])
            
            return jsonify({
                'success': True,
                'message': 'Étudiant mis à jour avec succès',
                'student': updated_student
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Aucune modification effectuée'
            }), 400
            
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A,B,C,D,E',
                    'location': 'app.py:529',
                    'message': 'update_student exception',
                    'data': {
                        'exception_type': type(e).__name__,
                        'exception_message': str(e),
                        'student_id': student_id
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """
    Supprime un étudiant.
    
    Paramètres:
        student_id (str): L'ID MongoDB de l'étudiant (_id)
        
    Retourne:
        JSON: Confirmation de la suppression
    """
    try:
        from bson import ObjectId
        
        # Récupérer la collection
        coll = get_collection()
        if coll is None:
            return jsonify({
                'success': False,
                'error': 'Impossible de se connecter à MongoDB'
            }), 500
        
        # Supprimer le document
        result = coll.delete_one({'_id': ObjectId(student_id)})
        
        if result.deleted_count > 0:
            return jsonify({
                'success': True,
                'message': 'Étudiant supprimé avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Étudiant non trouvé'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/similar/<student_id>', methods=['GET'])
def find_similar_students(student_id):
    """
    Trouve les étudiants similaires à un étudiant donné en utilisant la similarité vectorielle.
    
    Cette route utilise la recherche vectorielle pour trouver les étudiants
    ayant un profil similaire (âge, stress, dépression, performance, etc.).
    
    Paramètres:
        student_id (str): L'ID MongoDB de l'étudiant de référence (_id)
        
    Retourne:
        JSON: Liste des 10 étudiants les plus similaires avec leur score
    """
    try:
        from bson import ObjectId
        
        # Récupérer la collection
        coll = get_collection()
        if coll is None:
            return jsonify({
                'success': False,
                'error': 'Impossible de se connecter à MongoDB'
            }), 500
        
        # Récupérer l'étudiant de référence
        reference = coll.find_one({'_id': ObjectId(student_id)})
        
        if not reference:
            return jsonify({
                'success': False,
                'error': 'Étudiant non trouvé'
            }), 404
        
        # Créer l'embedding de l'étudiant de référence
        # Si l'étudiant a déjà un embedding stocké, l'utiliser, sinon le créer
        if 'embedding' in reference:
            reference_embedding = reference['embedding']
        else:
            reference_embedding = create_simple_embedding(reference)
        
        # Liste pour stocker les étudiants similaires avec leur score
        similar_students = []
        
        # Parcourir les étudiants et calculer la similarité
        # Note : Pour de meilleures performances, on limite à 2000 étudiants
        # Pour un dataset complet, considérez l'utilisation de MongoDB Vector Search
        for student in coll.find().limit(2000):
            # Ignorer l'étudiant de référence lui-même
            if str(student['_id']) == student_id:
                continue
            
            # Créer ou récupérer l'embedding
            if 'embedding' in student:
                student_embedding = student['embedding']
            else:
                student_embedding = create_simple_embedding(student)
            
            # Calculer la similarité cosinus
            similarity = cosine_similarity(reference_embedding, student_embedding)
            
            # Ajouter le score de similarité au document
            student['_id'] = str(student['_id'])
            student['similarity_score'] = round(similarity, 4)
            similar_students.append(student)
        
        # Trier par similarité décroissante (du plus similaire au moins similaire)
        similar_students.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Retourner les 10 plus similaires
        return jsonify({
            'success': True,
            'reference_id': reference['id'],
            'count': len(similar_students[:10]),
            'similar_students': similar_students[:10]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/student', methods=['POST'])
def create_student():
    """
    Crée un nouvel étudiant.
    
    Body (JSON): Les informations de l'étudiant
        
    Retourne:
        JSON: L'étudiant créé avec son ID
    """
    # #region agent log
    import json
    import time
    log_path = '/Users/adamandiaye/Documents/SDD1003/final/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'C',
                'location': 'app.py:663',
                'message': 'create_student entry',
                'data': {},
                'timestamp': int(time.time() * 1000)
            }) + '\n')
    except: pass
    # #endregion
    
    try:
        # Récupérer la collection
        coll = get_collection()
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A',
                    'location': 'app.py:675',
                    'message': 'create_student after get_collection',
                    'data': {'collection_is_none': coll is None},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if coll is None:
            return jsonify({
                'success': False,
                'error': 'Impossible de se connecter à MongoDB'
            }), 500
        
        # Récupérer les données depuis le body de la requête
        student_data = request.json
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'C',
                    'location': 'app.py:683',
                    'message': 'create_student request.json received',
                    'data': {
                        'student_data_is_none': student_data is None,
                        'student_data_keys': list(student_data.keys()) if student_data else []
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if student_data is None:
            return jsonify({
                'success': False,
                'error': 'Aucune donnée fournie'
            }), 400
        
        # Ajouter les timestamps
        from datetime import datetime
        student_data['createdAt'] = datetime.utcnow()
        student_data['updatedAt'] = datetime.utcnow()
        student_data['__v'] = 0
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'app.py:692',
                    'message': 'create_student before insert_one',
                    'data': {'student_id': student_data.get('id', 'N/A')},
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        # Insérer le nouveau document
        result = coll.insert_one(student_data)
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'D',
                    'location': 'app.py:692',
                    'message': 'create_student after insert_one',
                    'data': {
                        'has_inserted_id': result.inserted_id is not None,
                        'inserted_id': str(result.inserted_id) if result.inserted_id else None
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        if result.inserted_id:
            # Récupérer le document créé
            new_student = coll.find_one({'_id': result.inserted_id})
            new_student['_id'] = str(new_student['_id'])
            
            return jsonify({
                'success': True,
                'message': 'Étudiant créé avec succès',
                'student': new_student
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Échec de la création'
            }), 400
            
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A,B,C,D,E',
                    'location': 'app.py:710',
                    'message': 'create_student exception',
                    'data': {
                        'exception_type': type(e).__name__,
                        'exception_message': str(e)
                    },
                    'timestamp': int(time.time() * 1000)
                }) + '\n')
        except: pass
        # #endregion
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# ============================================================================
# ROUTES RECHERCHE CLASSIQUE
# ============================================================================
@app.route('/api/search', methods=['GET'])
def search():
    """
    API endpoint pour la recherche de documents.
    
    Cette route gère deux cas :
    - Cas a) Si query est vide ou espace : retourne les 10 premiers documents
    - Cas b) Si query contient du texte : recherche les documents correspondants
    
    Paramètres GET:
        query (str): Le terme de recherche (peut être vide)
        
    Retourne:
        JSON: Liste des documents trouvés avec leurs informations
    """
    try:
        # Récupérer la collection (établit la connexion si nécessaire)
        coll = get_collection()
        if coll is None:
            return jsonify({
                'success': False,
                'error': 'Impossible de se connecter à MongoDB'
            }), 500
        
        # Récupération du paramètre de recherche depuis l'URL
        # Exemple : /api/search?query=batman
        query = request.args.get('query', '').strip()
        
        # Cas a) : Si la recherche est vide ou contient seulement un espace
        # Retourner les 10 premiers documents comme spécifié
        if not query or query == ' ':
            # limit(10) : limite les résultats à 10 documents
            # sort('_id', 1) : trie par ID croissant (ordre d'insertion)
            results = list(coll.find().limit(10).sort('_id', 1))
            
        # Cas b) : Recherche avec le texte saisi
        else:
            search_filters = []
            
            # SYSTÈME DE RECHERCHE PAR PRÉFIXE
            # Permet de cibler un champ spécifique en utilisant la syntaxe : champ:valeur
            # Exemple : age:25, ville:Ahmedabad, id:166
            
            if ':' in query:
                # Recherche avec préfixe pour un champ spécifique
                parts = query.split(':', 1)
                field_prefix = parts[0].lower().strip()
                search_value = parts[1].strip()
                
                # Mapping des préfixes vers les noms de champs MongoDB
                field_mapping = {
                    'id': 'id',
                    'identifiant': 'id',
                    'genre': 'gender',
                    'gender': 'gender',
                    'age': 'age',
                    'âge': 'age',
                    'ville': 'city',
                    'city': 'city',
                    'profession': 'profession',
                    'degré': 'degree',
                    'degre': 'degree',
                    'degree': 'degree',
                    'cgpa': 'cgpa',
                    'moyenne': 'cgpa',
                    'pression': 'academicPressure',
                    'satisfaction': 'studySatisfaction',
                    'sommeil': 'sleepDuration',
                    'sleep': 'sleepDuration',
                    'habitudes': 'dietaryHabits',
                    'diet': 'dietaryHabits',
                    'stress': 'financialStress',
                    'depression': 'depression',
                    'dépression': 'depression',
                    'suicidaire': 'suicidalThoughts',
                    'suicide': 'suicidalThoughts',
                    'antecedents': 'familyHistoryMentalIllness',
                    'family': 'familyHistoryMentalIllness'
                }
                
                if field_prefix in field_mapping:
                    mongo_field = field_mapping[field_prefix]
                    
                    # Déterminer si c'est un champ numérique ou textuel
                    numeric_fields = ['id', 'age', 'academicPressure', 'studySatisfaction', 
                                    'financialStress', 'depression']
                    decimal_fields = ['cgpa']
                    
                    if mongo_field in numeric_fields:
                        # Champ numérique entier
                        try:
                            num_value = int(search_value)
                            search_filters.append({mongo_field: num_value})
                        except ValueError:
                            pass  # Valeur invalide, ignorer
                    elif mongo_field in decimal_fields:
                        # Champ numérique décimal
                        try:
                            float_value = float(search_value)
                            search_filters.append({mongo_field: float_value})
                        except ValueError:
                            pass  # Valeur invalide, ignorer
                    else:
                        # Champ textuel (recherche avec regex)
                        search_filters.append({mongo_field: {'$regex': search_value, '$options': 'i'}})
            
            else:
                # RECHERCHE GLOBALE (comme avant)
                # Recherche dans tous les champs sans préfixe
                
                # Recherche textuelle dans TOUS les champs texte
                search_filters.extend([
                    {'city': {'$regex': query, '$options': 'i'}},
                    {'profession': {'$regex': query, '$options': 'i'}},
                    {'degree': {'$regex': query, '$options': 'i'}},
                    {'gender': {'$regex': query, '$options': 'i'}},
                    {'sleepDuration': {'$regex': query, '$options': 'i'}},
                    {'dietaryHabits': {'$regex': query, '$options': 'i'}},
                    {'suicidalThoughts': {'$regex': query, '$options': 'i'}},
                    {'familyHistoryMentalIllness': {'$regex': query, '$options': 'i'}}
                ])
                
                # Si la requête est un nombre, chercher dans les champs numériques
                try:
                    num_value = int(query)
                    search_filters.extend([
                        {'id': num_value},
                        {'age': num_value},
                        {'academicPressure': num_value},
                        {'studySatisfaction': num_value},
                        {'financialStress': num_value},
                        {'depression': num_value}
                    ])
                except ValueError:
                    pass
                
                # Si la requête ressemble à un nombre décimal, chercher dans CGPA
                try:
                    float_value = float(query)
                    search_filters.append({'cgpa': float_value})
                except ValueError:
                    pass
            
            search_filter = {'$or': search_filters}
            
            # Exécution de la recherche avec limite de 10 résultats
            results = list(coll.find(search_filter).limit(10))
        
        # Conversion des résultats en format JSON
        # ObjectId MongoDB n'est pas JSON-serializable, donc on le convertit en string
        documents = []
        for doc in results:
            # Conversion de l'ObjectId en string pour JSON
            doc['_id'] = str(doc['_id'])
            documents.append(doc)
        
        # Retour des résultats en format JSON
        return jsonify({
            'success': True,
            'count': len(documents),
            'results': documents
        })
        
    except Exception as e:
        # Gestion des erreurs
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# ============================================================================
# ROUTES AUTCOMPLÉTION
# ============================================================================
@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    """
    API endpoint pour l'autocomplétion.
    
    Cette route retourne uniquement les titres correspondant à la recherche
    pour l'autocomplétion (liste déroulante).
    
    Paramètres GET:
        query (str): Le terme de recherche pour l'autocomplétion
        
    Retourne:
        JSON: Liste des titres correspondants (maximum 10)
    """
    try:
        # Récupérer la collection (établit la connexion si nécessaire)
        coll = get_collection()
        if coll is None:
            return jsonify({
                'success': False,
                'error': 'Impossible de se connecter à MongoDB'
            }), 500
        
        # Récupération du terme de recherche
        query = request.args.get('query', '').strip()
        
        # Si la recherche est vide, retourner une liste vide
        if not query:
            return jsonify({
                'success': True,
                'titles': []
            })
        
        # Recherche dans les champs pertinents pour les étudiants
        # On cherche dans : ville, profession, degré, genre
        search_filters = []
        
        # Recherche textuelle dans TOUS les champs texte (noms de champs en anglais)
        search_filters.extend([
            # Champs textuels
            {'city': {'$regex': query, '$options': 'i'}},                    # Ville
            {'profession': {'$regex': query, '$options': 'i'}},              # Profession
            {'degree': {'$regex': query, '$options': 'i'}},                  # Degré
            {'gender': {'$regex': query, '$options': 'i'}},                  # Genre
            {'sleepDuration': {'$regex': query, '$options': 'i'}},           # Durée du sommeil
            {'dietaryHabits': {'$regex': query, '$options': 'i'}},           # Habitudes alimentaires
            {'suicidalThoughts': {'$regex': query, '$options': 'i'}},        # Pensées suicidaires
            {'familyHistoryMentalIllness': {'$regex': query, '$options': 'i'}}  # Antécédents familiaux
        ])
        
        # Si c'est un nombre, chercher dans les champs numériques
        try:
            num_value = int(query)
            search_filters.extend([
                {'id': num_value},                      # ID
                {'age': num_value},                     # Âge
                {'academicPressure': num_value},        # Pression académique (0-5)
                {'studySatisfaction': num_value},       # Satisfaction des études (0-5)
                {'financialStress': num_value},         # Stress financier (0-5)
                {'depression': num_value}               # Dépression (0/1)
            ])
        except ValueError:
            pass
        
        # Si la requête ressemble à un nombre décimal, chercher dans CGPA
        try:
            float_value = float(query)
            search_filters.append({'cgpa': float_value})  # Moyenne cumulative
        except ValueError:
            pass
        
        search_filter = {'$or': search_filters}
        
        # Récupération des champs pertinents pour l'autocomplétion
        # On limite à 10 résultats pour l'autocomplétion
        results = list(coll.find(
            search_filter,
            {'id': 1, 'city': 1, 'profession': 1, 'degree': 1, 'gender': 1, 'age': 1, '_id': 0}
        ).limit(10))
        
        # Extraction des suggestions pour l'autocomplétion
        # Format : "ID - Âge ans - City - Profession (Degree)"
        titles = []
        for doc in results:
            id_val = doc.get('id', 'N/A')
            age = doc.get('age', '')
            city = doc.get('city', '')
            profession = doc.get('profession', '')
            degree = doc.get('degree', '')
            
            # Créer une suggestion descriptive avec l'âge
            suggestion = f"ID {id_val}"
            if age:
                suggestion += f" - {age} ans"
            if city:
                suggestion += f" - {city}"
            if profession:
                suggestion += f" - {profession}"
            if degree:
                suggestion += f" ({degree})"
            
            titles.append(suggestion)
        
        return jsonify({
            'success': True,
            'titles': titles
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ROUTES POUR RECHERCHE VECTORIELLE ML (AVANCÉE)
# ============================================================================

def get_ml_system():
    """
    Récupère ou initialise le système ML.
    
    Le système est initialisé une seule fois au premier appel (lazy loading),
    puis réutilisé pour les appels suivants.
    
    Retourne:
        StudentVectorML: Instance du système ML ou None si non disponible
    """
    global ml_system
    
    if not ML_AVAILABLE:
        return None
    
    if ml_system is None:
        print("Initialisation du système ML (premier appel, peut prendre 1-2 min)...")
        try:
            ml_system = StudentVectorML(
                mongodb_uri=MONGODB_URI,
                model_name='all-MiniLM-L6-v2',
                limit=2000  # Charger 2000 étudiants pour équilibre performance/qualité
            )
            print("✓ Système ML initialisé et prêt")
        except Exception as e:
            print(f"✗ Erreur d'initialisation ML: {e}")
            return None
    
    return ml_system


@app.route('/api/vector-search', methods=['POST'])
def vector_search_ml():
    """
    Effectue une recherche vectorielle ML avec post-traitement.
    
    Pipeline complet :
    1. Recherche vectorielle (Sentence Transformers + cosine similarity)
    2. Random Forest : Classification de la dépression
    3. Linear Regression : Prédiction du score de risque
    4. K-Means : Clustering des profils
    5. Génération des visualisations
    
    Body (JSON):
        query (str): Description textuelle de la recherche
                    Ex: "étudiant avec fort stress et peu de sommeil"
        top_k (int): Nombre de résultats (défaut: 10)
        
    Retourne:
        JSON: Résultats avec similarité + prédictions ML + chemins des visualisations
    """
    try:
        # Vérifier que le système ML est disponible
        if not ML_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Système ML non disponible. Installez : pip install -r requirements_ml.txt'
            }), 503
        
        # Récupérer les paramètres
        data = request.json
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'La requête ne peut pas être vide'
            }), 400
        
        # Récupérer le système ML (initialisation au premier appel)
        system = get_ml_system()
        
        if system is None:
            return jsonify({
                'success': False,
                'error': 'Impossible d\'initialiser le système ML'
            }), 500
        
        # Exécuter le pipeline complet
        results_df = system.pipeline(query, top_k=top_k)
        
        # Récupérer les chemins des visualisations générées depuis l'instance
        visualization_images = getattr(system, 'last_visualizations', {})
        query_id = getattr(system, 'last_query_id', '')
        
        # Construire les URLs des visualisations avec cache-busting
        visualization_urls = []
        if visualization_images:
            # Les fichiers sont dans static/ml_images, accessibles via /static/ml_images/
            # Ordre : Random Forest, Régression Linéaire, K-Means
            import time
            cache_buster = int(time.time() * 1000)  # Timestamp en millisecondes pour cache-busting
            for key in ['random_forest', 'linear_regression', 'kmeans']:
                if key in visualization_images:
                    # Extraire juste le nom du fichier
                    img_path = visualization_images[key]
                    filename = os.path.basename(img_path)
                    # Ajouter un paramètre de cache-busting pour forcer le rechargement
                    visualization_urls.append(f'/static/ml_images/{filename}?v={cache_buster}')
        
        # Si pas de visualisations, utiliser les chemins par défaut
        if not visualization_urls:
            visualization_urls = [
                '/api/visualization/1_random_forest_classification.png',
                '/api/visualization/2_linear_regression_relevance.png',
                '/api/visualization/3_kmeans_clustering.png'
            ]
        
        # Fonction helper pour récupérer une valeur de colonne de manière sécurisée
        def get_value(row, possible_names, default=None, convert_func=None):
            """Récupère une valeur d'une colonne en essayant plusieurs noms possibles"""
            for name in possible_names:
                if name in row and pd.notna(row[name]):
                    value = row[name]
                    if convert_func:
                        try:
                            return convert_func(value)
                        except (ValueError, TypeError):
                            return default
                    return value
            return default
        
        # Convertir les résultats en JSON
        results_list = []
        for _, row in results_df.iterrows():
            result = {
                '_id': str(get_value(row, ['_id', 'id'], '')),
                'id': int(get_value(row, ['id', 'ID', '_id'], 0)),
                'gender': get_value(row, ['gender', 'Gender'], ''),
                'age': int(get_value(row, ['age', 'Age'], 0)),
                'city': get_value(row, ['city', 'City'], ''),
                'profession': get_value(row, ['profession', 'Profession'], ''),
                'degree': get_value(row, ['degree', 'Degree'], ''),
                'cgpa': float(get_value(row, ['CGPA', 'cgpa', 'CGpa'], 0.0)),
                'academicPressure': int(get_value(row, ['Academic Pressure', 'academicPressure', 'academic_pressure'], 0)),
                'studySatisfaction': int(get_value(row, ['Study Satisfaction', 'studySatisfaction', 'study_satisfaction'], 0)),
                'financialStress': int(get_value(row, ['Financial Stress', 'financialStress', 'financial_stress'], 0)),
                'depression': int(get_value(row, ['Depression', 'depression'], 0)),
                'sleepDuration': get_value(row, ['sleepDuration', 'Sleep Duration', 'sleep_duration'], ''),
                'dietaryHabits': get_value(row, ['dietaryHabits', 'Dietary Habits', 'dietary_habits'], ''),
                'suicidalThoughts': get_value(row, ['suicidalThoughts', 'Suicidal Thoughts', 'suicidal_thoughts'], ''),
                'familyHistoryMentalIllness': get_value(row, ['familyHistoryMentalIllness', 'Family History Mental Illness', 'family_history_mental_illness'], ''),
                # Scores ML
                'similarity': round(float(get_value(row, ['similarity'], 0.0)), 4),
                # Random Forest : Classification
                'predicted_category': get_value(row, ['predicted_category'], 'Unknown'),
                'category_confidence': round(float(get_value(row, ['category_confidence'], 0.5)), 4),
                # Régression Linéaire : Score de pertinence
                'relevance_score': round(float(get_value(row, ['relevance_score'], 0.5)), 4),
                # K-Means : Cluster
                'cluster': int(get_value(row, ['cluster'], 0))
            }
            results_list.append(result)
        
        # Debug: afficher les URLs des visualisations
        print(f"📊 URLs des visualisations retournées: {visualization_urls}")
        print(f"📊 Nombre de visualisations: {len(visualization_urls)}")
        
        return jsonify({
            'success': True,
            'query': query,
            'count': len(results_list),
            'results': results_list,
            'visualizations': visualization_urls
        })
        
    except Exception as e:
        import traceback
        print("Erreur dans vector_search_ml:")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

#  VISUALISATIONS ML
@app.route('/api/visualization/<filename>')
def serve_visualization(filename):
    """
    Sert les fichiers de visualisation générés par les modèles ML.
    
    Les visualisations sont des graphiques PNG générés par matplotlib
    montrant les résultats des modèles ML.
    
    Paramètres:
        filename (str): Nom du fichier (ex: 1_random_forest_probability_20231201_120000.png)
        
    Retourne:
        Image PNG ou erreur 404
    """
    from flask import send_file
    
    # Chercher dans static/ml_images (nouveau emplacement)
    viz_path_ml = os.path.join('static', 'ml_images', filename)
    # Chercher aussi dans visualizations (ancien emplacement pour compatibilité)
    viz_path_old = os.path.join('visualizations', filename)
    
    if os.path.exists(viz_path_ml):
        return send_file(viz_path_ml, mimetype='image/png')
    elif os.path.exists(viz_path_old):
        return send_file(viz_path_old, mimetype='image/png')
    else:
        return jsonify({
            'success': False,
            'error': f'Visualisation non trouvée: {filename}. Effectuez une recherche ML d\'abord.'
        }), 404


# ============================================================================
# ROUTES POUR L'ANALYSE STATISTIQUE (EDF)
# ============================================================================

@app.route('/api/statistical/variables')
def get_statistical_variables():
    """
    Retourne la liste des variables quantitatives disponibles pour l'analyse EDF.
    """
    try:
        if not STATS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Module d\'analyse statistique non disponible'
            }), 503
        
        analyzer = StatisticalAnalyzer(MONGODB_URI, DATABASE_NAME, COLLECTION_NAME)
        analyzer.load_data(limit=5000)  # Charger un échantillon pour identifier les variables
        variables = analyzer.get_quantitative_variables()
        
        return jsonify({
            'success': True,
            'variables': variables
        })
    except Exception as e:
        import traceback
        print(f"Erreur dans get_statistical_variables: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistical/analyze', methods=['POST'])
def analyze_variable():
    """
    Effectue l'analyse EDF pour une variable quantitative.
    
    Body (JSON):
        variable_name (str): Nom de la variable à analyser
        distribution (str): Type de distribution théorique ('norm', 'expon', etc.)
    """
    try:
        if not STATS_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Module d\'analyse statistique non disponible'
            }), 503
        
        data = request.json
        variable_name = data.get('variable_name', '').strip()
        distribution = data.get('distribution', 'norm')
        
        if not variable_name:
            return jsonify({
                'success': False,
                'error': 'Le nom de la variable est requis'
            }), 400
        
        analyzer = StatisticalAnalyzer(MONGODB_URI, DATABASE_NAME, COLLECTION_NAME)
        analyzer.load_data(limit=10000)
        
        # Calculer l'EDF et créer la visualisation
        image_path = analyzer.visualize_edf_cdf(variable_name, distribution)
        
        # Obtenir les statistiques
        stats_summary = analyzer.get_statistics_summary(variable_name)
        
        # Calculer l'EDF pour les données JSON
        x_edf, y_edf, n = analyzer.calculate_edf(variable_name)
        
        # Convertir en listes pour JSON
        edf_data = {
            'x_values': x_edf.tolist()[:100],  # Limiter à 100 points pour la réponse JSON
            'y_values': y_edf.tolist()[:100],
            'n': int(n)
        }
        
        # Extraire le nom du fichier pour l'URL
        filename = os.path.basename(image_path)
        image_url = f'/static/statistical_analysis/{filename}'
        
        return jsonify({
            'success': True,
            'variable': variable_name,
            'distribution': distribution,
            'statistics': stats_summary,
            'edf_data': edf_data,
            'image_url': image_url,
            'formula': 'F_n(x) = (1/n) * Σ_{i=1}^{n} 1_{X_i ≤ x}'
        })
        
    except Exception as e:
        import traceback
        print(f"Erreur dans analyze_variable: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ROUTES STATUT ML
@app.route('/api/ml-status')
def ml_status():
    """
    Vérifie le statut du système ML.
    
    Retourne:
        JSON: Statut du système ML (disponible ou non)
    """
    return jsonify({
        'ml_available': ML_AVAILABLE,
        'ml_initialized': ml_system is not None,
        'message': 'Système ML prêt' if ML_AVAILABLE else 'Installez requirements_ml.txt'
    })


@app.route('/api/embeddings/clear', methods=['POST'])
def clear_embeddings():
    """
    Supprime tous les embeddings de la base de données.
    
    Retourne:
        JSON: Statistiques de suppression
    """
    try:
        if not ML_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Module ML non disponible'
            }), 503
        
        system = get_ml_system()
        if system is None:
            return jsonify({
                'success': False,
                'error': 'Impossible d\'initialiser le système ML'
            }), 500
        
        stats = system.clear_embeddings()
        
        return jsonify({
            'success': True,
            'message': f'{stats["deleted"]} embeddings supprimés',
            'deleted': stats['deleted'],
            'total_with_embeddings': stats['total_with_embeddings']
        })
        
    except Exception as e:
        import traceback
        print(f"Erreur dans clear_embeddings: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ROUTES RÉGÉNÉRATION DES EMBEDDINGS
@app.route('/api/embeddings/regenerate', methods=['POST'])
def regenerate_embeddings():
    """
    Supprime et régénère tous les embeddings.
    
    Body (JSON):
        limit (int, optionnel): Nombre maximum de documents à traiter
        force (bool, optionnel): Forcer la régénération même si embeddings existent
        
    Retourne:
        JSON: Statistiques de régénération
    """
    try:
        if not ML_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Module ML non disponible'
            }), 503
        
        data = request.json or {}
        limit = data.get('limit', None)
        
        system = get_ml_system()
        if system is None:
            return jsonify({
                'success': False,
                'error': 'Impossible d\'initialiser le système ML'
            }), 500
        
        print(f"🔄 Démarrage de la régénération des embeddings (limit={limit})...")
        stats = system.regenerate_embeddings(limit=limit)
        
        return jsonify({
            'success': True,
            'message': f'{stats["regenerated"]} embeddings régénérés',
            'deleted': stats['deleted'],
            'regenerated': stats['regenerated'],
            'dimension': stats['dimension']
        })
        
    except Exception as e:
        import traceback
        print(f"Erreur dans regenerate_embeddings: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ============================================================================
if __name__ == '__main__':
    """
    Point d'entrée principal.
    Cette section s'exécute uniquement si le script est lancé directement.
    """
    # Connexion à MongoDB au démarrage
    print("Connexion à MongoDB Atlas...")
    connect_to_mongodb()
    
    # Démarrage du serveur Flask
    # host='0.0.0.0' : accessible depuis toutes les interfaces réseau
    # port=5001 : port alternatif (5000 est souvent utilisé par AirPlay sur macOS)
    # debug=True : mode debug activé (rechargement automatique)
    print("\nDémarrage du serveur Flask...")
    print("Accédez à l'application sur: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)

