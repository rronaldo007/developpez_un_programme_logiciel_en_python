import json
from typing import List

from models.round import Round
from models.player import Player


class Tournament:
    _id_counter = 0

    def __init__(self, name: str, location: str, start_date: str, end_date: str, description: str = "", number_of_rounds: int = 4):
        self.id = Tournament._id_counter
        Tournament._id_counter += 1

        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.number_of_rounds = number_of_rounds
        self.current_round = 0
        self.rounds: List[Round] = []
        self.players: List[Player] = []

    def add_player(self, player: Player):  # CORRECTION: Enlever @staticmethod
        self.players.append(player)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
            "number_of_rounds": self.number_of_rounds,
            "current_round": self.current_round,
            "rounds": [round_.to_dict() for round_ in self.rounds],
            "players": [player.to_dict() for player in self.players]
        }

    def save_to_file(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load_from_file(path: str, player_lookup: dict) -> 'Tournament':
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        tournament = Tournament(
            data["name"],
            data["location"],
            data["start_date"],
            data["end_date"],
            data.get("description", ""),
            data.get("number_of_rounds", 4)
        )
        tournament.id = data.get("id", Tournament._id_counter)
        Tournament._id_counter = max(Tournament._id_counter, tournament.id + 1)
        tournament.current_round = data.get("current_round", 0)
        
        tournament.players = []
        for player_data in data.get("players", []):
            if isinstance(player_data, dict) and "national_id" in player_data:
                national_id = player_data["national_id"]
                if national_id in player_lookup:
                    player = player_lookup[national_id]
                    player.score = player_data.get("score", 0.0)
                    tournament.players.append(player)
            elif isinstance(player_data, str):
                if player_data in player_lookup:
                    tournament.players.append(player_lookup[player_data])
        
        tournament.rounds = []
        for round_data in data.get("rounds", []):
            round_obj = Round.from_dict(round_data, player_lookup)
            tournament.rounds.append(round_obj)
        
        return tournament