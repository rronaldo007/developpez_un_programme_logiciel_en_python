from controllers.player_controller import PlayerController
from controllers.tournament_controller import TournamentController
from views.statistic_view import StatisticsView


class StatisticsController:

    def __init__(self, player_controller: PlayerController,
                 tournament_controller: TournamentController):
        self.player_controller = player_controller
        self.tournament_controller = tournament_controller
        self.statistics_view = StatisticsView()

    def run(self):
        try:
            while True:
                self.statistics_view.display_simple_statistics_menu()
                choice = self.statistics_view.get_user_choice("Votre choix")

                if not self._handle_statistics_menu_choice(choice):
                    break

        except Exception as e:
            self.statistics_view.display_error(
                f"Erreur dans les statistiques: {e}"
            )

    def _handle_statistics_menu_choice(self, choice: str) -> bool:
        try:
            if choice == "1":
                self._show_all_players_alphabetical()
            elif choice == "2":
                self._show_all_tournaments()
            elif choice == "3":
                self._show_tournament_details()
            elif choice == "4":
                self._show_tournament_players()
            elif choice == "5":
                self._show_tournament_rounds_and_matches()
            elif choice == "6":
                self._show_simple_global_stats()
            elif choice == "0":
                return False
            else:
                self.statistics_view.display_error(
                    "Choix invalide. Entrez 0, 1, 2, 3, 4, 5 ou 6."
                )

        except Exception as e:
            self.statistics_view.display_error(
                f"Erreur lors du traitement: {e}"
            )

        return True

    def _show_all_players_alphabetical(self):
        players = self.player_controller.get_all_players()

        if not players:
            self.statistics_view.display_info("Aucun joueur enregistré.")
            return

        sorted_players = sorted(
            players,
            key=lambda p: (p.last_name.lower(), p.first_name.lower())
        )
        self.statistics_view.display_players_alphabetical_list(sorted_players)
        self.statistics_view.wait_for_user()

    def _show_all_tournaments(self):
        tournaments = self.tournament_controller.get_all_tournaments()

        if not tournaments:
            self.statistics_view.display_info("Aucun tournoi créé.")
            return

        self.statistics_view.display_tournaments_list(tournaments)
        self.statistics_view.wait_for_user()

    def _show_tournament_details(self):
        tournaments = self.tournament_controller.get_all_tournaments()

        if not tournaments:
            self.statistics_view.display_info("Aucun tournoi créé.")
            return

        tournament = self.statistics_view.select_tournament_for_report(
            tournaments
        )
        if not tournament:
            return

        self.statistics_view.display_tournament_details_report(tournament)
        self.statistics_view.wait_for_user()

    def _show_tournament_players(self):
        tournaments = self.tournament_controller.get_all_tournaments()

        if not tournaments:
            self.statistics_view.display_info("Aucun tournoi créé.")
            return

        tournament = self.statistics_view.select_tournament_for_report(
            tournaments
        )
        if not tournament:
            return

        if not tournament.players:
            self.statistics_view.display_info(
                "Aucun joueur dans ce tournoi."
            )
            return

        sorted_players = sorted(
            tournament.players,
            key=lambda p: (p.last_name.lower(), p.first_name.lower())
        )
        self.statistics_view.display_tournament_players_report(
            tournament, sorted_players
        )
        self.statistics_view.wait_for_user()

    def _show_tournament_rounds_and_matches(self):
        tournaments = self.tournament_controller.get_all_tournaments()

        if not tournaments:
            self.statistics_view.display_info("Aucun tournoi créé.")
            return

        tournament = self.statistics_view.select_tournament_for_report(
            tournaments
        )
        if not tournament:
            return

        if not tournament.rounds:
            self.statistics_view.display_info(
                "Aucun tour joué dans ce tournoi."
            )
            return

        self.statistics_view.display_tournament_rounds_matches_report(
            tournament
        )
        self.statistics_view.wait_for_user()

    def _show_simple_global_stats(self):
        players = self.player_controller.get_all_players()
        tournaments = self.tournament_controller.get_all_tournaments()

        finished_tournaments = [
            t for t in tournaments if t.is_finished()
        ]
        in_progress_tournaments = [
            t for t in tournaments
            if t.has_started() and not t.is_finished()
        ]
        not_started_tournaments = [
            t for t in tournaments if not t.has_started()
        ]
        active_players_ids = set(
            p.national_id for t in tournaments for p in t.players
        )

        stats = {
            'total_players': len(players),
            'total_tournaments': len(tournaments),
            'finished_tournaments': len(finished_tournaments),
            'in_progress_tournaments': len(in_progress_tournaments),
            'not_started_tournaments': len(not_started_tournaments),
            'total_rounds': sum(len(t.rounds) for t in tournaments),
            'total_matches': sum(
                len(r.matches) for t in tournaments for r in t.rounds
            ),
            'active_players': len(active_players_ids)
        }

        self.statistics_view.display_simple_global_stats(stats)
        self.statistics_view.wait_for_user()
