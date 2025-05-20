class PlayerView:
    @staticmethod
    def display_player(player):
        """Affiche les informations d'un joueur."""
        print(f"{player.first_name} {player.last_name} | "
              f"ID national : {player.national_id} | "
              f"ID échecs : {player.chess_id} | "
              f"Score : {player.score}")

    @staticmethod
    def list_players_alphabetically(players):
        """Affiche la liste des joueurs par ordre alphabétique."""
        print("\n----- Liste des joueurs par ordre alphabétique -----")
        sorted_players = sorted(players, key=lambda p: (p.last_name, p.first_name))
        for idx, player in enumerate(sorted_players, 1):
            print(f"{idx}. {player.last_name}, {player.first_name} - "
                  f"ID: {player.national_id}, Score: {player.score}")