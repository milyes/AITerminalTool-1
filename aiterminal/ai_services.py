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
            
            try:
                response = self.client.chat.completions.create(
                    model=model,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response.choices[0].message.content
            except Exception as api_error:
                logger.error(f"Erreur API OpenAI: {str(api_error)}")
                return self._fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération de texte: {str(e)}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """
        Fournit une réponse par défaut lorsque l'API OpenAI n'est pas disponible.
        
        Args:
            prompt (str): Le prompt original.
            
        Returns:
            str: Une réponse par défaut.
        """
        # Réponses simples pour des cas courants
        if "bonjour" in prompt.lower() or "salut" in prompt.lower():
            return "Bonjour ! Je suis AITerminal, votre assistant en mode hors ligne. Comment puis-je vous aider ?"
            
        elif "comment" in prompt.lower() and ("vas" in prompt.lower() or "allez" in prompt.lower()):
            return "Je fonctionne actuellement en mode hors ligne, mais je suis prêt à vous aider avec des fonctionnalités de base."
            
        elif "aide" in prompt.lower() or "help" in prompt.lower():
            return "Je peux vous aider avec plusieurs tâches, même en mode hors ligne. Vous pouvez utiliser des commandes comme 'ping', 'http', ou 'système' pour accéder à diverses fonctionnalités."
            
        elif "merci" in prompt.lower():
            return "Je vous en prie ! N'hésitez pas si vous avez besoin d'autre chose."
            
        else:
            return ("Je fonctionne actuellement en mode hors ligne car la connexion à l'API OpenAI n'est pas disponible. "
                   "Veuillez vérifier votre clé API ou votre connexion internet. "
                   "Vous pouvez toujours utiliser les fonctionnalités réseau, système et autres commandes qui ne nécessitent pas l'IA.")
    
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
            
            try:
                response = self.client.chat.completions.create(
                    model=model,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                return result
            except Exception as api_error:
                logger.error(f"Erreur API OpenAI: {str(api_error)}")
                return self._fallback_sentiment_analysis(text)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de sentiment: {str(e)}")
            return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Fournit une analyse de sentiment par défaut lorsque l'API OpenAI n'est pas disponible.
        
        Args:
            text (str): Le texte à analyser.
            
        Returns:
            Dict[str, Any]: Une analyse de sentiment par défaut.
        """
        # Analyse simpliste basée sur des mots-clés
        text_lower = text.lower()
        
        # Mots positifs et négatifs en français
        positive_words = ["bon", "bien", "super", "excellent", "génial", "heureux", "content", "merci", "bravo", "aimer"]
        negative_words = ["mauvais", "mal", "terrible", "horrible", "nul", "triste", "déçu", "problème", "erreur", "détester"]
        
        # Compter les mots positifs et négatifs
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Déterminer le sentiment et le score
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = max(-0.9, -0.5 - (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            "sentiment": sentiment,
            "score": round(score, 1),
            "explanation": "Analyse effectuée en mode hors ligne avec une précision limitée.",
            "offline_mode": True
        }
    
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
            
            try:
                response = self.client.chat.completions.create(
                    model=model,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                return result
            except Exception as api_error:
                logger.error(f"Erreur API OpenAI: {str(api_error)}")
                return self._fallback_entity_extraction(text)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction d'entités: {str(e)}")
            return self._fallback_entity_extraction(text)
    
    def _fallback_entity_extraction(self, text: str) -> Dict[str, Any]:
        """
        Fournit une extraction d'entités par défaut lorsque l'API OpenAI n'est pas disponible.
        
        Args:
            text (str): Le texte à analyser.
            
        Returns:
            Dict[str, Any]: Des entités extraites par défaut.
        """
        # Analyse simpliste basée sur des patterns communs
        import re
        
        text_lines = text.split('\n')
        words = re.findall(r'\b[A-Z][a-zA-Z]*\b', text)  # Mots commençant par une majuscule
        dates = re.findall(r'\b\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{2,4}\b', text)  # Dates au format JJ/MM/AAAA
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)  # Emails
        urls = re.findall(r'https?://[^\s]+', text)  # URLs
        
        # Tentative d'identification de lieux communs français
        lieux_communs = ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Lille", "France", "Europe"]
        lieux_trouves = [lieu for lieu in lieux_communs if lieu in text]
        
        return {
            "entities": {
                "personnes": words[:5],  # Premiers mots capitalisés comme noms possibles
                "lieux": lieux_trouves,
                "dates": dates,
                "emails": emails,
                "urls": urls
            },
            "offline_mode": True,
            "note": "Extraction effectuée en mode hors ligne avec une précision limitée."
        }
    
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
