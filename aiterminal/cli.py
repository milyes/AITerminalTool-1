"""
Module principal pour l'interface en ligne de commande.
Gère les commandes et l'interaction utilisateur.
"""

import os
import sys
import typer
import logging
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .config import Config
from .ai_services import AIService
from .network import NetworkService
from .system import SystemService
from .internet import InternetService
from .utils import format_response

# Initialiser Typer
app = typer.Typer(
    help="AITerminal - Un terminal intelligent en ligne de commande",
    add_completion=False
)
console = Console()
logger = logging.getLogger(__name__)

# Services
config = Config()
ai_service = AIService(config)
network_service = NetworkService(config)
system_service = SystemService(config)
internet_service = InternetService(config)

@app.callback()
def callback():
    """
    AITerminal - Un terminal intelligent en ligne de commande.
    """
    pass

@app.command("config")
def configure(
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Définir la clé API OpenAI"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Définir le modèle OpenAI à utiliser"),
    show: bool = typer.Option(False, "--show", "-s", help="Afficher la configuration actuelle")
):
    """
    Configurer les paramètres de AITerminal.
    """
    if show:
        conf = config.get_config()
        table = Table(title="Configuration Actuelle")
        table.add_column("Paramètre", style="cyan")
        table.add_column("Valeur", style="green")
        
        for key, value in conf.items():
            if key == "api_key" and value:
                # Masquer la clé API pour des raisons de sécurité
                display_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            else:
                display_value = str(value)
            table.add_row(key, display_value)
        
        console.print(table)
        return

    if api_key:
        config.set_value("api_key", api_key)
        console.print("[green]Clé API mise à jour[/green]")
    
    if model:
        config.set_value("model", model)
        console.print(f"[green]Modèle défini sur: [bold]{model}[/bold][/green]")

