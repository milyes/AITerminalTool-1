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
- **Interface web** : Terminal virtuel accessible via navigateur

## Modes d'utilisation

### Mode ligne de commande (CLI)

AITerminal peut être utilisé directement depuis votre terminal:

```bash
# Générer du texte avec l'IA
python -m aiterminal ai "Explique-moi la programmation en 3 phrases."

# Analyser le sentiment d'un texte
python -m aiterminal analyser "Ce produit est fantastique, je suis très satisfait !" --type sentiment

# Rechercher sur internet
python -m aiterminal rechercher "Actualités technologiques"

# Effectuer un ping
python -m aiterminal ping example.com

# Afficher les informations système
python -m aiterminal système --type all
```

### Mode interface web

AITerminal est également accessible via une interface web interactive:

1. Démarrez le serveur web: `gunicorn --bind 0.0.0.0:5000 main:app`
2. Ouvrez votre navigateur à l'adresse: `http://localhost:5000`
3. Utilisez le terminal virtuel dans votre navigateur en tapant des commandes comme:
   - `aide` pour afficher la liste des commandes disponibles
   - `ai "Génère un poème sur la technologie"` pour générer du contenu
   - `système` pour afficher les informations système

## Prérequis

- Python 3.8 ou plus récent
- Connexion Internet
- Clé API OpenAI (pour les fonctionnalités d'IA complètes)

## Installation

```bash
# Installer les dépendances
pip install typer openai requests beautifulsoup4 psutil rich flask gunicorn

# Configurer la clé API OpenAI (recommandé)
export OPENAI_API_KEY="votre-clé-api"
# ou configurez-la via l'interface
python -m aiterminal config --api-key="votre-clé-api"

# Cloner le repository (si disponible)
git clone https://github.com/username/aiterminal.git
cd aiterminal
