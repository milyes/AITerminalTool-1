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

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API pour analyser du texte"""
    data = request.json
    text = data.get('text', '')
    analysis_type = data.get('type', 'sentiment')
    
    if not text:
        return jsonify({"error": "Aucun texte fourni"}), 400
    
    try:
        from aiterminal.config import Config
        from aiterminal.ai_services import AIService
        
        config = Config()
        ai_service = AIService(config)
        
        if analysis_type == 'sentiment':
            result = ai_service.analyze_sentiment(text)
        elif analysis_type == 'summary':
            result = {"summary": ai_service.summarize_text(text)}
        elif analysis_type == 'entities':
            result = ai_service.extract_entities(text)
        else:
            return jsonify({"error": f"Type d'analyse non reconnu: {analysis_type}"}), 400
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system', methods=['GET'])
def system_info():
    """API pour récupérer des informations système"""
    info_type = request.args.get('type', 'all')
    
    try:
        from aiterminal.config import Config
        from aiterminal.system import SystemService
        
        config = Config()
        system_service = SystemService(config)
        
        if info_type == 'cpu':
            result = system_service.get_cpu_info()
        elif info_type == 'memory':
            result = system_service.get_memory_info()
        elif info_type == 'disk':
            result = system_service.get_disk_info()
        elif info_type == 'network':
            result = system_service.get_network_info()
        elif info_type == 'all':
            result = {
                'cpu': system_service.get_cpu_info(),
                'memory': system_service.get_memory_info(),
                'disk': system_service.get_disk_info(),
                'network': system_service.get_network_info()
            }
        else:
            return jsonify({"error": f"Type d'information non reconnu: {info_type}"}), 400
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/ping', methods=['POST'])
def ping():
    """API pour effectuer un ping"""
    data = request.json
    host = data.get('host', '')
    count = data.get('count', 4)
    
    if not host:
        return jsonify({"error": "Aucun hôte fourni"}), 400
    
    try:
        from aiterminal.config import Config
        from aiterminal.network import NetworkService
        
        config = Config()
        network_service = NetworkService(config)
        
        results = network_service.ping(host, count)
        summary = network_service.get_ping_summary(results)
        
        return jsonify({"results": results, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/network/http', methods=['POST'])
def http_request():
    """API pour effectuer une requête HTTP"""
    data = request.json
    url = data.get('url', '')
    method = data.get('method', 'GET')
    headers = data.get('headers', None)
    request_data = data.get('data', None)
    timeout = data.get('timeout', 10)
    
    if not url:
        return jsonify({"error": "Aucune URL fournie"}), 400
    
    try:
        from aiterminal.config import Config
        from aiterminal.network import NetworkService
        
        config = Config()
        network_service = NetworkService(config)
        
        result = network_service.http_request(
            url=url,
            method=method,
            headers_str=headers,
            data_str=request_data,
            timeout=timeout
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    """Point d'entrée principal de l'application CLI"""
    from aiterminal.cli import run_cli
    run_cli()

if __name__ == "__main__":
    main()
