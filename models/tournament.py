from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import random


class Tournament:
    _id_counter = 0
    
    def __init__(
        self,
        name: str,
        location: str,
        start_date: datetime,
        end_date: datetime,
        num_rounds: int = 4,
        description: Optional[str] = None,
    ):
        self.id = Tournament._id_counter
        Tournament._id_counter += 1
        
        if start_date > end_date:
            raise ValueError("La date de début doit être antérieure à la date de fin.")
        
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.num_rounds = num_rounds
        self.current_round_index = 0
        self.rounds: List[Dict[str, Any]] = []
        self.players: List[str] = []
        self.description = description or ""
        
        self.player_matches: Dict[str, List[str]] = {}
        
        self.player_scores: Dict[str, float] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "num_rounds": self.num_rounds,
            "current_round_index": self.current_round_index,
            "rounds": self.rounds,
            "players": self.players,
            "description": self.description,
        }
    
    def add_player(self, chess_id: str) -> None:
        if chess_id not in self.players:
            self.players.append(chess_id)
            self.player_scores[chess_id] = 0.0
            self.player_matches[chess_id] = []
    
    def _generate_pairs(self) -> List[Tuple[str, str]]:

        pairs = []
        
        available_players = self.players.copy()
        
        if self.current_round_index == 0:
            random.shuffle(available_players)
            
            for i in range(0, len(available_players), 2):
                if i + 1 < len(available_players):
                    pairs.append((available_players[i], available_players[i + 1]))

        else:
            pass
        
        return pairs
    
    
    def __repr__(self) -> str:
        return (
            f"Tournament(id={self.id}, name={self.name}, location={self.location}, "
            f"start_date={self.start_date}, end_date={self.end_date}, "
            f"num_rounds={self.num_rounds}, current_round_index={self.current_round_index})"
        )