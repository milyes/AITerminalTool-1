"""
Module des services système.
Gère les fonctionnalités liées au système d'exploitation et aux ressources.
"""

import os
import platform
import psutil
import logging
from typing import Dict, Any

from .config import Config

logger = logging.getLogger(__name__)

class SystemService:
    """Service pour les fonctionnalités système."""
    
    def __init__(self, config: Config):
        """
        Initialise le service système.
        
        Args:
            config (Config): L'objet de configuration.
        """
        self.config = config
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le CPU.
        
        Returns:
            Dict[str, Any]: Informations sur le CPU.
            
        Raises:
            Exception: Si une erreur se produit lors de la récupération des informations.
        """
        try:
            return {
                "percent": psutil.cpu_percent(interval=1),
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "system": platform.system(),
                "processor": platform.processor()
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations CPU: {str(e)}")
            raise Exception(f"Erreur lors de la récupération des informations CPU: {str(e)}")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur la mémoire.
        
        Returns:
            Dict[str, Any]: Informations sur la mémoire.
            
        Raises:
            Exception: Si une erreur se produit lors de la récupération des informations.
        """
        try:
            memory = psutil.virtual_memory()
            return {
                "total": round(memory.total / (1024**3), 2),  # GB
                "available": round(memory.available / (1024**3), 2),  # GB
                "used": round(memory.used / (1024**3), 2),  # GB
                "percent": memory.percent
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations mémoire: {str(e)}")
            raise Exception(f"Erreur lors de la récupération des informations mémoire: {str(e)}")
    
    def get_disk_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le disque.
        
        Returns:
            Dict[str, Any]: Informations sur le disque.
            
        Raises:
            Exception: Si une erreur se produit lors de la récupération des informations.
        """
        try:
            disk = psutil.disk_usage('/')
            return {
                "total": round(disk.total / (1024**3), 2),  # GB
                "used": round(disk.used / (1024**3), 2),  # GB
                "free": round(disk.free / (1024**3), 2),  # GB
                "percent": disk.percent
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations disque: {str(e)}")
            raise Exception(f"Erreur lors de la récupération des informations disque: {str(e)}")
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le réseau.
        
        Returns:
            Dict[str, Any]: Informations sur le réseau.
            
        Raises:
            Exception: Si une erreur se produit lors de la récupération des informations.
        """
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": self._format_bytes(net_io.bytes_sent),
                "bytes_recv": self._format_bytes(net_io.bytes_recv),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations réseau: {str(e)}")
            raise Exception(f"Erreur lors de la récupération des informations réseau: {str(e)}")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """
        Formate une valeur en octets en une chaîne lisible.
        
        Args:
            bytes_value (int): Valeur en octets.
            
        Returns:
            str: Chaîne formatée.
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024 or unit == 'TB':
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
