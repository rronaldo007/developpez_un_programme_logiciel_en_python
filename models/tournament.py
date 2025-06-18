#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèle Tournament - Architecture MVC épurée - 
Responsabilité : Données et logique métier essentielle + gestion des scores
"""

from typing import List, Optional, Tuple, Dict
from .player import Player
from .round import Round
from .match import Match
from utils.validators import validate_date_format
import re


class Tournament:
    """
    Modèle représentant un tournoi d'échecs - Version épurée
    
    Responsabilités LIMITÉES :
    - Stockage des données du tournoi
    - Gestion de base des joueurs et tours
    - Gestion des scores par joueur
    - Validation essentielle
    - Sérialisation/désérialisation
    
    Logique complexe (système suisse, statistiques, validation) 
    déléguée aux tournament_helpers
    """
    
    _id_counter = 1  # Compteur pour les IDs uniques
    
    def __init__(self, name: str, location: str, start_date: str, end_date: str, 
                 description: str = "", number_of_rounds: int = 4):
        """
        Initialise un nouveau tournoi avec validation de base
        
        Args:
            name (str): Nom du tournoi
            location (str): Lieu du tournoi
            start_date (str): Date de début (YYYY-MM-DD)
            end_date (str): Date de fin (YYYY-MM-DD)
            description (str): Description optionnelle
            number_of_rounds (int): Nombre de tours (défaut: 4)
            
        Raises:
            ValueError: Si les données sont invalides
        """
        # Validation de base via utils
        self._validate_basic_data(name, location, start_date, end_date, number_of_rounds)
        
        # Assignation de l'ID unique
        self.id = Tournament._id_counter
        Tournament._id_counter += 1
        
        # Données de base
        self.name = name.strip()
        self.location = location.strip()
        self.start_date = start_date.strip()
        self.end_date = end_date.strip()
        self.description = description.strip()
        self.number_of_rounds = number_of_rounds
        
        # État du tournoi
        self.current_round = 0
        self.rounds: List[Round] = []
        self.players: List[Player] = []
        self._is_finished = False
        
        # Gestion des scores par joueur (national_id -> score)
        self.player_scores: Dict[str, float] = {}
        
    def _validate_basic_data(self, name: str, location: str, start_date: str, 
                           end_date: str, number_of_rounds: int):
        """Validation de base via utils - """
        # : Utiliser une validation flexible pour les noms de tournois
        if not self._validate_tournament_name(name):
            raise ValueError("Nom du tournoi invalide")
        if not self._validate_location(location):
            raise ValueError("Lieu du tournoi invalide")
        if not validate_date_format(start_date):
            raise ValueError("Date de début invalide")
        if not validate_date_format(end_date):
            raise ValueError("Date de fin invalide")
        if not isinstance(number_of_rounds, int) or number_of_rounds < 1 or number_of_rounds > 20:
            raise ValueError("Nombre de tours invalide (1-20)")

    def _validate_tournament_name(self, name: str) -> bool:
        """
        Validation flexible pour les noms de tournois
        Accepte lettres, chiffres, espaces, tirets, apostrophes, points
        """
        if not name or not isinstance(name, str):
            return False
            
        name = name.strip()
        
        # Minimum 1 caractère, maximum 100
        if len(name) < 1 or len(name) > 100:
            return False
            
        # Pattern flexible : lettres, chiffres, espaces, tirets, apostrophes, points
        pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-'\.]+$"
        return bool(re.match(pattern, name))

    def _validate_location(self, location: str) -> bool:
        """
        Validation flexible pour les lieux
        Accepte lettres, chiffres, espaces, tirets, apostrophes, virgules, points
        """
        if not location or not isinstance(location, str):
            return False
            
        location = location.strip()
        
        # Minimum 1 caractère, maximum 200
        if len(location) < 1 or len(location) > 200:
            return False
            
        # Pattern flexible
        pattern = r"^[a-zA-ZÀ-ÿ0-9\s\-',\.]+$"
        return bool(re.match(pattern, location))
            
    def add_player(self, player: Player):
        """Ajoute un joueur - Logique simple"""
        if not isinstance(player, Player):
            raise TypeError("L'objet doit être une instance de Player")
        if self.has_started():
            raise ValueError("Impossible d'ajouter un joueur à un tournoi commencé")
        if any(p.national_id == player.national_id for p in self.players):
            raise ValueError(f"Le joueur {player.national_id} participe déjà au tournoi")
        
        self.players.append(player)
        self.player_scores[player.national_id] = 0.0
        
    def remove_player(self, player: Player) -> bool:
        """Supprime un joueur"""
        if self.has_started():
            raise ValueError("Impossible de supprimer un joueur d'un tournoi commencé")
        try:
            self.players.remove(player)
            if player.national_id in self.player_scores:
                del self.player_scores[player.national_id]
            return True
        except ValueError:
            return False
            
    def get_player_by_id(self, national_id: str) -> Optional[Player]:
        """Trouve un joueur par son ID"""
        for player in self.players:
            if player.national_id == national_id:
                return player
        return None
        
    def get_player_score(self, national_id: str) -> float:
        """Récupère le score d'un joueur"""
        return self.player_scores.get(national_id, 0.0)
        
    def add_score_to_player(self, national_id: str, points: float):
        """
        Ajoute des points au score d'un joueur -  NOM DE MÉTHODE
        
        Args:
            national_id (str): ID du joueur
            points (float): Points à ajouter (0, 0.5 ou 1)
            
        Raises:
            ValueError: Si les points ne sont pas valides
        """
        from utils.validators import validate_score
        if not validate_score(points):
            raise ValueError("Les points doivent être 0, 0.5 ou 1")
        
        current_score = self.player_scores.get(national_id, 0.0)
        self.player_scores[national_id] = current_score + points

    def add_points_to_player(self, national_id: str, points: float):
        """Alias pour add_score_to_player pour compatibilité"""
        self.add_score_to_player(national_id, points)
        
    def reset_player_score(self, national_id: str):
        """Remet le score d'un joueur à zéro"""
        if national_id in self.player_scores:
            self.player_scores[national_id] = 0.0
            
    def reset_all_scores(self):
        """Remet tous les scores à zéro"""
        for national_id in self.player_scores:
            self.player_scores[national_id] = 0.0
        
    def has_started(self) -> bool:
        """Vérifie si le tournoi a commencé"""
        return len(self.rounds) > 0
        
    def is_finished(self) -> bool:
        """Vérifie si le tournoi est terminé"""
        return (self._is_finished or 
                (self.current_round >= self.number_of_rounds and 
                 self.rounds and self.rounds[-1].is_finished))
                 
    def finish_tournament(self):
        """Marque le tournoi comme terminé"""
        self._is_finished = True
        
    def can_start_next_round(self) -> bool:
        """Vérifie si on peut démarrer le tour suivant"""
        return (not self.is_finished() and 
                len(self.players) >= 2 and 
                len(self.players) % 2 == 0 and 
                self.current_round < self.number_of_rounds and
                (not self.rounds or self.rounds[-1].is_finished))
                
    def start_next_round(self, pairs: List[Tuple[Player, Player]]) -> Round:
        """
        Démarre le tour suivant avec des paires pré-calculées
        
        Args:
            pairs (List[Tuple[Player, Player]]): Paires calculées par le helper
            
        Returns:
            Round: Nouveau tour créé
        """
        if not self.can_start_next_round():
            raise ValueError("Impossible de démarrer le tour suivant")
            
        self.current_round += 1
        round_name = f"Tour {self.current_round}"
        new_round = Round(round_name)
        
        # Créer les matchs à partir des paires
        for player1, player2 in pairs:
            match = Match(player1.national_id, player2.national_id)
            new_round.add_match(match)
            
        self.rounds.append(new_round)
        return new_round
        
    def update_player_scores(self):
        """Met à jour les scores - Logique simple"""
        # Réinitialiser
        self.reset_all_scores()
            
        # Recalculer
        for round_obj in self.rounds:
            for match in round_obj.get_finished_matches():
                self.add_score_to_player(match.player1_national_id, match.player1_score)
                self.add_score_to_player(match.player2_national_id, match.player2_score)
                    
    def get_current_rankings(self) -> List[Player]:
        """Classement actuel - Logique simple"""
        # Trier par score décroissant, puis par nom
        return sorted(
            self.players, 
            key=lambda p: (-self.get_player_score(p.national_id), p.last_name, p.first_name)
        )
        
    def get_final_rankings(self) -> List[Player]:
        """Classement final"""
        if not self.is_finished():
            return self.get_current_rankings()
        self.update_player_scores()
        return self.get_current_rankings()
        
    def has_tie_for_first_place(self) -> bool:
        """
        Vérifie s'il y a égalité au premier rang
        
        Returns:
            bool: True s'il y a égalité, False sinon
        """
        if len(self.players) < 2:
            return False
            
        rankings = self.get_current_rankings()
        if len(rankings) < 2:
            return False
            
        # Vérifier si les deux premiers ont le même score
        first_score = self.get_player_score(rankings[0].national_id)
        second_score = self.get_player_score(rankings[1].national_id)
        
        return abs(first_score - second_score) < 0.001

    def get_tied_players_for_first(self) -> List[Player]:
        """
        Retourne la liste des joueurs à égalité au premier rang
        
        Returns:
            List[Player]: Joueurs à égalité pour la première place
        """
        rankings = self.get_current_rankings()
        if not rankings:
            return []
            
        first_score = self.get_player_score(rankings[0].national_id)
        tied_players = []
        
        for player in rankings:
            if abs(self.get_player_score(player.national_id) - first_score) < 0.001:
                tied_players.append(player)
            else:
                break  # Plus d'égalité
                
        return tied_players if len(tied_players) > 1 else []

    def needs_tiebreaker_round(self) -> bool:
        """
        Détermine si un tour de départage est nécessaire
        
        Returns:
            bool: True si un départage est nécessaire
        """
        return (self.current_round >= self.number_of_rounds and 
                self.has_tie_for_first_place() and
                not self._is_finished)

    def can_create_tiebreaker_pairs(self) -> bool:
        """
        Vérifie si on peut créer des paires pour le départage
        
        Returns:
            bool: True si possible de faire des paires
        """
        tied_players = self.get_tied_players_for_first()
        return len(tied_players) >= 2 and len(tied_players) % 2 == 0
        
    # Méthodes déléguées aux helpers (appelées par les contrôleurs)
    def generate_pairs_for_next_round(self) -> List[Tuple[Player, Player]]:
        """Délègue au TournamentPairingHelper"""
        from utils.tournament_helpers import TournamentPairingHelper
        return TournamentPairingHelper.generate_pairs_for_next_round(self)
        
    def get_tournament_statistics(self) -> Dict:
        """Délègue au TournamentStatisticsHelper"""
        from utils.tournament_helpers import TournamentStatisticsHelper
        return TournamentStatisticsHelper.calculate_tournament_statistics(self)
        
    def validate_tournament_state(self) -> List[str]:
        """Délègue au TournamentValidationHelper"""
        from utils.tournament_helpers import TournamentValidationHelper
        return TournamentValidationHelper.validate_tournament_state(self)
        
    def to_dict(self) -> dict:
        """Sérialisation simple"""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
            "number_of_rounds": self.number_of_rounds,
            "current_round": self.current_round,
            "rounds": [round_obj.to_dict() for round_obj in self.rounds],
            "players": [player.to_dict() for player in self.players],
            "player_scores": self.player_scores,
            "is_finished": self._is_finished
        }
        
    @staticmethod
    def from_dict(data: dict, players_lookup: Dict[str, Player]) -> 'Tournament':
        """Désérialisation simple"""
        # Vérifier les champs requis
        required_fields = ["name", "location", "start_date", "end_date"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Champ requis manquant: {field}")
                
        # Créer le tournoi
        tournament = Tournament(
            name=data["name"],
            location=data["location"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            description=data.get("description", ""),
            number_of_rounds=data.get("number_of_rounds", 4)
        )
        
        # Restaurer l'état
        tournament.id = data.get("id", tournament.id)
        Tournament._id_counter = max(Tournament._id_counter, tournament.id + 1)
        tournament.current_round = data.get("current_round", 0)
        tournament._is_finished = data.get("is_finished", False)
        
        # Reconstruire les joueurs
        for player_data in data.get("players", []):
            if isinstance(player_data, dict) and "national_id" in player_data:
                national_id = player_data["national_id"]
                if national_id in players_lookup:
                    player = players_lookup[national_id]
                    tournament.players.append(player)
                    
        # Restaurer les scores
        tournament.player_scores = data.get("player_scores", {})
        
        # S'assurer que tous les joueurs ont un score
        for player in tournament.players:
            if player.national_id not in tournament.player_scores:
                tournament.player_scores[player.national_id] = 0.0
                
        # Reconstruire les tours
        for round_data in data.get("rounds", []):
            try:
                round_obj = Round.from_dict(round_data)
                tournament.rounds.append(round_obj)
            except Exception as e:
                print(f"Erreur lors du chargement d'un tour: {e}")
                
        return tournament
        
    def __str__(self) -> str:
        """Représentation textuelle"""
        status = "Terminé" if self.is_finished() else ("En cours" if self.has_started() else "Non commencé")
        return f"{self.name} ({self.location}) - {len(self.players)} joueurs - {status}"
        
    def __repr__(self) -> str:
        """Représentation pour le debug"""
        return f"Tournament(id={self.id}, name='{self.name}', players={len(self.players)}, rounds={len(self.rounds)})"