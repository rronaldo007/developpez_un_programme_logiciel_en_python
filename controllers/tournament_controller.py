import random
import os
import json
from models.chess_models import Tournament, Round, Match, Player


class TournamentController:
    def __init__(self, tournament: Tournament):
        self.tournament = tournament
        self.match_history = set()
        
        # Reconstruire l'historique des matchs à partir des tours existants
        for round_ in self.tournament.rounds:
            for match in round_.matches:
                p1, _ = match.match[0]
                p2, _ = match.match[1]
                pair_key = tuple(sorted((p1.id, p2.id)))
                self.match_history.add(pair_key)

    def generate_pairings(self):
        """
        Génère les appariements pour le prochain tour.
        
        Au premier tour, les joueurs sont appariés aléatoirement.
        Pour les tours suivants, les joueurs sont triés par score et appariés
        en évitant les matchs déjà joués.
        """
        players = self.tournament.players[:]
        
        # Premier tour: appariement aléatoire
        if self.tournament.current_round == 0:
            random.shuffle(players)
            pairs = []
            for i in range(0, len(players), 2):
                if i + 1 < len(players):
                    p1, p2 = players[i], players[i+1]
                    pairs.append((p1, p2))
                    pair_key = tuple(sorted((p1.id, p2.id)))
                    self.match_history.add(pair_key)
            return pairs
        
        # Tours suivants: appariement par score
        else:
            # Trier les joueurs par score
            players.sort(key=lambda p: p.score, reverse=True)
            pairs = []
            used = set()
            
            for i, p1 in enumerate(players):
                if p1.id in used:
                    continue
                    
                # Trouver le prochain joueur disponible qui n'a pas encore joué contre p1
                for j in range(i + 1, len(players)):
                    p2 = players[j]
                    if p2.id in used:
                        continue
                        
                    pair_key = tuple(sorted((p1.id, p2.id)))
                    if pair_key not in self.match_history:
                        pairs.append((p1, p2))
                        self.match_history.add(pair_key)
                        used.update({p1.id, p2.id})
                        break
                
                # Si aucun joueur disponible n'a été trouvé, prendre le premier disponible
                if p1.id not in used:
                    for j in range(i + 1, len(players)):
                        p2 = players[j]
                        if p2.id not in used:
                            pairs.append((p1, p2))
                            pair_key = tuple(sorted((p1.id, p2.id)))
                            self.match_history.add(pair_key)
                            used.update({p1.id, p2.id})
                            break
            
            return pairs

    def create_new_round(self):
        """Crée un nouveau tour avec les appariements générés."""
        round_name = f"Round {self.tournament.current_round + 1}"
        round_ = Round(round_name)
        pairings = self.generate_pairings()

        for p1, p2 in pairings:
            match = Match(p1, p2)
            round_.matches.append(match)

        self.tournament.rounds.append(round_)
        self.tournament.current_round += 1
        return round_

    def end_current_round(self):
        """Termine le tour actuel en enregistrant la date et l'heure de fin."""
        if not self.tournament.rounds:
            return
            
        current_round = self.tournament.rounds[-1]
        current_round.end_round()

    def update_scores(self, match_results):
        """Met à jour les scores des joueurs en fonction des résultats des matchs."""
        if not self.tournament.rounds:
            return
            
        current_round = self.tournament.rounds[-1]
        
        for match in current_round.matches:
            for match_id, s1, s2 in match_results:
                if match.id == match_id:
                    # Mettre à jour les scores dans l'objet Match
                    match.match[0] = (match.match[0][0], s1)
                    match.match[1] = (match.match[1][0], s2)
                    
                    # Mettre à jour les scores des joueurs
                    match.match[0][0].score += s1
                    match.match[1][0].score += s2

    def save_tournament(self, directory="data"):
        """Sauvegarde le tournoi dans un fichier JSON."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        filename = f"{self.tournament.name.replace(' ', '_').lower()}.json"
        filepath = os.path.join(directory, filename)
        
        self.tournament.save_to_file(filepath)
        print(f"✅ Tournoi sauvegardé dans {filepath}")
        return filepath

    @staticmethod
    def load_tournament(filepath: str) -> Tournament:
        """Charge un tournoi à partir d'un fichier JSON."""
        # Vérifier que le fichier existe
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le fichier {filepath} n'existe pas")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Création d'une map des joueurs pour relier les matchs
        players = [Player.from_dict(p) for p in data["players"]]
        player_map = {p.national_id: p for p in players}

        tournament = Tournament(
            data["name"],
            data["location"],
            data["start_date"],
            data["end_date"],
            data.get("description", ""),
            data.get("number_of_rounds", 4)
        )
        tournament.id = data.get("id", 0)
        tournament.players = players
        tournament.current_round = data.get("current_round", 0)

        # Reconstruction des rounds et matchs
        for round_data in data.get("rounds", []):
            round_ = Round(round_data["name"])
            round_.id = round_data.get("id", 0)
            round_.start_time = round_data.get("start_time", "")
            round_.end_time = round_data.get("end_time", None)
            
            for match_data in round_data.get("matches", []):
                try:
                    player1_id = match_data["match"][0]["player"]
                    score1 = match_data["match"][0]["score"]
                    player2_id = match_data["match"][1]["player"]
                    score2 = match_data["match"][1]["score"]
                    
                    p1 = player_map[player1_id]
                    p2 = player_map[player2_id]
                    
                    match = Match(p1, p2, score1, score2)
                    match.id = match_data.get("id", 0)
                    round_.matches.append(match)
                except KeyError as e:
                    print(f"Erreur lors du chargement d'un match: {e}")
                    continue
                    
            tournament.rounds.append(round_)

        return tournament
        
    @staticmethod
    def list_tournaments(directory="data"):
        """Liste tous les tournois sauvegardés dans le répertoire des données."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        files = [f for f in os.listdir(directory) if f.endswith(".json")]
        tournaments = []
        
        for filename in files:
            path = os.path.join(directory, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                tournaments.append((filename, data))
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {filename}: {e}")
                continue
                
        return tournaments

    def generate_reports(self):
        """Génère les rapports demandés pour le tournoi actuel."""
        reports = {
            "tournament_info": {
                "name": self.tournament.name,
                "location": self.tournament.location,
                "dates": f"{self.tournament.start_date} au {self.tournament.end_date}",
                "current_round": f"{self.tournament.current_round}/{self.tournament.number_of_rounds}",
                "description": self.tournament.description
            },
            "players_alphabetical": sorted(
                [p.to_dict() for p in self.tournament.players],
                key=lambda p: (p["last_name"], p["first_name"])
            ),
            "players_by_score": sorted(
                [p.to_dict() for p in self.tournament.players],
                key=lambda p: -p["score"]
            ),
            "rounds": [r.to_dict() for r in self.tournament.rounds]
        }
        
        return reports