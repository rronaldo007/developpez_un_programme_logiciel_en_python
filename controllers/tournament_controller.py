import os
from typing import List, Dict

from models.tournament import Tournament
from models.match import Match
from models.player import Player
from views.tournament_view import TournamentView
from data.data_manager import DataManager
from utils.validators import validate_date_format, validate_tournament_dates
from utils.tournament_helpers import TournamentPairingHelper
from controllers.player_controller import PlayerController


class TournamentController:

    def __init__(self, data_manager: DataManager, players: List[Player]):
        self.data_manager = data_manager
        self.players = players
        self.tournaments = self._load_all_tournaments()
        self.tournament_view = TournamentView()

    def run(self):
        try:
            while True:
                choice = self.tournament_view.show_tournament_menu()
                if not self._handle_tournament_menu_choice(choice):
                    break
        except Exception as e:
            self.tournament_view.show_error(
                f"Erreur dans le gestionnaire de tournois: {e}"
            )

    def get_all_tournaments(self) -> List[Tournament]:
        return self.tournaments.copy()

    def update_players_data(self, new_players: List[Player]):
        self.players = new_players

    def save_data(self):
        for tournament in self.tournaments:
            self._save_tournament(tournament)

    def _handle_tournament_menu_choice(self, choice: str) -> bool:
        handlers = {
            "1": self._handle_create_tournament,
            "2": self._handle_list_tournaments,
            "3": self._handle_manage_tournament,
            "4": self._handle_tournament_reports,
            "0": lambda: False
        }
        handler = handlers.get(choice)
        if handler:
            return handler() if choice == "0" else (handler() or True)
        else:
            self.tournament_view.show_error(
                "Choix invalide. Entrez 0, 1, 2, 3 ou 4."
            )
            return True

    def _handle_create_tournament(self):
        try:
            data = self.tournament_view.get_tournament_creation_data()
            if not data:
                return
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
                self.tournament_view.show_success(
                    f"Tournoi '{tournament.name}' créé avec succès!"
                )
                if self._can_start_tournament(tournament):
                    if self.tournament_view.confirm_start_first_round():
                        self._handle_start_next_round(tournament)
                else:
                    self._show_tournament_creation_warnings(tournament)
            else:
                self.tournament_view.show_error(
                    "Erreur lors de la sauvegarde."
                )
        except Exception as e:
            self.tournament_view.show_error(
                f"Erreur lors de la création: {e}"
            )

    def _handle_add_players_to_tournament(self, tournament: Tournament):
        while True:
            available_players = self._get_available_players(tournament)
            if not available_players:
                self.tournament_view.show_info(
                    "Tous les joueurs ont été ajoutés."
                )
                return
            choice = self.tournament_view.show_player_selection_menu(
                available_players, tournament.players
            )
            if choice == "done":
                return
            elif choice == "create":
                self._handle_create_new_player()
            elif (isinstance(choice, int) and
                  0 <= choice < len(available_players)):
                self._add_player_to_tournament(
                    tournament, available_players[choice]
                )

    def _handle_list_tournaments(self):
        if not self.tournaments:
            self.tournament_view.show_info("Aucun tournoi enregistré.")
        else:
            self.tournament_view.show_tournaments_list(self.tournaments)

    def _handle_manage_tournament(self):
        if not self.tournaments:
            self.tournament_view.show_info("Aucun tournoi disponible.")
            return
        tournament = self.tournament_view.select_tournament(self.tournaments)
        if tournament:
            self._handle_tournament_management_menu(tournament)

    def _handle_tournament_management_menu(self, tournament: Tournament):
        while True:
            choice = self.tournament_view.show_tournament_management_menu(
                tournament
            )
            handlers = {
                "1": lambda: self.tournament_view.show_tournament_details(
                    tournament
                ),
                "2": lambda: self._handle_round_management(tournament),
                "3": lambda: self.tournament_view.show_current_standings(
                    tournament, tournament.get_current_rankings()
                ),
                "4": lambda: self.tournament_view.show_tournament_history(
                    tournament
                ),
                "5": lambda: self._handle_manage_players_in_tournament(
                    tournament
                ),
                "0": lambda: False
            }
            handler = handlers.get(choice)
            if handler:
                result = handler()
                if result is False:
                    break
            else:
                self.tournament_view.show_error("Choix invalide.")

    def _handle_round_management(self, tournament: Tournament):
        while True:
            self._auto_finish_completed_rounds_silent(tournament)
            if tournament.is_finished():
                self._handle_tournament_finished_workflow(tournament)
                return
            choice = self.tournament_view.show_round_management_menu(
                tournament
            )
            handlers = {
                "1": lambda: self._handle_start_next_round(tournament),
                "2": lambda: self._handle_enter_match_results(tournament),
                "3": lambda: self.tournament_view.show_round_details(
                    tournament.rounds[-1] if tournament.rounds else None
                ),
                "0": lambda: False
            }
            handler = handlers.get(choice)
            if handler:
                result = handler()
                if result is False:
                    break
                if tournament.is_finished():
                    self._handle_tournament_finished_workflow(tournament)
                    return
            else:
                self.tournament_view.show_error("Choix invalide.")

    def _handle_tournament_finished_workflow(self, tournament: Tournament):
        if hasattr(tournament, '_results_displayed'):
            return
        tournament._results_displayed = True
        self.tournament_view.announce_tournament_end(tournament)
        self.tournament_view.wait_for_user(
            "Appuyez sur Entrée pour retourner au menu du tournoi..."
        )

    def _handle_start_next_round(self, tournament: Tournament):
        validation_result = self._validate_next_round_conditions(tournament)
        if not validation_result['can_start']:
            self.tournament_view.show_error(
                validation_result['error_message']
            )
            return
        try:
            pairs = TournamentPairingHelper.generate_pairs_for_next_round(
                tournament
            )
            round_number = tournament.current_round + 1
            if not self.tournament_view.confirm_round_start(
                pairs, round_number
            ):
                return
            tournament.start_next_round(pairs)
            if self._save_tournament(tournament):
                self.tournament_view.show_success(
                    f"Tour {round_number} démarré avec succès!"
                )
                self._handle_post_round_start_workflow(tournament)
            else:
                self.tournament_view.show_error(
                    "Erreur lors de la sauvegarde."
                )
        except Exception as e:
            self.tournament_view.show_error(
                f"Erreur lors du démarrage du tour: {e}"
            )

    def _handle_post_round_start_workflow(self, tournament: Tournament):
        while True:
            if tournament.is_finished():
                return
            choice = self.tournament_view.show_post_round_start_menu()
            if choice == "1":
                self._handle_enter_match_results_continuous(tournament)
                if tournament.is_finished():
                    return
            elif choice == "2":
                current_round = (tournament.rounds[-1]
                                 if tournament.rounds else None)
                if current_round:
                    self.tournament_view.show_round_details(current_round)
                else:
                    self.tournament_view.show_info("Aucun tour disponible.")
            elif choice == "3":
                rankings = tournament.get_current_rankings()
                self.tournament_view.show_current_standings(
                    tournament, rankings
                )
            elif choice in ["4", "5", "0"]:
                break
            else:
                self.tournament_view.show_error("Choix invalide.")

    def _handle_enter_match_results(self, tournament: Tournament):
        if not tournament.has_started():
            self.tournament_view.show_info(
                "Le tournoi n'a pas encore commencé."
            )
            return
        if tournament.is_finished():
            self.tournament_view.show_info("Le tournoi est terminé.")
            return
        current_round = (tournament.rounds[-1]
                         if tournament.rounds else None)
        if not current_round:
            self.tournament_view.show_info("Aucun tour disponible.")
            return
        if current_round.is_finished:
            self.tournament_view.show_info(
                "Le tour actuel est déjà terminé."
            )
            if tournament.current_round < tournament.number_of_rounds:
                if self.tournament_view.confirm_next_round_immediate():
                    self._handle_start_next_round(tournament)
            return
        unfinished_matches = current_round.get_unfinished_matches()
        if not unfinished_matches:
            self.tournament_view.show_info("Finalisation du tour en cours...")
            self._auto_finish_completed_rounds_silent(tournament)
            return
        self._handle_enter_match_results_continuous(tournament)

    def _handle_enter_match_results_continuous(self, tournament: Tournament):
        while True:
            if tournament.is_finished():
                return
            current_round = (tournament.rounds[-1]
                             if tournament.rounds else None)
            if not current_round or current_round.is_finished:
                return
            unfinished_matches = current_round.get_unfinished_matches()
            if not unfinished_matches:
                return
            match_choice = self.tournament_view.select_match_for_results(
                current_round, unfinished_matches, tournament
            )
            if match_choice == "back":
                return
            elif (isinstance(match_choice, int) and
                  0 <= match_choice < len(unfinished_matches)):
                result = self._handle_single_match_result(
                    tournament, unfinished_matches[match_choice]
                )
                if tournament.is_finished():
                    return
                if not result:
                    continue

    def _handle_single_match_result(self, tournament: Tournament,
                                    match: Match) -> bool:
        result = self.tournament_view.get_match_result_input(
            match, tournament.players
        )

        if result:
            match.set_result(result['player1_score'], result['player2_score'])
            tournament.add_score_to_player(
                match.player1_national_id, match.player1_score
            )
            tournament.add_score_to_player(
                match.player2_national_id, match.player2_score
            )

            if self._save_tournament(tournament):
                self.tournament_view.announce_match_result(
                    match, tournament.players
                )

                current_round = (tournament.rounds[-1]
                                 if tournament.rounds else None)
                if current_round and current_round.all_matches_finished():
                    self._auto_finish_completed_rounds_silent(tournament)

                    if tournament.is_finished():
                        self._handle_tournament_finished_workflow(tournament)
                        return False

                return True
            else:
                self.tournament_view.show_error(
                    "Erreur lors de la sauvegarde."
                )
                return False
        return False

    def _auto_finish_completed_rounds_silent(self, tournament: Tournament):
        if not tournament.rounds:
            return

        current_round = tournament.rounds[-1]
        if (current_round.all_matches_finished() and
                not current_round.is_finished):
            try:
                current_round.end_round()
                if tournament.current_round >= tournament.number_of_rounds:
                    tournament.finish_tournament()
                if self._save_tournament(tournament):
                    if not tournament.is_finished():
                        self._handle_round_completion_workflow(tournament)
                else:
                    self.tournament_view.show_error(
                        "Erreur lors de la sauvegarde."
                    )
            except Exception as e:
                self.tournament_view.show_error(
                    f"Erreur lors de la finalisation: {e}"
                )

    def _handle_round_completion_workflow(self, tournament: Tournament):
        if tournament.current_round >= tournament.number_of_rounds:
            tournament.finish_tournament()
            return

        current_round = (tournament.rounds[-1]
                         if tournament.rounds else None)
        if current_round:
            round_name = current_round.name
            self.tournament_view.show_success(f"{round_name} terminé!")

        if self.tournament_view.confirm_next_round_immediate():
            self._handle_start_next_round(tournament)

    def _validate_next_round_conditions(self, tournament: Tournament) -> Dict:
        if len(tournament.players) < 2:
            return {
                'can_start': False,
                'error_message': ("Il faut au moins 2 joueurs pour "
                                  "commencer un tournoi.")
            }
        if len(tournament.players) % 2 != 0:
            return {
                'can_start': False,
                'error_message': (f"Il faut un nombre PAIR de joueurs. "
                                  f"Vous en avez {len(tournament.players)}.")
            }
        if tournament.is_finished():
            return {
                'can_start': False,
                'error_message': "Ce tournoi est terminé."
            }
        if tournament.rounds:
            current_round = tournament.rounds[-1]
            if (not current_round.is_finished and
                    current_round.all_matches_finished()):
                return {
                    'can_start': False,
                    'error_message': ("Le tour actuel doit être finalisé. "
                                      "Utilisez 'Saisir résultats' pour "
                                      "le terminer.")
                }
            if not current_round.is_finished:
                unfinished_count = len(current_round.get_unfinished_matches())
                return {
                    'can_start': False,
                    'error_message': (f"Le tour actuel n'est pas terminé "
                                      f"({unfinished_count} match(s) "
                                      f"restant(s)).")
                }
        if tournament.current_round >= tournament.number_of_rounds:
            return {
                'can_start': False,
                'error_message': "Tous les tours prévus ont été joués."
            }
        return {'can_start': True}

    def _validate_tournament_data(self, data: Dict[str, str]) -> bool:
        if not self._validate_tournament_name_flexible(data['name']):
            self.tournament_view.show_error("Nom invalide.")
            return False
        if not self._validate_location_flexible(data['location']):
            self.tournament_view.show_error("Lieu invalide.")
            return False
        if not validate_date_format(data['start_date']):
            self.tournament_view.show_error(
                "Format de date de début invalide (YYYY-MM-DD)."
            )
            return False
        if not validate_date_format(data['end_date']):
            self.tournament_view.show_error(
                "Format de date de fin invalide (YYYY-MM-DD)."
            )
            return False
        dates_valid, error_message = validate_tournament_dates(
            data['start_date'],
            data['end_date']
        )
        if not dates_valid:
            self.tournament_view.show_error(error_message)
            return False
        try:
            rounds = int(data.get('number_of_rounds', 4))
            if rounds < 1 or rounds > 20:
                self.tournament_view.show_error(
                    "Nombre de tours invalide (1-20)."
                )
                return False
        except ValueError:
            self.tournament_view.show_error(
                "Nombre de tours doit être un nombre entier."
            )
            return False
        return True

    def _validate_tournament_name_flexible(self, name: str) -> bool:
        if not name or not isinstance(name, str):
            return False
        name = name.strip()
        if len(name) < 1 or len(name) > 100:
            return False
        import re
        pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-'\.]+$"
        return bool(re.match(pattern, name))

    def _validate_location_flexible(self, location: str) -> bool:
        if not location or not isinstance(location, str):
            return False
        location = location.strip()
        if len(location) < 1 or len(location) > 200:
            return False
        import re
        pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-',\.]+$"
        return bool(re.match(pattern, location))

    def _can_start_tournament(self, tournament: Tournament) -> bool:
        return (len(tournament.players) >= 2 and
                len(tournament.players) % 2 == 0)

    def _show_tournament_creation_warnings(self, tournament: Tournament):
        if len(tournament.players) < 2:
            self.tournament_view.show_warning(
                "Il faut au moins 2 joueurs pour démarrer un tour."
            )
        elif len(tournament.players) % 2 != 0:
            self.tournament_view.show_warning(
                "Le nombre de joueurs est impair. Ajoutez un joueur."
            )

    def _get_available_players(self, tournament: Tournament) -> List[Player]:
        return [
            p for p in self.players
            if p.national_id not in [tp.national_id for tp in
                                     tournament.players]
        ]

    def _add_player_to_tournament(self, tournament: Tournament,
                                  player: Player) -> bool:
        try:
            tournament.add_player(player)
            if self.data_manager.save_tournament(tournament):
                self.tournament_view.show_success(
                    f"{player.get_full_name()} ajouté au tournoi."
                )
                return True
            else:
                tournament.remove_player(player)
                self.tournament_view.show_error(
                    "Erreur lors de la sauvegarde."
                )
                return False
        except Exception as e:
            self.tournament_view.show_error(f"Erreur lors de l'ajout: {e}")
            return False

    def _handle_create_new_player(self):
        player_controller = PlayerController(self.data_manager, self.players)
        player_controller._handle_add_player()
        self.players = self.data_manager.load_players()

    def _handle_manage_players_in_tournament(self, tournament: Tournament):
        if not tournament.has_started():
            self._handle_add_players_to_tournament(tournament)
            self._save_tournament(tournament)
        else:
            self.tournament_view.show_error(
                "Impossible d'ajouter des joueurs après le début du tournoi."
            )

    def _handle_tournament_reports(self):
        choice = self.tournament_view.show_reports_menu()
        report_handlers = {
            "1": (lambda: self.tournament_view.show_all_tournaments_report(
                self.tournaments
            ) if self.tournaments else None),
            "2": self._generate_tournament_details_report,
            "3": self._generate_rounds_report,
            "4": self._generate_matches_report
        }
        handler = report_handlers.get(choice)
        if handler:
            handler()

    def _generate_tournament_details_report(self):
        if not self.tournaments:
            self.tournament_view.show_info("Aucun tournoi disponible.")
            return
        tournament = self.tournament_view.select_tournament(self.tournaments)
        if tournament:
            self.tournament_view.show_detailed_tournament_report(tournament)

    def _generate_rounds_report(self):
        if not self.tournaments:
            self.tournament_view.show_info("Aucun tournoi disponible.")
            return
        tournament = self.tournament_view.select_tournament(self.tournaments)
        if tournament and tournament.rounds:
            self.tournament_view.show_rounds_report(tournament)
        elif tournament:
            self.tournament_view.show_info(
                "Aucun tour joué dans ce tournoi."
            )

    def _generate_matches_report(self):
        if not self.tournaments:
            self.tournament_view.show_info("Aucun tournoi disponible.")
            return
        tournament = self.tournament_view.select_tournament(self.tournaments)
        if tournament and tournament.rounds:
            self.tournament_view.show_matches_report(tournament)
        elif tournament:
            self.tournament_view.show_info(
                "Aucun match joué dans ce tournoi."
            )

    def _load_all_tournaments(self) -> List[Tournament]:
        tournaments = []
        players_lookup = {p.national_id: p for p in self.players}
        for file_path in self.data_manager.get_all_tournament_files():
            try:
                filename = os.path.basename(file_path)
                tournament_id = int(
                    filename.replace('tournament_', '').replace('.json', '')
                )
                tournament = self.data_manager.load_tournament(
                    tournament_id, players_lookup
                )
                if tournament:
                    tournaments.append(tournament)
            except Exception as e:
                print(f"Erreur chargement tournoi {file_path}: {e}")
        return tournaments

    def _save_tournament(self, tournament: Tournament) -> bool:
        return self.data_manager.save_tournament(tournament)
