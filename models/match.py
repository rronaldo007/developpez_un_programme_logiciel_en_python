class Match:
    """
    Modèle représentant un match d'échecs entre deux joueurs
    """
    
    def __init__(self, player1_national_id: str, player2_national_id: str):
        self.player1_national_id = player1_national_id
        self.player2_national_id = player2_national_id
        self.player1_score = 0.0
        self.player2_score = 0.0
        self.is_finished = False

    def set_result(self, player1_score: float, player2_score: float):
        """
        Définit le résultat du match
        
        Args:
            player1_score (float): Score du joueur 1 (0, 0.5 ou 1)
            player2_score (float): Score du joueur 2 (0, 0.5 ou 1)
        """
        if player1_score + player2_score != 1.0:
            raise ValueError("La somme des scores doit être égale à 1.0")
        
        if player1_score not in [0.0, 0.5, 1.0] or player2_score not in [0.0, 0.5, 1.0]:
            raise ValueError("Les scores doivent être 0, 0.5 ou 1")
        
        self.player1_score = player1_score
        self.player2_score = player2_score
        self.is_finished = True

    def get_match_tuple(self):
        """
        Retourne le match sous forme de tuple comme spécifié dans les exigences
        Format: ((player1, score1), (player2, score2))
        
        Returns:
            tuple: Tuple contenant deux listes [joueur, score]
        """
        return (
            [self.player1_national_id, self.player1_score],
            [self.player2_national_id, self.player2_score]
        )

    def to_dict(self):
        """Convertit le match en dictionnaire pour la sérialisation JSON"""
        return {
            "player1_national_id": self.player1_national_id,
            "player2_national_id": self.player2_national_id,
            "player1_score": self.player1_score,
            "player2_score": self.player2_score,
            "is_finished": self.is_finished
        }

    @staticmethod
    def from_dict(data):
        """Crée un match à partir d'un dictionnaire"""
        match = Match(
            data["player1_national_id"],
            data["player2_national_id"]
        )
        match.player1_score = data.get("player1_score", 0.0)
        match.player2_score = data.get("player2_score", 0.0)
        match.is_finished = data.get("is_finished", False)
        return match


