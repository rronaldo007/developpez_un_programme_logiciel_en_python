import re
from models.chess_models import Player


class PlayerController:
    @staticmethod
    def create_player():
        """Crée un nouveau joueur en demandant ses informations à l'utilisateur."""
        print("\n--- Ajouter un nouveau joueur ---")
        first_name = input("Prénom : ").strip()
        last_name = input("Nom de famille : ").strip()
        birthdate = input("Date de naissance (YYYY-MM-DD) : ").strip()
        
        national_id = PlayerController.prompt_national_id()
        
        chess_id = input("ID d'échecs (ex : FRA001) : ").strip()
        
        player = Player(last_name, first_name, birthdate, national_id, chess_id)
        print(f"✅ Joueur créé : {first_name} {last_name} ({chess_id})")
        return player
    
    @staticmethod
    def prompt_national_id():
        """Demande et valide l'ID national d'un joueur."""
        while True:
            national_id = input("ID national (2 lettres + 5 chiffres, ex: AB12345) : ").strip().upper()
            if re.fullmatch(r"[A-Z]{2}\d{5}", national_id):
                return national_id
            print("Format invalide. Veuillez entrer 2 lettres suivies de 5 chiffres.")