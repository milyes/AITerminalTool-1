"""
Module des services d'IA.
Gère les interactions avec les APIs d'IA comme OpenAI.
"""

import os
import json
import logging
from openai import OpenAI
from typing import Optional, Dict, Any

from .config import Config

logger = logging.getLogger(__name__)

class AIService:
    """Service pour interagir avec les APIs d'IA."""
    
    def __init__(self, config: Config):
        """
        Initialise le service IA.
        
        Args:
            config (Config): L'objet de configuration.
        """
        self.config = config
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """
        Initialise le client OpenAI.
        
        Returns:
            OpenAI: Le client OpenAI initialisé.
        """
        api_key = self.config.get_api_key()
        if not api_key:
            logger.warning("Clé API OpenAI non configurée")
        
        return OpenAI(api_key=api_key)
    
    def generate_text(self, prompt: str, model: Optional[str] = None, temperature: Optional[float] = None) -> str:
        """
        Génère du texte à partir d'un prompt en utilisant OpenAI.
        
        Args:
            prompt (str): Le prompt à envoyer à l'IA.
            model (str, optional): Le modèle à utiliser. Si None, utilise celui configuré.
            temperature (float, optional): La température pour la génération. Si None, utilise celle configurée.
            
        Returns:
            str: Le texte généré.
            
        Raises:
            Exception: Si une erreur se produit lors de la génération.
        """
        try:
            model = model or self.config.get_model()
            temperature = temperature if temperature is not None else self.config.get_value("temperature", 0.7)
            max_tokens = self.config.get_value("max_tokens", 2000)
            
            if not self.config.get_api_key():
                return "Erreur: Clé API OpenAI non configurée. Utilisez 'aiterminal config --api-key=votre-clé' pour configurer."
            
            response = self.client.chat.completions.create(
                model=model,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur lors de la génération de texte: {str(e)}")
            raise Exception(f"Erreur lors de la génération de texte: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyse le sentiment d'un texte.
        
        Args:
            text (str): Le texte à analyser.
            
        Returns:
            Dict[str, Any]: Les résultats de l'analyse de sentiment.
            
        Raises:
            Exception: Si une erreur se produit lors de l'analyse.
        """
        try:
            model = self.config.get_model()
            
            if not self.config.get_api_key():
                return {"error": "Clé API OpenAI non configurée. Utilisez 'aiterminal config --api-key=votre-clé' pour configurer."}
            
            prompt = (
                "Effectue une analyse de sentiment sur le texte suivant et réponds exclusivement au format JSON. "
                "Le JSON doit contenir: 'sentiment' (positive, negative, ou neutral), 'score' (entre -1 et 1), "
                "et 'explanation' (courte explication).\n\n"
                f"Texte : {text}"
            )
            
            response = self.client.chat.completions.create(
                model=model,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de sentiment: {str(e)}")
            raise Exception(f"Erreur lors de l'analyse de sentiment: {str(e)}")
    
    def summarize_text(self, text: str) -> str:
        """
        Résume un texte.
        
        Args:
            text (str): Le texte à résumer.
            
        Returns:
            str: Le résumé du texte.
            
        Raises:
            Exception: Si une erreur se produit lors du résumé.
        """
        try:
            prompt = f"Résume le texte suivant de manière concise tout en conservant les points clés:\n\n{text}"
            return self.generate_text(prompt)
        except Exception as e:
            logger.error(f"Erreur lors du résumé: {str(e)}")
            raise Exception(f"Erreur lors du résumé: {str(e)}")
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extrait les entités nommées d'un texte.
        
        Args:
            text (str): Le texte à analyser.
            
        Returns:
            Dict[str, Any]: Les entités extraites.
            
        Raises:
            Exception: Si une erreur se produit lors de l'extraction.
        """
        try:
            model = self.config.get_model()
            
            if not self.config.get_api_key():
                return {"error": "Clé API OpenAI non configurée. Utilisez 'aiterminal config --api-key=votre-clé' pour configurer."}
            
            prompt = (
                "Extrait les entités nommées du texte suivant et réponds exclusivement au format JSON. "
                "Les catégories à identifier: personnes, lieux, organisations, dates, etc. "
                "Le format doit être: {'entities': {'personnes': [...], 'lieux': [...], ...}}\n\n"
                f"Texte : {text}"
            )
            
            response = self.client.chat.completions.create(
                model=model,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction d'entités: {str(e)}")
            raise Exception(f"Erreur lors de l'extraction d'entités: {str(e)}")
    
    def generate_code(self, description: str, language: str = "python") -> str:
        """
        Génère du code basé sur une description.
        
        Args:
            description (str): Description du code à générer.
            language (str): Langage de programmation cible.
            
        Returns:
            str: Le code généré.
            
        Raises:
            Exception: Si une erreur se produit lors de la génération.
        """
        try:
            prompt = (
                f"Génère du code {language} pour la tâche suivante. "
                f"Retourne uniquement le code, sans explication ni commentaire d'introduction:\n\n"
                f"{description}"
            )
            
            return self.generate_text(prompt)
        except Exception as e:
            logger.error(f"Erreur lors de la génération de code: {str(e)}")
            raise Exception(f"Erreur lors de la génération de code: {str(e)}")
