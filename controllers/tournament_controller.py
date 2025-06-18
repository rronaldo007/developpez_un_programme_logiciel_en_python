
import os
from typing import List, Optional, Dict, Tuple
from models.tournament import Tournament
from models.round import Round
from models.match import Match
from models.player import Player
from views.tournament_view import TournamentView
from data.data_manager import DataManager
from utils.validators import validate_name, validate_date_format
from controllers.player_controller import PlayerController
from utils.tournament_helpers import TournamentPairingHelper


class TournamentController:
    def __init__(self, data_manager: DataManager, players: List[Player]):
        self.data_manager = data_manager
        self.players = players
        self.tournaments = self._load_all_tournaments()
        self.tournament_view = TournamentView()

    def run(self):
        try:
            while True:
                self.tournament_view.display_tournament_menu()
                choice = self.tournament_view.get_user_choice("Votre choix")
                if not self._handle_tournament_menu_choice(choice):
                    break
        except Exception as e:
            self.tournament_view.display_error(f"Erreur dans le gestionnaire de tournois: {e}")

    def _handle_tournament_menu_choice(self, choice: str) -> bool:
        try:
            if choice == "1":
                self._handle_create_tournament()
            elif choice == "2":
                self._handle_list_tournaments()
            elif choice == "3":
                self._handle_manage_tournament()
            elif choice == "4":
                self._handle_tournament_reports()
            elif choice == "0":
                return False
            else:
                self.tournament_view.display_error("Choix invalide. Entrez 0, 1, 2, 3 ou 4.")
        except Exception as e:
            self.tournament_view.display_error(f"Erreur lors du traitement: {e}")
        return True

    def _validate_tournament_name_flexible(self, name: str) -> bool:
        """
        Validation flexible pour les noms de tournois
        Accepte lettres, chiffres, espaces, tirets, apostrophes, points
        """
        if not name or not isinstance(name, str):
            return False
            
        name = name.strip()
        
        # Minimum 1 caractère, maximum 100
        if len(name) < 1 or len(name) > 100:
            return False
            
        # Pattern flexible : lettres, chiffres, espaces, tirets, apostrophes, points
        import re
        pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-'\.]+$"
        return bool(re.match(pattern, name))

    def _validate_location_flexible(self, location: str) -> bool:
        """
        Validation flexible pour les lieux
        Accepte lettres, chiffres, espaces, tirets, apostrophes, virgules, points
        """
        if not location or not isinstance(location, str):
            return False
            
        location = location.strip()
        
        # Minimum 1 caractère, maximum 200
        if len(location) < 1 or len(location) > 200:
            return False
            
        # Pattern flexible
        import re
        pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-',\.]+$"
        return bool(re.match(pattern, location))

    def _handle_list_tournaments(self):
        if not self.tournaments:
            self.tournament_view.display_info("Aucun tournoi enregistré.")
            return
        self.tournament_view.display_tournaments_list(self.tournaments)
        self.tournament_view.wait_for_user()

    def _handle_create_tournament(self):
        try:
            data = self.tournament_view.get_tournament_info()
            if not self._validate_tournament_data(data):
                return

            tournament = Tournament(
                name=data['name'],
                location=data['location'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                description=data.get('description', ''),
                number_of_rounds=int(data.get('number_of_rounds', 4))
            )

            self.tournaments.append(tournament)
            self._handle_add_players_to_tournament(tournament)

            if self._save_tournament(tournament):
                self.tournament_view.display_success(f"Tournoi '{tournament.name}' créé avec succès!")
                self.tournament_view.display_tournament_details(tournament)

                if len(tournament.players) < 2:
                    self.tournament_view.display_warning("Tournoi sauvegardé, mais il faut au moins 2 joueurs pour démarrer un tour.")
                    return
                if len(tournament.players) % 2 != 0:
                    self.tournament_view.display_warning("Le nombre de joueurs est impair. Ajoutez un joueur pour permettre l'appariement.")
                    return

                if self.tournament_view.confirm_action("Voulez-vous commencer le premier tour"):
                    self._handle_start_next_round(tournament.id)
            else:
                self.tournament_view.display_error("Erreur lors de la sauvegarde.")
        except Exception as e:
            self.tournament_view.display_error(f"Erreur lors de la création: {e}")

    def _handle_add_players_to_tournament(self, tournament: Tournament):
        """Gère l'ajout de joueurs à un tournoi - Ajout immédiat"""
        try:
            while True:
                if not self.players:
                    self.tournament_view.display_error("Aucun joueur disponible.")
                    return
                    
                available_players = [
                    p for p in self.players
                    if p.national_id not in [tp.national_id for tp in tournament.players]
                ]
                
                if not available_players:
                    self.tournament_view.display_info("Tous les joueurs ont déjà été ajoutés.")
                    return
                    
                choice = self.tournament_view.select_multiple_players_inline(
                    available_players, tournament.players
                )
                
                if choice == "__done__":
                    return
                    
                elif choice == "__create__":
                    from controllers.player_controller import PlayerController
                    player_controller = PlayerController(self.data_manager, self.players)
                    player_controller._handle_add_player()
                    
                    # Recharge les données après création
                    self.players = self.data_manager.load_players()
                    continue
                    
                elif isinstance(choice, int):
                    try:
                        # Recalculer les joueurs disponibles AVANT d'utiliser l'index
                        available_players = [
                            p for p in self.players
                            if p.national_id not in [tp.national_id for tp in tournament.players]
                        ]
                        selected = available_players[choice]
                        tournament.add_player(selected)
                        
                        # Sauvegarde immédiate
                        self.data_manager.save_tournament(tournament)
                        self.tournament_view.display_success(f"{selected.get_full_name()} ajouté au tournoi.")
                        
                        # Continue la boucle pour permettre d'ajouter d'autres joueurs
                        continue
                        
                    except (IndexError, ValueError):
                        self.tournament_view.display_error("Erreur lors de l'ajout du joueur.")
                        
        except KeyboardInterrupt:
            pass

    def _handle_manage_tournament(self):
        tournament = self.tournament_view.select_tournament_from_list(self.tournaments)
        if tournament:
            self._handle_tournament_management_menu(tournament)

    def _handle_tournament_management_menu(self, tournament: Tournament):
        """Menu principal de gestion d'un tournoi avec redirection vers le menu des tours"""
        while True:
            self.tournament_view.display_tournament_management_menu(tournament)
            choice = self.tournament_view.get_user_choice("Votre choix")
            
            if choice == "1":
                self.tournament_view.display_tournament_details(tournament)
                self.tournament_view.wait_for_user()
                
            elif choice == "2":
                # Rediriger vers le menu des tours
                self._handle_round_management(tournament)
                
            elif choice == "3":
                self._handle_view_current_standings(tournament.id)
                
            elif choice == "4":
                self._handle_tournament_history(tournament.id)
                
            elif choice == "5":
                if not tournament.has_started():
                    self._handle_add_players_to_tournament(tournament)
                    self._save_tournament(tournament)
                else:
                    self.tournament_view.display_error("Impossible d'ajouter des joueurs après le début du tournoi.")
                    
            elif choice == "0":
                break
            else:
                self.tournament_view.display_error("Choix invalide.")

    def _handle_round_management(self, tournament: Tournament):
        """
        Gère le menu spécialisé pour les tours et matchs
        
        Args:
            tournament: Tournoi à gérer
        """
        while True:
            # Afficher le menu des tours
            self.tournament_view.display_round_management_menu(tournament)
            choice = self.tournament_view.get_user_choice("Votre choix")
            
            if choice == "1":
                # Commencer le tour suivant
                self._handle_start_next_round(tournament.id)
                
            elif choice == "2":
                # Saisir les résultats des matchs
                if tournament.has_started() and not tournament.is_finished():
                    current_round = tournament.rounds[-1] if tournament.rounds else None
                    if current_round and not current_round.is_finished:
                        self._handle_enter_match_results_continuous(tournament.id)
                    else:
                        self.tournament_view.display_info("Tous les matchs du tour précédent sont terminés.")
                else:
                    self.tournament_view.display_info("Aucun tour en cours.")
                    
            elif choice == "3":
                # Voir l'état du tour actuel
                self._handle_view_current_round_status(tournament)
                
            elif choice == "0":
                # Retour au menu du tournoi
                break
            else:
                self.tournament_view.display_error("Choix invalide.")

    def _handle_start_next_round(self, tournament_id: int):
        tournament = self.get_tournament_by_id(tournament_id)
        if not tournament:
            self.tournament_view.display_error("Tournoi introuvable.")
            return
        
        if len(tournament.players) < 2:
            self.tournament_view.display_error("Il faut au moins 2 joueurs pour commencer un tournoi.")
            return
            
        if len(tournament.players) % 2 != 0:
            self.tournament_view.display_error("Il faut un nombre PAIR de joueurs pour commencer un tournoi.")
            self.tournament_view.display_info(f"Vous avez actuellement {len(tournament.players)} joueurs. Ajoutez 1 joueur supplémentaire.")
            return
        
        if not tournament.can_start_next_round():
            if tournament.is_finished():
                self.tournament_view.display_info("Ce tournoi est terminé.")
                self._display_tournament_completion(tournament)
            elif tournament.rounds and not tournament.rounds[-1].is_finished:
                self.tournament_view.display_error("Le tour actuel n'est pas terminé.")
            else:
                self.tournament_view.display_error("Impossible de démarrer un nouveau tour.")
            return
            
        try:
            pairs = TournamentPairingHelper.generate_pairs_for_next_round(tournament)
            round_number = tournament.current_round + 1
            self.tournament_view.display_round_preview(pairs, round_number)
            if not self.tournament_view.confirm_action("Confirmer le démarrage de ce tour"):
                return
            new_round = tournament.start_next_round(pairs)
            if self._save_tournament(tournament):
                self.tournament_view.display_success(f"Tour {round_number} démarré avec succès!")
                self.tournament_view.display_round_details(new_round)
        except Exception as e:
            self.tournament_view.display_error(f"Erreur: {e}")

    def _handle_enter_match_results(self, tournament_id: int):
        """Gère la saisie des résultats - """
        tournament = self.get_tournament_by_id(tournament_id)
        if not tournament:
            self.tournament_view.display_error("Tournoi introuvable.")
            return
            
        if not tournament.rounds or tournament.rounds[-1].is_finished:
            self.tournament_view.display_info("Aucun tour en cours.")
            return
            
        current_round = tournament.rounds[-1]
        unfinished_matches = current_round.get_unfinished_matches()
        
        if not unfinished_matches:
            self.tournament_view.display_info("Tous les matchs sont terminés.")
            return
            
        match = self.tournament_view.select_match_from_list(unfinished_matches)
        if not match:
            return
        
        # : Passer la liste des joueurs du tournoi
        result = self.tournament_view.get_match_result(match, tournament.players)
        
        if result:
            match.set_result(result['player1_score'], result['player2_score'])
            # : Mettre à jour les scores via le tournament
            self._update_tournament_scores_from_match(match, tournament)
            
            if current_round.all_matches_finished():
                self._try_finish_round(tournament, current_round)
                
            self._save_tournament(tournament)

    def _handle_enter_match_results_continuous(self, tournament_id: int):
        """Saisie continue des résultats - """
        tournament = self.get_tournament_by_id(tournament_id)
        if not tournament:
            return
            
        while True:
            current_round = tournament.rounds[-1] if tournament.rounds else None
            if not current_round or current_round.is_finished:
                break
                
            unfinished_matches = current_round.get_unfinished_matches()
            if not unfinished_matches:
                break
                
            # Afficher l'interface de saisie
            match_choice = self.tournament_view.display_match_results_menu(
                current_round, unfinished_matches, tournament
            )
            
            if match_choice == "__back__":
                break
            elif isinstance(match_choice, int) and 0 <= match_choice < len(unfinished_matches):
                match = unfinished_matches[match_choice]
                
                # : Passer la liste des joueurs du tournoi
                result = self.tournament_view.get_match_result(match, tournament.players)
                
                if result:
                    match.set_result(result['player1_score'], result['player2_score'])
                    # : Mettre à jour les scores via le tournament
                    self._update_tournament_scores_from_match(match, tournament)
                    self.tournament_view.display_success("Résultat enregistré!")
                    
                    # Vérifier si le tour est terminé
                    if current_round.all_matches_finished():
                        self._try_finish_round(tournament, current_round)
                        break
                    
                    self._save_tournament(tournament)

    def _handle_view_current_round_status(self, tournament: Tournament):
        """Affiche l'état détaillé du tour actuel"""
        if not tournament.has_started():
            self.tournament_view.display_info("Le tournoi n'a pas encore commencé.")
            return
            
        if tournament.is_finished():
            self.tournament_view.display_info("Le tournoi est terminé.")
            return
            
        current_round = tournament.rounds[-1] if tournament.rounds else None
        if current_round:
            self.tournament_view.display_round_details(current_round)
            self.tournament_view.wait_for_user()
        else:
            self.tournament_view.display_info("Aucun tour disponible.")

    def _try_finish_round(self, tournament: Tournament, round_obj: Round):
        """Version complète avec gestion du départage"""
        try:
            round_obj.end_round()
            
            # Déterminer si c'est un tour de départage
            is_tiebreaker = "départage" in round_obj.name.lower()
            
            if is_tiebreaker:
                self.tournament_view.display_success(f"Tour de départage {round_obj.name} terminé!")
                self._handle_tiebreaker_completion(tournament)
            else:
                self.tournament_view.display_success(f"Tour {round_obj.name} terminé!")
                
                # Logique normale de fin de tour
                if tournament.current_round >= tournament.number_of_rounds:
                    if self._needs_tiebreaker_round(tournament):
                        tied_players = self._get_tied_players_for_first(tournament)
                        
                        self.tournament_view.display_tiebreaker_notification(tied_players)
                        
                        if self._can_create_tiebreaker_pairs(tournament):
                            if self.tournament_view.confirm_action("Organiser un tour de départage"):
                                self._handle_tiebreaker_round(tournament)
                                return
                    
                    # Terminer le tournoi (avec ou sans égalité)
                    tournament.finish_tournament()
                    self._display_tournament_completion(tournament)
                else:
                    # Proposer le tour suivant
                    if self.tournament_view.confirm_action("Démarrer le tour suivant"):
                        self._handle_start_next_round(tournament.id)
                        
        except Exception as e:
            self.tournament_view.display_error(f"Erreur: {e}")

    def _needs_tiebreaker_round(self, tournament: Tournament) -> bool:
        """
        Détermine si un tour de départage est nécessaire 
        
        Args:
            tournament: Tournoi à vérifier
            
        Returns:
            bool: True si un départage est nécessaire
        """
        if len(tournament.players) < 2:
            return False
            
        rankings = tournament.get_current_rankings()
        if len(rankings) < 2:
            return False
            
        # : Récupérer les scores depuis le tournoi
        first_score = tournament.get_player_score(rankings[0].national_id)
        second_score = tournament.get_player_score(rankings[1].national_id)
        
        return abs(first_score - second_score) < 0.001

    def _get_tied_players_for_first(self, tournament: Tournament) -> List[Player]:
        """
        Retourne la liste des joueurs à égalité au premier rang 
        
        Args:
            tournament: Tournoi à analyser
            
        Returns:
            List[Player]: Joueurs à égalité pour la première place
        """
        rankings = tournament.get_current_rankings()
        if not rankings:
            return []
            
        # : Récupérer le score depuis le tournoi
        first_score = tournament.get_player_score(rankings[0].national_id)
        tied_players = []
        
        for player in rankings:
            player_score = tournament.get_player_score(player.national_id)
            if abs(player_score - first_score) < 0.001:
                tied_players.append(player)
            else:
                break  # Plus d'égalité
                
        return tied_players if len(tied_players) > 1 else []

    def _can_create_tiebreaker_pairs(self, tournament: Tournament) -> bool:
        """
        Vérifie si on peut créer des paires pour le départage
        
        Args:
            tournament: Tournoi à vérifier
            
        Returns:
            bool: True si possible de faire des paires
        """
        tied_players = self._get_tied_players_for_first(tournament)
        return len(tied_players) >= 2 and len(tied_players) % 2 == 0

    def _generate_tiebreaker_pairs(self, tournament: Tournament) -> List[Tuple[Player, Player]]:
        """
        Génère les paires pour un tour de départage
        
        Args:
            tournament: Tournoi nécessitant un départage
            
        Returns:
            List[Tuple[Player, Player]]: Paires pour le départage
        """
        tied_players = self._get_tied_players_for_first(tournament)
        
        if len(tied_players) < 2:
            raise ValueError("Pas assez de joueurs à égalité pour un départage")
            
        if len(tied_players) % 2 != 0:
            raise ValueError("Nombre impair de joueurs à égalité - départage impossible")
        
        # Pour le départage, apparier les joueurs à égalité entre eux
        pairs = []
        
        if len(tied_players) == 2:
            # Cas simple : 2 joueurs à égalité
            pairs.append((tied_players[0], tied_players[1]))
            
        elif len(tied_players) == 4:
            # 4 joueurs à égalité : apparier 1vs2 et 3vs4
            pairs.append((tied_players[0], tied_players[1]))
            pairs.append((tied_players[2], tied_players[3]))
            
        else:
            # Plus de 4 joueurs : appariement séquentiel
            for i in range(0, len(tied_players), 2):
                if i + 1 < len(tied_players):
                    pairs.append((tied_players[i], tied_players[i + 1]))
        
        return pairs

    def _handle_tiebreaker_round(self, tournament: Tournament):
        """
        Gère un tour de départage
        
        Args:
            tournament: Tournoi nécessitant un départage
        """
        try:
            # Générer les paires de départage
            tiebreaker_pairs = self._generate_tiebreaker_pairs(tournament)
            
            # Créer le tour de départage
            tiebreaker_round_number = tournament.current_round + 1
            tiebreaker_name = f"Départage {tiebreaker_round_number}"
            
            self.tournament_view.display_title("TOUR DE DÉPARTAGE")
            self.tournament_view.display_info(f"Organisation du {tiebreaker_name}")
            
            # Afficher l'aperçu des paires
            self.tournament_view.display_tiebreaker_preview(tiebreaker_pairs, tiebreaker_round_number)
            
            if not self.tournament_view.confirm_action("Confirmer le démarrage du tour de départage"):
                self.tournament_view.display_info("Tour de départage annulé. Égalité maintenue.")
                tournament.finish_tournament()
                self._display_tournament_completion(tournament)
                return
            
            # Démarrer le tour de départage
            new_round = tournament.start_next_round(tiebreaker_pairs)
            new_round.name = tiebreaker_name  # Changer le nom pour indiquer que c'est un départage
            
            if self._save_tournament(tournament):
                self.tournament_view.display_success(f"{tiebreaker_name} démarré avec succès!")
                self.tournament_view.display_round_details(new_round)
                
                # Saisie immédiate des résultats du départage
                if self.tournament_view.confirm_action("Voulez-vous saisir les résultats maintenant"):
                    self._handle_enter_match_results_continuous(tournament.id)
            else:
                self.tournament_view.display_error("Erreur lors de la sauvegarde du tour de départage.")
                
        except Exception as e:
            self.tournament_view.display_error(f"Erreur lors du départage: {e}")

    def _handle_tiebreaker_completion(self, tournament: Tournament):
        """
        Gère la fin d'un tour de départage
        
        Args:
            tournament: Tournoi après départage
        """
        try:
            # Analyser les résultats du départage
            tiebreaker_results = self._check_tiebreaker_resolution(tournament)
            
            # Afficher l'analyse des résultats
            self.tournament_view.display_tiebreaker_completion_analysis(tiebreaker_results)
            
            if tiebreaker_results['resolved']:
                # Égalité résolue !
                tournament.finish_tournament()
                self._display_tournament_completion(tournament)
                
            else:
                # Encore une égalité
                if tiebreaker_results['can_continue']:
                    if self.tournament_view.confirm_action("Continuer avec un nouveau tour de départage"):
                        self._handle_tiebreaker_round(tournament)
                        return
                
                # Arrêter les départages
                self.tournament_view.display_info("Départages terminés. Égalité maintenue.")
                tournament.finish_tournament()
                self._display_tournament_completion(tournament)
                
        except Exception as e:
            self.tournament_view.display_error(f"Erreur lors de l'analyse du départage: {e}")

    def _check_tiebreaker_resolution(self, tournament: Tournament) -> Dict:
        """
        Vérifie si le départage a résolu l'égalité 
        
        Args:
            tournament: Tournoi après départage
            
        Returns:
            Dict: Résultats de l'analyse du départage
        """
        rankings = tournament.get_current_rankings()
        
        if len(rankings) < 2:
            return {'resolved': True, 'winner': rankings[0] if rankings else None}
        
        # : Récupérer les scores depuis le tournoi
        first_score = tournament.get_player_score(rankings[0].national_id)
        second_score = tournament.get_player_score(rankings[1].national_id)
        
        if abs(first_score - second_score) < 0.001:
            # Encore une égalité
            tied_count = len([p for p in rankings 
                            if abs(tournament.get_player_score(p.national_id) - first_score) < 0.001])
            return {
                'resolved': False,
                'tied_players_count': tied_count,
                'can_continue': tied_count <= 4 and tied_count % 2 == 0
            }
        else:
            # Égalité résolue
            return {
                'resolved': True,
                'winner': rankings[0],
                'final_score': first_score
            }

    def _display_tournament_completion(self, tournament: Tournament):
        rankings = tournament.get_final_rankings()
        winner = rankings[0] if rankings else None
        
        # Ajouter des statistiques de départage si applicable
        stats = tournament.get_tournament_statistics() if hasattr(tournament, 'get_tournament_statistics') else {}
        
        # Compter les tours de départage
        tiebreaker_rounds = sum(1 for r in tournament.rounds if "départage" in r.name.lower())
        if tiebreaker_rounds > 0:
            stats['tiebreaker_rounds'] = tiebreaker_rounds
        
        self.tournament_view.display_tournament_completion(tournament, winner, rankings, stats)

    def _update_tournament_scores_from_match(self, match: Match, tournament: Tournament):
        """
        : Met à jour les scores via le tournament au lieu des objets Player
        
        Args:
            match: Match terminé
            tournament: Tournoi contenant les scores
        """
        # Mettre à jour les scores dans le tournoi
        tournament.add_score_to_player(match.player1_national_id, match.player1_score)
        tournament.add_score_to_player(match.player2_national_id, match.player2_score)

    def _handle_view_current_standings(self, tournament_id: int):
        tournament = self.get_tournament_by_id(tournament_id)
        if tournament:
            rankings = tournament.get_current_rankings()
            self.tournament_view.display_current_standings(tournament, rankings)
            self.tournament_view.wait_for_user()

    def _handle_tournament_history(self, tournament_id: int):
        tournament = self.get_tournament_by_id(tournament_id)
        if tournament:
            self.tournament_view.display_tournament_history(tournament)
            self.tournament_view.wait_for_user()

    def _handle_tournament_reports(self):
        self.tournament_view.display_reports_menu()
        choice = self.tournament_view.get_user_choice("Votre choix")
        if choice == "1":
            self._generate_all_tournaments_report()
        elif choice == "2":
            self._generate_tournament_details_report()
        elif choice == "3":
            self._generate_rounds_report()
        elif choice == "4":
            self._generate_matches_report()

    def _generate_all_tournaments_report(self):
        if self.tournaments:
            self.tournament_view.display_all_tournaments_report(self.tournaments)
            self.tournament_view.wait_for_user()

    def _generate_tournament_details_report(self):
        tournament = self.tournament_view.select_tournament_from_list(self.tournaments)
        if tournament:
            self.tournament_view.display_detailed_tournament_report(tournament)
            self.tournament_view.wait_for_user()

    def _generate_rounds_report(self):
        tournament = self.tournament_view.select_tournament_from_list(self.tournaments)
        if tournament and tournament.rounds:
            self.tournament_view.display_rounds_report(tournament)
            self.tournament_view.wait_for_user()

    def _generate_matches_report(self):
        tournament = self.tournament_view.select_tournament_from_list(self.tournaments)
        if tournament and tournament.rounds:
            self.tournament_view.display_matches_report(tournament)
            self.tournament_view.wait_for_user()

    def _validate_tournament_data(self, data: Dict[str, str]) -> bool:
        # : Utiliser validate_tournament_name au lieu de validate_name pour le nom du tournoi
        if not self._validate_tournament_name_flexible(data['name']):
            self.tournament_view.display_error("Nom invalide.")
            return False
        if not self._validate_location_flexible(data['location']):
            self.tournament_view.display_error("Lieu invalide.")
            return False
        if not validate_date_format(data['start_date']) or not validate_date_format(data['end_date']):
            self.tournament_view.display_error("Dates invalides.")
            return False
        try:
            rounds = int(data.get('number_of_rounds', 4))
            if rounds < 1 or rounds > 20:
                self.tournament_view.display_error("Nombre de tours invalide.")
                return False
        except ValueError:
            self.tournament_view.display_error("Nombre de tours doit être un nombre entier.")
            return False
        return True

    def _load_all_tournaments(self) -> List[Tournament]:
        tournaments = []
        players_lookup = {p.national_id: p for p in self.players}
        for file_path in self.data_manager.get_all_tournament_files():
            try:
                filename = os.path.basename(file_path)
                tournament_id = int(filename.replace('tournament_', '').replace('.json', ''))
                tournament = self.data_manager.load_tournament(tournament_id, players_lookup)
                if tournament:
                    tournaments.append(tournament)
            except Exception as e:
                print(f"Erreur chargement tournoi {file_path}: {e}")
        return tournaments

    def _save_tournament(self, tournament: Tournament) -> bool:
        return self.data_manager.save_tournament(tournament)

    def get_all_tournaments(self) -> List[Tournament]:
        return self.tournaments.copy()

    def get_tournament_by_id(self, tournament_id: int) -> Optional[Tournament]:
        for t in self.tournaments:
            if t.id == tournament_id:
                return t
        return None

    def update_players_data(self, new_players: List[Player]):
        self.players = new_players

    def save_data(self):
        for tournament in self.tournaments:
            self._save_tournament(tournament)