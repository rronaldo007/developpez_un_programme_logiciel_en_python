from views.player_view import PlayerView
from views.tournament_view import TournamentView
from views.statistic_view import StatisticsView

if __name__ == "__main__":
    while True:
        print("\n=== CENTRE D'ÉCHECS ===")
        print("1. Gestion des joueurs")
        print("2. Gestion des tournois")
        print("3. Statistiques")
        print("0. Quitter")
        
        choice = input("\nVotre choix: ").strip()
        
        if choice == "1":
            player_view = PlayerView()
            player_view.display_player_menu()
        elif choice == "2":
            tournament_view = TournamentView()
            tournament_view.display_tournament_menu()
        elif choice == "3":
            stats_view = StatisticsView()
            stats_view.display_statistics_menu()
        elif choice == "0":
            print("Au revoir !")
            break
        else:
            print("ERREUR: Choix invalide")