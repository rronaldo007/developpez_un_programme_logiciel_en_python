"""MainController module.

Defines the MainController class, which orchestrates
application startup, user interaction, and data flow
between the data layer, sub‐controllers, and views.
"""

from views.menu_view import MenuView
from controllers.player_controller import PlayerController
from controllers.tournament_controller import TournamentController
from controllers.statistic_controller import StatisticsController
from data.data_manager import DataManager


class MainController:
    def __init__(self):
        self._init_data_layer()
        self._init_controllers()
        self._init_views()

    def _init_data_layer(self):
        self.data_manager = DataManager()
        self.players = self.data_manager.load_players()

    def _init_controllers(self):
        self.player_controller = PlayerController(
            self.data_manager, self.players
        )
        self.tournament_controller = TournamentController(
            self.data_manager, self.players
        )
        self.statistics_controller = StatisticsController(
            self.player_controller,
            self.tournament_controller
        )

    def _init_views(self):
        self.menu_view = MenuView()

    def run(self):
        print("Application démarrée avec succès!")
        try:
            while True:
                self._sync_data()
                self.menu_view.display_main_menu()
                choice = self.menu_view.get_user_choice("Votre choix")

                if not self._handle_main_menu_choice(choice):
                    break
        except Exception as e:
            self.menu_view.display_error(
                f"Erreur dans l'application: {e}"
            )

    def _handle_main_menu_choice(self, choice: str) -> bool:
        try:
            if choice == "1":
                self.player_controller.run()
            elif choice == "2":
                self.tournament_controller.run()
            elif choice == "3":
                self.statistics_controller.run()
            elif choice == "0":
                return self._handle_quit()
            else:
                self.menu_view.display_error(
                    "Choix invalide. Veuillez entrer 0, 1, 2 ou 3."
                )
        except Exception as e:
            self.menu_view.display_error(
                f"Erreur lors du traitement: {e}"
            )

        return True

    def _handle_quit(self) -> bool:
        if self.menu_view.confirm_action(
            "Êtes-vous sûr de vouloir quitter l'application"
        ):
            self._save_all_data()
            self.menu_view.display_success(
                "Données sauvegardées. Au revoir !"
            )
            return False
        return True

    def _sync_data(self):
        self.players = self.player_controller.get_all_players()
        self.tournament_controller.update_players_data(self.players)

    def _save_all_data(self):
        try:
            self.player_controller.save_data()
            self.tournament_controller.save_data()
        except Exception as e:
            self.menu_view.display_error(
                f"Erreur lors de la sauvegarde: {e}"
            )
