# WakStuff

**WakStuff** est un projet visant à simplifier la création et l’optimisation de stuffs dans le jeu **Wakfu** (Ankama) pour tous les niveaux et types de joueurs.

## Objectif

Fournir un outil capable de :
- Télécharger les données officielles du jeu au format JSON
- Les analyser et nettoyer automatiquement
- Générer des exports clairs (CSV, XLSX, SQLite…)
- Faciliter la création de builds optimisés selon le niveau, les objectifs (PvM, Stasis, PvP…) et les contraintes du joueur

## Fonctionnalités prévues

- Téléchargement automatisé des données de l’API Ankama
- Parser croisé des fichiers (objets, effets, sets, stats…)
- Filtres personnalisés : rareté, maîtrise, niveau, distance/mêlée…
- Générateur de builds et export

## Dossier de travail

- `ApiScrapper.py` : script principal pour récupérer les données JSON depuis l’API
- `wakfu_api_json/` : dossier où sont stockés les fichiers JSON récupérés
- `log.txt` : journal d’exécution du script

## Requis

- Python 3.8+
- `pip install -r requirements.txt`

## Lancement

```bash
python ApiScrapper.py
