
import os
from typing import List

from views.menu_view import MenuView
from controllers.player_controller import PlayerController
from controllers.tournament_controller import TournamentController
from controllers.statistic_controller import StatisticsController
from data.data_manager import DataManager
from models.player import Player


class MainController:
    """
    Contrôleur principal de l'application - Chef d'orchestre MVC
    
    Responsabilités :
    - Coordination entre tous les modules
    - Gestion du menu principal
    - Initialisation des données
    - Synchronisation entre contrôleurs
    """
    
    def __init__(self):
        """Initialise le contrôleur principal et tous ses composants"""
        # Initialiser les composants MVC
        self._init_data_layer()
        self._init_controllers()
        self._init_views()
        
    def _init_data_layer(self):
        """Initialise la couche de données"""
        self.data_manager = DataManager()
        self.players = self.data_manager.load_players()
        
    def _init_controllers(self):
        """Initialise tous les contrôleurs spécialisés"""
        # Contrôleur des joueurs
        self.player_controller = PlayerController(self.data_manager, self.players)
        
        # Contrôleur des tournois
        self.tournament_controller = TournamentController(self.data_manager, self.players)
        
        # Contrôleur des statistiques
        self.statistics_controller = StatisticsController(
            self.player_controller, 
            self.tournament_controller
        )
        
    def _init_views(self):
        """Initialise les vues"""
        self.menu_view = MenuView()
        
    def run(self):
        """
        Boucle principale de l'application
        Gère la navigation et délègue aux contrôleurs appropriés
        """
        print("Application démarrée avec succès!")
        
        try:
            while True:
                # Synchroniser les données entre contrôleurs
                self._sync_data()
                
                # Afficher le menu principal
                self.menu_view.display_main_menu()
                
                # Obtenir le choix de l'utilisateur
                choice = self.menu_view.get_user_choice("Votre choix")
                
                # Traiter le choix
                if not self._handle_main_menu_choice(choice):
                    break
                    
        except Exception as e:
            self.menu_view.display_error(f"Erreur dans l'application: {e}")
            
    def _handle_main_menu_choice(self, choice: str) -> bool:
        """
        Traite le choix du menu principal
        
        Args:
            choice (str): Choix de l'utilisateur
            
        Returns:
            bool: True pour continuer, False pour quitter
        """
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
                self.menu_view.display_error("Choix invalide. Veuillez entrer 0, 1, 2 ou 3.")
                
        except Exception as e:
            self.menu_view.display_error(f"Erreur lors du traitement: {e}")
            
        return True
        
    def _handle_quit(self) -> bool:
        """
        Gère la sortie de l'application
        
        Returns:
            bool: False pour arrêter la boucle principale
        """
        if self.menu_view.confirm_action("Êtes-vous sûr de vouloir quitter l'application"):
            # Sauvegarder avant de quitter
            self._save_all_data()
            self.menu_view.display_success("Données sauvegardées. Au revoir !")
            return False
        return True
        
    def _sync_data(self):
        """
        Synchronise les données entre tous les contrôleurs
        Maintient la cohérence des données dans l'application
        """
        # Récupérer les joueurs mis à jour
        self.players = self.player_controller.get_all_players()
        
        # Mettre à jour les autres contrôleurs
        self.tournament_controller.update_players_data(self.players)
        
    def _save_all_data(self):
        """Sauvegarde toutes les données avant fermeture"""
        try:
            # Sauvegarder via les contrôleurs spécialisés
            self.player_controller.save_data()
            self.tournament_controller.save_data()
            
        except Exception as e:
            self.menu_view.display_error(f"Erreur lors de la sauvegarde: {e}")
            
