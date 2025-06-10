from datetime import datetime

class Player:

    def __init__(self, last_name: str, first_name: str, birthdate: str, national_id: str):

        self.last_name = last_name
        self.first_name = first_name
        self.birthdate = birthdate 
        self.national_id = national_id  
        self.score = 0.0

    def to_dict(self):
        return {
            "id": self.id,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birthdate": self.birthdate,
            "national_id": self.national_id,
            "score": self.score
        }

    @staticmethod
    def from_dict(data):
        player = Player(
            data["last_name"],
            data["first_name"],
            data["birthdate"],
            data["national_id"],
        )
        player.score = data.get("score", 0.0)
        return player
