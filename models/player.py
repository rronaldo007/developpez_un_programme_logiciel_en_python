from typing import Optional
from utils.validators import (
    validate_chess_id, validate_name, validate_date_format
)
from utils.date_utils import calculate_age


class Player:
    def __init__(self, last_name: str, first_name: str, birthdate: str,
                 national_id: str):
        self._validate_data(last_name, first_name, birthdate, national_id)

        self.last_name = last_name.strip().title()
        self.first_name = first_name.strip().title()
        self.birthdate = birthdate.strip()
        self.national_id = national_id.strip().upper()

    def _validate_data(self, last_name: str, first_name: str, birthdate: str,
                       national_id: str):
        if not validate_name(last_name):
            raise ValueError("Nom de famille invalide")
        if not validate_name(first_name):
            raise ValueError("Prénom invalide")
        if not validate_date_format(birthdate):
            raise ValueError(
                "Date de naissance invalide (format: YYYY-MM-DD)"
            )
        if not validate_chess_id(national_id):
            raise ValueError(
                "Identifiant national invalide (format: AB12345)"
            )

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def calculate_age(self, reference_date: Optional[str] = None) -> Optional[int]:
        return calculate_age(self.birthdate, reference_date)

    def to_dict(self) -> dict:
        """Sérialisation simple"""
        return {
            "last_name": self.last_name,
            "first_name": self.first_name,
            "birthdate": self.birthdate,
            "national_id": self.national_id
        }

    @staticmethod
    def from_dict(data: dict) -> 'Player':
        required_fields = ["last_name", "first_name", "birthdate", "national_id"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Champ requis manquant: {field}")

        player = Player(
            last_name=data["last_name"],
            first_name=data["first_name"],
            birthdate=data["birthdate"],
            national_id=data["national_id"]
        )

        return player

    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.national_id})"

    def __repr__(self) -> str:
        return (f"Player('{self.last_name}', '{self.first_name}', "
                f"'{self.birthdate}', '{self.national_id}')")