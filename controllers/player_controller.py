
from typing import List, Optional, Dict
from models.player import Player
from views.player_view import PlayerView
from data.data_manager import DataManager
from utils.validators import validate_chess_id, validate_name, validate_date_format


class PlayerController:
    """
    Contrôleur pour la gestion des joueurs - Pattern MVC - 
    
    Responsabilités :
    - Coordination entre PlayerView et Player model
    - Validation des données joueurs
    - Logique métier CRUD (Create, Read, Update, Delete)
    - Gestion de la persistance via DataManager
    
    Note: Les scores sont maintenant gérés au niveau des tournois
    """
    
    def __init__(self, data_manager: DataManager, players: List[Player]):
        """
        Initialise le contrôleur des joueurs
        
        Args:
            data_manager (DataManager): Gestionnaire de persistance
            players (List[Player]): Liste des joueurs existants
        """
        self.data_manager = data_manager
        self.players = players
        self.player_view = PlayerView()
        
    def run(self):
        """
        Point d'entrée principal du contrôleur des joueurs
        Gère le menu et délègue aux méthodes appropriées
        """
        try:
            while True:
                # VUE : Affiche le menu
                self.player_view.display_player_menu()
                
                # VUE : Récupère le choix
                choice = self.player_view.get_user_choice("Votre choix")
                
                # CONTRÔLEUR : Traite le choix
                if not self._handle_player_menu_choice(choice):
                    break
                    
        except Exception as e:
            self.player_view.display_error(f"Erreur dans le gestionnaire de joueurs: {e}")
            
    def _handle_player_menu_choice(self, choice: str) -> bool:
        """
        Traite les choix du menu des joueurs
        
        Args:
            choice (str): Choix de l'utilisateur
            
        Returns:
            bool: True pour continuer, False pour retour au menu principal
        """
        try:
            if choice == "1":
                self._handle_add_player()
            elif choice == "2":
                self._handle_list_all_players()
            elif choice == "3":
                self._handle_modify_player()
            elif choice == "4":
                self._handle_delete_player()
            elif choice == "0":
                return False
            else:
                self.player_view.display_error("Choix invalide. Entrez un nombre entre 0 et 7.")
                
        except Exception as e:
            self.player_view.display_error(f"Erreur lors du traitement: {e}")
            
        return True
        
    def _handle_add_player(self):
        """Gère l'ajout d'un nouveau joueur"""
        try:
            # VUE : Collecte les données
            player_data = self.player_view.get_player_info()
            
            # CONTRÔLEUR : Valide les données
            if not self._validate_player_data(player_data):
                return
                
            # CONTRÔLEUR : Vérifie l'unicité de l'ID
            if self._player_exists(player_data['national_id']):
                self.player_view.display_error(
                    f"Un joueur avec l'ID {player_data['national_id']} existe déjà."
                )
                return
                
            # MODÈLE : Crée le joueur
            player = Player(
                last_name=player_data['last_name'],
                first_name=player_data['first_name'],
                birthdate=player_data['birthdate'],
                national_id=player_data['national_id']
            )
            
            # CONTRÔLEUR : Ajoute à la liste
            self.players.append(player)
            
            # DONNÉES : Sauvegarde
            if self._save_players():
                # VUE : Affiche le succès
                self.player_view.display_success(
                    f"Joueur {player.first_name} {player.last_name} ajouté avec succès!"
                )
                self.player_view.display_player_details(player)
            else:
                # Rollback en cas d'erreur de sauvegarde
                self.players.remove(player)
                self.player_view.display_error("Erreur lors de la sauvegarde.")
                
        except ValueError as e:
            self.player_view.display_error(f"Données invalides: {e}")
        except Exception as e:
            self.player_view.display_error(f"Erreur lors de l'ajout: {e}")
            
    def _handle_list_all_players(self):
        """Affiche tous les joueurs - """
        if not self.players:
            self.player_view.display_info("Aucun joueur enregistré.")
            return
            
        # Trier par nom de famille puis prénom
        sorted_players = sorted(
            self.players, 
            key=lambda p: (p.last_name.lower(), p.first_name.lower())
        )
        
        # VUE : Affiche la liste (la vue gère maintenant l'affichage sans score)
        self.player_view.display_players_list(sorted_players)
        self.player_view.wait_for_user()
        
        
    def _handle_modify_player(self):
        """Gère la modification d'un joueur"""
        if not self.players:
            self.player_view.display_info("Aucun joueur à modifier.")
            return
            
        # VUE : Sélection du joueur
        player = self.player_view.select_player_from_list(
            self.players, 
            "SÉLECTIONNER LE JOUEUR À MODIFIER"
        )
        
        if not player:
            return
            
        # VUE : Collecte les modifications
        new_data = self.player_view.get_player_modification_info(player)
        
        # CONTRÔLEUR : Valide les nouvelles données
        if not self._validate_player_data(new_data):
            return
            
        # CONTRÔLEUR : Vérifie l'unicité du nouvel ID (si changé)
        if (new_data['national_id'] != player.national_id and 
            self._player_exists(new_data['national_id'])):
            self.player_view.display_error(
                f"L'ID {new_data['national_id']} est déjà utilisé."
            )
            return
            
        # CONTRÔLEUR : Sauvegarde les anciennes valeurs pour rollback
        old_data = {
            'last_name': player.last_name,
            'first_name': player.first_name,
            'birthdate': player.birthdate,
            'national_id': player.national_id
        }
        
        try:
            # MODÈLE : Applique les modifications
            player.last_name = new_data['last_name']
            player.first_name = new_data['first_name']
            player.birthdate = new_data['birthdate']
            player.national_id = new_data['national_id']
            
            # DONNÉES : Sauvegarde
            if self._save_players():
                self.player_view.display_success("Joueur modifié avec succès!")
                self.player_view.display_player_details(player)
            else:
                # Rollback en cas d'erreur
                player.last_name = old_data['last_name']
                player.first_name = old_data['first_name']
                player.birthdate = old_data['birthdate']
                player.national_id = old_data['national_id']
                self.player_view.display_error("Erreur lors de la sauvegarde.")
                
        except Exception as e:
            # Rollback en cas d'erreur
            player.last_name = old_data['last_name']
            player.first_name = old_data['first_name']
            player.birthdate = old_data['birthdate']
            player.national_id = old_data['national_id']
            self.player_view.display_error(f"Erreur lors de la modification: {e}")
            
    def _handle_delete_player(self):
        """Gère la suppression d'un joueur"""
        if not self.players:
            self.player_view.display_info("Aucun joueur à supprimer.")
            return
            
        # VUE : Sélection du joueur
        player = self.player_view.select_player_from_list(
            self.players,
            "SÉLECTIONNER LE JOUEUR À SUPPRIMER"
        )
        
        if not player:
            return
            
        # VUE : Confirmation
        if not self.player_view.confirm_player_deletion(player):
            self.player_view.display_info("Suppression annulée.")
            return
            
        try:
            # CONTRÔLEUR : Supprime de la liste
            self.players.remove(player)
            
            # DONNÉES : Sauvegarde
            if self._save_players():
                self.player_view.display_success(
                    f"Joueur {player.first_name} {player.last_name} supprimé avec succès!"
                )
            else:
                # Rollback en cas d'erreur
                self.players.append(player)
                self.player_view.display_error("Erreur lors de la sauvegarde.")
                
        except Exception as e:
            self.player_view.display_error(f"Erreur lors de la suppression: {e}")
            
    def _validate_player_data(self, player_data: Dict[str, str]) -> bool:
        """
        Valide les données d'un joueur
        
        Args:
            player_data (Dict[str, str]): Données à valider
            
        Returns:
            bool: True si valides, False sinon
        """
        # Validation du nom de famille
        if not validate_name(player_data['last_name']):
            self.player_view.display_error("Nom de famille invalide.")
            return False
            
        # Validation du prénom
        if not validate_name(player_data['first_name']):
            self.player_view.display_error("Prénom invalide.")
            return False
            
        # Validation de la date de naissance
        if not validate_date_format(player_data['birthdate']):
            self.player_view.display_error("Date de naissance invalide (format: YYYY-MM-DD).")
            return False
            
        # Validation de l'identifiant national
        if not validate_chess_id(player_data['national_id']):
            self.player_view.display_error("Identifiant national invalide (format: AB12345).")
            return False
            
        return True
        
    def _player_exists(self, national_id: str) -> bool:
        """Vérifie si un joueur avec cet ID existe déjà"""
        return any(player.national_id == national_id for player in self.players)

        
    def _save_players(self) -> bool:
        """Sauvegarde la liste des joueurs"""
        return self.data_manager.save_players(self.players)
        
    # API publique pour les autres contrôleurs
    def get_all_players(self) -> List[Player]:
        """Retourne tous les joueurs"""
        return self.players.copy()
        
    def get_player_by_id(self, national_id: str) -> Optional[Player]:
        """Trouve un joueur par son ID"""
        for player in self.players:
            if player.national_id == national_id:
                return player
        return None
    
    
    def _get_age_distribution(self) -> Dict[str, int]:
        """Calcule la distribution d'âge des joueurs"""
        age_groups = {
            "Moins de 18 ans": 0,
            "18-25 ans": 0,
            "26-35 ans": 0,
            "36-50 ans": 0,
            "Plus de 50 ans": 0
        }
        
        for player in self.players:
            try:
                age = player.calculate_age()
                if age is not None:
                    if age < 18:
                        age_groups["Moins de 18 ans"] += 1
                    elif age <= 25:
                        age_groups["18-25 ans"] += 1
                    elif age <= 35:
                        age_groups["26-35 ans"] += 1
                    elif age <= 50:
                        age_groups["36-50 ans"] += 1
                    else:
                        age_groups["Plus de 50 ans"] += 1
            except:
                # Ignorer les joueurs sans âge calculable
                pass
        
        return age_groups
    
    def _get_current_timestamp(self) -> str:
        """Retourne le timestamp actuel formaté"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_data(self):
        """Sauvegarde publique pour MainController"""
        if not self._save_players():
            self.player_view.display_error("Erreur lors de la sauvegarde des joueurs.")
    
