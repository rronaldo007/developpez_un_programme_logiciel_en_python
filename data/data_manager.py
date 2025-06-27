import os
from typing import List, Optional, Dict
from models.player import Player
from models.tournament import Tournament
from utils.file_utils import (
    ensure_directory_exists, safe_json_save, safe_json_load
)


class DataManager:

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.players_file = os.path.join(data_dir, "players.json")
        self.tournaments_dir = os.path.join(data_dir, "tournaments")

        self._init_data_directories()

        self._stats = {
            'saves_count': 0,
            'loads_count': 0,
            'errors_count': 0,
            'last_operation': None
        }

    def _init_data_directories(self):
        try:
            ensure_directory_exists(self.data_dir)
            ensure_directory_exists(self.tournaments_dir)
        except Exception as e:
            raise IOError(
                f"Impossible de créer les répertoires de données: {e}"
            )

    def save_players(self, players: List[Player]) -> bool:
        try:
            self._stats['last_operation'] = (
                f"save_players_{len(players)}_players"
            )

            if not self._validate_players_data(players):
                return False

            players_data = []
            for player in players:
                try:
                    player_dict = player.to_dict()
                    players_data.append(player_dict)
                except Exception as e:
                    print(f"Erreur sérialisation joueur {player}: {e}")
                    self._stats['errors_count'] += 1
                    continue

            success = safe_json_save(players_data, self.players_file)

            if success:
                self._stats['saves_count'] += 1
                return True
            else:
                self._stats['errors_count'] += 1
                return False

        except Exception as e:
            print(f"Erreur sauvegarde joueurs: {e}")
            self._stats['errors_count'] += 1
            return False

    def load_players(self) -> List[Player]:
        try:
            self._stats['last_operation'] = "load_players"

            players_data = safe_json_load(self.players_file)
            if not players_data:
                return []

            players = []
            for i, player_data in enumerate(players_data):
                try:
                    if not self._validate_player_dict(player_data):
                        print(
                            f"ATTENTION: Joueur {i} ignoré - "
                            "données invalides"
                        )
                        continue

                    player = Player.from_dict(player_data)
                    players.append(player)

                except Exception as e:
                    print(
                        f"ATTENTION: Joueur {i} ignoré lors du "
                        f"chargement: {e}"
                    )
                    self._stats['errors_count'] += 1
                    continue

            self._stats['loads_count'] += 1
            print(f"Chargement réussi: {len(players)} joueurs")
            return players

        except Exception as e:
            print(f"Erreur chargement joueurs: {e}")
            self._stats['errors_count'] += 1

            backup_file = self._find_latest_backup(self.players_file)
            if backup_file:
                try:
                    print(f"Tentative de récupération depuis {backup_file}")
                    backup_data = safe_json_load(backup_file)
                    if backup_data:
                        players = []
                        for player_data in backup_data:
                            try:
                                player = Player.from_dict(player_data)
                                players.append(player)
                            except Exception:
                                continue
                        print(f"Récupération réussie: {len(players)} joueurs")
                        return players
                except Exception:
                    pass

            return []

    def save_tournament(self, tournament: Tournament) -> bool:
        try:
            self._stats['last_operation'] = f"save_tournament_{tournament.id}"

            if not self._validate_tournament_data(tournament):
                return False

            filename = f"tournament_{tournament.id}.json"
            file_path = os.path.join(self.tournaments_dir, filename)

            tournament_data = tournament.to_dict()

            success = safe_json_save(tournament_data, file_path)

            if success:
                self._stats['saves_count'] += 1
                return True
            else:
                self._stats['errors_count'] += 1
                return False

        except Exception as e:
            print(f"Erreur sauvegarde tournoi {tournament.id}: {e}")
            self._stats['errors_count'] += 1
            return False

    def load_tournament(self, tournament_id: int,
                        players_lookup: Dict[str, Player]) -> Optional[Tournament]:
        try:
            self._stats['last_operation'] = f"load_tournament_{tournament_id}"

            filename = f"tournament_{tournament_id}.json"
            file_path = os.path.join(self.tournaments_dir, filename)

            if not os.path.exists(file_path):
                return None

            tournament_data = safe_json_load(file_path)
            if not tournament_data:
                return None

            if not self._validate_tournament_dict(tournament_data):
                print(
                    f"ERREUR: Données du tournoi {tournament_id} invalides"
                )
                return None

            tournament = Tournament.from_dict(tournament_data, players_lookup)

            self._stats['loads_count'] += 1
            return tournament

        except Exception as e:
            print(f"Erreur chargement tournoi {tournament_id}: {e}")
            self._stats['errors_count'] += 1
            return None

    def get_all_tournament_files(self) -> List[str]:
        try:
            if not os.path.exists(self.tournaments_dir):
                return []

            files = []
            for filename in os.listdir(self.tournaments_dir):
                if (filename.startswith("tournament_") and
                    filename.endswith(".json") and
                        not filename.endswith(".backup")):
                    files.append(
                        os.path.join(self.tournaments_dir, filename)
                    )

            files.sort(key=lambda x: self._extract_tournament_id(x))
            return files

        except Exception as e:
            print(f"Erreur lecture répertoire tournois: {e}")
            return []

    def delete_tournament(self, tournament_id: int) -> bool:
        try:
            filename = f"tournament_{tournament_id}.json"
            file_path = os.path.join(self.tournaments_dir, filename)

            if not os.path.exists(file_path):
                return False

            os.remove(file_path)

            print(f"Tournoi {tournament_id} supprimé")
            return True

        except Exception as e:
            print(f"Erreur suppression tournoi {tournament_id}: {e}")
            return False

    def _find_latest_backup(self, original_file: str) -> Optional[str]:
        """Find the latest backup file for the given original file."""
        try:
            backup_pattern = f"{original_file}.backup"
            if os.path.exists(backup_pattern):
                return backup_pattern
            return None
        except Exception:
            return None

    def _validate_players_data(self, players: List[Player]) -> bool:
        try:
            if not isinstance(players, list):
                return False

            seen_ids = set()
            for player in players:
                if not isinstance(player, Player):
                    return False
                if player.national_id in seen_ids:
                    print(f"ERREUR: ID dupliqué détecté: {player.national_id}")
                    return False
                seen_ids.add(player.national_id)

            return True

        except Exception:
            return False

    def _validate_player_dict(self, player_data: Dict) -> bool:
        required_fields = ["last_name", "first_name", "birthdate", "national_id"]
        return all(
            field in player_data and player_data[field]
            for field in required_fields
        )

    def _validate_tournament_data(self, tournament: Tournament) -> bool:
        try:
            if not isinstance(tournament, Tournament):
                return False
            if not tournament.name or not tournament.location:
                return False
            return True
        except Exception:
            return False

    def _validate_tournament_dict(self, tournament_data: Dict) -> bool:
        required_fields = ["id", "name", "location", "start_date", "end_date"]
        return all(field in tournament_data for field in required_fields)

    def _extract_tournament_id(self, file_path: str) -> int:
        try:
            filename = os.path.basename(file_path)
            id_str = filename.replace("tournament_", "").replace(".json", "")
            return int(id_str)
        except Exception:
            return 0