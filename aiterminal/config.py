"""
Module de gestion de la configuration.
Gère le chargement et l'enregistrement des paramètres de configuration.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "api_key": "",
    "model": "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
    "max_tokens": 2000,
    "temperature": 0.7,
    "search_engine": "duckduckgo",
    "timeout": 30,
    "history_size": 10
}

class Config:
    """Classe pour gérer la configuration de l'application."""
    
    def __init__(self, config_path=None):
        """
        Initialise la configuration.
        
        Args:
            config_path (str, optional): Chemin vers le fichier de configuration. 
                                         Par défaut, utilise config.json dans le répertoire courant.
        """
        self.config_path = config_path or os.path.join(os.getcwd(), "config.json")
        self.config = self._load_config()
    
    def _load_config(self):
        """
        Charge la configuration depuis le fichier.
        Si le fichier n'existe pas, crée une configuration par défaut.
        
        Returns:
            dict: La configuration chargée.
        """
        try:
            if not os.path.exists(self.config_path):
                logger.info(f"Fichier de configuration non trouvé à {self.config_path}. Création par défaut.")
                self._save_config(DEFAULT_CONFIG)
                return DEFAULT_CONFIG.copy()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # S'assurer que toutes les clés par défaut sont présentes
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
                    
            return config
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
            logger.info("Utilisation de la configuration par défaut.")
            return DEFAULT_CONFIG.copy()
    
    def _save_config(self, config):
        """
        Enregistre la configuration dans le fichier.
        
        Args:
            config (dict): La configuration à enregistrer.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la configuration: {str(e)}")
    
    def get_config(self):
        """
        Récupère la configuration actuelle.
        
        Returns:
            dict: La configuration actuelle.
        """
        return self.config.copy()
    
    def get_value(self, key, default=None):
        """
        Récupère une valeur spécifique de la configuration.
        
        Args:
            key (str): La clé de la valeur à récupérer.
            default: Valeur par défaut si la clé n'existe pas.
            
        Returns:
            La valeur associée à la clé ou la valeur par défaut si la clé n'existe pas.
        """
        return self.config.get(key, default)
    
    def set_value(self, key, value):
        """
        Définit une valeur dans la configuration et l'enregistre.
        
        Args:
            key (str): La clé à définir.
            value: La valeur à associer à la clé.
        """
        self.config[key] = value
        self._save_config(self.config)
    
    def get_api_key(self):
        """
        Récupère la clé API d'OpenAI, en priorité depuis les variables d'environnement.
        
        Returns:
            str: La clé API OpenAI.
        """
        return os.environ.get("OPENAI_API_KEY", self.config.get("api_key", ""))
    
    def get_model(self):
        """
        Récupère le modèle OpenAI configuré.
        
        Returns:
            str: Le nom du modèle OpenAI.
        """
        return self.config.get("model", "gpt-4o")  # the newest OpenAI model is "gpt-4o"
