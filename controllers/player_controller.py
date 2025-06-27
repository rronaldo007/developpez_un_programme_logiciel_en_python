"""PlayerController module.

Manages CRUD operations for Player objects, handles input validation,
user interaction via PlayerView, and persistence through DataManager.
"""

from typing import List, Dict
from models.player import Player
from views.player_view import PlayerView
from data.data_manager import DataManager
from utils.validators import (
    validate_chess_id,
    validate_name,
    validate_date_format
)


class PlayerController:
    """Handles player-related workflows: add, list, modify, delete."""

    def __init__(self, data_manager: DataManager, players: List[Player]):
        """Initialize with a DataManager instance and existing players."""
        self.data_manager = data_manager
        self.players = players
        self.player_view = PlayerView()

    def run(self):
        """Main loop for the player menu until the user exits."""
        try:
            while True:
                self.player_view.display_player_menu()
                choice = self.player_view.get_user_choice("Votre choix")
                if not self._handle_player_menu_choice(choice):
                    break
        except Exception as e:
            self.player_view.display_error(
                f"Erreur dans le gestionnaire de joueurs: {e}"
            )

    def _handle_player_menu_choice(self, choice: str) -> bool:
        """Dispatch menu choices: 1-add, 2-list, 3-modify, 4-delete, 0-exit."""
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
                self.player_view.display_error(
                    "Choix invalide. Entrez un nombre entre 0 et 4."
                )
        except Exception as e:
            self.player_view.display_error(f"Erreur lors du traitement: {e}")
        return True

    def _handle_add_player(self):
        """Prompt for and add a new player if data is valid."""
        try:
            player_data = self.player_view.get_player_info()
            if not self._validate_player_data(player_data):
                return
            if self._player_exists(player_data['national_id']):
                self.player_view.display_error(
                    f"Un joueur avec l'ID {player_data['national_id']} existe déjà."
                )
                return

            player = Player(
                last_name=player_data['last_name'],
                first_name=player_data['first_name'],
                birthdate=player_data['birthdate'],
                national_id=player_data['national_id']
            )
            self.players.append(player)

            if self._save_players():
                self.player_view.display_success(
                    f"Joueur {player.first_name} {player.last_name} ajouté avec succès!"
                )
                self.player_view.display_player_details(player)
            else:
                self.players.remove(player)
                self.player_view.display_error("Erreur lors de la sauvegarde.")
        except ValueError as e:
            self.player_view.display_error(f"Données invalides: {e}")
        except Exception as e:
            self.player_view.display_error(f"Erreur lors de l'ajout: {e}")

    def _handle_list_all_players(self):
        """List all players, sorted by last and first name."""
        if not self.players:
            self.player_view.display_info("Aucun joueur enregistré.")
            return
        sorted_players = sorted(
            self.players,
            key=lambda p: (p.last_name.lower(), p.first_name.lower())
        )
        self.player_view.display_players_list(sorted_players)
        self.player_view.wait_for_user()

    def _handle_modify_player(self):
        """Modify an existing player's details."""
        if not self.players:
            self.player_view.display_info("Aucun joueur à modifier.")
            return

        player = self.player_view.select_player_from_list(
            self.players,
            "SÉLECTIONNER LE JOUEUR À MODIFIER"
        )
        if not player:
            return

        new_data = self.player_view.get_player_modification_info(player)
        if not self._validate_player_data(new_data):
            return

        if (new_data['national_id'] != player.national_id and
                self._player_exists(new_data['national_id'])):
            self.player_view.display_error(
                f"L'ID {new_data['national_id']} est déjà utilisé."
            )
            return

        old = {
            'last_name': player.last_name,
            'first_name': player.first_name,
            'birthdate': player.birthdate,
            'national_id': player.national_id
        }
        try:
            player.last_name = new_data['last_name']
            player.first_name = new_data['first_name']
            player.birthdate = new_data['birthdate']
            player.national_id = new_data['national_id']

            if self._save_players():
                self.player_view.display_success("Joueur modifié avec succès!")
                self.player_view.display_player_details(player)
            else:
                # rollback
                player.last_name = old['last_name']
                player.first_name = old['first_name']
                player.birthdate = old['birthdate']
                player.national_id = old['national_id']
                self.player_view.display_error("Erreur lors de la sauvegarde.")
        except Exception as e:
            # rollback on unexpected error
            player.last_name = old['last_name']
            player.first_name = old['first_name']
            player.birthdate = old['birthdate']
            player.national_id = old['national_id']
            self.player_view.display_error(f"Erreur lors de la modification: {e}")

    def _handle_delete_player(self):
        """Remove a player after confirmation and save changes."""
        if not self.players:
            self.player_view.display_info("Aucun joueur à supprimer.")
            return

        player = self.player_view.select_player_from_list(
            self.players,
            "SÉLECTIONNER LE JOUEUR À SUPPRIMER"
        )
        if not player:
            return

        if not self.player_view.confirm_player_deletion(player):
            self.player_view.display_info("Suppression annulée.")
            return

        try:
            self.players.remove(player)
            if self._save_players():
                self.player_view.display_success(
                    f"Joueur {player.first_name} {player.last_name} supprimé avec succès!"
                )
            else:
                self.players.append(player)
                self.player_view.display_error("Erreur lors de la sauvegarde.")
        except Exception as e:
            self.player_view.display_error(f"Erreur lors de la suppression: {e}")

    def _validate_player_data(self, player_data: Dict[str, str]) -> bool:
        """Validate name, date format, and chess ID for a player."""
        if not validate_name(player_data['last_name']):
            self.player_view.display_error("Nom de famille invalide.")
            return False
        if not validate_name(player_data['first_name']):
            self.player_view.display_error("Prénom invalide.")
            return False
        if not validate_date_format(player_data['birthdate']):
            self.player_view.display_error(
                "Date de naissance invalide (format: YYYY-MM-DD)."
            )
            return False
        if not validate_chess_id(player_data['national_id']):
            self.player_view.display_error(
                "Identifiant national invalide (format: AB12345)."
            )
            return False
        return True

    def _player_exists(self, national_id: str) -> bool:
        """Check if a player with the given national ID already exists."""
        return any(p.national_id == national_id for p in self.players)

    def _save_players(self) -> bool:
        """Persist the current players list via DataManager."""
        return self.data_manager.save_players(self.players)

    def get_all_players(self) -> List[Player]:
        """Return a shallow copy of the players list."""
        return self.players.copy()

    def save_data(self):
        """Ensure all player data is saved, reporting any error."""
        if not self._save_players():
            self.player_view.display_error(
                "Erreur lors de la sauvegarde des joueurs."
            )
