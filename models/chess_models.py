from datetime import datetime
from typing import List, Tuple, Optional
import json


class Player:
    _id_counter = 0

    def __init__(self, last_name: str, first_name: str, birthdate: str, national_id: str, chess_id: str):
        self.id = Player._id_counter
        Player._id_counter += 1

        self.last_name = last_name
        self.first_name = first_name
        self.birthdate = birthdate 
        self.national_id = national_id  
        self.chess_id = chess_id
        self.score = 0.0

    def to_dict(self):
        return {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birthdate": self.birthdate,
            "national_id": self.national_id,
            "chess_id": self.chess_id,
            "score": self.score
        }

    @staticmethod
    def from_dict(data):
        player = Player(
            data["last_name"],
            data["first_name"],
            data["birthdate"],
            data["national_id"],
            data["chess_id"]
        )
        player.id = data.get("id", Player._id_counter)
        Player._id_counter = max(Player._id_counter, player.id + 1)
        player.score = data.get("score", 0.0)
        return player


class Match:
    _id_counter = 0

    def __init__(self, player1: Player, player2: Player, score1: float = 0.0, score2: float = 0.0):
        self.id = Match._id_counter
        Match._id_counter += 1

        self.match = [(player1, score1), (player2, score2)]

    def to_dict(self):
        return {
            "id": self.id,
            "match": [
                {"player": self.match[0][0].national_id, "score": self.match[0][1]},
                {"player": self.match[1][0].national_id, "score": self.match[1][1]}
            ]
        }


class Round:
    _id_counter = 0

    def __init__(self, name: str):
        self.id = Round._id_counter
        Round._id_counter += 1

        self.name = name  # ex: "Round 1"
        self.start_time = datetime.now().isoformat()
        self.end_time: Optional[str] = None
        self.matches: List[Match] = []

    def end_round(self):
        self.end_time = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "matches": [match.to_dict() for match in self.matches]
        }


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

    def add_player(self, player: Player):
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
        tournament.players = [player_lookup[p["national_id"]] for p in data["players"]]
        # Loading rounds is omitted for now
        return tournament
