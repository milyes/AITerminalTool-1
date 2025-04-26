"""
Module d'utilitaires.
Contient des fonctions et classes utilitaires pour l'application.
"""

import json
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

def format_response(response: Any) -> str:
    """
    Formate une réponse pour l'affichage dans la console.
    
    Args:
        response (Any): La réponse à formater.
        
    Returns:
        str: La réponse formatée.
    """
    try:
        if isinstance(response, (dict, list)):
            # Si c'est déjà un dict ou une liste, le formater en JSON
            return json.dumps(response, indent=2, ensure_ascii=False)
        elif isinstance(response, str):
            # Si c'est une chaîne, essayer de la parser comme JSON
            try:
                parsed = json.loads(response)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON, retourner la chaîne telle quelle
                return response
        else:
            # Pour les autres types, convertir en chaîne
            return str(response)
    except Exception as e:
        logger.error(f"Erreur lors du formatage de la réponse: {str(e)}")
        return str(response)
