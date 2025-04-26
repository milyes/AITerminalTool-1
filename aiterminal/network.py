"""
Module des services réseau.
Gère les fonctionnalités réseau comme les requêtes HTTP et les pings.
"""

import json
import logging
import subprocess
import platform
import re
import requests
from typing import Dict, List, Any, Optional
import time

from .config import Config

logger = logging.getLogger(__name__)

class NetworkService:
    """Service pour les fonctionnalités réseau."""
    
    def __init__(self, config: Config):
        """
        Initialise le service réseau.
        
        Args:
            config (Config): L'objet de configuration.
        """
        self.config = config
    
    def ping(self, host: str, count: int = 4) -> List[Dict[str, Any]]:
        """
        Envoie des requêtes ping à un hôte.
        
        Args:
            host (str): L'hôte à pinguer.
            count (int): Le nombre de paquets à envoyer.
            
        Returns:
            List[Dict[str, Any]]: Résultats des pings.
            
        Raises:
            Exception: Si une erreur se produit lors du ping.
        """
        results = []
        
        try:
            # Détermine la commande ping selon le système d'exploitation
            os_name = platform.system().lower()
            
            if os_name == "windows":
                ping_cmd = ["ping", "-n", str(count), host]
            else:  # Linux, macOS, etc.
                ping_cmd = ["ping", "-c", str(count), host]
            
            process = subprocess.Popen(
                ping_cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Traiter chaque ligne de sortie
            for line in process.stdout:
                # Pour les lignes contenant une réponse de ping
                if "bytes from" in line.lower() or "Reply from" in line:
                    # Extraire le temps (ms)
                    time_match = re.search(r"time=(\d+\.?\d*)", line)
                    time_ms = float(time_match.group(1)) if time_match else None
                    
                    results.append({
                        "success": True,
                        "message": line.strip(),
                        "time_ms": time_ms
                    })
                # Pour les lignes indiquant une absence de réponse
                elif "request timed out" in line.lower() or "destination host unreachable" in line.lower():
                    results.append({
                        "success": False,
                        "message": line.strip(),
                        "time_ms": None
                    })
            
            # Si aucun résultat n'a été obtenu, c'est probablement une erreur
            if not results:
                stderr_output = process.stderr.read()
                if stderr_output:
                    raise Exception(f"Erreur de ping: {stderr_output}")
                else:
                    raise Exception("Aucune réponse reçue du ping")
            
            return results
        except Exception as e:
            logger.error(f"Erreur lors du ping: {str(e)}")
            raise Exception(f"Erreur lors du ping: {str(e)}")
    
    def get_ping_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un résumé des résultats de ping.
        
        Args:
            results (List[Dict[str, Any]]): Résultats des pings.
            
        Returns:
            Dict[str, Any]: Résumé des pings.
        """
        sent = len(results)
        received = sum(1 for r in results if r.get("success", False))
        lost = sent - received
        loss_percent = (lost / sent * 100) if sent > 0 else 0
        
        times = [r.get("time_ms") for r in results if r.get("success", False) and r.get("time_ms") is not None]
        min_rtt = min(times) if times else 0
        max_rtt = max(times) if times else 0
        avg_rtt = sum(times) / len(times) if times else 0
        
        return {
            "sent": sent,
            "received": received,
            "lost": lost,
            "loss_percent": round(loss_percent, 1),
            "min_rtt": round(min_rtt, 2) if min_rtt else 0,
            "max_rtt": round(max_rtt, 2) if max_rtt else 0,
            "avg_rtt": round(avg_rtt, 2) if avg_rtt else 0
        }
    
    def http_request(
        self, 
        url: str, 
        method: str = "GET", 
        headers_str: Optional[str] = None,
        data_str: Optional[str] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Envoie une requête HTTP.
        
        Args:
            url (str): L'URL pour la requête.
            method (str): La méthode HTTP (GET, POST, etc.).
            headers_str (str, optional): Les en-têtes au format JSON.
            data_str (str, optional): Les données à envoyer (pour POST, PUT).
            timeout (int): Le timeout en secondes.
            
        Returns:
            Dict[str, Any]: Le résultat de la requête.
            
        Raises:
            Exception: Si une erreur se produit lors de la requête.
        """
        try:
            # Préparer les en-têtes
            headers = {}
            if headers_str:
                try:
                    headers = json.loads(headers_str)
                except json.JSONDecodeError:
                    raise Exception("Format d'en-têtes JSON invalide")
            
            # Préparer les données
            data = None
            if data_str:
                # Tenter de parser comme JSON, sinon utiliser comme données brutes
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    data = data_str
            
            # Envoyer la requête
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=data if isinstance(data, dict) else None,
                data=data if not isinstance(data, dict) else None,
                timeout=timeout
            )
            
            # Préparer le résultat
            result = {
                "status_code": response.status_code,
                "reason": response.reason,
                "headers": dict(response.headers),
                "url": response.url,
            }
            
            # Tenter de parser le contenu comme JSON
            try:
                result["content"] = response.json()
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON, utiliser le texte brut
                result["content"] = response.text
            
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête HTTP: {str(e)}")
            raise Exception(f"Erreur lors de la requête HTTP: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            raise Exception(f"Erreur inattendue: {str(e)}")
