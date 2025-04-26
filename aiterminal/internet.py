"""
Module des services internet.
Gère les fonctionnalités de recherche et d'analyse internet.
"""

import logging
import re
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

from .config import Config

logger = logging.getLogger(__name__)

class InternetService:
    """Service pour les fonctionnalités d'internet."""
    
    def __init__(self, config: Config):
        """
        Initialise le service internet.
        
        Args:
            config (Config): L'objet de configuration.
        """
        self.config = config
        self.search_engine = config.get_value("search_engine", "duckduckgo")
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Effectue une recherche sur internet.
        
        Args:
            query (str): La requête de recherche.
            limit (int): Le nombre maximum de résultats à retourner.
            
        Returns:
            List[Dict[str, Any]]: Les résultats de la recherche.
            
        Raises:
            Exception: Si une erreur se produit lors de la recherche.
        """
        try:
            if self.search_engine.lower() == "duckduckgo":
                return self._search_duckduckgo(query, limit)
            else:
                raise Exception(f"Moteur de recherche non pris en charge: {self.search_engine}")
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            raise Exception(f"Erreur lors de la recherche: {str(e)}")
    
    def _search_duckduckgo(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Effectue une recherche sur DuckDuckGo.
        
        Args:
            query (str): La requête de recherche.
            limit (int): Le nombre maximum de résultats à retourner.
            
        Returns:
            List[Dict[str, Any]]: Les résultats de la recherche.
            
        Raises:
            Exception: Si une erreur se produit lors de la recherche.
        """
        results = []
        
        try:
            # L'URL de l'API HTML de DuckDuckGo
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=self.config.get_value("timeout", 30))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = soup.find_all("div", class_="result")
            
            count = 0
            for result in search_results:
                if count >= limit:
                    break
                
                title_element = result.find("a", class_="result__a")
                if not title_element:
                    continue
                
                title = title_element.get_text(strip=True)
                url = title_element["href"]
                
                # Nettoyer l'URL (DuckDuckGo utilise des redirections)
                url_match = re.search(r"uddg=([^&]+)", url)
                if url_match:
                    url = requests.utils.unquote(url_match.group(1))
                
                snippet_element = result.find("a", class_="result__snippet")
                snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
                
                count += 1
            
            return results
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête DuckDuckGo: {str(e)}")
            raise Exception(f"Erreur lors de la recherche DuckDuckGo: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la recherche DuckDuckGo: {str(e)}")
            raise Exception(f"Erreur inattendue lors de la recherche DuckDuckGo: {str(e)}")
    
    def get_page_content(self, url: str) -> Dict[str, Any]:
        """
        Récupère le contenu d'une page web.
        
        Args:
            url (str): L'URL de la page.
            
        Returns:
            Dict[str, Any]: Le contenu de la page.
            
        Raises:
            Exception: Si une erreur se produit lors de la récupération.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=self.config.get_value("timeout", 30))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extraire le titre
            title = soup.title.string if soup.title else ""
            
            # Extraire le contenu principal
            # C'est difficile de déterminer le contenu principal d'une page arbitraire,
            # mais on peut essayer d'extraire le texte des paragraphes
            paragraphs = soup.find_all("p")
            content = "\n\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            # Extraire les liens
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)
                if href.startswith("http") and text:
                    links.append({
                        "url": href,
                        "text": text
                    })
            
            return {
                "title": title,
                "content": content,
                "links": links[:10]  # Limiter à 10 liens
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la requête HTTP: {str(e)}")
            raise Exception(f"Erreur lors de la récupération de la page: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            raise Exception(f"Erreur inattendue: {str(e)}")
