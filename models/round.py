from typing import List, Optional, Tuple
from .match import Match
from utils.date_utils import (
    get_current_timestamp, calculate_duration_minutes
)


class Round:

    def __init__(self, name: str):
        if not name or not name.strip():
            raise ValueError("Le nom du tour ne peut pas être vide")

        self.name = name.strip()
        self.start_time = get_current_timestamp()
        self.end_time: Optional[str] = None
        self.matches: List[Match] = []
        self.is_finished = False

    def add_match(self, match: Match):
        if self.is_finished:
            raise ValueError(
                "Impossible d'ajouter un match à un tour terminé"
            )
        if not isinstance(match, Match):
            raise TypeError("L'objet doit être une instance de Match")
        self.matches.append(match)

    def end_round(self):
        if not self.all_matches_finished():
            unfinished_count = len(self.get_unfinished_matches())
            raise ValueError(
                f"Il reste {unfinished_count} match(s) non terminé(s)"
            )
        self.end_time = get_current_timestamp()
        self.is_finished = True

    def all_matches_finished(self) -> bool:
        return all(match.is_finished for match in self.matches)

    def get_finished_matches(self) -> List[Match]:
        return [match for match in self.matches if match.is_finished]

    def get_unfinished_matches(self) -> List[Match]:
        return [match for match in self.matches if not match.is_finished]

    def get_completion_percentage(self) -> float:
        if not self.matches:
            return 0.0
        finished_count = len(self.get_finished_matches())
        return (finished_count / len(self.matches)) * 100

    def get_duration_minutes(self) -> Optional[int]:
        if not self.end_time:
            return None
        return calculate_duration_minutes(self.start_time, self.end_time)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "matches": [match.to_dict() for match in self.matches],
            "is_finished": self.is_finished
        }

    @staticmethod
    def from_dict(data: dict) -> 'Round':
        if "name" not in data:
            raise KeyError("Champ requis manquant: name")

        round_obj = Round(data["name"])
        round_obj.start_time = data.get("start_time", get_current_timestamp())
        round_obj.end_time = data.get("end_time")
        round_obj.is_finished = data.get("is_finished", False)

        for match_data in data.get("matches", []):
            try:
                match = Match.from_dict(match_data)
                round_obj.matches.append(match)
            except Exception as e:
                print(f"Erreur lors du chargement d'un match: {e}")

        return round_obj

    def __str__(self) -> str:
        status = "Terminé" if self.is_finished else "En cours"
        return f"{self.name} - {len(self.matches)} matchs ({status})"

    def __repr__(self) -> str:
        return (f"Round('{self.name}', matches={len(self.matches)}, "
                f"finished={self.is_finished})")