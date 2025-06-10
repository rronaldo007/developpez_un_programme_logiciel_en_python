from datetime import datetime
from typing import List, Optional

from .match import Match

class Round:
    """
    Modèle représentant un round/tour de tournoi
    """
    
    def __init__(self, name: str):
        self.name = name  # ex: "Round 1"
        self.start_time = datetime.now().isoformat()
        self.end_time: Optional[str] = None
        self.matches: List[Match] = []
        self.is_finished = False

    def add_match(self, match: Match):
        """Ajoute un match au round"""
        self.matches.append(match)

    def end_round(self):
        """Termine le round"""
        if not self.all_matches_finished():
            raise ValueError("Tous les matchs doivent être terminés avant de clôturer le round")
        
        self.end_time = datetime.now().isoformat()
        self.is_finished = True

    def all_matches_finished(self) -> bool:
        """Vérifie si tous les matchs du round sont terminés"""
        return all(match.is_finished for match in self.matches)

    def get_matches_as_tuples(self):
        """
        Retourne tous les matchs sous forme de tuples
        Conforme aux spécifications du projet
        
        Returns:
            list: Liste de tuples de matchs
        """
        return [match.get_match_tuple() for match in self.matches]

    def to_dict(self):
        """Convertit le round en dictionnaire pour la sérialisation JSON"""
        return {
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "matches": [match.to_dict() for match in self.matches],
            "is_finished": self.is_finished
        }

    @staticmethod
    def from_dict(data):
        """Crée un round à partir d'un dictionnaire"""
        round_obj = Round(data["name"])
        round_obj.start_time = data.get("start_time", datetime.now().isoformat())
        round_obj.end_time = data.get("end_time")
        round_obj.is_finished = data.get("is_finished", False)
        
        # Reconstruire les matchs
        for match_data in data.get("matches", []):
            match = Match.from_dict(match_data)
            round_obj.matches.append(match)
        
        return round_obj