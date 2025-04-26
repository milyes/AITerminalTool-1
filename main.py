#!/usr/bin/env python3
"""
AITerminal - Un terminal intelligent en ligne de commande
qui intègre des services d'IA, des fonctionnalités réseau
et des capacités d'analyse internet.
"""

import sys
import os
import logging
from flask import Flask, render_template, jsonify, request

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter le répertoire courant au chemin de recherche
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Créer l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "aiterminal_secret_key")

@app.route('/')
def index():
    """Page d'accueil de l'interface web d'AITerminal"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """API pour générer du contenu avec l'IA"""
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"error": "Aucun prompt fourni"}), 400
    
    try:
        from aiterminal.config import Config
        from aiterminal.ai_services import AIService
        
        config = Config()
        ai_service = AIService(config)
        
        result = ai_service.generate_text(prompt)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    """Point d'entrée principal de l'application CLI"""
    from aiterminal.cli import run_cli
    run_cli()

if __name__ == "__main__":
    main()