@app.command("ai")
def generate_ai_content(
    prompt: str = typer.Argument(..., help="Prompt à envoyer à l'IA"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Modèle à utiliser (par défaut: celui configuré)"),
    temperature: float = typer.Option(0.7, "--temperature", "-t", help="Température pour la génération (0.0-1.0)")
):
    """
    Générer du contenu avec l'IA.
    """
    try:
        with console.status("[bold green]Génération en cours...[/bold green]"):
            response = ai_service.generate_text(prompt, model, temperature)
        rprint(format_response(response))
    except Exception as e:
        logger.error(f"Erreur lors de la génération de contenu: {str(e)}")
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")

@app.command("analyze")
def analyze_text(
    text: str = typer.Argument(..., help="Texte à analyser"),
    type: str = typer.Option("sentiment", "--type", "-t", 
                             help="Type d'analyse (sentiment, summary, entities)")
):
    """
    Analyser du texte avec l'IA.
    """
    try:
        with console.status(f"[bold green]Analyse {type} en cours...[/bold green]"):
            if type == "sentiment":
                result = ai_service.analyze_sentiment(text)
            elif type == "summary":
                result = ai_service.summarize_text(text)
            elif type == "entities":
                result = ai_service.extract_entities(text)
            else:
                console.print(f"[bold red]Type d'analyse inconnu: {type}[/bold red]")
                return
        
        rprint(format_response(result))
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")

@app.command("search")
def search_internet(
    query: str = typer.Argument(..., help="Requête de recherche"),
    limit: int = typer.Option(5, "--limit", "-l", help="Nombre de résultats à afficher")
):
    """
    Rechercher des informations sur internet.
    """
    try:
        with console.status("[bold green]Recherche en cours...[/bold green]"):
            results = internet_service.search(query, limit)
        
        table = Table(title=f"Résultats pour: {query}")
        table.add_column("Titre", style="cyan")
        table.add_column("URL", style="blue")
        table.add_column("Description", style="green")
        
        for result in results:
            table.add_row(
                result.get("title", "N/A"),
                result.get("url", "N/A"),
                result.get("snippet", "N/A")
            )
        
        console.print(table)
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {str(e)}")
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")

@app.command("ping")
def ping_host(
    host: str = typer.Argument(..., help="Hôte à pinguer"),
    count: int = typer.Option(4, "--count", "-c", help="Nombre de paquets à envoyer")
):
    """
    Envoyer des requêtes ping à un hôte.
    """
    try:
        with console.status(f"[bold green]Ping vers {host}...[/bold green]"):
            results = network_service.ping(host, count)
        
        for result in results:
            if result.get("success"):
                console.print(f"[green]{result.get('message')}[/green]")
            else:
                console.print(f"[red]{result.get('message')}[/red]")
        
        summary = network_service.get_ping_summary(results)
        console.print(f"\n[bold]--- Résumé ping pour {host} ---[/bold]")
        console.print(f"Paquets: Envoyés = {summary['sent']}, Reçus = {summary['received']}, "
                      f"Perdus = {summary['lost']} ({summary['loss_percent']}% perte)")
        if summary['received'] > 0:
            console.print(f"RTT (ms): Min = {summary['min_rtt']}, Max = {summary['max_rtt']}, "
                         f"Moy = {summary['avg_rtt']}")
    except Exception as e:
        logger.error(f"Erreur lors du ping: {str(e)}")
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")

@app.command("sys")
def system_info(
    type: str = typer.Option("all", "--type", "-t", 
                             help="Type d'information (cpu, memory, disk, network, all)")
):
    """
    Afficher des informations système.
    """
    try:
        if type == "all" or type == "cpu":
            cpu_info = system_service.get_cpu_info()
            console.print("[bold cyan]--- Information CPU ---[/bold cyan]")
            console.print(f"Utilisation CPU: {cpu_info['percent']}%")
            console.print(f"Cœurs physiques: {cpu_info['physical_cores']}")
            console.print(f"Cœurs logiques: {cpu_info['logical_cores']}")
            console.print(f"Fréquence: {cpu_info['frequency']} MHz")
            console.print()
        
        if type == "all" or type == "memory":
            mem_info = system_service.get_memory_info()
            console.print("[bold cyan]--- Mémoire ---[/bold cyan]")
            console.print(f"Total: {mem_info['total']} GB")
            console.print(f"Utilisée: {mem_info['used']} GB ({mem_info['percent']}%)")
            console.print(f"Disponible: {mem_info['available']} GB")
            console.print()
        
        if type == "all" or type == "disk":
            disk_info = system_service.get_disk_info()
            console.print("[bold cyan]--- Espace Disque ---[/bold cyan]")
            console.print(f"Total: {disk_info['total']} GB")
            console.print(f"Utilisé: {disk_info['used']} GB ({disk_info['percent']}%)")
            console.print(f"Libre: {disk_info['free']} GB")
            console.print()
        
        if type == "all" or type == "network":
            net_info = system_service.get_network_info()
            console.print("[bold cyan]--- Réseau ---[/bold cyan]")
            console.print(f"Octets envoyés: {net_info['bytes_sent']}")
            console.print(f"Octets reçus: {net_info['bytes_recv']}")
            console.print(f"Paquets envoyés: {net_info['packets_sent']}")
            console.print(f"Paquets reçus: {net_info['packets_recv']}")
            console.print()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations système: {str(e)}")
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")

@app.command("http")
def http_request(
    url: str = typer.Argument(..., help="URL pour la requête HTTP"),
    method: str = typer.Option("GET", "--method", "-m", help="Méthode HTTP (GET, POST, etc.)"),
    headers: Optional[str] = typer.Option(None, "--headers", "-h", help="En-têtes au format JSON"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Données à envoyer (pour POST, PUT)"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Timeout en secondes")
):
    """
    Envoyer une requête HTTP.
    """
    try:
        with console.status(f"[bold green]Envoi d'une requête {method} à {url}...[/bold green]"):
            response = network_service.http_request(url, method, headers, data, timeout)
        
        console.print(f"[bold]Status:[/bold] [{'green' if response['status_code'] < 400 else 'red'}]{response['status_code']} {response['reason']}[/{'green' if response['status_code'] < 400 else 'red'}]")
        
        if response.get('headers'):
            console.print("\n[bold]Headers:[/bold]")
            for key, value in response['headers'].items():
                console.print(f"  [cyan]{key}:[/cyan] {value}")
        
        if response.get('content'):
            console.print("\n[bold]Contenu:[/bold]")
            try:
                # Tenter de formater le JSON pour une meilleure lisibilité
                content = response['content']
                rprint(format_response(content))
            except:
                console.print(response['content'])
    except Exception as e:
        logger.error(f"Erreur lors de la requête HTTP: {str(e)}")
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")

@app.command("code")
def generate_code(
    description: str = typer.Argument(..., help="Description du code à générer"),
    language: str = typer.Option("python", "--language", "-l", help="Langage de programmation")
):
    """
    Générer du code avec l'IA.
    """
    try:
        with console.status(f"[bold green]Génération de code {language}...[/bold green]"):
            code = ai_service.generate_code(description, language)
        
        console.print(f"[bold green]Code {language} généré:[/bold green]")
        console.print(f"```{language}")
        console.print(code)
        console.print("```")
    except Exception as e:
        logger.error(f"Erreur lors de la génération de code: {str(e)}")
        console.print(f"[bold red]Erreur:[/bold red] {str(e)}")

@app.command("help")
def show_help():
    """
    Afficher l'aide détaillée pour AITerminal.
    """
    console.print("[bold cyan]AITerminal - Documentation[/bold cyan]")
    console.print("\nAITerminal est un terminal intelligent en ligne de commande qui intègre des services d'IA, ")
    console.print("des fonctionnalités réseau et des capacités d'analyse internet.\n")
    
    console.print("[bold]Commandes disponibles:[/bold]")
    
    commands = [
        ("config", "Configurer les paramètres de AITerminal"),
        ("ai", "Générer du contenu avec l'IA"),
        ("analyze", "Analyser du texte avec l'IA"),
        ("search", "Rechercher des informations sur internet"),
        ("ping", "Envoyer des requêtes ping à un hôte"),
        ("sys", "Afficher des informations système"),
        ("http", "Envoyer une requête HTTP"),
        ("code", "Générer du code avec l'IA"),
        ("help", "Afficher cette aide")
    ]
    
    table = Table()
    table.add_column("Commande", style="cyan")
    table.add_column("Description", style="green")
    
    for cmd, desc in commands:
        table.add_row(cmd, desc)
    
    console.print(table)
    
    console.print("\n[bold]Pour plus de détails sur une commande spécifique:[/bold]")
    console.print("  aiterminal [commande] --help")
    
    console.print("\n[bold]Exemples d'utilisation:[/bold]")
    console.print("  aiterminal config --api-key=your-api-key")
    console.print("  aiterminal ai \"Explique-moi comment fonctionne l'apprentissage par renforcement\"")
    console.print("  aiterminal analyze \"Ce produit est incroyable !\" --type=sentiment")
    console.print("  aiterminal search \"Python best practices 2023\"")
    console.print("  aiterminal ping google.com")
    console.print("  aiterminal sys --type=cpu")
    console.print("  aiterminal http https://api.example.com/data")
    console.print("  aiterminal code \"Fonction pour calculer le nombre de Fibonacci\" --language=python")

def run_cli():
    """
    Point d'entrée pour l'exécution du CLI.
    """
    try:
        app()
    except Exception as e:
        logger.error(f"Erreur non gérée: {str(e)}")
        console.print(f"[bold red]Erreur fatale:[/bold red] {str(e)}")
        sys.exit(1)
