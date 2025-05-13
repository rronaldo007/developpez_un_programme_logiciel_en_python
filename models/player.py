from datetime import datetime
from typing import Dict, Any


class Player:
    _id_counter = 0
    
    def __init__(
        self,
        last_name: str,
        first_name: str,
        birthdate: datetime,
        chess_id: str,
    ):
        self.id = Player._id_counter
        Player._id_counter += 1
        
        self.last_name = last_name
        self.first_name = first_name
        self.birthdate = birthdate
        
        if not (len(chess_id) == 7 and 
                chess_id[:2].isalpha() and 
                chess_id[2:].isdigit()):
            raise ValueError("Chess ID must be in format AB12345 (2 letters followed by 5 digits)")
        self.chess_id = chess_id
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birthdate": self.birthdate.isoformat(),
            "chess_id": self.chess_id
        }
    
    def __repr__(self) -> str:
        return f"Player(id={self.id}, last_name={self.last_name}, first_name={self.first_name}, chess_id={self.chess_id})"