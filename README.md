# AITerminal

Un terminal intelligent en ligne de commande qui intègre des services d'IA, des fonctionnalités réseau et des capacités d'analyse internet.

## Description

AITerminal est un outil puissant pour interagir avec des services d'intelligence artificielle directement depuis votre terminal. Il vous permet de générer du contenu, d'analyser des textes, de rechercher des informations sur internet, de tester des connexions réseau et de surveiller les ressources système.

## Fonctionnalités

- **Services d'IA** : Génération de texte, analyse de sentiment, résumés, extraction d'entités, génération de code
- **Fonctionnalités réseau** : Ping, requêtes HTTP
- **Analyse internet** : Recherche web, extraction de contenu
- **Gestion système** : Surveillance CPU, mémoire, disque et réseau
- **Configuration facile** : Via ligne de commande ou fichier JSON

## Prérequis

- Python 3.8 ou plus récent
- Connexion Internet
- Clé API OpenAI (pour les fonctionnalités d'IA)

## Installation

```bash
# Installer les dépendances
pip install typer openai requests beautifulsoup4 psutil rich

# Cloner le repository (si disponible)
git clone https://github.com/username/aiterminal.git
cd aiterminal
