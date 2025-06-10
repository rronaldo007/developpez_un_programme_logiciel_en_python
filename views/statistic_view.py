import os
from controllers.player_controller import PlayerController
from controllers.tournament_controller import TournamentController
from controllers.statistic_controller import StatisticsController
from models.player import Player
class StatisticsView:
    """Vue pour l'affichage des statistiques"""
    
    def display_statistics_menu(self):
        """Affiche le menu principal des statistiques"""
        while True:
            print("\n=== STATISTIQUES ===")
            print("1. Statistiques d'un joueur")
            print("2. Statistiques d'un tournoi")
            print("3. Statistiques globales du club")
            print("4. Classements des meilleurs joueurs")
            print("0. Retour au menu principal")
            
            choice = input("\nVotre choix: ").strip()
            
            if choice == "1":
                self.show_player_statistics_interface()
            elif choice == "2":
                self.show_tournament_statistics_interface()
            elif choice == "3":
                self.show_global_statistics_interface()
            elif choice == "4":
                self.show_top_players_interface()
            elif choice == "0":
                break
            else:
                self.show_error("Choix invalide")

    def show_player_statistics_interface(self):
        """Interface pour voir les statistiques d'un joueur"""
        print("\n=== STATISTIQUES D'UN JOUEUR ===")
        
        try:
            # Afficher la liste des joueurs
            all_players = PlayerController.get_all_players()
            if not all_players:
                print("Aucun joueur disponible.")
                return
            
            print("\nJoueurs disponibles:")
            print("-" * 80)
            print(f"{'#':<3} {'Nom':<20} {'Prénom':<15} {'Identifiant':<12}")
            print("-" * 80)
            
            for i, player in enumerate(all_players, 1):
                print(f"{i:<3} {player.last_name:<20} {player.first_name:<15} {player.national_id:<12}")
            
            print("-" * 80)
            
            # Demander le choix
            choice = input(f"\nChoisissez un joueur (1-{len(all_players)}) ou 0 pour annuler: ").strip()
            
            if choice == "0":
                return
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(all_players):
                    selected_player = all_players[choice_num - 1]
                    stats = StatisticsController.get_player_statistics(selected_player.national_id)
                    if stats:
                        self.display_player_statistics(stats)
                    else:
                        self.show_error("Impossible de calculer les statistiques")
                else:
                    self.show_error(f"Choisissez un nombre entre 1 et {len(all_players)}")
            except ValueError:
                self.show_error("Veuillez entrer un nombre valide")
                
        except KeyboardInterrupt:
            print("\nConsultation annulée.")

    def display_player_statistics(self, stats):
        """Affiche les statistiques détaillées d'un joueur"""
        print(f"\n{'='*60}")
        print(f"STATISTIQUES DE {stats['player_name']}")
        print(f"{'='*60}")
        print(f"Identifiant: {stats['national_id']}")
        
        # Statistiques générales
        print(f"\nRÉSUMÉ GÉNÉRAL:")
        print(f"  Tournois joués      : {stats['tournaments_played']}")
        print(f"  Tournois gagnés     : {stats['tournaments_won']}")
        print(f"  Podiums (top 3)     : {stats['tournaments_podium']}")
        
        # Statistiques de matchs
        print(f"\nSTATISTIQUES DE MATCHS:")
        print(f"  Matchs joués        : {stats['total_matches']}")
        print(f"  Victoires           : {stats['matches_won']}")
        print(f"  Matchs nuls         : {stats['matches_drawn']}")
        print(f"  Défaites            : {stats['matches_lost']}")
        print(f"  Taux de victoire    : {stats['win_rate']:.1f}%")
        
        # Statistiques de scores
        print(f"\nSTATISTIQUES DE SCORES:")
        print(f"  Points totaux       : {stats['total_points']:.1f}")
        print(f"  Score moyen         : {stats['average_score']:.1f}")
        print(f"  Meilleur score      : {stats['best_score']:.1f}")
        print(f"  Plus faible score   : {stats['worst_score']:.1f}")
        
        # Historique des tournois
        if stats['tournaments_details']:
            print(f"\nHISTORIQUE DES TOURNOIS:")
            print("-" * 70)
            print(f"{'Tournoi':<25} {'Date':<12} {'Score':<6} {'Position':<10} {'Joueurs':<8}")
            print("-" * 70)
            for detail in stats['tournaments_details'][-10:]:  # 10 derniers tournois
                print(f"{detail['name'][:24]:<25} "
                      f"{detail['date']:<12} "
                      f"{detail['score']:<6.1f} "
                      f"{detail['position']}/{detail['total_players']:<8} "
                      f"{detail['total_players']:<8}")
            print("-" * 70)
        
        print(f"{'='*60}")
        input("\nAppuyez sur Entrée pour continuer...")

    def show_tournament_statistics_interface(self):
        """Interface pour voir les statistiques d'un tournoi"""
        print("\n=== STATISTIQUES D'UN TOURNOI ===")
        
        try:
            tournaments = TournamentController.get_all_tournaments()
            if not tournaments:
                print("Aucun tournoi disponible.")
                return
            
            print("\nTournois disponibles:")
            print("-" * 80)
            print(f"{'ID':<5} {'Nom':<25} {'Lieu':<20} {'Date':<12} {'Joueurs':<8}")
            print("-" * 80)
            
            for tournament in tournaments:
                print(f"{tournament.id:<5} "
                      f"{tournament.name[:24]:<25} "
                      f"{tournament.location[:19]:<20} "
                      f"{tournament.start_date:<12} "
                      f"{len(tournament.players):<8}")
            
            print("-" * 80)
            
            tournament_id = input("\nID du tournoi: ").strip()
            if not tournament_id:
                return
            
            try:
                tournament_id = int(tournament_id)
                stats = StatisticsController.get_tournament_statistics(tournament_id)
                if stats:
                    self.display_tournament_statistics(stats)
                else:
                    self.show_error("Tournoi non trouvé")
            except ValueError:
                self.show_error("L'ID doit être un nombre")
                
        except KeyboardInterrupt:
            print("\nConsultation annulée.")

    def display_tournament_statistics(self, stats):
        """Affiche les statistiques d'un tournoi"""
        print(f"\n{'='*60}")
        print(f"STATISTIQUES DU TOURNOI")
        print(f"{'='*60}")
        print(f"Nom         : {stats['tournament_name']}")
        print(f"Lieu        : {stats['location']}")
        print(f"Dates       : {stats['start_date']} - {stats['end_date']}")
        
        print(f"\nPARTICIPATION:")
        print(f"  Joueurs inscrits    : {stats['total_players']}")
        print(f"  Rounds organisés    : {stats['total_rounds']}")
        print(f"  Matchs programmés   : {stats['total_matches']}")
        print(f"  Matchs terminés     : {stats['completed_matches']}")
        print(f"  Taux de completion  : {stats['completion_rate']:.1f}%")
        
        if stats['total_players'] > 0:
            print(f"\nSTATISTIQUES DE SCORES:")
            print(f"  Score moyen         : {stats['average_score']:.1f}")
            print(f"  Score le plus haut  : {stats['highest_score']:.1f}")
            print(f"  Score le plus bas   : {stats['lowest_score']:.1f}")
            
            if stats['winner_name']:
                print(f"\nGAGNANT:")
                print(f"  Champion            : {stats['winner_name']}")
                print(f"  Score final         : {stats['winner_score']:.1f}")
            
            # Classement
            if stats['players_ranking']:
                print(f"\nCLASSEMENT FINAL:")
                print("-" * 40)
                print(f"{'Pos':<5} {'Joueur':<25} {'Score':<8}")
                print("-" * 40)
                for ranking in stats['players_ranking'][:10]:
                    print(f"{ranking['position']:<5} "
                          f"{ranking['name'][:24]:<25} "
                          f"{ranking['score']:<8.1f}")
                print("-" * 40)
        
        print(f"{'='*60}")
        input("\nAppuyez sur Entrée pour continuer...")

    def show_global_statistics_interface(self):
        """Interface pour les statistiques globales"""
        print("\n=== STATISTIQUES GLOBALES DU CLUB ===")
        
        stats = StatisticsController.get_global_statistics()
        self.display_global_statistics(stats)

    def display_global_statistics(self, stats):
        """Affiche les statistiques globales"""
        print(f"\n{'='*60}")
        print(f"STATISTIQUES GLOBALES DU CLUB")
        print(f"{'='*60}")
        
        print(f"VUE D'ENSEMBLE:")
        print(f"  Joueurs inscrits       : {stats['total_players']}")
        print(f"  Tournois organisés     : {stats['total_tournaments']}")
        print(f"  Tournois terminés      : {stats['completed_tournaments']}")
        print(f"  Rounds joués           : {stats['total_rounds']}")
        print(f"  Matchs joués           : {stats['total_matches']}")
        
        print(f"\nMOYENNES:")
        print(f"  Joueurs par tournoi    : {stats['average_players_per_tournament']:.1f}")
        
        print(f"\nRECORDS:")
        if stats['most_active_player']:
            print(f"  Joueur le plus actif   : {stats['most_active_player']}")
        if stats['most_successful_player']:
            print(f"  Joueur le plus titré   : {stats['most_successful_player']}")
        if stats['most_popular_location']:
            print(f"  Lieu le plus populaire : {stats['most_popular_location']}")
        
        # Tournois récents
        if stats['recent_tournaments']:
            print(f"\nTOURNOIS RÉCENTS:")
            print("-" * 50)
            print(f"{'Nom':<25} {'Date':<12} {'Joueurs':<8} {'Statut':<10}")
            print("-" * 50)
            for tournament in stats['recent_tournaments']:
                print(f"{tournament['name'][:24]:<25} "
                      f"{tournament['date']:<12} "
                      f"{tournament['players']:<8} "
                      f"{tournament['status']:<10}")
            print("-" * 50)
        
        print(f"{'='*60}")
        input("\nAppuyez sur Entrée pour continuer...")

    def show_top_players_interface(self):
        """Interface pour les classements des meilleurs joueurs"""
        print("\n=== CLASSEMENTS DES MEILLEURS JOUEURS ===")
        
        rankings = StatisticsController.get_top_players()
        
        while True:
            print("\nClassements disponibles:")
            print("1. Par nombre de tournois gagnés")
            print("2. Par taux de victoire en matchs")
            print("3. Par score moyen par tournoi")
            print("4. Joueurs les plus actifs")
            print("0. Retour")
            
            choice = input("\nVotre choix: ").strip()
            
            if choice == "1":
                self.display_ranking("TOURNOIS GAGNÉS", rankings['by_tournaments_won'], "tournaments_won", "tournois")
            elif choice == "2":
                self.display_ranking("TAUX DE VICTOIRE", rankings['by_win_rate'], "win_rate", "%")
            elif choice == "3":
                self.display_ranking("SCORE MOYEN", rankings['by_average_score'], "average_score", "pts")
            elif choice == "4":
                self.display_ranking("PLUS ACTIFS", rankings['most_active'], "tournaments_played", "tournois")
            elif choice == "0":
                break
            else:
                self.show_error("Choix invalide")

    def display_ranking(self, title, players, metric, unit):
        """Affiche un classement spécifique"""
        print(f"\n{'='*60}")
        print(f"TOP 10 - {title}")
        print(f"{'='*60}")
        
        if not players:
            print("Aucune donnée disponible.")
        else:
            print(f"{'Pos':<5} {'Joueur':<25} {title.split()[0]:<15}")
            print("-" * 45)
            for i, player in enumerate(players, 1):
                value = player[metric]
                if unit == "%":
                    print(f"{i:<5} {player['name'][:24]:<25} {value:.1f} {unit}")
                elif unit == "pts":
                    print(f"{i:<5} {player['name'][:24]:<25} {value:.1f} {unit}")
                else:
                    print(f"{i:<5} {player['name'][:24]:<25} {value} {unit}")
            print("-" * 45)
        
        print(f"{'='*60}")
        input("\nAppuyez sur Entrée pour continuer...")

    def show_error(self, message):
        """Affiche un message d'erreur"""
        print(f"ERREUR: {message}")

    def show_success(self, message):
        """Affiche un message de succès"""
        print(f"SUCCÈS: {message}")