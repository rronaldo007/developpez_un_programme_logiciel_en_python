# Gestionnaire de Tournois d'Échecs

Application console Python pour la gestion complète de tournois d'échecs selon le système suisse, développée en architecture MVC.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du Projet](#structure-du-projet)
- [Spécifications Techniques](#spécifications-techniques)
- [Conformité PEP 8](#conformité-pep-8)
- [Exemples d'Usage](#exemples-dusage)
- [Dépannage](#dépannage)
- [Contribution](#contribution)

## Fonctionnalités

### Gestion des Joueurs
- Ajout, modification et suppression de joueurs
- Validation des identifiants nationaux (format AB12345)
- Calcul automatique de l'âge
- Recherche et tri alphabétique
- Profils détaillés avec statistiques

### Gestion des Tournois
- Création de tournois avec paramètres personnalisables
- Système suisse d'appariement automatique
- Évitement des rematches entre joueurs
- Gestion des tours et saisie des résultats
- Classements en temps réel
- Tours de départage automatiques en cas d'égalité

### Rapports et Statistiques
- Liste de tous les joueurs (ordre alphabétique)
- Liste de tous les tournois
- Détails complets d'un tournoi (nom et dates)
- Joueurs d'un tournoi (ordre alphabétique)
- Tours et matchs détaillés
- Statistiques globales du système

### Persistance et Sauvegarde
- Sauvegarde automatique en JSON
- Chargement/restauration d'état
- Intégrité des données garantie

## Architecture

L'application suit rigoureusement le pattern **Model-View-Controller (MVC)** :

```
models/          # Logique métier et données
views/           # Interface utilisateur et affichage  
controllers/     # Coordination et logique applicative
utils/           # Utilitaires et helpers
data/            # Fichiers JSON de persistance
```

### Principe de Séparation des Responsabilités

- **Models** : Stockage des données, validation de base, sérialisation
- **Views** : Affichage, saisie utilisateur, formatage  
- **Controllers** : Logique métier, coordination, gestion des flux
- **Utils** : Algorithmes complexes, validation, formatage, helpers

## Installation

### Prérequis

- **Python 3.8+** installé sur votre système
- **pip** pour la gestion des dépendances

### Étapes d'Installation

1. **Cloner ou télécharger le projet**
   ```bash
   git clone <repository-url>
   cd gestionnaire-tournois-echecs
   ```

2. **Créer un environnement virtuel (recommandé)**
   ```bash
   python -m venv tournament_env
   
   # Windows
   tournament_env\Scripts\activate
   
   # Linux/Mac
   source tournament_env/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Vérifier l'installation**
   ```bash
   python main.py
   ```

## Utilisation

### Démarrage de l'Application

```bash
python main.py
```

### Navigation dans les Menus

L'application utilise une interface console intuitive :

1. **Menu Principal** : Sélectionnez 1, 2, 3 ou 0
   - `1` : Gestion des joueurs
   - `2` : Gestion des tournois  
   - `3` : Rapports et statistiques
   - `0` : Quitter

2. **Navigation** : Utilisez les numéros pour naviguer
3. **Retour** : Tapez `0` pour revenir au menu précédent
4. **Aide** : Les instructions sont affichées pour chaque action

### Workflow Typique

1. **Ajouter des joueurs** (Menu → 1 → 1)
2. **Créer un tournoi** (Menu → 2 → 1)
3. **Ajouter les joueurs au tournoi**
4. **Démarrer les tours successivement**
5. **Saisir les résultats des matchs**
6. **Consulter les classements et rapports**

## Structure du Projet

```
gestionnaire-tournois-echecs/
├── main.py                     # Point d'entrée de l'application
├── requirements.txt            # Dépendances Python
├── README.md                   # Ce fichier
│
├── models/                     # Modèles de données
│   ├── __init__.py
│   ├── player.py              # Modèle Joueur
│   ├── match.py               # Modèle Match  
│   ├── round.py               # Modèle Tour
│   └── tournament.py          # Modèle Tournoi
│
├── views/                      # Interface utilisateur
│   ├── __init__.py
│   ├── base_view.py           # Vue de base commune
│   ├── menu_view.py           # Menus principaux
│   ├── player_view.py         # Interface joueurs
│   ├── tournament_view.py     # Interface tournois
│   └── statistic_view.py      # Interface rapports
│
├── controllers/                # Contrôleurs applicatifs
│   ├── __init__.py
│   ├── main_controller.py     # Contrôleur principal
│   ├── player_controller.py   # Gestion des joueurs
│   ├── tournament_controller.py # Gestion des tournois
│   └── statistic_controller.py # Gestion des rapports
│
├── utils/                      # Utilitaires et helpers
│   ├── __init__.py
│   ├── date_utils.py          # Gestion des dates
│   ├── file_utils.py          # Persistance fichiers
│   ├── formatters.py          # Formatage d'affichage
│   ├── validators.py          # Validation des données
│   ├── match_helpers.py       # Logique des matchs
│   └── tournament_helpers.py  # Logique des tournois
│
├── data/                       # Données persistantes
│   ├── players.json           # Base de données des joueurs
│   └── tournaments/           # Tournois individuels
│       ├── tournament_1.json
│       ├── tournament_2.json
│       └── ...
│
└── flake8_rapport/            # Rapport de conformité PEP 8
    └── index.html
```

## Spécifications Techniques

### Formats de Données

- **Identifiants Nationaux** : 2 lettres + 5 chiffres (ex: `AB12345`)
- **Dates** : Format ISO `YYYY-MM-DD` (ex: `2024-03-15`)
- **Scores** : `0` (défaite), `0.5` (nul), `1` (victoire)
- **Persistance** : Fichiers JSON avec sauvegarde atomique

### Système Suisse

L'application implémente le **système suisse authentique** :

1. **Premier tour** : Appariement aléatoire
2. **Tours suivants** : 
   - Tri par score décroissant
   - Appariement des joueurs adjacents
   - Évitement des rematches
   - Départage automatique en cas d'égalité finale

### Validation des Données

- **Noms** : Lettres, espaces, tirets, apostrophes, accents
- **Dates** : Format ISO valide, cohérence temporelle
- **Scores** : Uniquement 0, 0.5 ou 1
- **Tournois** : Nombre pair de joueurs, minimum 2

## Conformité PEP 8

### Génération du Rapport

```bash
# Installer flake8 et flake8-html
pip install flake8 flake8-html

# Générer le rapport de conformité
flake8 --format=html --htmldir=flake8_rapport --max-line-length=119

# Consulter le rapport
# Ouvrir flake8_rapport/index.html dans un navigateur
```

### Standards Respectés

- **Longueur de ligne** : Maximum 119 caractères
- **Nommage** : Snake_case pour fonctions et variables
- **Indentation** : 4 espaces (pas de tabs)
- **Imports** : Triés et organisés
- **Docstrings** : Documentation complète
- **Type hints** : Annotations de type

## Exemples d'Usage

### Création d'un Joueur

```
Menu Principal → 1 (Joueurs) → 1 (Ajouter)

Nom de famille: Dupont
Prénom: Jean
Date de naissance: 1985-06-15
Identifiant national: AB12345
```

### Organisation d'un Tournoi

```
Menu Principal → 2 (Tournois) → 1 (Créer)

Nom: Championnat du Club
Lieu: Salle Municipal
Date début: 2024-06-01  
Date fin: 2024-06-02
Nombre de tours: 4
```

### Génération de Rapports

```
Menu Principal → 3 (Statistiques) → 1 (Joueurs alphabétique)

╔══════════════════════════════════════════════════╗
║                LISTE DES JOUEURS                ║
╚══════════════════════════════════════════════════╝

#    Nom                  Prénom               ID         Âge
─────────────────────────────────────────────────────────────
1    Dupont               Jean                 AB12345    39
2    Martin               Marie                CD67890    28
3    Durand               Pierre               EF13579    45
```

## Dépannage

### Problèmes Courants

**Erreur : "Module not found"**
```bash
# Vérifier que vous êtes dans le bon répertoire
pwd
# Réinstaller les dépendances
pip install -r requirements.txt
```


**Données corrompues**
```
Vérifier l'intégrité des fichiers JSON dans data/
Restaurer depuis une copie manuelle si nécessaire
```

# Redémarrer l'application pour recréer les structures
python main.py
```

## Contribution

### Standards de Développement

1. **Respect de l'architecture MVC**
2. **Conformité PEP 8** (vérifier avec flake8)
3. **Documentation** des nouvelles classes/méthodes
4. **Gestion d'erreurs** appropriée


**Objectif** : Créer un outil professionnel, robuste et facile à utiliser pour les clubs d'échecs souhaitant organiser leurs tournois de manière efficace et conforme aux standards internationaux.

**Support** : Pour toute question ou problème, consultez la section [Dépannage](#dépannage) ou créez une issue sur le repository.