import re
from typing import List, Tuple, Dict

from .player import Player
from .round import Round
from .match import Match
from utils.validators import validate_score, validate_date_format
from utils.tournament_helpers import (
    TournamentValidationHelper,
    TournamentPairingHelper
)


class Tournament:

    _id_counter = 1

    def __init__(self, name: str, location: str, start_date: str,
                 end_date: str, description: str = "",
                 number_of_rounds: int = 4):
        self._validate_basic_data(
            name, location, start_date, end_date, number_of_rounds
        )

        self.id = Tournament._id_counter
        Tournament._id_counter += 1

        self.name = name.strip()
        self.location = location.strip()
        self.start_date = start_date.strip()
        self.end_date = end_date.strip()
        self.description = description.strip()
        self.number_of_rounds = number_of_rounds

        self.current_round = 0
        self.rounds: List[Round] = []
        self.players: List[Player] = []
        self._is_finished = False

        self.player_scores: Dict[str, float] = {}

    def _validate_basic_data(self, name: str, location: str, start_date: str,
                             end_date: str, number_of_rounds: int):
        if not self._validate_tournament_name(name):
            raise ValueError("Nom du tournoi invalide")
        if not self._validate_location(location):
            raise ValueError("Lieu du tournoi invalide")
        if not validate_date_format(start_date):
            raise ValueError("Date de début invalide")
        if not validate_date_format(end_date):
            raise ValueError("Date de fin invalide")
        if (not isinstance(number_of_rounds, int) or
                number_of_rounds < 1 or number_of_rounds > 20):
            raise ValueError("Nombre de tours invalide (1-20)")

    def _validate_tournament_name(self, name: str) -> bool:
        if not name or not isinstance(name, str):
            return False
        name = name.strip()
        if len(name) < 1 or len(name) > 100:
            return False
        pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-'\.]+$"
        return bool(re.match(pattern, name))

    def _validate_location(self, location: str) -> bool:
        if not location or not isinstance(location, str):
            return False
        location = location.strip()
        if len(location) < 1 or len(location) > 200:
            return False
        pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-',\.]+$"
        return bool(re.match(pattern, location))

    def add_player(self, player: Player):
        if not isinstance(player, Player):
            raise TypeError("L'objet doit être une instance de Player")
        if self.has_started():
            raise ValueError(
                "Impossible d'ajouter un joueur à un tournoi commencé"
            )
        if any(p.national_id == player.national_id for p in self.players):
            raise ValueError(
                f"Le joueur {player.national_id} participe déjà au tournoi"
            )
        self.players.append(player)
        self.player_scores[player.national_id] = 0.0

    def remove_player(self, player: Player) -> bool:
        if self.has_started():
            raise ValueError(
                "Impossible de supprimer un joueur d'un tournoi commencé"
            )
        try:
            self.players.remove(player)
            self.player_scores.pop(player.national_id, None)
            return True
        except ValueError:
            return False

    def get_player_score(self, national_id: str) -> float:
        return self.player_scores.get(national_id, 0.0)

    def add_score_to_player(self, national_id: str, points: float):
        if not validate_score(points):
            raise ValueError("Les points doivent être 0, 0.5 ou 1")
        self.player_scores[national_id] = (
            self.player_scores.get(national_id, 0.0) + points
        )

    def reset_all_scores(self):
        for nat_id in self.player_scores:
            self.player_scores[nat_id] = 0.0

    def has_started(self) -> bool:
        return bool(self.rounds)

    def is_finished(self) -> bool:
        return (
            self._is_finished or
            (self.current_round >= self.number_of_rounds and
             self.rounds and self.rounds[-1].is_finished)
        )

    def finish_tournament(self):
        self._is_finished = True

    def can_start_next_round(self) -> bool:
        return (
            not self.is_finished() and
            len(self.players) >= 2 and
            len(self.players) % 2 == 0 and
            self.current_round < self.number_of_rounds and
            (not self.rounds or self.rounds[-1].is_finished)
        )

    def start_next_round(self, pairs: List[Tuple[Player, Player]]) -> Round:
        if not self.can_start_next_round():
            raise ValueError("Impossible de démarrer le tour suivant")
        self.current_round += 1
        new_round = Round(f"Tour {self.current_round}")
        for p1, p2 in pairs:
            new_round.add_match(Match(p1.national_id, p2.national_id))
        self.rounds.append(new_round)
        return new_round

    def update_player_scores(self):
        self.reset_all_scores()
        for rnd in self.rounds:
            for m in rnd.get_finished_matches():
                self.add_score_to_player(m.player1_national_id, m.player1_score)
                self.add_score_to_player(m.player2_national_id, m.player2_score)

    def get_current_rankings(self) -> List[Player]:
        return sorted(
            self.players,
            key=lambda p: (
                -self.get_player_score(p.national_id),
                p.last_name,
                p.first_name
            )
        )

    def get_final_rankings(self) -> List[Player]:
        if not self.is_finished():
            return self.get_current_rankings()
        self.update_player_scores()
        return self.get_current_rankings()

    def generate_pairs_for_next_round(self) -> List[Tuple[Player, Player]]:
        return TournamentPairingHelper.generate_pairs_for_next_round(self)

    def validate_tournament_state(self) -> List[str]:
        return TournamentValidationHelper.validate_tournament_state(self)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
            "number_of_rounds": self.number_of_rounds,
            "current_round": self.current_round,
            "rounds": [rnd.to_dict() for rnd in self.rounds],
            "players": [pl.to_dict() for pl in self.players],
            "player_scores": self.player_scores,
            "is_finished": self._is_finished
        }

    @staticmethod
    def from_dict(data: dict, players_lookup: Dict[str, Player]) -> 'Tournament':
        required = ["name", "location", "start_date", "end_date"]
        for field in required:
            if field not in data:
                raise KeyError(f"Champ requis manquant: {field}")

        t = Tournament(
            name=data["name"],
            location=data["location"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            description=data.get("description", ""),
            number_of_rounds=data.get("number_of_rounds", 4)
        )
        # restore ID and counter
        t.id = data.get("id", t.id)
        Tournament._id_counter = max(Tournament._id_counter, t.id + 1)
        t.current_round = data.get("current_round", 0)
        t._is_finished = data.get("is_finished", False)

        t._load_players(data.get("players", []), players_lookup)
        t.player_scores = data.get("player_scores", {})
        for pid in (p.national_id for p in t.players):
            t.player_scores.setdefault(pid, 0.0)

        t._load_rounds(data.get("rounds", []))
        return t

    def _load_players(self, raw_players: List[dict],
                      lookup: Dict[str, Player]):
        for pd in raw_players:
            if not isinstance(pd, dict):
                continue
            nid = pd.get("national_id")
            if nid in lookup:
                self.players.append(lookup[nid])

    def _load_rounds(self, raw_rounds: List[dict]):
        for rd in raw_rounds:
            try:
                self.rounds.append(Round.from_dict(rd))
            except Exception as e:
                print(f"Erreur lors du chargement d'un tour: {e}")

    def __str__(self) -> str:
        status = (
            "Terminé" if self.is_finished()
            else ("En cours" if self.has_started() else "Non commencé")
        )
        return (
            f"{self.name} ({self.location}) - {len(self.players)} "
            f"joueurs - {status}"
        )

    def __repr__(self) -> str:
        return (
            f"Tournament(id={self.id}, name='{self.name}', "
            f"players={len(self.players)}, rounds={len(self.rounds)})"
        )
