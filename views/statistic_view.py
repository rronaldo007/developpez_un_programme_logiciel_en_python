from typing import List, Dict, Optional
from .base_view import BaseView
from utils.formatters import (
    format_player_name,
    format_date_display,
    format_tournament_status
)


class StatisticsView(BaseView):

    def display_simple_statistics_menu(self):
        """Affiche le menu simplifié des statistiques"""
        self.display_title("RAPPORTS ET STATISTIQUES")
        print("1. Liste de tous les joueurs (alphabétique)")
        print("2. Liste de tous les tournois")
        print("3. Détails d'un tournoi (nom et dates)")
        print("4. Joueurs d'un tournoi (alphabétique)")
        print("5. Tours et matchs d'un tournoi")
        print("6. Statistiques globales simples")
        print("0. Retour au menu principal")
        self.display_separator()

    def display_players_alphabetical_list(self, players: List):
        self.display_title("LISTE DES JOUEURS (ORDRE ALPHABÉTIQUE)")

        if not players:
            self.display_info("Aucun joueur enregistré.")
            return

        print(f"Nombre total de joueurs : {len(players)}")
        self.display_separator()

        print(f"{'#':<4} {'Nom de famille':<20} {'Prénom':<20} "
              f"{'ID National':<10} {'Naissance':<12}")
        self.display_separator()

        for i, player in enumerate(players, 1):
            birth_display = "N/A"
            if hasattr(player, 'birthdate'):
                birth_display = format_date_display(player.birthdate)
            print(f"{i:<4} {player.last_name:<20} {player.first_name:<20} "
                  f"{player.national_id:<10} {birth_display:<12}")

    def display_tournaments_list(self, tournaments: List):
        self.display_title("LISTE DE TOUS LES TOURNOIS")

        if not tournaments:
            self.display_info("Aucun tournoi créé.")
            return

        print(f"Nombre total de tournois : {len(tournaments)}")
        self.display_separator()

        print(f"{'#':<4} {'Nom':<25} {'Lieu':<15} {'Début':<12} "
              f"{'Fin':<12} {'Statut':<15}")
        self.display_separator()

        for i, tournament in enumerate(tournaments, 1):
            name = tournament.name[:24] if len(tournament.name) > 24 else tournament.name
            location = tournament.location[:14] if len(tournament.location) > 14 else tournament.location
            start_date = format_date_display(tournament.start_date)
            end_date = format_date_display(tournament.end_date)
            status = format_tournament_status(tournament)

            print(f"{i:<4} {name:<25} {location:<15} {start_date:<12} "
                  f"{end_date:<12} {status:<15}")

    def select_tournament_for_report(self, tournaments: List):
        if not tournaments:
            return None

        display_items = []
        for tournament in tournaments:
            status = format_tournament_status(tournament)
            display_items.append(
                f"{tournament.name} ({tournament.location}) - {status}"
            )

        choice_index = self.get_choice_from_list(
            display_items, "SÉLECTIONNER UN TOURNOI"
        )

        if choice_index >= 0:
            return tournaments[choice_index]
        return None

    def display_tournament_details_report(self, tournament):
        self.display_title("DÉTAILS DU TOURNOI")

        print(f"Nom du tournoi       : {tournament.name}")
        print(f"Lieu                 : {tournament.location}")
        print(f"Date de début        : "
              f"{format_date_display(tournament.start_date)}")
        print(f"Date de fin          : "
              f"{format_date_display(tournament.end_date)}")
        print(f"Description          : {tournament.description or 'Aucune'}")
        print(f"Nombre de tours      : {tournament.number_of_rounds}")
        print(f"Tour actuel          : {tournament.current_round}")
        print(f"Statut               : {format_tournament_status(tournament)}")
        print(f"Nombre de joueurs    : {len(tournament.players)}")

    def display_tournament_players_report(self, tournament,
                                          sorted_players: List):
        self.display_title(f"JOUEURS DU TOURNOI - {tournament.name}")

        print(f"Lieu : {tournament.location}")
        print(f"Dates : {format_date_display(tournament.start_date)} - "
              f"{format_date_display(tournament.end_date)}")
        print(f"Nombre de joueurs : {len(sorted_players)}")
        self.display_separator()

        print(f"{'#':<4} {'Nom de famille':<20} {'Prénom':<20} "
              f"{'ID National':<10} {'Score':<8}")
        self.display_separator()

        for i, player in enumerate(sorted_players, 1):
            score = tournament.get_player_score(player.national_id)
            print(f"{i:<4} {player.last_name:<20} {player.first_name:<20} "
                  f"{player.national_id:<10} {score:<8}")

    def display_tournament_rounds_matches_report(self, tournament):
        self.display_title(f"TOURS ET MATCHS - {tournament.name}")

        print(f"Lieu : {tournament.location}")
        print(f"Dates : {format_date_display(tournament.start_date)} - "
              f"{format_date_display(tournament.end_date)}")
        print(f"Nombre de tours : {len(tournament.rounds)}")
        self.display_separator()

        for i, round_obj in enumerate(tournament.rounds, 1):
            print(f"\n{round_obj.name} :")
            status_text = "Terminé" if round_obj.is_finished else "En cours"
            print(f"  Statut : {status_text}")
            print(f"  Nombre de matchs : {len(round_obj.matches)}")

            if round_obj.matches:
                print("  Matchs :")
                for j, match in enumerate(round_obj.matches, 1):
                    player1_name = self._get_player_name_from_tournament(
                        tournament, match.player1_national_id
                    )
                    player2_name = self._get_player_name_from_tournament(
                        tournament, match.player2_national_id
                    )

                    if match.is_finished:
                        result = f"{match.player1_score} - {match.player2_score}"
                        print(f"    {j}. {player1_name} vs {player2_name} : "
                              f"{result}")
                    else:
                        print(f"    {j}. {player1_name} vs {player2_name} : "
                              "En cours")
            else:
                print("  Aucun match")

    def display_simple_global_stats(self, stats: Dict):
        self.display_title("STATISTIQUES GLOBALES")

        print("Vue d'ensemble du système :")
        print(f"  Joueurs enregistrés    : {stats.get('total_players', 0)}")
        print(f"  Joueurs actifs         : {stats.get('active_players', 0)}")
        self.display_separator()

        print("Tournois :")
        print(f"  Total créés            : {stats.get('total_tournaments', 0)}")
        print(f"  Terminés               : {stats.get('finished_tournaments', 0)}")
        print(f"  En cours               : "
              f"{stats.get('in_progress_tournaments', 0)}")
        print(f"  Non commencés          : "
              f"{stats.get('not_started_tournaments', 0)}")
        self.display_separator()

        print("Activité :")
        print(f"  Tours joués total      : {stats.get('total_rounds', 0)}")
        print(f"  Matchs joués total     : {stats.get('total_matches', 0)}")

        total_tournaments = stats.get('total_tournaments', 0)
        finished_tournaments = stats.get('finished_tournaments', 0)
        if total_tournaments > 0:
            completion_rate = (finished_tournaments / total_tournaments) * 100
            print(f"  Taux de completion     : {completion_rate:.1f}%")

        total_players = stats.get('total_players', 0)
        active_players = stats.get('active_players', 0)
        if total_players > 0:
            participation_rate = (active_players / total_players) * 100
            print(f"  Taux de participation  : {participation_rate:.1f}%")

    def _get_player_name_from_tournament(self, tournament,
                                         national_id: str) -> str:
        for player in tournament.players:
            if player.national_id == national_id:
                return format_player_name(player)
        return national_id