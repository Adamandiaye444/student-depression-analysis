#!/bin/bash
# Script de lancement de l'application Flask
# ============================================
# Ce script active l'environnement virtuel et lance l'application Flask

# Aller dans le répertoire du script
cd "$(dirname "$0")"

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    echo "✓ Activation de l'environnement virtuel..."
    source venv/bin/activate
    PYTHON_CMD="python3"
else
    echo "  Avertissement: Environnement virtuel non trouvé."
    echo "   Créez-en un avec: python3 -m venv venv"
    PYTHON_CMD="python3"
fi

# Vérifier que Python est disponible
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo " Erreur: Python3 n'est pas installé ou n'est pas dans le PATH"
    exit 
fi

# Vérifier que Flask est installé
if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
    echo " Flask n'est pas installé. Installation des dépendances..."
    pip install -r requirements.txt
fi

# Vérifier que le port 5001 est libre
if lsof -ti:5001 &> /dev/null; then
    echo "  Le port 5001 est déjà utilisé. Arrêt du processus existant..."
    kill -9 $(lsof -ti:5001) 2>/dev/null
    sleep 1
fi

# Lancer l'application Flask
echo ""
echo " Démarrage de l'application Flask..."
echo " Accédez à l'application sur : http://localhost:5001"
echo "   (Appuyez sur Ctrl+C pour arrêter)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""


# Fonction pour ouvrir le navigateur (multi-plateforme)
open_browser() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open http://localhost:5001
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open http://localhost:5001 2>/dev/null
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        start http://localhost:5001 2>/dev/null
    fi
}

# Lancer Flask en arrière-plan
venv/bin/python3 app.py > /tmp/flask_app_$$.log 2>&1 &
FLASK_PID=$!

# Attendre que le serveur démarre (vérifier que le port est actif)
echo "⏳ Attente du démarrage du serveur..."
BROWSER_OPENED=0
for i in {1..15}; do
    # Vérifier si le port est actif
    if lsof -ti:5001 &> /dev/null; then
        # Vérifier si le serveur répond (avec curl si disponible, sinon juste vérifier le port)
        if command -v curl &> /dev/null; then
            if curl -s http://localhost:5001 > /dev/null 2>&1; then
                if [ $BROWSER_OPENED -eq 0 ]; then
                    echo " Serveur démarré avec succès!"
                    sleep 2
                    # Ouvrir le navigateur automatiquement
                    echo "🌐 Ouverture du navigateur..."
                    open_browser
                    BROWSER_OPENED=1
                fi
            fi
        else
            # Si curl n'est pas disponible, attendre un peu plus et ouvrir quand même
            if [ $i -ge 3 ] && [ $BROWSER_OPENED -eq 0 ]; then
                echo " Serveur démarré avec succès!"
                sleep 2
                echo "🌐 Ouverture du navigateur..."
                open_browser
                BROWSER_OPENED=1
            fi
        fi
    fi
    sleep 1
done

# Afficher les logs en temps réel
echo ""
echo "📋 Logs du serveur (Ctrl+C pour arrêter):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -f /tmp/flask_app_$$.log &
TAIL_PID=$!

# Fonction de nettoyage
cleanup() {
    echo ""
    echo " Arrêt du serveur..."
    kill $FLASK_PID 2>/dev/null
    kill $TAIL_PID 2>/dev/null
    rm -f /tmp/flask_app_$$.log
    exit 0
}

# Capturer Ctrl+C
trap cleanup INT TERM

# Attendre que Flask se termine
wait $FLASK_PID

# Nettoyer
cleanup

