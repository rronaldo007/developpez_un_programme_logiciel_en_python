
from typing import Optional
from utils.validators import validate_chess_id, validate_name, validate_date_format
from utils.date_utils import calculate_age


class Player:
    """
    Modèle représentant un joueur d'échecs - Version épurée
    
    Responsabilités LIMITÉES :
    - Stockage des données permanentes du joueur
    - Validation essentielle à la création
    - Sérialisation/désérialisation
    
    Note: Le score est géré par le Tournament, pas par le Player
    """
    
    def __init__(self, last_name: str, first_name: str, birthdate: str, national_id: str):
        """
        Initialise un nouveau joueur avec validation
        
        Args:
            last_name (str): Nom de famille
            first_name (str): Prénom
            birthdate (str): Date de naissance (YYYY-MM-DD)
            national_id (str): Identifiant national (AB12345)
            
        Raises:
            ValueError: Si les données sont invalides
        """
        # Validation via utils
        self._validate_data(last_name, first_name, birthdate, national_id)
        
        # Assignation des données nettoyées
        self.last_name = last_name.strip().title()
        self.first_name = first_name.strip().title()
        self.birthdate = birthdate.strip()
        self.national_id = national_id.strip().upper()
        
    def _validate_data(self, last_name: str, first_name: str, birthdate: str, national_id: str):
        """Validation des données via les utilitaires"""
        if not validate_name(last_name):
            raise ValueError("Nom de famille invalide")
        if not validate_name(first_name):
            raise ValueError("Prénom invalide")
        if not validate_date_format(birthdate):
            raise ValueError("Date de naissance invalide (format: YYYY-MM-DD)")
        if not validate_chess_id(national_id):
            raise ValueError("Identifiant national invalide (format: AB12345)")
            
    def get_full_name(self) -> str:
        """Retourne le nom complet du joueur"""
        return f"{self.first_name} {self.last_name}"
        
    def calculate_age(self, reference_date: Optional[str] = None) -> Optional[int]:
        """
        Calcule l'âge du joueur via les utilitaires
        
        Args:
            reference_date (Optional[str]): Date de référence
            
        Returns:
            Optional[int]: Âge en années ou None si erreur
        """
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
        """
        Désérialisation simple
        
        Args:
            data (dict): Données du joueur
            
        Returns:
            Player: Instance de joueur créée
        """
        # Vérifier les champs requis
        required_fields = ["last_name", "first_name", "birthdate", "national_id"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Champ requis manquant: {field}")
                
        # Créer le joueur
        player = Player(
            last_name=data["last_name"],
            first_name=data["first_name"],
            birthdate=data["birthdate"],
            national_id=data["national_id"]
        )
        
        return player
        
    def __str__(self) -> str:
        """Représentation textuelle"""
        return f"{self.get_full_name()} ({self.national_id})"
        
    def __repr__(self) -> str:
        """Représentation pour le debug"""
        return f"Player('{self.last_name}', '{self.first_name}', '{self.birthdate}', '{self.national_id}')"
        
    def __eq__(self, other) -> bool:
        """Égalité basée sur l'identifiant national"""
        if not isinstance(other, Player):
            return False
        return self.national_id == other.national_id
        
    def __hash__(self) -> int:
        """Hash basé sur l'identifiant national"""
        return hash(self.national_id)