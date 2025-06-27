from typing import Optional, Tuple, List
from utils.validators import validate_score
from utils.match_helpers import MatchAnalysisHelper


class Match:

    def __init__(self, player1_national_id: str, player2_national_id: str):
        if player1_national_id == player2_national_id:
            raise ValueError("Un joueur ne peut pas jouer contre lui-même")

        self.player1_national_id = player1_national_id
        self.player2_national_id = player2_national_id
        self.player1_score = 0.0
        self.player2_score = 0.0
        self.is_finished = False

    def set_result(self, player1_score: float, player2_score: float):
        if not validate_score(player1_score) or not validate_score(player2_score):
            raise ValueError("Les scores doivent être 0, 0.5 ou 1")

        if abs(player1_score + player2_score - 1.0) > 0.001:
            raise ValueError("La somme des scores doit être égale à 1.0")

        self.player1_score = float(player1_score)
        self.player2_score = float(player2_score)
        self.is_finished = True

    def get_match_tuple(self) -> Tuple[List, List]:
        return (
            [self.player1_national_id, self.player1_score],
            [self.player2_national_id, self.player2_score]
        )

    def get_winner_id(self) -> Optional[str]:
        if not self.is_finished:
            return None
        if self.player1_score > self.player2_score:
            return self.player1_national_id
        elif self.player2_score > self.player1_score:
            return self.player2_national_id
        return None

    def get_loser_id(self) -> Optional[str]:
        if not self.is_finished:
            return None
        if self.player1_score < self.player2_score:
            return self.player1_national_id
        elif self.player2_score < self.player1_score:
            return self.player2_national_id
        return None

    def is_draw(self) -> bool:
        return (self.is_finished and
                abs(self.player1_score - self.player2_score) < 0.001)

    def involves_player(self, national_id: str) -> bool:
        return (national_id == self.player1_national_id or
                national_id == self.player2_national_id)

    def get_score_for_player(self, player_id: str) -> Optional[float]:
        if player_id == self.player1_national_id:
            return self.player1_score
        elif player_id == self.player2_national_id:
            return self.player2_score
        return None

    def analyze_result(self) -> dict:
        return MatchAnalysisHelper.analyze_match_result(self)

    def to_dict(self) -> dict:
        return {
            "player1_national_id": self.player1_national_id,
            "player2_national_id": self.player2_national_id,
            "player1_score": self.player1_score,
            "player2_score": self.player2_score,
            "is_finished": self.is_finished
        }

    @staticmethod
    def from_dict(data: dict) -> 'Match':
        required_fields = ["player1_national_id", "player2_national_id"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Champ requis manquant: {field}")

        match = Match(
            player1_national_id=data["player1_national_id"],
            player2_national_id=data["player2_national_id"]
        )

        match.player1_score = data.get("player1_score", 0.0)
        match.player2_score = data.get("player2_score", 0.0)
        match.is_finished = data.get("is_finished", False)

        return match

    def __str__(self) -> str:
        if self.is_finished:
            return (f"{self.player1_national_id} {self.player1_score}-"
                    f"{self.player2_score} {self.player2_national_id}")
        else:
            return (f"{self.player1_national_id} vs "
                    f"{self.player2_national_id} (En cours)")

    def __repr__(self) -> str:
        return (f"Match('{self.player1_national_id}', "
                f"'{self.player2_national_id}', "
                f"finished={self.is_finished})")