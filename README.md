# Centre d'Échecs - Gestion de Tournois

Application hors ligne de gestion de tournois d'échecs développée en Python avec architecture MVC.

## Fonctionnalités

- **Gestion des joueurs** : CRUD complet avec validation des données
- **Tournois** : Création, gestion des tours, système Swiss d'appariement
- **Rapports** : Classements, historiques, statistiques détaillées
- **Persistence** : Sauvegarde automatique en JSON

## Installation

### Prérequis
- Python 3.8 ou supérieur
- Aucune dépendance externe

### Installation avec environnement virtuel (recommandé)
```bash
git clone <repository>
cd DEVELOPPEZ_UN_PROGRAMME_LOGIC

# Créer et activer l'environnement virtuel
python -m venv venv
# Windows :
venv\Scripts\activate
# macOS/Linux :
source venv/bin/activate

# Lancer l'application
python main.py
```

### Installation simple
```bash
git clone <repository>
cd DEVELOPPEZ_UN_PROGRAMME_LOGIC
python main.py
```

## Structure du Projet

```
├── main.py                    # Point d'entrée
├── controllers/               # Logique métier (MVC)
├── models/                    # Entités du domaine
├── views/                     # Interface utilisateur console
├── data/                      # Persistence JSON
├── utils/                     # Utilitaires et validators
└── flake8_rapport/           # Rapport qualité code
```

## Utilisation

### Menu Principal
1. **Gestion des joueurs** - Ajouter, modifier, consulter, supprimer
2. **Gestion des tournois** - Créer, organiser, suivre les tournois
3. **Rapports et statistiques** - Analyses et classements

### Workflow Tournoi
1. Créer un tournoi (nom, lieu, dates, nombre de tours)
2. Inscrire les joueurs (nombre pair requis)
3. Démarrer le premier tour (appariement aléatoire)
4. Saisir les résultats des matchs (1/0.5/0)
5. Tours automatiques selon le système Swiss
6. Consulter les résultats finaux

### Formats de Données
- **ID national** : `AB12345` (2 lettres + 5 chiffres)
- **Dates** : `YYYY-MM-DD` (ex: 2024-03-15)
- **Scores** : `1` (victoire), `0.5` (nul), `0` (défaite)

## Rapports Disponibles

Les 5 rapports conformes au cahier des charges :
- Liste de tous les joueurs par ordre alphabétique
- Liste de tous les tournois
- Nom et dates d'un tournoi donné
- Liste des joueurs du tournoi par ordre alphabétique
- Liste de tous les tours du tournoi et matchs

Plus les statistiques globales du système.

## Architecture

**MVC Pattern** :
- **Models** : Player, Tournament, Round, Match avec validation
- **Views** : Interface console avec menus contextuels
- **Controllers** : Orchestration et logique métier

**Persistence** : Fichiers JSON avec sauvegarde atomique

## Qualité du Code

- Conformité PEP 8 (flake8, ligne max 119 caractères)
- Architecture MVC stricte
- Validation complète des données
- Gestion d'erreurs robuste

### Générer le Rapport Flake8
```bash
pip install flake8 flake8-html
flake8 --format=html --htmldir=flake8_rapport --max-line-length=119
```

## Données

**Structure** :
- `data/players.json` : Base centralisée des joueurs
- `data/tournaments/` : Un fichier JSON par tournoi

**Sauvegarde** : Automatique après chaque modification importante

## Notes Importantes

- Application entièrement hors ligne
- Nombre pair de joueurs requis pour les tournois
- Suppressions de joueurs irréversibles
- Validation stricte des formats de données

## Dépannage

**Problèmes courants** :
- Vérifier les permissions du dossier `data/`
- Respecter les formats de données (ID, dates)
- S'assurer d'avoir un nombre pair de joueurs

**Récupération** : Les fichiers JSON sont lisibles et éditables manuellement

---

*Application conforme au cahier des charges avec architecture MVC et respect des standards Python.*