import json
import os
import re
from datetime import datetime

from models.player import Player


class PlayerController:
    """
    Contrôleur pour la gestion des joueurs - MVC Pattern
    Responsabilité : Logique métier et gestion des données
    """
    
    DATA_FILE = "data/players.json"
    
    @staticmethod
    def _ensure_data_directory():
        """Crée le répertoire data s'il n'existe pas"""
        os.makedirs(os.path.dirname(PlayerController.DATA_FILE), exist_ok=True)

    @staticmethod
    def _load_players():
        """Charge les joueurs depuis le fichier JSON"""
        players = {}
        try:
            if os.path.exists(PlayerController.DATA_FILE):
                with open(PlayerController.DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for player_data in data:
                        player = Player.from_dict(player_data)
                        players[player.national_id] = player
        except Exception as e:
            print(f"ERREUR lors du chargement: {e}")
        return players

    @staticmethod
    def _save_players(players):
        """Sauvegarde les joueurs dans le fichier JSON"""
        try:
            PlayerController._ensure_data_directory()
            players_data = [player.to_dict() for player in players.values()]
            with open(PlayerController.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(players_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"ERREUR lors de la sauvegarde: {e}")
            return False
    
    @staticmethod
    def _validate_player_data(last_name, first_name, birthdate, national_id):
        """Valide les données d'un joueur"""
        # Validation des champs requis
        if not last_name.strip():
            print("ERREUR: Le nom de famille est obligatoire")
            return False
        
        if not first_name.strip():
            print("ERREUR: Le prénom est obligatoire")
            return False
        
        # Validation du format de date
        try:
            datetime.strptime(birthdate, "%Y-%m-%d")
        except ValueError:
            print("ERREUR: Format de date invalide. Utilisez YYYY-MM-DD")
            return False
        
        # Validation de l'identifiant national
        national_id_pattern = r'^[A-Z]{2}\d{5}$'
        if not re.match(national_id_pattern, national_id):
            print("ERREUR: L'identifiant national doit avoir le format AB12345 (2 lettres + 5 chiffres)")
            return False
        
        return True

    @staticmethod
    def create_player(last_name, first_name, birthdate, national_id):
        """
        Crée un nouveau joueur
        
        Args:
            last_name (str): Nom de famille
            first_name (str): Prénom
            birthdate (str): Date de naissance
            national_id (str): Identifiant national
        """
        # Valider les données
        if not PlayerController._validate_player_data(last_name, first_name, birthdate, national_id):
            return False
        
        # Charger les joueurs existants
        players = PlayerController._load_players()
        
        # Vérifier que le joueur n'existe pas déjà
        if national_id in players:
            print(f"ERREUR: Un joueur avec l'identifiant {national_id} existe déjà")
            return False
        
        try:
            # Créer le joueur
            player = Player(last_name, first_name, birthdate, national_id)
            
            # Ajouter à la collection
            players[player.national_id] = player
            
            # Sauvegarder
            if PlayerController._save_players(players):
                print(f"SUCCÈS: Joueur {player.first_name} {player.last_name} créé avec succès")
                return True
            
        except Exception as e:
            print(f"ERREUR lors de la création: {e}")
            return False

    @staticmethod
    def modify_player(current_national_id, new_last_name, new_first_name, new_birthdate, new_national_id):
        """
        Modifie un joueur existant
        
        Args:
            current_national_id (str): Identifiant actuel
            new_last_name (str): Nouveau nom
            new_first_name (str): Nouveau prénom
            new_birthdate (str): Nouvelle date
            new_national_id (str): Nouvel identifiant
        """
        # Charger les joueurs existants
        players = PlayerController._load_players()
        
        # Vérifier que le joueur existe
        if current_national_id not in players:
            print(f"ERREUR: Aucun joueur trouvé avec l'identifiant {current_national_id}")
            return False
        
        # Valider les nouvelles données
        if not PlayerController._validate_player_data(new_last_name, new_first_name, new_birthdate, new_national_id):
            return False
        
        # Vérifier si le nouvel identifiant existe déjà (si changé)
        if (new_national_id != current_national_id and new_national_id in players):
            print(f"ERREUR: L'identifiant {new_national_id} est déjà utilisé")
            return False
        
        try:
            current_player = players[current_national_id]
            old_score = current_player.score  # Conserver le score
            
            # Supprimer l'ancienne entrée si l'identifiant a changé
            if new_national_id != current_national_id:
                del players[current_national_id]
            
            # Mettre à jour les données
            current_player.last_name = new_last_name
            current_player.first_name = new_first_name
            current_player.birthdate = new_birthdate
            current_player.national_id = new_national_id
            current_player.score = old_score  # Restaurer le score
            
            # Ajouter avec le nouvel identifiant
            players[new_national_id] = current_player
            
            # Sauvegarder
            if PlayerController._save_players(players):
                print(f"SUCCÈS: Joueur {current_player.first_name} {current_player.last_name} modifié avec succès")
                return True
            
        except Exception as e:
            print(f"ERREUR lors de la modification: {e}")
            return False

    @staticmethod
    def delete_player(national_id):
        """
        Supprime un joueur
        
        Args:
            national_id (str): Identifiant du joueur à supprimer
        """
        # Charger les joueurs existants
        players = PlayerController._load_players()
        
        # Vérifier que le joueur existe
        if national_id not in players:
            print(f"ERREUR: Aucun joueur trouvé avec l'identifiant {national_id}")
            return False
        
        try:
            player = players[national_id]
            
            # Supprimer le joueur
            del players[national_id]
            
            # Sauvegarder
            if PlayerController._save_players(players):
                print(f"SUCCÈS: Joueur {player.first_name} {player.last_name} supprimé avec succès")
                return True
            
        except Exception as e:
            print(f"ERREUR lors de la suppression: {e}")
            return False

    @staticmethod
    def get_player(national_id):
        """Retourne un joueur par son identifiant"""
        players = PlayerController._load_players()
        return players.get(national_id)

    @staticmethod
    def get_all_players():
        """Retourne tous les joueurs"""
        players = PlayerController._load_players()
        return list(players.values())

    @staticmethod
    def get_player_tournaments(national_id):
        """
        Récupère tous les tournois auxquels un joueur a participé
        
        Args:
            national_id (str): Identifiant du joueur
            
        Returns:
            list: Liste des tournois avec informations du joueur
        """
        tournaments = []
        tournaments_dir = "data/tournaments"
        
        try:
            if os.path.exists(tournaments_dir):
                for filename in os.listdir(tournaments_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(tournaments_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            tournament_data = json.load(f)
                            
                            # Vérifier si le joueur participe à ce tournoi
                            for player_data in tournament_data.get('players', []):
                                if player_data['national_id'] == national_id:
                                    tournaments.append({
                                        'name': tournament_data['name'],
                                        'location': tournament_data['location'],
                                        'start_date': tournament_data['start_date'],
                                        'end_date': tournament_data['end_date'],
                                        'is_finished': tournament_data.get('is_finished', False),
                                        'player_score': player_data.get('score', 0.0),
                                        'current_round': tournament_data.get('current_round', 0),
                                        'total_rounds': tournament_data.get('number_of_rounds', 4)
                                    })
                                    break
        except Exception as e:
            print(f"ERREUR lors de la récupération des tournois: {e}")
        
        return tournaments

    @staticmethod
    def get_player_matches(national_id):
        """
        Récupère tous les matchs joués par un joueur
        
        Args:
            national_id (str): Identifiant du joueur
            
        Returns:
            list: Liste des matchs avec détails
        """
        matches = []
        tournaments_dir = "data/tournaments"
        
        try:
            if os.path.exists(tournaments_dir):
                for filename in os.listdir(tournaments_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(tournaments_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            tournament_data = json.load(f)
                            tournament_name = tournament_data['name']
                            
                            # Parcourir tous les rounds du tournoi
                            for round_data in tournament_data.get('rounds', []):
                                round_name = round_data['name']
                                
                                # Parcourir tous les matchs du round
                                for match_data in round_data.get('matches', []):
                                    player1_id = match_data['player1_national_id']
                                    player2_id = match_data['player2_national_id']
                                    
                                    # Vérifier si notre joueur participe à ce match
                                    if national_id in [player1_id, player2_id]:
                                        # Déterminer l'adversaire et les scores
                                        if national_id == player1_id:
                                            opponent_id = player2_id
                                            player_score = match_data.get('player1_score', 0.0)
                                            opponent_score = match_data.get('player2_score', 0.0)
                                        else:
                                            opponent_id = player1_id
                                            player_score = match_data.get('player2_score', 0.0)
                                            opponent_score = match_data.get('player1_score', 0.0)
                                        
                                        # Récupérer le nom de l'adversaire
                                        opponent_name = PlayerController._get_player_name(opponent_id)
                                        
                                        matches.append({
                                            'tournament_name': tournament_name,
                                            'round_name': round_name,
                                            'opponent_id': opponent_id,
                                            'opponent_name': opponent_name,
                                            'player_score': player_score,
                                            'opponent_score': opponent_score,
                                            'is_finished': match_data.get('is_finished', False),
                                            'date': round_data.get('start_time', '')
                                        })
        except Exception as e:
            print(f"ERREUR lors de la récupération des matchs: {e}")
        
        return matches

    @staticmethod
    def get_player_rounds(national_id):
        """
        Récupère tous les rounds auxquels un joueur a participé
        
        Args:
            national_id (str): Identifiant du joueur
            
        Returns:
            list: Liste des rounds avec informations
        """
        rounds = []
        tournaments_dir = "data/tournaments"
        
        try:
            if os.path.exists(tournaments_dir):
                for filename in os.listdir(tournaments_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(tournaments_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            tournament_data = json.load(f)
                            tournament_name = tournament_data['name']
                            
                            # Vérifier si le joueur participe à ce tournoi
                            player_in_tournament = any(
                                player['national_id'] == national_id 
                                for player in tournament_data.get('players', [])
                            )
                            
                            if player_in_tournament:
                                # Parcourir tous les rounds du tournoi
                                for round_data in tournament_data.get('rounds', []):
                                    # Vérifier si le joueur a des matchs dans ce round
                                    player_in_round = any(
                                        national_id in [match['player1_national_id'], match['player2_national_id']]
                                        for match in round_data.get('matches', [])
                                    )
                                    
                                    if player_in_round:
                                        rounds.append({
                                            'name': round_data['name'],
                                            'tournament_name': tournament_name,
                                            'start_time': round_data.get('start_time', ''),
                                            'end_time': round_data.get('end_time', ''),
                                            'is_finished': round_data.get('is_finished', False),
                                            'matches_count': len(round_data.get('matches', []))
                                        })
        except Exception as e:
            print(f"ERREUR lors de la récupération des rounds: {e}")
        
        return rounds

    @staticmethod
    def _get_player_name(national_id):
        """
        Récupère le nom complet d'un joueur par son identifiant
        
        Args:
            national_id (str): Identifiant du joueur
            
        Returns:
            str: Nom complet du joueur ou identifiant si non trouvé
        """
        players = PlayerController._load_players()
        player = players.get(national_id)
        if player:
            return f"{player.first_name} {player.last_name}"
        return national_id  # Retourne l'ID si le joueur n'est pas trouvé

    @staticmethod
    def show_complete_player_details(player, tournaments, matches, rounds):
        """Affiche les détails complets d'un joueur avec tournois, matchs et rounds"""
        
        # Informations personnelles
        print(f"\n{'='*60}")
        print(f"DÉTAILS COMPLETS DU JOUEUR")
        print(f"{'='*60}")
        print(f"Nom complet    : {player.first_name} {player.last_name}")
        print(f"Identifiant    : {player.national_id}")
        print(f"Date naissance : {player.birthdate}")
        print(f"Score actuel   : {player.score}")
        
        # Statistiques générales
        print(f"\n{'='*60}")
        print(f"STATISTIQUES")
        print(f"{'='*60}")
        print(f"Tournois participés : {len(tournaments)}")
        print(f"Matchs joués        : {len(matches)}")
        print(f"Rounds participés   : {len(rounds)}")
        
        # Détails des tournois
        if tournaments:
            print(f"\n{'='*60}")
            print(f"TOURNOIS PARTICIPÉS ({len(tournaments)})")
            print(f"{'='*60}")
            for i, tournament in enumerate(tournaments, 1):
                print(f"{i}. {tournament['name']}")
                print(f"   Lieu: {tournament['location']}")
                print(f"   Dates: {tournament['start_date']} - {tournament['end_date']}")
                print(f"   Score dans ce tournoi: {tournament['player_score']}")
                print(f"   Statut: {'Terminé' if tournament['is_finished'] else 'En cours'}")
                print()
        else:
            print(f"\n{'='*60}")
            print(f"TOURNOIS")
            print(f"{'='*60}")
            print("Aucun tournoi participé")
        
        # Détails des matchs
        if matches:
            print(f"\n{'='*60}")
            print(f"HISTORIQUE DES MATCHS ({len(matches)})")
            print(f"{'='*60}")
            for i, match in enumerate(matches, 1):
                opponent = match['opponent_name']
                result = PlayerController._format_match_result(match)
                tournament_name = match.get('tournament_name', 'Tournoi inconnu')
                round_name = match.get('round_name', 'Round inconnu')
                
                print(f"{i}. vs {opponent}")
                print(f"   Résultat: {result}")
                print(f"   Tournoi: {tournament_name}")
                print(f"   Round: {round_name}")
                if match.get('date'):
                    print(f"   Date: {match['date']}")
                print()
        else:
            print(f"\n{'='*60}")
            print(f"MATCHS")
            print(f"{'='*60}")
            print("Aucun match joué")
        
        # Détails des rounds
        if rounds:
            print(f"\n{'='*60}")
            print(f"ROUNDS PARTICIPÉS ({len(rounds)})")
            print(f"{'='*60}")
            for i, round_info in enumerate(rounds, 1):
                print(f"{i}. {round_info['name']}")
                print(f"   Tournoi: {round_info.get('tournament_name', 'Tournoi inconnu')}")
                print(f"   Statut: {'Terminé' if round_info['is_finished'] else 'En cours'}")
                if round_info.get('start_time'):
                    print(f"   Début: {round_info['start_time']}")
                if round_info.get('end_time'):
                    print(f"   Fin: {round_info['end_time']}")
                print(f"   Matchs dans ce round: {round_info.get('matches_count', 0)}")
                print()
        else:
            print(f"\n{'='*60}")
            print(f"ROUNDS")
            print(f"{'='*60}")
            print("Aucun round participé")
        
        print(f"{'='*60}")

    @staticmethod
    def _format_match_result(match):
        """Formate le résultat d'un match pour l'affichage"""
        player_score = match['player_score']
        opponent_score = match['opponent_score']
        
        if player_score == 1.0:
            return f"Victoire ({player_score} - {opponent_score})"
        elif player_score == 0.0:
            return f"Défaite ({player_score} - {opponent_score})"
        else:
            return f"Match nul ({player_score} - {opponent_score})"