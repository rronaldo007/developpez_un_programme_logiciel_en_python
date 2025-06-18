
from typing import List, Dict, Optional, Tuple, Union
from .base_view import BaseView
from utils.formatters import (
    format_tournament_status, format_date_display, format_score_display,
    format_player_name, format_match_result, format_duration, format_percentage
)


class TournamentView(BaseView):
    """
    Vue pour la gestion des tournois -  SANS SCORE SUR PLAYER
    Gère l'affichage et la saisie pour toutes les opérations sur les tournois
    """
    
    def display_tournament_menu(self):
        """Affiche le menu principal de gestion des tournois"""
        self.display_title("GESTION DES TOURNOIS")
        print("1. Créer un nouveau tournoi")
        print("2. Voir tous les tournois")
        print("3. Gérer un tournoi existant")
        print("4. Rapports de tournois")
        print("0. Retour au menu principal")
        self.display_separator()
        
    def get_tournament_info(self) -> Dict[str, str]:
        """
        Collecte les informations d'un nouveau tournoi
        
        Returns:
            Dict[str, str]: Données du tournoi saisies
        """
        self.display_title("NOUVEAU TOURNOI")
        
        tournament_data = {
            'name': self.get_input("Nom du tournoi"),
            'location': self.get_input("Lieu du tournoi"),
            'start_date': self.get_input("Date de début (YYYY-MM-DD)"),
            'end_date': self.get_input("Date de fin (YYYY-MM-DD)"),
            'description': self.get_input("Description (optionnel)"),
            'number_of_rounds': self.get_input_with_default("Nombre de tours", "4")
        }
        
        return tournament_data
        
    def display_tournaments_list(self, tournaments: List, title: str = "LISTE DES TOURNOIS"):
        """
        Affiche la liste des tournois
        
        Args:
            tournaments (List): Liste des tournois à afficher
            title (str): Titre de la liste
        """
        if not tournaments:
            self.display_info("Aucun tournoi créé.")
            return
            
        self.display_title(title)
        
        # En-tête du tableau
        print(f"{'#':<3} {'Nom':<25} {'Lieu':<15} {'Dates':<20} {'Joueurs':<8} {'Statut':<20}")
        self.display_separator()
        
        for i, tournament in enumerate(tournaments, 1):
            # Formatage des données
            start_date = format_date_display(tournament.start_date)
            end_date = format_date_display(tournament.end_date)
            dates = f"{start_date} - {end_date}"
            players_count = len(tournament.players)
            status = format_tournament_status(tournament)
            
            # Tronquer le nom si trop long
            name = tournament.name[:22] + "..." if len(tournament.name) > 25 else tournament.name
            location = tournament.location[:12] + "..." if len(tournament.location) > 15 else tournament.location
            
            print(f"{i:<3} {name:<25} {location:<15} {dates:<20} {players_count:<8} {status:<20}")
            
    def display_tournament_details(self, tournament):
        """
        Affiche les détails complets d'un tournoi - 
        
        Args:
            tournament: Tournoi à afficher
        """
        self.display_title(f"DÉTAILS DU TOURNOI - {tournament.name}")
        
        print(f"ID du tournoi        : {tournament.id}")
        print(f"Nom                  : {tournament.name}")
        print(f"Lieu                 : {tournament.location}")
        print(f"Date de début        : {format_date_display(tournament.start_date)}")
        print(f"Date de fin          : {format_date_display(tournament.end_date)}")
        print(f"Description          : {tournament.description or 'Aucune'}")
        print(f"Nombre de tours      : {tournament.number_of_rounds}")
        print(f"Tour actuel          : {tournament.current_round}")
        print(f"Statut               : {format_tournament_status(tournament)}")
        print(f"Nombre de joueurs    : {len(tournament.players)}")
        
        # Afficher les joueurs inscrits avec leurs scores dans ce tournoi
        if tournament.players:
            print(f"\nJoueurs inscrits ({len(tournament.players)}) :")
            for i, player in enumerate(tournament.players, 1):
                # : Récupérer le score depuis le tournament, pas le player
                score = tournament.get_player_score(player.national_id)
                print(f"  {i}. {format_player_name(player)} - Score: {format_score_display(score)}")
        
        # Afficher l'historique des tours
        if tournament.rounds:
            print(f"\nHistorique des tours ({len(tournament.rounds)}) :")
            for i, round_obj in enumerate(tournament.rounds, 1):
                status = "Terminé" if round_obj.is_finished else "En cours"
                completion = format_percentage(round_obj.get_completion_percentage())
                print(f"  {i}. {round_obj.name} - {status} ({completion})")
                
    def display_tournament_management_menu(self, tournament):
        """
        Affiche le menu de gestion d'un tournoi spécifique
        
        Args:
            tournament: Tournoi à gérer
        """
        self.display_title(f"GESTION - {tournament.name}")
        
        # Informations rapides
        status = format_tournament_status(tournament)
        print(f"Statut: {status} | Joueurs: {len(tournament.players)} | Tour: {tournament.current_round}/{tournament.number_of_rounds}")
        self.display_separator()
        print("1. Voir les détails complets")
        print("2. Gestion des tours et matchs")
        print("3. Voir le classement actuel")
        print("4. Voir l'historique complet")
        
        if not tournament.has_started():
            print("5. Ajouter des joueurs au tournoi")
        else:
            print("5. Impossible d'ajouter des joueurs (tournoi commencé)")
        
        print("0. Retour au menu des tournois")
        self.display_separator()

    def display_round_management_menu(self, tournament):
        """
        Menu spécialisé pour la gestion des tours et matchs
        
        Args:
            tournament: Tournoi à gérer
        """
        self.display_title(f"GESTION DES TOURS - {tournament.name}")
        
        # État actuel du tournoi
        status = format_tournament_status(tournament)
        print(f"Statut: {status} | Tour: {tournament.current_round}/{tournament.number_of_rounds}")
        
        # Informations sur le tour actuel
        if tournament.has_started() and not tournament.is_finished():
            current_round = tournament.rounds[-1] if tournament.rounds else None
            if current_round:
                total_matches = len(current_round.matches)
                finished_matches = len(current_round.get_finished_matches())
                print(f"Tour actuel: {current_round.name} - {finished_matches}/{total_matches} matchs terminés")
        
        self.display_separator()
        
        # Options adaptatives
        if not tournament.has_started():
            # Tournoi pas encore commencé
            if len(tournament.players) >= 2 and len(tournament.players) % 2 == 0:
                print("1. Commencer le premier tour")
            else:
                if len(tournament.players) < 2:
                    print("1. Commencer le premier tour (minimum 2 joueurs requis)")
                else:
                    print("1. Commencer le premier tour (nombre pair de joueurs requis)")
            print("2. Saisir les résultats (aucun tour en cours)")
            
        elif tournament.is_finished():
            # Tournoi terminé
            print("1. Tournoi terminé - Voir les résultats finaux")
            print("2. Tous les résultats sont saisis")
            
        else:
            # Tournoi en cours
            current_round = tournament.rounds[-1] if tournament.rounds else None
            if current_round and not current_round.is_finished:
                print("1. Tour en cours - Terminer d'abord les matchs actuels")
                unfinished_count = len(current_round.get_unfinished_matches())
                print(f"2. Saisir les résultats des matchs ({unfinished_count} en attente)")
            elif tournament.current_round < tournament.number_of_rounds:
                print("1. Commencer le tour suivant")
                print("2. Tous les matchs du tour précédent sont terminés")
            else:
                print("1. Finaliser le tournoi")
                print("2. Tous les matchs sont terminés")
        
        print("3. Voir l'état du tour actuel")
        print("0. Retour au menu du tournoi")
        
        self.display_separator()
        
        # Conseils contextuels
        if not tournament.has_started():
            if len(tournament.players) == 0:
                print("Conseil: Ajoutez d'abord des joueurs au tournoi")
            elif len(tournament.players) < 2:
                print("Conseil: Il faut au moins 2 joueurs pour commencer")
            elif len(tournament.players) % 2 != 0:
                print("Conseil: Ajoutez un joueur pour avoir un nombre pair")
            else:
                print("Prêt à commencer le tournoi!")
        elif tournament.has_started() and not tournament.is_finished():
            current_round = tournament.rounds[-1] if tournament.rounds else None
            if current_round and not current_round.is_finished:
                unfinished = len(current_round.get_unfinished_matches())
                print(f"Action requise: {unfinished} match(s) en attente de résultats")
            else:
                print("Prêt pour le tour suivant!")

    def select_multiple_players_inline(self, available_players: List, selected_players: List) -> Optional[Union[int, str]]:
        """
        Interface incrémentale de sélection des joueurs avec option de création - 
        
        Args:
            available_players (List): Joueurs non encore ajoutés au tournoi.
            selected_players (List): Joueurs déjà sélectionnés.
            
        Returns:
            int: Index du joueur sélectionné dans available_players
            str: "__create__" pour créer un joueur, "__done__" pour terminer
        """
        self.display_title("SÉLECTION DES JOUEURS")
        print("Tapez le numéro du joueur pour l'ajouter au tournoi.")
        print("Tapez 0 pour terminer la sélection.")
        
        if selected_players:
            print(f"\nJoueurs sélectionnés ({len(selected_players)}) :")
            for i, player in enumerate(selected_players, 1):
                print(f"  {i}. {format_player_name(player)}")
        else:
            print("\nAucun joueur sélectionné.")
        
        print("\nJoueurs disponibles :")
        for i, player in enumerate(available_players, 1):
            print(f"{i}. {format_player_name(player)} ({player.national_id})")
        
        create_index = len(available_players) + 1
        print(f"{create_index}. Créer un nouveau joueur")
        print("0. Terminer")
        
        choice = self.get_input("Votre choix")
        
        try:
            choice = int(choice)
            if choice == 0:
                return "__done__"
            elif 1 <= choice <= len(available_players):
                return choice - 1
            elif choice == create_index:
                return "__create__"
            else:
                self.display_error("Choix invalide.")
        except ValueError:
            self.display_error("Veuillez entrer un nombre valide.")
        return None

    def select_tournament_from_list(self, tournaments: List, title: str = "SÉLECTIONNER UN TOURNOI") -> Optional:
        """
        Permet de sélectionner un tournoi dans une liste
        
        Args:
            tournaments (List): Liste des tournois
            title (str): Titre de la sélection
            
        Returns:
            Optional: Tournoi sélectionné ou None
        """
        if not tournaments:
            self.display_info("Aucun tournoi disponible.")
            return None
            
        # Créer la liste d'affichage
        display_items = []
        for tournament in tournaments:
            status = format_tournament_status(tournament)
            display_items.append(f"{tournament.name} ({tournament.location}) - {status}")
        
        choice_index = self.get_choice_from_list(display_items, title)
        
        if choice_index >= 0:
            return tournaments[choice_index]
        return None
        
    def display_round_preview(self, pairs: List[Tuple], round_number: int):
        """
        Affiche l'aperçu des paires pour un tour - 
        
        Args:
            pairs (List[Tuple]): Paires de joueurs
            round_number (int): Numéro du tour
        """
        self.display_title(f"APERÇU DU TOUR {round_number}")
        
        print(f"Nombre de matchs : {len(pairs)}")
        self.display_separator()
        
        for i, (player1, player2) in enumerate(pairs, 1):
            p1_name = format_player_name(player1)
            p2_name = format_player_name(player2)
            
            # : Pour l'aperçu, on affiche sans les scores spécifiques
            # car ils seront récupérés au niveau du tournoi si nécessaire
            print(f"Match {i}: {p1_name} vs {p2_name}")
            
    def display_round_details(self, round_obj):
        """
        Affiche les détails d'un tour
        
        Args:
            round_obj: Tour à afficher
        """
        self.display_title(f"DÉTAILS - {round_obj.name}")
        
        status = "Terminé" if round_obj.is_finished else "En cours"
        completion = format_percentage(round_obj.get_completion_percentage())
        
        print(f"Statut               : {status}")
        print(f"Progression          : {completion}")
        print(f"Nombre de matchs     : {len(round_obj.matches)}")
        print(f"Matchs terminés      : {len(round_obj.get_finished_matches())}")
        
        if round_obj.is_finished and round_obj.end_time:
            duration = format_duration(round_obj.start_time, round_obj.end_time)
            print(f"Durée                : {duration}")
            
        # Afficher les matchs
        print(f"\nMatchs du {round_obj.name} :")
        for i, match in enumerate(round_obj.matches, 1):
            if match.is_finished:
                result = format_match_result(match)
                print(f"  {i}. {result}")
            else:
                print(f"  {i}. {match.player1_national_id} vs {match.player2_national_id} (En cours)")
                
    def select_match_from_list(self, matches: List, title: str = "SÉLECTIONNER UN MATCH") -> Optional:
        """
        Permet de sélectionner un match dans une liste
        
        Args:
            matches (List): Liste des matchs
            title (str): Titre de la sélection
            
        Returns:
            Optional: Match sélectionné ou None
        """
        if not matches:
            self.display_info("Aucun match disponible.")
            return None
            
        # Créer la liste d'affichage
        display_items = []
        for match in matches:
            if match.is_finished:
                display_items.append(format_match_result(match))
            else:
                display_items.append(f"{match.player1_national_id} vs {match.player2_national_id} (En cours)")
        
        choice_index = self.get_choice_from_list(display_items, title)
        
        if choice_index >= 0:
            return matches[choice_index]
        return None
        
    def get_match_result(self, match, players_data=None) -> Optional[Dict]:
        """
        Demande la saisie du résultat d'un match - 
        
        Args:
            match: Match pour lequel saisir le résultat
            players_data: Liste des joueurs du tournoi
            
        Returns:
            Optional[Dict]: Résultat saisi ou None si annulé
        """
        # Obtenir les noms des joueurs depuis la liste des joueurs du tournoi
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
        print("1. Victoire du premier joueur (1-0)")
        print("2. Match nul (0.5-0.5)")
        print("3. Victoire du deuxième joueur (0-1)")
        print("0. Annuler")
        
        while True:
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
                    self.display_error("Choix invalide. Entrez 1, 2, 3 ou 0.")
                    
            except ValueError:
                self.display_error("Veuillez entrer un nombre valide.")
                
    def display_current_standings(self, tournament, rankings: List):
        """
        Affiche le classement actuel d'un tournoi - 
        
        Args:
            tournament: Tournoi
            rankings (List): Joueurs classés par score
        """
        self.display_title(f"CLASSEMENT ACTUEL - {tournament.name}")
        
        if not rankings:
            self.display_info("Aucun classement disponible.")
            return
            
        print(f"Après {tournament.current_round} tour(s) sur {tournament.number_of_rounds}")
        self.display_separator()
        
        # En-tête
        print(f"{'Pos':<4} {'Joueur':<25} {'Score':<6} {'ID':<10}")
        self.display_separator()
        
        for i, player in enumerate(rankings, 1):
            position = f"{i}."
            name = format_player_name(player)
            
            # : Récupérer le score depuis le tournoi
            score = tournament.get_player_score(player.national_id)
            score_display = format_score_display(score)
            
            # Tronquer le nom si trop long
            if len(name) > 25:
                name = name[:22] + "..."
                
            print(f"{position:<4} {name:<25} {score_display:<6} {player.national_id:<10}")
            
    def display_tournament_completion(self, tournament, winner, rankings: List, statistics: Dict):
        """
        Affiche la conclusion d'un tournoi terminé - 
        
        Args:
            tournament: Tournoi terminé
            winner: Joueur gagnant
            rankings (List): Classement final
            statistics (Dict): Statistiques du tournoi
        """
        self.display_title("TOURNOI TERMINÉ")
        
        print(f"Tournoi : {tournament.name}")
        print(f"Lieu    : {tournament.location}")
        self.display_separator()
        
        # Vérifier s'il y a égalité au premier rang
        tied_winners = []
        if rankings:
            first_score = tournament.get_player_score(rankings[0].national_id)
            tied_winners = [p for p in rankings 
                           if abs(tournament.get_player_score(p.national_id) - first_score) < 0.001]
        
        if len(tied_winners) > 1:
            # Égalité au premier rang
            print(f"ÉGALITÉ AU PREMIER RANG !")
            print(f"GAGNANTS EX AEQUO ({len(tied_winners)}) :")
            for i, player in enumerate(tied_winners, 1):
                score = tournament.get_player_score(player.national_id)
                print(f"  {i}. {format_player_name(player)} - {format_score_display(score)} points")
        else:
            # Gagnant unique
            if winner:
                winner_score = tournament.get_player_score(winner.national_id)
                print(f"CHAMPION : {format_player_name(winner)}")
                print(f"Score final : {format_score_display(winner_score)} points")
        
        # Podium
        print(f"\nPODIUM :")
        podium_positions = ["[1] Champion", "[2] 2e place", "[3] 3e place"]
        for i, player in enumerate(rankings[:3]):
            if i < len(podium_positions):
                score = tournament.get_player_score(player.national_id)
                print(f"  {podium_positions[i]} : {format_player_name(player)} ({format_score_display(score)} pts)")
        
        # Statistiques
        if statistics:
            print(f"\nSTATISTIQUES :")
            if 'total_matches' in statistics:
                print(f"  Matchs joués     : {statistics['total_matches']}")
            if 'wins' in statistics and 'draws' in statistics:
                print(f"  Parties décisives: {statistics['wins']}")
                print(f"  Parties nulles   : {statistics['draws']}")
            if 'tiebreaker_rounds' in statistics:
                print(f"  Tours de départage: {statistics['tiebreaker_rounds']}")
            if 'completion_rate' in statistics:
                print(f"  Taux de completion: {format_percentage(statistics['completion_rate'])}")

    def display_tiebreaker_notification(self, tied_players: List):
        """
        Affiche une notification d'égalité avec les joueurs concernés - 
        
        Args:
            tied_players (List): Joueurs à égalité
        """
        self.display_title("ÉGALITÉ DÉTECTÉE")
        
        print(f"ÉGALITÉ AU PREMIER RANG entre {len(tied_players)} joueurs !")
        self.display_separator()
        
        print("Joueurs à égalité :")
        for i, player in enumerate(tied_players, 1):
            # Note: Dans ce contexte, tous les joueurs ont le même score
            print(f"  {i}. {format_player_name(player)}")
        
        self.display_separator()
        print("Un tour de départage peut être organisé pour déterminer le gagnant unique.")

    def display_match_results_menu(self, current_round, unfinished_matches, tournament):
        """
        Interface pour la saisie des résultats avec progression
        
        Args:
            current_round: Tour actuel
            unfinished_matches: Matchs non terminés
            tournament: Tournoi
            
        Returns:
            int: Index du match sélectionné ou "__back__" pour retour
        """
        self.display_title(f"SAISIE DES RÉSULTATS - {current_round.name}")
        
        # Progression
        total_matches = len(current_round.matches)
        finished_matches = len(current_round.get_finished_matches())
        progression = (finished_matches / total_matches) * 100
        
        print(f"Progression: {finished_matches}/{total_matches} matchs terminés ({progression:.0f}%)")
        self.display_separator()
        
        # Afficher les matchs en attente
        print("Matchs en attente de résultats:")
        for i, match in enumerate(unfinished_matches, 1):
            p1_name = self._get_player_name_from_match(match, tournament)
            p2_name = self._get_player_name_from_match(match, tournament, player2=True)
            print(f"{i}. {p1_name} vs {p2_name}")
        
        print("0. Retour au menu des tours")
        self.display_separator()
        
        try:
            choice = int(self.get_input("Sélectionner un match"))
            
            if choice == 0:
                return "__back__"
            elif 1 <= choice <= len(unfinished_matches):
                return choice - 1
            else:
                self.display_error("Choix invalide.")
                return None
                
        except ValueError:
            self.display_error("Veuillez entrer un nombre valide.")
            return None

    def _get_player_name_from_match(self, match, tournament, player2=False):
        """Helper pour récupérer le nom d'un joueur depuis un match"""
        national_id = match.player2_national_id if player2 else match.player1_national_id
        
        for player in tournament.players:
            if player.national_id == national_id:
                return format_player_name(player)
        
        return national_id
                
    def display_reports_menu(self):
        """Affiche le menu des rapports de tournois"""
        self.display_title("RAPPORTS DE TOURNOIS")
        print("1. Tous les tournois")
        print("2. Détails d'un tournoi")
        print("3. Tours d'un tournoi")
        print("4. Matchs d'un tournoi")
        print("0. Retour au menu des tournois")
        self.display_separator()
        
    def display_all_tournaments_report(self, tournaments: List):
        """
        Génère un rapport de tous les tournois
        
        Args:
            tournaments (List): Liste de tous les tournois
        """
        self.display_title("RAPPORT - TOUS LES TOURNOIS")
        
        if not tournaments:
            self.display_info("Aucun tournoi à afficher.")
            return
            
        # Statistiques générales
        total = len(tournaments)
        finished = len([t for t in tournaments if t.is_finished()])
        in_progress = len([t for t in tournaments if t.has_started() and not t.is_finished()])
        not_started = total - finished - in_progress
        
        print(f"Nombre total de tournois : {total}")
        print(f"  - Terminés             : {finished}")
        print(f"  - En cours             : {in_progress}")
        print(f"  - Non commencés        : {not_started}")
        self.display_separator()
        
        # Liste détaillée
        self.display_tournaments_list(tournaments, "LISTE COMPLÈTE")
        
    def display_detailed_tournament_report(self, tournament):
        """
        Génère un rapport détaillé d'un tournoi
        
        Args:
            tournament: Tournoi à analyser
        """
        self.display_title(f"RAPPORT DÉTAILLÉ - {tournament.name}")
        
        # Informations générales
        self.display_tournament_details(tournament)
        
        # Statistiques avancées
        if hasattr(tournament, 'get_tournament_statistics'):
            stats = tournament.get_tournament_statistics()
            
            print(f"\nSTATISTIQUES AVANCÉES :")
            if 'completion_rate' in stats:
                print(f"  Taux de completion    : {format_percentage(stats['completion_rate'])}")
            if 'total_matches' in stats and 'finished_matches' in stats:
                print(f"  Matchs total/terminés : {stats['finished_matches']}/{stats['total_matches']}")
            if 'wins' in stats and 'draws' in stats:
                total_decided = stats['wins'] + stats['draws']
                if total_decided > 0:
                    draw_rate = stats['draws'] / total_decided * 100
                    print(f"  Taux de matchs nuls   : {format_percentage(draw_rate)}")
                    
    def display_rounds_report(self, tournament):
        """
        Génère un rapport des tours d'un tournoi
        
        Args:
            tournament: Tournoi à analyser
        """
        self.display_title(f"RAPPORT DES TOURS - {tournament.name}")
        
        if not tournament.rounds:
            self.display_info("Aucun tour joué dans ce tournoi.")
            return
            
        for i, round_obj in enumerate(tournament.rounds, 1):
            print(f"\n{round_obj.name} :")
            print(f"  Statut      : {'Terminé' if round_obj.is_finished else 'En cours'}")
            print(f"  Matchs      : {len(round_obj.get_finished_matches())}/{len(round_obj.matches)}")
            print(f"  Completion  : {format_percentage(round_obj.get_completion_percentage())}")
            
            if round_obj.is_finished and round_obj.get_duration_minutes():
                duration = format_duration(round_obj.start_time, round_obj.end_time)
                print(f"  Durée       : {duration}")
                
    def display_matches_report(self, tournament):
        """
        Génère un rapport des matchs d'un tournoi
        
        Args:
            tournament: Tournoi à analyser
        """
        self.display_title(f"RAPPORT DES MATCHS - {tournament.name}")
        
        if not tournament.rounds:
            self.display_info("Aucun match joué dans ce tournoi.")
            return
            
        for round_obj in tournament.rounds:
            print(f"\n{round_obj.name} :")
            if not round_obj.matches:
                print("  Aucun match")
                continue
                
            for i, match in enumerate(round_obj.matches, 1):
                if match.is_finished:
                    result = format_match_result(match)
                    print(f"  {i}. {result}")
                else:
                    print(f"  {i}. {match.player1_national_id} vs {match.player2_national_id} (En cours)")
                    
    def display_tournament_history(self, tournament):
        """
        Affiche l'historique complet d'un tournoi
        
        Args:
            tournament: Tournoi à afficher
        """
        self.display_title(f"HISTORIQUE COMPLET - {tournament.name}")
        
        # Informations générales
        print(f"Tournoi créé le : {format_date_display(tournament.start_date)}")
        print(f"Lieu            : {tournament.location}")
        print(f"Statut actuel   : {format_tournament_status(tournament)}")
        print(f"Tours joués     : {len(tournament.rounds)}/{tournament.number_of_rounds}")
        
        # Historique des tours
        if tournament.rounds:
            print(f"\nHistorique des tours :")
            for round_obj in tournament.rounds:
                self.display_separator()
                self.display_round_details(round_obj)
        else:
            print(f"\nAucun tour joué.")
            
        # Classement actuel
        if tournament.players:
            print(f"\n")
            rankings = tournament.get_current_rankings()
            self.display_current_standings(tournament, rankings)

    def display_tiebreaker_preview(self, pairs: List[Tuple], tiebreaker_number: int):
        """
        Affiche l'aperçu des paires pour un tour de départage - 
        
        Args:
            pairs (List[Tuple]): Paires de joueurs pour le départage
            tiebreaker_number (int): Numéro du tour de départage
        """
        self.display_title(f"APERÇU DU TOUR DE DÉPARTAGE {tiebreaker_number}")
        
        print("TOUR DE DÉPARTAGE - RÉSOLUTION D'ÉGALITÉ")
        print(f"Nombre de matchs : {len(pairs)}")
        self.display_separator()
        
        for i, (player1, player2) in enumerate(pairs, 1):
            p1_name = format_player_name(player1)
            p2_name = format_player_name(player2)
            
            # Pour les départages, on affiche sans les scores spécifiques
            # car ils sont à égalité par définition
            print(f"Match de départage {i}: {p1_name} vs {p2_name}")
        
        self.display_separator()
        print("ATTENTION: Ce tour déterminera le gagnant unique du tournoi")

    def display_tiebreaker_completion_analysis(self, tiebreaker_results: Dict):
        """
        Affiche l'analyse des résultats d'un tour de départage
        
        Args:
            tiebreaker_results (Dict): Résultats de l'analyse du départage
        """
        self.display_title("ANALYSE DU TOUR DE DÉPARTAGE")
        
        if tiebreaker_results.get('resolved', False):
            # Égalité résolue
            winner = tiebreaker_results.get('winner')
            if winner:
                print("ÉGALITÉ RÉSOLUE AVEC SUCCÈS !")
                print(f"Gagnant unique : {format_player_name(winner)}")
                final_score = tiebreaker_results.get('final_score', 0)
                print(f"Score final : {format_score_display(final_score)} points")
                print("\nLe tournoi peut maintenant être terminé officiellement.")
            else:
                print("Égalité résolue mais aucun gagnant identifié.")
        else:
            # Égalité persistante
            tied_count = tiebreaker_results.get('tied_players_count', 0)
            can_continue = tiebreaker_results.get('can_continue', False)
            
            print("ÉGALITÉ PERSISTANTE")
            print(f"Nombre de joueurs encore à égalité : {tied_count}")
            
            if can_continue:
                print("\nUn nouveau tour de départage est possible.")
                print("Recommandation : Continuer avec un autre départage.")
            else:
                print("\nNouveau départage impossible (nombre impair ou trop de joueurs).")
                print("Recommandation : Accepter l'égalité avec plusieurs gagnants.")


