from typing import List, Dict, Optional, Union
from .base_view import BaseView
from utils.formatters import (
    format_tournament_status, format_date_display, format_score_display,
    format_player_name, format_match_result, format_duration,
    format_percentage
)
from utils.validators import validate_tournament_dates


class TournamentView(BaseView):
    def show_tournament_menu(self) -> str:
        """Displays the main tournament management menu and gets user choice."""
        self.display_title("GESTION DES TOURNOIS")
        print("1. Créer un nouveau tournoi")
        print("2. Voir tous les tournois")
        print("3. Gérer un tournoi existant")
        print("4. Rapports de tournois")
        print("0. Retour au menu principal")
        self.display_separator()
        return self.get_user_choice("Votre choix")

    def show_tournament_management_menu(self, tournament) -> str:
        self.display_title(f"GESTION - {tournament.name}")

        status = format_tournament_status(tournament)
        players_count = len(tournament.players)
        current_round = tournament.current_round
        total_rounds = tournament.number_of_rounds

        print(f"Statut: {status} | "
              f"Joueurs: {players_count} | "
              f"Tour: {current_round}/{total_rounds}")
        self.display_separator()

        print("1. Voir les détails complets")
        print("2. Gestion des tours et matchs")
        print("3. Voir le classement actuel")
        print("4. Voir l'historique complet")
        print("5. Gérer les joueurs du tournoi")
        print("0. Retour au menu des tournois")
        self.display_separator()

        return self.get_user_choice("Votre choix")

    def show_round_management_menu(self, tournament) -> str:
        self.display_title(f"GESTION DES TOURS - {tournament.name}")

        status = format_tournament_status(tournament)
        print(f"Statut: {status} | "
              f"Tour: {tournament.current_round}/{tournament.number_of_rounds}")

        if tournament.has_started() and not tournament.is_finished():
            current_round = (tournament.rounds[-1]
                             if tournament.rounds else None)
            if current_round:
                total_matches = len(current_round.matches)
                finished_matches = len(current_round.get_finished_matches())

                if current_round.is_finished:
                    print(f"Dernier tour: {current_round.name} - TERMINÉ")
                    if tournament.current_round < tournament.number_of_rounds:
                        print("Action suggérée: Démarrer le tour suivant")
                elif current_round.all_matches_finished():
                    print(f"Tour actuel: {current_round.name} - "
                          f"PRÊT À TERMINER ({finished_matches}/"
                          f"{total_matches} matchs)")
                    print("Action suggérée: Finaliser le tour (option 2)")
                else:
                    print(f"Tour actuel: {current_round.name} - "
                          f"EN COURS ({finished_matches}/{total_matches} "
                          "matchs terminés)")
                    print("Action suggérée: Saisir les résultats des matchs")

        self.display_separator()

        print("1. Commencer le tour suivant")
        print("2. Saisir les résultats des matchs")
        print("3. Voir l'état du tour actuel")
        print("0. Retour au menu du tournoi")
        self.display_separator()

        self._show_contextual_hints(tournament)

        return self.get_user_choice("Votre choix")

    def show_post_round_start_menu(self) -> str:
        self.display_title("QUE VOULEZ-VOUS FAIRE MAINTENANT ?")

        print("Le tour vient de démarrer. Choisissez votre action :")
        print("1. Saisir immédiatement les résultats des matchs")
        print("2. Voir l'état actuel du tour")
        print("3. Voir le classement actuel du tournoi")
        print("4. Retourner à la gestion des tours")
        print("5. Retourner à la gestion du tournoi")
        print("0. Retourner au menu principal des tournois")
        self.display_separator()

        return self.get_user_choice("Votre choix")

    def show_reports_menu(self) -> str:
        self.display_title("RAPPORTS DE TOURNOIS")
        print("1. Tous les tournois")
        print("2. Détails d'un tournoi")
        print("3. Tours d'un tournoi")
        print("4. Matchs d'un tournoi")
        print("0. Retour au menu des tournois")
        self.display_separator()
        return self.get_user_choice("Votre choix")

    def get_tournament_creation_data(self) -> Optional[Dict[str, str]]:
        self.display_title("NOUVEAU TOURNOI")

        print("Veuillez saisir les informations du nouveau tournoi :")
        self.display_separator()

        name = self.get_input("Nom du tournoi")
        if not name:
            return None

        location = self.get_input("Lieu du tournoi")
        if not location:
            return None

        print("\nFormat date : YYYY-MM-DD (ex: 2024-03-15)")

        while True:
            start_date = self.get_input("Date de début")
            if not start_date:
                return None

            end_date = self.get_input("Date de fin")
            if not end_date:
                return None

            dates_valid, error_message = validate_tournament_dates(
                start_date, end_date
            )

            if dates_valid:
                break
            else:
                self.display_error(error_message)
                print("Veuillez saisir à nouveau les dates :")
                continue

        description = self.get_input("Description (optionnel)")
        number_of_rounds = self.get_input_with_default("Nombre de tours", "4")

        print(f"\nTournoi: {name} à {location}")
        print(f"Du {start_date} au {end_date} - {number_of_rounds} tours")

        try:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            duration = (end - start).days

            if duration == 0:
                print("Durée: Tournoi sur 1 jour")
            else:
                print(f"Durée: {duration + 1} jour(s)")

        except ValueError:
            pass

        return {
            'name': name,
            'location': location,
            'start_date': start_date,
            'end_date': end_date,
            'description': description,
            'number_of_rounds': number_of_rounds
        }

    def show_player_selection_menu(self, available_players: List,
                                   selected_players: List) -> Union[str, int]:
        self.display_title("SÉLECTION DES JOUEURS")

        if selected_players:
            print(f"Joueurs sélectionnés ({len(selected_players)}) :")
            for i, player in enumerate(selected_players, 1):
                print(f"  {i}. {format_player_name(player)}")

        if not available_players:
            print("Aucun joueur disponible.")
            return "done"

        print(f"\nJoueurs disponibles ({len(available_players)}) :")
        for i, player in enumerate(available_players, 1):
            print(f"{i}. {format_player_name(player)} ({player.national_id})")

        create_index = len(available_players) + 1
        print(f"{create_index}. Créer un nouveau joueur")
        print("0. Terminer la sélection")
        self.display_separator()

        try:
            choice = int(self.get_input("Votre choix"))
            if choice == 0:
                return "done"
            elif 1 <= choice <= len(available_players):
                return choice - 1
            elif choice == create_index:
                return "create"
            else:
                self.show_error("Choix invalide.")
                return self.show_player_selection_menu(
                    available_players, selected_players
                )
        except ValueError:
            self.show_error("Veuillez entrer un nombre valide.")
            return self.show_player_selection_menu(
                available_players, selected_players
            )

    def select_tournament(self, tournaments: List) -> Optional[Dict]:
        if not tournaments:
            return None

        self.display_title("SÉLECTIONNER UN TOURNOI")

        for i, tournament in enumerate(tournaments, 1):
            status = format_tournament_status(tournament)
            players_count = len(tournament.players)
            print(f"{i}. {tournament.name} ({tournament.location})")
            print(f"    {status} - {players_count} joueurs - "
                  f"Tours: {tournament.current_round}/"
                  f"{tournament.number_of_rounds}")

        print("0. Annuler")
        self.display_separator()

        try:
            choice = int(self.get_input("Numéro du tournoi"))
            if choice == 0:
                return None
            elif 1 <= choice <= len(tournaments):
                return tournaments[choice - 1]
            else:
                self.show_error(
                    f"Numéro invalide. Entrez un nombre entre 0 et "
                    f"{len(tournaments)}."
                )
                return self.select_tournament(tournaments)
        except ValueError:
            self.show_error("Veuillez entrer un numéro valide.")
            return self.select_tournament(tournaments)

    def show_tournament_details(self, tournament):
        self.display_title(f"DÉTAILS DU TOURNOI - {tournament.name}")

        print(f"Nom                  : {tournament.name}")
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

        if tournament.players:
            print(f"\nJoueurs inscrits ({len(tournament.players)}) :")
            for i, player in enumerate(tournament.players, 1):
                score = tournament.get_player_score(player.national_id)
                print(f"  {i}. {format_player_name(player)} - "
                      f"Score: {format_score_display(score)}")

        if tournament.rounds:
            print(f"\nHistorique des tours ({len(tournament.rounds)}) :")
            for i, round_obj in enumerate(tournament.rounds, 1):
                status_text = "Terminé" if round_obj.is_finished else "En cours"
                completion = format_percentage(
                    round_obj.get_completion_percentage()
                )
                print(f"  {i}. {round_obj.name} - {status_text} "
                      f"({completion})")

        self.wait_for_user()

    def show_current_standings(self, tournament, rankings: List):
        self.display_title(f"CLASSEMENT ACTUEL - {tournament.name}")

        if not rankings:
            self.show_info("Aucun classement disponible.")
            return

        print(f"Après {tournament.current_round} tour(s) sur "
              f"{tournament.number_of_rounds}")
        self.display_separator()

        print(f"{'Pos':<4} {'Joueur':<25} {'Score':<6}")
        self.display_separator()

        for i, player in enumerate(rankings, 1):
            position = f"{i}."
            name = format_player_name(player)
            score = tournament.get_player_score(player.national_id)
            score_display = format_score_display(score)

            if len(name) > 25:
                name = name[:22] + "..."

            print(f"{position:<4} {name:<25} {score_display:<6}")

        self.wait_for_user()

    def select_match_for_results(self, current_round, unfinished_matches,
                                 tournament) -> Union[str, int]:
        self.display_title(f"SAISIE DES RÉSULTATS - {current_round.name}")

        total_matches = len(current_round.matches)
        finished_matches = len(current_round.get_finished_matches())
        progression = (finished_matches / total_matches) * 100

        print(f"Progression: {finished_matches}/{total_matches} "
              f"matchs terminés ({progression:.0f}%)")
        self.display_separator()

        print("Matchs en attente :")
        for i, match in enumerate(unfinished_matches, 1):
            p1_name = self._get_player_name_from_match(match, tournament)
            p2_name = self._get_player_name_from_match(
                match, tournament, player2=True
            )
            print(f"{i}. {p1_name} vs {p2_name}")

        print("0. Retour")
        self.display_separator()

        try:
            choice = int(self.get_input("Sélectionner un match"))
            if choice == 0:
                return "back"
            elif 1 <= choice <= len(unfinished_matches):
                return choice - 1
            else:
                self.show_error("Choix invalide.")
                return self.select_match_for_results(
                    current_round, unfinished_matches, tournament
                )
        except ValueError:
            self.show_error("Veuillez entrer un nombre valide.")
            return self.select_match_for_results(
                current_round, unfinished_matches, tournament
            )

    def get_match_result_input(self, match,
                               players_data=None) -> Optional[Dict]:
        p1_name = match.player1_national_id
        p2_name = match.player2_national_id

        if players_data:
            for player in players_data:
                if player.national_id == match.player1_national_id:
                    p1_name = format_player_name(player)
                elif player.national_id == match.player2_national_id:
                    p2_name = format_player_name(player)

        self.display_title("SAISIE DU RÉSULTAT")
        print(f"Match : {p1_name} vs {p2_name}")
        self.display_separator()

        print("Résultats possibles :")
        print(f"1. Victoire de {p1_name} (1-0)")
        print("2. Match nul (0.5-0.5)")
        print(f"3. Victoire de {p2_name} (0-1)")
        print("0. Annuler")

        try:
            choice = int(self.get_input("Résultat"))

            if choice == 0:
                return None
            elif choice == 1:
                return {'player1_score': 1.0, 'player2_score': 0.0}
            elif choice == 2:
                return {'player1_score': 0.5, 'player2_score': 0.5}
            elif choice == 3:
                return {'player1_score': 0.0, 'player2_score': 1.0}
            else:
                self.show_error("Choix invalide. Entrez 1, 2, 3 ou 0.")
                return self.get_match_result_input(match, players_data)
        except ValueError:
            self.show_error("Veuillez entrer un nombre valide.")
            return self.get_match_result_input(match, players_data)

    def announce_match_result(self, match, players_data=None):
        p1_name = match.player1_national_id
        p2_name = match.player2_national_id

        if players_data:
            for player in players_data:
                if player.national_id == match.player1_national_id:
                    p1_name = format_player_name(player)
                elif player.national_id == match.player2_national_id:
                    p2_name = format_player_name(player)

        self.display_title("RÉSULTAT DU MATCH")

        print(f"Match : {p1_name} vs {p2_name}")
        self.display_separator()

        if match.is_draw():
            print("RÉSULTAT : MATCH NUL")
            print(f"{p1_name} : {format_score_display(match.player1_score)} "
                  "point")
            print(f"{p2_name} : {format_score_display(match.player2_score)} "
                  "point")
        else:
            winner_id = match.get_winner_id()

            winner_name = (p1_name if winner_id == match.player1_national_id
                           else p2_name)
            loser_name = (p2_name if winner_id == match.player1_national_id
                          else p1_name)

            print(f"RÉSULTAT : VICTOIRE DE {winner_name.upper()}")
            print(f"Gagnant : {winner_name} (1 point)")
            print(f"Perdant : {loser_name} (0 point)")

        self.display_separator()
        print("Résultat enregistré avec succès!")

        self.wait_for_user("Appuyez sur Entrée pour continuer...")

    def announce_tournament_end(self, tournament):
        rankings = tournament.get_final_rankings()

        if not rankings:
            self.show_info("Aucun classement disponible.")
            return

        winner = rankings[0]
        winner_score = tournament.get_player_score(winner.national_id)

        self.display_title("RÉSULTATS FINAUX DU TOURNOI")

        print(f"Tournoi : {tournament.name}")
        print(f"Lieu    : {tournament.location}")
        print(f"Dates   : {format_date_display(tournament.start_date)} - "
              f"{format_date_display(tournament.end_date)}")
        print(f"Tours   : {tournament.current_round}/"
              f"{tournament.number_of_rounds}")

        total_matches = sum(
            len(round_obj.matches) for round_obj in tournament.rounds
        )
        total_players = len(tournament.players)

        print(f"Matchs  : {total_matches} joués")
        print(f"Joueurs : {total_players} participants")

        self.display_separator()

        print(f"CHAMPION DU TOURNOI : "
              f"{format_player_name(winner).upper()}")
        print(f"Score final : {format_score_display(winner_score)} points")

        tied_winners = [
            p for p in rankings
            if tournament.get_player_score(p.national_id) == winner_score
        ]
        if len(tied_winners) > 1:
            print(f"ÉGALITÉ : {len(tied_winners)} joueurs à égalité "
                  "au premier rang")

        self.display_separator()

        print("CLASSEMENT FINAL DÉTAILLÉ")
        self.display_separator()

        header_format = "{:<4} {:<25} {:<8}"
        print(header_format.format("Pos", "Joueur", "Score"))
        self.display_separator("-", 70)

        for i, player in enumerate(rankings, 1):
            position = f"{i}."
            name = format_player_name(player)
            score = tournament.get_player_score(player.national_id)
            score_display = format_score_display(score)

            if len(name) > 25:
                name = name[:22] + "..."

            print(f"{position:<4} {name:<25} {score_display:<6}")

        self.wait_for_user()

    def show_round_details(self, round_obj, tournament=None):
        if not round_obj:
            self.show_info("Aucun tour disponible.")
            return

        self.display_title(f"DÉTAILS - {round_obj.name}")

        if round_obj.is_finished:
            status = "Terminé"
        elif round_obj.all_matches_finished():
            status = "Prêt à terminer"
        else:
            status = "En cours"

        completion = format_percentage(round_obj.get_completion_percentage())

        print(f"Statut               : {status}")
        print(f"Progression          : {completion}")
        print(f"Nombre de matchs     : {len(round_obj.matches)}")
        print(f"Matchs terminés      : "
              f"{len(round_obj.get_finished_matches())}")

        if round_obj.is_finished and round_obj.end_time:
            duration = format_duration(round_obj.start_time,
                                       round_obj.end_time)
            print(f"Durée                : {duration}")
        elif round_obj.all_matches_finished() and not round_obj.is_finished:
            print("Note                 : Le tour peut être finalisé")

        print(f"\nMatchs du {round_obj.name} :")
        for i, match in enumerate(round_obj.matches, 1):
            if match.is_finished:
                if tournament:
                    p1_name = self._get_player_name_from_tournament(
                        tournament, match.player1_national_id
                    )
                    p2_name = self._get_player_name_from_tournament(
                        tournament, match.player2_national_id
                    )
                    result = (f"{p1_name} {match.player1_score}-"
                              f"{match.player2_score} {p2_name}")
                    print(f"  {i}. {result}")
                else:
                    result = format_match_result(match)
                    print(f"  {i}. {result}")
            else:
                if tournament:
                    p1_name = self._get_player_name_from_tournament(
                        tournament, match.player1_national_id
                    )
                    p2_name = self._get_player_name_from_tournament(
                        tournament, match.player2_national_id
                    )
                    print(f"  {i}. {p1_name} vs {p2_name} (En cours)")
                else:
                    p1_name = self._get_player_name_from_id(
                        match.player1_national_id
                    )
                    p2_name = self._get_player_name_from_id(
                        match.player2_national_id
                    )
                    print(f"  {i}. {p1_name} vs {p2_name} (En cours)")

        self.wait_for_user()

    def show_tournament_history(self, tournament):
        self.display_title(f"HISTORIQUE COMPLET - {tournament.name}")

        print(f"Lieu            : {tournament.location}")
        print(f"Statut actuel   : {format_tournament_status(tournament)}")
        print(f"Tours joués     : {len(tournament.rounds)}/"
              f"{tournament.number_of_rounds}")

        if tournament.rounds:
            print("\nHistorique des tours :")
            for round_obj in tournament.rounds:
                self.display_separator()
                print(f"\n{round_obj.name} :")
                status_text = "Terminé" if round_obj.is_finished else "En cours"
                print(f"  Statut : {status_text}")
                print(f"  Matchs : {len(round_obj.get_finished_matches())}/"
                      f"{len(round_obj.matches)}")

                if round_obj.matches:
                    for j, match in enumerate(round_obj.matches, 1):
                        if match.is_finished:
                            p1_name = self._get_player_name_from_tournament(
                                tournament, match.player1_national_id
                            )
                            p2_name = self._get_player_name_from_tournament(
                                tournament, match.player2_national_id
                            )
                            result = (f"{p1_name} {match.player1_score}-"
                                      f"{match.player2_score} {p2_name}")
                            print(f"    {j}. {result}")
                        else:
                            p1_name = self._get_player_name_from_tournament(
                                tournament, match.player1_national_id
                            )
                            p2_name = self._get_player_name_from_tournament(
                                tournament, match.player2_national_id
                            )
                            print(f"    {j}. {p1_name} vs {p2_name} (En cours)")
        else:
            print("\nAucun tour joué.")

        self.wait_for_user()

    def show_all_tournaments_report(self, tournaments: List):
        self.display_title("RAPPORT - TOUS LES TOURNOIS")

        if not tournaments:
            self.show_info("Aucun tournoi à afficher.")
            return

        total = len(tournaments)
        finished = len([t for t in tournaments if t.is_finished()])
        in_progress = len([
            t for t in tournaments
            if t.has_started() and not t.is_finished()
        ])
        not_started = total - finished - in_progress

        print(f"Total tournois : {total} | Terminés : {finished} | "
              f"En cours : {in_progress} | Non commencés : {not_started}")
        self.display_separator()

        self.show_tournaments_list(tournaments)

    def show_detailed_tournament_report(self, tournament):
        self.display_title(f"RAPPORT DÉTAILLÉ - {tournament.name}")
        self.show_tournament_details(tournament)

    def show_rounds_report(self, tournament):
        self.display_title(f"RAPPORT DES TOURS - {tournament.name}")

        if not tournament.rounds:
            self.show_info("Aucun tour joué dans ce tournoi.")
            return

        for i, round_obj in enumerate(tournament.rounds, 1):
            status_text = "Terminé" if round_obj.is_finished else "En cours"
            print(f"{round_obj.name} : {status_text}")
            print(f"  Matchs : {len(round_obj.get_finished_matches())}/"
                  f"{len(round_obj.matches)}")

            if round_obj.is_finished and round_obj.get_duration_minutes():
                duration = format_duration(
                    round_obj.start_time, round_obj.end_time
                )
                print(f"  Durée : {duration}")

        self.wait_for_user()

    def show_matches_report(self, tournament):
        self.display_title(f"RAPPORT DES MATCHS - {tournament.name}")

        if not tournament.rounds:
            self.show_info("Aucun match joué dans ce tournoi.")
            return

        for round_obj in tournament.rounds:
            print(f"\n{round_obj.name} :")
            if not round_obj.matches:
                print("  Aucun match")
                continue

            for i, match in enumerate(round_obj.matches, 1):
                if match.is_finished:
                    p1_name = self._get_player_name_from_tournament(
                        tournament, match.player1_national_id
                    )
                    p2_name = self._get_player_name_from_tournament(
                        tournament, match.player2_national_id
                    )
                    result = (f"{p1_name} {match.player1_score}-"
                              f"{match.player2_score} {p2_name}")
                    print(f"  {i}. {result}")
                else:
                    p1_name = self._get_player_name_from_tournament(
                        tournament, match.player1_national_id
                    )
                    p2_name = self._get_player_name_from_tournament(
                        tournament, match.player2_national_id
                    )
                    print(f"  {i}. {p1_name} vs {p2_name} (En cours)")

        self.wait_for_user()

    def show_tournaments_list(self, tournaments: List):
        self.display_title("LISTE DES TOURNOIS")

        if not tournaments:
            self.show_info("Aucun tournoi enregistré.")
            return

        print(f"{'#':<3} {'Nom':<25} {'Lieu':<15} {'Statut':<15} {'Joueurs':<8}")
        self.display_separator()

        for i, tournament in enumerate(tournaments, 1):
            status = format_tournament_status(tournament)
            players_count = len(tournament.players)

            name = (tournament.name[:22] + "..."
                    if len(tournament.name) > 25 else tournament.name)
            location = (tournament.location[:12] + "..."
                        if len(tournament.location) > 15 else tournament.location)

            print(f"{i:<3} {name:<25} {location:<15} {status:<15} "
                  f"{players_count:<8}")

        self.wait_for_user()

    def show_success(self, message: str):
        self.display_success(message)

    def show_error(self, message: str):
        self.display_error(message)

    def show_warning(self, message: str):
        self.display_warning(message)

    def show_info(self, message: str):
        self.display_info(message)

    def _show_contextual_hints(self, tournament):
        if not tournament.has_started():
            if len(tournament.players) == 0:
                print("Conseil: Ajoutez d'abord des joueurs au tournoi")
            elif len(tournament.players) < 2:
                print("Conseil: Il faut au moins 2 joueurs pour commencer")
            elif len(tournament.players) % 2 != 0:
                print("Conseil: Ajoutez un joueur pour avoir un nombre pair")
            else:
                print("Prêt à commencer le tournoi!")
                if len(tournament.players) < 4:
                    print("Note: Avec moins de 4 joueurs, "
                          "des rematches seront nécessaires")
        elif tournament.has_started() and not tournament.is_finished():
            current_round = (tournament.rounds[-1]
                             if tournament.rounds else None)
            if current_round:
                if current_round.is_finished:
                    if tournament.current_round < tournament.number_of_rounds:
                        print("Prêt pour le tour suivant!")
                    else:
                        print("Tournoi prêt à être terminé!")
                elif current_round.all_matches_finished():
                    print("Tous les matchs sont terminés - "
                          "Le tour peut être finalisé")
                else:
                    unfinished = len(current_round.get_unfinished_matches())
                    print(f"Action requise: {unfinished} match(s) "
                          "en attente de résultats")
        elif tournament.is_finished():
            print("Tournoi terminé - Consultez les résultats finaux")

    def _get_player_name_from_match(self, match, tournament, player2=False):
        national_id = (match.player2_national_id if player2
                       else match.player1_national_id)
        return self._get_player_name_from_tournament(tournament, national_id)

    def _get_player_name_from_tournament(self, tournament, national_id: str):
        for player in tournament.players:
            if player.national_id == national_id:
                return format_player_name(player)

        try:
            return f"Joueur {national_id}"
        except Exception:
            return national_id

    def _get_player_name_from_id(self, national_id: str):
        return national_id

    def confirm_start_first_round(self) -> bool:
        return self.confirm_action("Voulez-vous commencer le premier tour")

    def confirm_round_start(self, pairs, round_number: int) -> bool:
        self.display_title(f"APERÇU DU TOUR {round_number}")

        print(f"Nombre de matchs : {len(pairs)}")
        self.display_separator()

        for i, (player1, player2) in enumerate(pairs, 1):
            p1_name = format_player_name(player1)
            p2_name = format_player_name(player2)
            print(f"Match {i}: {p1_name} vs {p2_name}")

        self.display_separator()
        return self.confirm_action("Confirmer le démarrage de ce tour")

    def confirm_next_round_immediate(self) -> bool:
        return self.confirm_action(
            "Voulez-vous démarrer immédiatement le tour suivant"
        )
