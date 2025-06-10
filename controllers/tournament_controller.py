import os
import json
import random
from datetime import datetime

from models.tournament import Tournament
from models.round import Round
from models.match import Match
from models.player import Player
from controllers.player_controller import PlayerController


class TournamentController:
    """
    Contrôleur pour la gestion des tournois - MVC Pattern
    """
    
    TOURNAMENTS_DIR = "data/tournaments"
    
    @staticmethod
    def _ensure_tournaments_directory():
        """Crée le répertoire tournaments s'il n'existe pas"""
        os.makedirs(TournamentController.TOURNAMENTS_DIR, exist_ok=True)

    @staticmethod
    def _get_tournament_filename(tournament_id):
        """Retourne le nom de fichier pour un tournoi"""
        return os.path.join(TournamentController.TOURNAMENTS_DIR, f"tournament_{tournament_id}.json")

    @staticmethod
    def create_tournament(name, location, start_date, end_date, description="", number_of_rounds=4):
        """Crée un nouveau tournoi"""
        if not TournamentController._validate_tournament_data(name, location, start_date, end_date):
            return False
        
        try:
            TournamentController._ensure_tournaments_directory()
            
            # Créer le tournoi
            tournament = Tournament(name, location, start_date, end_date, description, number_of_rounds)
            
            # Sauvegarder
            filename = TournamentController._get_tournament_filename(tournament.id)
            tournament.save_to_file(filename)
            
            print(f"SUCCÈS: Tournoi '{tournament.name}' créé avec l'ID {tournament.id}")
            return True
            
        except Exception as e:
            print(f"ERREUR lors de la création: {e}")
            return False

    @staticmethod
    def modify_tournament(tournament_id, new_name, new_location, new_start_date, new_end_date, new_description):
        """Modifie un tournoi existant"""
        if not TournamentController._validate_tournament_data(new_name, new_location, new_start_date, new_end_date):
            return False
        
        try:
            filename = TournamentController._get_tournament_filename(tournament_id)
            if not os.path.exists(filename):
                print(f"ERREUR: Tournoi avec l'ID {tournament_id} non trouvé")
                return False
            
            # Charger le tournoi
            player_lookup = {p.national_id: p for p in PlayerController.get_all_players()}
            tournament = Tournament.load_from_file(filename, player_lookup)
            
            # Modifier les données
            tournament.name = new_name
            tournament.location = new_location
            tournament.start_date = new_start_date
            tournament.end_date = new_end_date
            tournament.description = new_description
            
            # Sauvegarder
            tournament.save_to_file(filename)
            
            print(f"SUCCÈS: Tournoi '{tournament.name}' modifié avec succès")
            return True
            
        except Exception as e:
            print(f"ERREUR lors de la modification: {e}")
            return False

    @staticmethod
    def get_tournament(tournament_id):
        """Récupère un tournoi par son ID"""
        try:
            filename = TournamentController._get_tournament_filename(tournament_id)
            if not os.path.exists(filename):
                return None
            
            if os.path.getsize(filename) == 0:
                print(f"ERREUR: Fichier tournoi vide pour l'ID {tournament_id}")
                return None
            
            player_lookup = {p.national_id: p for p in PlayerController.get_all_players()}
            
            try:
                return Tournament.load_from_file(filename, player_lookup)
            except TypeError as e:
                if "takes 1 positional argument but 2 were given" in str(e):
                    return TournamentController._load_tournament_alternative(filename, player_lookup)
                else:
                    raise e
            
        except json.JSONDecodeError as e:
            print(f"ERREUR: Fichier JSON corrompu pour le tournoi {tournament_id}: {e}")
            return None
        except Exception as e:
            print(f"ERREUR lors du chargement du tournoi {tournament_id}: {e}")
            return None

    @staticmethod
    def _load_tournament_alternative(filename, player_lookup):
        """Méthode alternative pour charger un tournoi si Round.from_dict pose problème"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            tournament = Tournament(
                data["name"],
                data["location"],
                data["start_date"],
                data["end_date"],
                data.get("description", ""),
                data.get("number_of_rounds", 4)
            )
            tournament.id = data.get("id", Tournament._id_counter)
            Tournament._id_counter = max(Tournament._id_counter, tournament.id + 1)
            tournament.current_round = data.get("current_round", 0)
            
            # Charger les joueurs
            tournament.players = []
            for player_data in data.get("players", []):
                if isinstance(player_data, dict) and "national_id" in player_data:
                    national_id = player_data["national_id"]
                    if national_id in player_lookup:
                        player = player_lookup[national_id]
                        tournament_player = Player(
                            player.last_name,
                            player.first_name, 
                            player.birthdate,
                            player.national_id
                        )
                        tournament_player.score = player_data.get("score", 0.0)
                        tournament.players.append(tournament_player)
            
            # Charger les rounds SANS appeler Round.from_dict
            tournament.rounds = []
            for round_data in data.get("rounds", []):
                # Créer le round manuellement
                round_obj = Round(round_data["name"])
                round_obj.start_time = round_data.get("start_time", datetime.now().isoformat())
                round_obj.end_time = round_data.get("end_time")
                round_obj.is_finished = round_data.get("is_finished", False)
                
                # Charger les matchs manuellement
                for match_data in round_data.get("matches", []):
                    match = Match(
                        match_data["player1_national_id"],
                        match_data["player2_national_id"]
                    )
                    match.player1_score = match_data.get("player1_score", 0.0)
                    match.player2_score = match_data.get("player2_score", 0.0)
                    match.is_finished = match_data.get("is_finished", False)
                    round_obj.matches.append(match)
                
                tournament.rounds.append(round_obj)
            
            return tournament
            
        except Exception as e:
            print(f"ERREUR lors du chargement alternatif: {e}")
            return None

    @staticmethod
    def get_all_tournaments():
        """Retourne tous les tournois"""
        tournaments = []
        try:
            if not os.path.exists(TournamentController.TOURNAMENTS_DIR):
                return tournaments
                
            player_lookup = {p.national_id: p for p in PlayerController.get_all_players()}
            
            for filename in os.listdir(TournamentController.TOURNAMENTS_DIR):
                if filename.startswith("tournament_") and filename.endswith(".json"):
                    filepath = os.path.join(TournamentController.TOURNAMENTS_DIR, filename)
                    try:
                        # Vérifier que le fichier n'est pas vide
                        if os.path.getsize(filepath) == 0:
                            print(f"ATTENTION: Fichier vide ignoré: {filename}")
                            continue
                            
                        # CORRECTION: Utiliser la méthode alternative pour éviter Round.from_dict()
                        tournament = TournamentController._load_tournament_alternative(filepath, player_lookup)
                        if tournament:
                            tournaments.append(tournament)
                        else:
                            print(f"ATTENTION: Impossible de charger {filename}")
                        
                    except json.JSONDecodeError as e:
                        print(f"ERREUR JSON dans {filename}: {e}")
                        print(f"ATTENTION: Fichier corrompu ignoré: {filename}")
                        continue
                    except Exception as e:
                        print(f"ERREUR lors du chargement de {filename}: {e}")
                        continue
                        
        except Exception as e:
            print(f"ERREUR lors du chargement des tournois: {e}")
        
        return tournaments

    @staticmethod
    def add_player_to_tournament(tournament_id, national_id):
        """Ajoute un joueur à un tournoi"""
        try:
            # Récupérer le tournoi
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament:
                print(f"ERREUR: Tournoi avec l'ID {tournament_id} non trouvé")
                return False
            
            # Récupérer le joueur
            player = PlayerController.get_player(national_id)
            if not player:
                print(f"ERREUR: Joueur avec l'identifiant {national_id} non trouvé")
                return False
            
            # Vérifier si le joueur est déjà inscrit
            if any(p.national_id == national_id for p in tournament.players):
                print(f"ERREUR: Le joueur {player.first_name} {player.last_name} est déjà inscrit")
                return False
            
            # Créer une copie du joueur pour ce tournoi (évite les conflits de score)
            tournament_player = Player(
                player.last_name,
                player.first_name,
                player.birthdate,
                player.national_id
            )
            tournament_player.score = 0.0  # Score initial pour ce tournoi
            
            # Ajouter le joueur
            tournament.add_player(tournament_player)
            
            # Sauvegarder le tournoi
            filename = TournamentController._get_tournament_filename(tournament_id)
            tournament.save_to_file(filename)
            
            print(f"SUCCÈS: Joueur {player.first_name} {player.last_name} ajouté au tournoi")
            return True
            
        except Exception as e:
            print(f"ERREUR lors de l'ajout: {e}")
            return False

    @staticmethod
    def start_round(tournament_id):
        """Démarre un nouveau round avec génération automatique des paires"""
        try:
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament:
                print(f"ERREUR: Tournoi avec l'ID {tournament_id} non trouvé")
                return False
            
            if tournament.current_round >= tournament.number_of_rounds:
                print("ERREUR: Le tournoi est déjà terminé")
                return False
            
            if len(tournament.players) < 2:
                print("ERREUR: Il faut au moins 2 joueurs pour démarrer un round")
                return False
            
            if len(tournament.players) % 2 != 0:
                print("ERREUR: Il faut un nombre pair de joueurs")
                return False
            
            fixed_players = []
            for player in tournament.players:
                if isinstance(player, str):
                    global_player = PlayerController.get_player(player)
                    if global_player:
                        # Créer une copie pour ce tournoi
                        tournament_player = Player(
                            global_player.last_name,
                            global_player.first_name,
                            global_player.birthdate,
                            global_player.national_id
                        )
                        tournament_player.score = 0.0
                        fixed_players.append(tournament_player)
                    else:
                        print(f"ERREUR: Joueur {player} introuvable")
                        return False
                elif hasattr(player, 'national_id'):
                    # Si c'est déjà un objet Player, le garder
                    fixed_players.append(player)
                else:
                    print(f"ERREUR: Objet joueur invalide: {player}")
                    return False
            
            # Remplacer la liste des joueurs par les objets corrigés
            tournament.players = fixed_players
            print(f"INFO: {len(fixed_players)} joueurs convertis en objets Player")
            
            # Créer le nouveau round
            tournament.current_round += 1
            round_name = f"Round {tournament.current_round}"
            new_round = Round(round_name)
            
            # Générer les paires automatiquement
            if tournament.current_round == 1:
                # Premier round : mélange aléatoire
                players_copy = tournament.players.copy()
                random.shuffle(players_copy)
                print(f"\nPremier round - Paires générées aléatoirement:")
            else:
                # Rounds suivants : tri par score
                players_copy = sorted(tournament.players, key=lambda p: p.score, reverse=True)
                print(f"\n{round_name} - Paires générées selon le classement:")
            
            # Afficher les paires générées et créer les matchs
            print("-" * 60)
            for i in range(0, len(players_copy), 2):
                player1 = players_copy[i]
                player2 = players_copy[i + 1]
                
                # Maintenant player1 et player2 sont des objets Player
                match = Match(player1.national_id, player2.national_id)
                new_round.add_match(match)
                
                print(f"Match {i//2 + 1}: {player1.first_name} {player1.last_name} vs {player2.first_name} {player2.last_name}")
            print("-" * 60)
            
            tournament.rounds.append(new_round)
            
            # Sauvegarder
            filename = TournamentController._get_tournament_filename(tournament_id)
            tournament.save_to_file(filename)
            
            print(f"SUCCÈS: {round_name} démarré avec {len(new_round.matches)} matchs")
            return True
            
        except Exception as e:
            print(f"ERREUR lors du démarrage: {e}")
            import traceback
            traceback.print_exc()
            return False

    @staticmethod
    def _fix_player_objects(tournament):
        """Convertit les strings de joueurs en objets Player"""
        fixed_players = []
        
        for player in tournament.players:
            if isinstance(player, str):
                # Si c'est un string, le convertir en objet Player
                global_player = PlayerController.get_player(player)
                if global_player:
                    # Créer une copie pour ce tournoi
                    tournament_player = Player(
                        global_player.last_name,
                        global_player.first_name,
                        global_player.birthdate,
                        global_player.national_id
                    )
                    tournament_player.score = 0.0
                    fixed_players.append(tournament_player)
                else:
                    print(f"ATTENTION: Joueur {player} introuvable")
            elif hasattr(player, 'national_id'):
                # Si c'est déjà un objet Player, le garder
                fixed_players.append(player)
            else:
                print(f"ATTENTION: Objet joueur invalide: {player}")
        
        # Remplacer la liste des joueurs
        tournament.players = fixed_players
        print(f"INFO: {len(fixed_players)} joueurs convertis en objets Player")

    @staticmethod
    def enter_match_results(tournament_id):
        """Interface pour entrer les résultats des matchs avec continuation automatique"""
        try:
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament:
                print(f"ERREUR: Tournoi avec l'ID {tournament_id} non trouvé")
                return False
            
            if not tournament.rounds:
                print("ERREUR: Aucun round démarré")
                return False
            
            # Boucle pour traiter tous les rounds jusqu'à la fin du tournoi
            while tournament.current_round <= tournament.number_of_rounds:
                current_round = tournament.rounds[-1] if tournament.rounds else None
                
                if not current_round or current_round.is_finished:
                    # Le round actuel est terminé, vérifier s'il faut en démarrer un nouveau
                    if tournament.current_round >= tournament.number_of_rounds:
                        # Tournoi terminé
                        print("SUCCÈS: Tournoi terminé!")
                        TournamentController._show_final_rankings(tournament)
                        break
                    else:
                        # Proposer de démarrer le round suivant
                        next_round_num = tournament.current_round + 1
                        print(f"\nLe round actuel est terminé.")
                        print(f"Souhaitez-vous démarrer le Round {next_round_num} ?")
                        choice = input("(oui/non): ").strip().lower()
                        
                        if choice in ['oui', 'o', 'yes', 'y']:
                            # Démarrer le round suivant automatiquement
                            if TournamentController.start_round(tournament_id):
                                # Recharger le tournoi après création du nouveau round
                                tournament = TournamentController.get_tournament(tournament_id)
                                continue
                            else:
                                print("ERREUR: Impossible de démarrer le round suivant")
                                break
                        else:
                            print("Vous pourrez démarrer le round suivant plus tard.")
                            break
                
                # Traiter le round en cours
                print(f"\n=== RÉSULTATS POUR {current_round.name} ===")
                
                # Vérifier s'il y a des matchs non terminés
                unfinished_matches = [match for match in current_round.matches if not match.is_finished]
                
                if not unfinished_matches:
                    print("Tous les matchs de ce round sont déjà terminés.")
                    current_round.end_round()
                    print(f"SUCCÈS: {current_round.name} terminé!")
                    
                    # Sauvegarder et continuer avec le round suivant
                    filename = TournamentController._get_tournament_filename(tournament_id)
                    tournament.save_to_file(filename)
                    continue
                
                # Entrer les résultats des matchs non terminés
                for i, match in enumerate(current_round.matches, 1):
                    if match.is_finished:
                        continue
                    
                    player1 = PlayerController.get_player(match.player1_national_id)
                    player2 = PlayerController.get_player(match.player2_national_id)
                    
                    print(f"\nMatch {i}: {player1.first_name} {player1.last_name} vs {player2.first_name} {player2.last_name}")
                    print("Résultats possibles:")
                    print("1 - Victoire de", player1.first_name, player1.last_name)
                    print("2 - Victoire de", player2.first_name, player2.last_name)
                    print("3 - Match nul")
                    print("0 - Passer ce match")
                    print("q - Quitter la saisie")
                    
                    choice = input("Votre choix: ").strip().lower()
                    
                    if choice == "q":
                        print("Saisie interrompue. Vous pourrez continuer plus tard.")
                        filename = TournamentController._get_tournament_filename(tournament_id)
                        tournament.save_to_file(filename)
                        return True
                    elif choice == "1":
                        match.set_result(1.0, 0.0)
                        TournamentController._update_player_score_in_tournament(tournament, match.player1_national_id, 1.0)
                        TournamentController._update_player_score_in_tournament(tournament, match.player2_national_id, 0.0)
                        print(f"Résultat enregistré: {player1.first_name} {player1.last_name} gagne!")
                    elif choice == "2":
                        match.set_result(0.0, 1.0)
                        TournamentController._update_player_score_in_tournament(tournament, match.player1_national_id, 0.0)
                        TournamentController._update_player_score_in_tournament(tournament, match.player2_national_id, 1.0)
                        print(f"Résultat enregistré: {player2.first_name} {player2.last_name} gagne!")
                    elif choice == "3":
                        match.set_result(0.5, 0.5)
                        TournamentController._update_player_score_in_tournament(tournament, match.player1_national_id, 0.5)
                        TournamentController._update_player_score_in_tournament(tournament, match.player2_national_id, 0.5)
                        print("Résultat enregistré: Match nul!")
                    elif choice == "0":
                        print("Match passé.")
                        continue
                    else:
                        print("Choix invalide, match passé")
                        continue
                
                # Vérifier si tous les matchs du round sont maintenant terminés
                if current_round.all_matches_finished():
                    current_round.end_round()
                    print(f"\nSUCCÈS: {current_round.name} terminé!")
                    
                    # Afficher le classement intermédiaire
                    if tournament.current_round < tournament.number_of_rounds:
                        print(f"\nCLASSEMENT APRÈS {current_round.name}:")
                        sorted_players = sorted(tournament.players, key=lambda p: p.score, reverse=True)
                        for i, player in enumerate(sorted_players, 1):
                            print(f"{i}. {player.first_name} {player.last_name} - {player.score} pts")
                else:
                    print(f"\nIl reste des matchs non terminés dans {current_round.name}.")
                    print("Vous pourrez continuer la saisie plus tard.")
                    break
                
                # Sauvegarder après chaque round
                filename = TournamentController._get_tournament_filename(tournament_id)
                tournament.save_to_file(filename)
            
            return True
            
        except Exception as e:
            print(f"ERREUR lors de la saisie: {e}")
            return False

    @staticmethod
    def _update_player_score_in_tournament(tournament, national_id, points):
        """Met à jour le score d'un joueur dans le tournoi"""
        for player in tournament.players:
            if player.national_id == national_id:
                player.score += points
                break

    @staticmethod
    def show_tournament_details(tournament_id):
        """Affiche les détails complets d'un tournoi"""
        try:
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament:
                print(f"ERREUR: Tournoi avec l'ID {tournament_id} non trouvé")
                return
            
            print(f"\n{'='*60}")
            print(f"DÉTAILS DU TOURNOI")
            print(f"{'='*60}")
            print(f"Nom        : {tournament.name}")
            print(f"ID         : {tournament.id}")
            print(f"Lieu       : {tournament.location}")
            print(f"Dates      : {tournament.start_date} - {tournament.end_date}")
            print(f"Description: {tournament.description}")
            print(f"Rounds     : {tournament.current_round}/{tournament.number_of_rounds}")
            print(f"Joueurs    : {len(tournament.players)}")
            
            # Statut du tournoi
            if tournament.current_round >= tournament.number_of_rounds:
                print(f"Statut     : TERMINÉ")
            elif tournament.current_round > 0:
                print(f"Statut     : EN COURS")
            else:
                print(f"Statut     : PAS DÉMARRÉ")
            
            # Afficher le classement actuel des joueurs
            if tournament.players:
                print(f"\n{'='*60}")
                print(f"CLASSEMENT ACTUEL")
                print(f"{'='*60}")
                sorted_players = sorted(tournament.players, key=lambda p: p.score, reverse=True)
                
                # Si le tournoi est terminé, afficher la célébration
                if tournament.current_round >= tournament.number_of_rounds and sorted_players:
                    winner = sorted_players[0]
                    print(f"\nFÉLICITATIONS AU CHAMPION !")
                    print(f"GAGNANT: {winner.first_name} {winner.last_name}")
                    print(f"Score final: {winner.score} points")
                    
                    # Vérifier s'il y a des ex aequo
                    winners = [p for p in sorted_players if p.score == winner.score]
                    if len(winners) > 1:
                        print(f"\nÉGALITÉ AU SOMMET ! {len(winners)} gagnants ex aequo:")
                        for i, w in enumerate(winners, 1):
                            print(f"   {i}. {w.first_name} {w.last_name} - {w.score} points")
                    print()
                
                # Affichage du classement
                for i, player in enumerate(sorted_players, 1):
                    if tournament.current_round >= tournament.number_of_rounds:
                        # Tournoi terminé : affichage avec podium
                        if i == 1:
                            medal = "1er"
                        elif i == 2:
                            medal = "2e "
                        elif i == 3:
                            medal = "3e "
                        else:
                            medal = f"{i:2d}e"
                        print(f"{medal} {player.first_name} {player.last_name} ({player.national_id}) - {player.score} pts")
                    else:
                        # Tournoi en cours : affichage simple
                        print(f"{i}. {player.first_name} {player.last_name} ({player.national_id}) - {player.score} pts")
            
            # Afficher les statistiques si le tournoi a démarré
            if tournament.rounds:
                total_matches = sum(len(round_obj.matches) for round_obj in tournament.rounds)
                finished_matches = sum(
                    sum(1 for match in round_obj.matches if match.is_finished) 
                    for round_obj in tournament.rounds
                )
                
                print(f"\n{'='*60}")
                print(f"STATISTIQUES")
                print(f"{'='*60}")
                print(f"Rounds joués     : {len(tournament.rounds)}")
                print(f"Matchs totaux    : {total_matches}")
                print(f"Matchs terminés  : {finished_matches}")
                if total_matches > 0:
                    progression = (finished_matches / total_matches) * 100
                    print(f"Progression      : {progression:.1f}%")
            
            # Afficher l'historique des rounds
            if tournament.rounds:
                print(f"\n{'='*60}")
                print(f"HISTORIQUE DES ROUNDS")
                print(f"{'='*60}")
                for round_obj in tournament.rounds:
                    status = "Terminé" if round_obj.is_finished else "En cours"
                    finished_matches_in_round = sum(1 for match in round_obj.matches if match.is_finished)
                    total_matches_in_round = len(round_obj.matches)
                    
                    print(f"{round_obj.name} [{status}] - {finished_matches_in_round}/{total_matches_in_round} matchs")
                    if round_obj.start_time:
                        start_date = round_obj.start_time[:19].replace('T', ' ')
                        print(f"   Début: {start_date}")
                    if round_obj.end_time:
                        end_date = round_obj.end_time[:19].replace('T', ' ')
                        print(f"   Fin: {end_date}")
            
            # Message final si tournoi terminé
            if tournament.current_round >= tournament.number_of_rounds:
                print(f"\n{'='*60}")
                print(f"MERCI À TOUS LES PARTICIPANTS !")
                print(f"{'='*60}")
            else:
                print(f"\n{'='*60}")
            
        except Exception as e:
            print(f"ERREUR lors de l'affichage: {e}")

    @staticmethod
    def _show_final_rankings(tournament):
        """Affiche le classement final avec célébration du gagnant"""
        print(f"\n{'='*60}")
        print(f"TOURNOI TERMINÉ - {tournament.name}")
        print(f"{'='*60}")
        
        # Trier les joueurs par score décroissant
        sorted_players = sorted(tournament.players, key=lambda p: p.score, reverse=True)
        
        if sorted_players:
            winner = sorted_players[0]
            
            # Célébration du gagnant
            print(f"\nFÉLICITATIONS AU CHAMPION !")
            print(f"GAGNANT: {winner.first_name} {winner.last_name}")
            print(f"Score final: {winner.score} points")
            print(f"Identifiant: {winner.national_id}")
            
            # Vérifier s'il y a des ex aequo
            winners = [p for p in sorted_players if p.score == winner.score]
            if len(winners) > 1:
                print(f"\nÉGALITÉ AU SOMMET ! {len(winners)} gagnants ex aequo:")
                for i, w in enumerate(winners, 1):
                    print(f"   {i}. {w.first_name} {w.last_name} - {w.score} points")
            
            print(f"\n{'='*60}")
            print(f"CLASSEMENT FINAL COMPLET")
            print(f"{'='*60}")
            
            # Affichage du podium
            for i, player in enumerate(sorted_players, 1):
                if i == 1:
                    medal = "1er"
                elif i == 2:
                    medal = "2e "
                elif i == 3:
                    medal = "3e "
                else:
                    medal = f"{i:2d}e"
                
                print(f"{medal} {player.first_name} {player.last_name} - {player.score} points")
            
            print(f"{'='*60}")
            
            # Statistiques du tournoi
            total_rounds = len(tournament.rounds)
            total_matches = sum(len(round_obj.matches) for round_obj in tournament.rounds)
            
            print(f"\nSTATISTIQUES DU TOURNOI:")
            print(f"   Lieu: {tournament.location}")
            print(f"   Dates: {tournament.start_date} - {tournament.end_date}")
            print(f"   Participants: {len(tournament.players)} joueurs")
            print(f"   Rounds joués: {total_rounds}")
            print(f"   Matchs joués: {total_matches}")
            
            print(f"\nMERCI À TOUS LES PARTICIPANTS !")
            print(f"{'='*60}")
        else:
            print("Aucun joueur trouvé dans le tournoi.")
        
        input("\nAppuyez sur Entrée pour continuer...")

    @staticmethod
    def _save_tournament(tournament, tournament_id):
        """Sauvegarde un tournoi"""
        try:
            filename = TournamentController._get_tournament_filename(tournament_id)
            tournament.save_to_file(filename)
            return True
        except Exception as e:
            print(f"ERREUR lors de la sauvegarde: {e}")
            return False

    @staticmethod
    def _validate_tournament_data(name, location, start_date, end_date):
        """Valide les données d'un tournoi"""
        # Validation des champs requis
        if not name.strip():
            print("ERREUR: Le nom du tournoi est obligatoire")
            return False
        
        if not location.strip():
            print("ERREUR: Le lieu est obligatoire")
            return False
        
        # Validation du format de date
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            print("ERREUR: Format de date de début invalide. Utilisez YYYY-MM-DD")
            return False
        
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            print("ERREUR: Format de date de fin invalide. Utilisez YYYY-MM-DD")
            return False
        
        # Validation que la date de fin soit après la date de début
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if end < start:
                print("ERREUR: La date de fin doit être après la date de début")
                return False
        except ValueError:
            print("ERREUR: Dates invalides")
            return False
        
        return True