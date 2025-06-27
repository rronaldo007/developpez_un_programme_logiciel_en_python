from typing import List, Dict, Optional
from .base_view import BaseView
from utils.formatters import format_player_name, format_date_display
from models.player import Player


class PlayerView(BaseView):

    def display_player_menu(self):
        self.display_title("GESTION DES JOUEURS")

        print("Gestion complète des joueurs du club :")
        self.display_separator()

        print("1. Ajouter un nouveau joueur")
        print("   - Enregistrer un nouveau membre")
        print()
        print("2. Voir tous les joueurs")
        print("   - Liste complète avec tri")
        print()
        print("3. Modifier un joueur")
        print("   - Mettre à jour les informations")
        print()
        print("4. Supprimer un joueur")
        print("   - Retirer un membre (attention !)")
        print()
        print("0. Retour au menu principal")

        self.display_separator()

    def get_player_info(self) -> Dict[str, str]:
        self.display_title("NOUVEAU JOUEUR")

        print("Veuillez saisir les informations du nouveau joueur :")
        print("(Tous les champs sont obligatoires)")
        self.display_separator()

        print("Nom de famille :")
        print("  Exemple : Dupont, Martin, Dubois")
        last_name = self.get_input("Nom de famille")

        print("\nPrénom :")
        print("  Exemple : Jean, Marie, Pierre")
        first_name = self.get_input("Prénom")

        print("\nDate de naissance :")
        print("  Format requis : YYYY-MM-DD")
        print("  Exemple : 1990-03-15 pour le 15 mars 1990")
        birthdate = self.get_input("Date de naissance")

        print("\nIdentifiant national d'échecs :")
        print("  Format requis : 2 lettres + 5 chiffres")
        print("  Exemple : AB12345, CD67890")
        national_id = self.get_input("Identifiant national")

        player_data = {
            'last_name': last_name,
            'first_name': first_name,
            'birthdate': birthdate,
            'national_id': national_id
        }

        print("\nRécapitulatif des informations saisies :")
        print(f"  Nom complet    : {first_name} {last_name}")
        print(f"  Date naissance : {birthdate}")
        print(f"  Identifiant    : {national_id}")

        return player_data

    def get_player_modification_info(self,
                                     current_player: Player) -> Dict[str, str]:
        self.display_title("MODIFIER JOUEUR")

        print("Informations actuelles :")
        self.display_player_details(current_player)

        print("\nSaisie des nouvelles informations :")
        print("(Laissez vide pour conserver la valeur actuelle)")
        self.display_separator()

        new_last_name = self.get_input_with_default(
            "Nouveau nom de famille",
            current_player.last_name
        )

        new_first_name = self.get_input_with_default(
            "Nouveau prénom",
            current_player.first_name
        )

        new_birthdate = self.get_input_with_default(
            "Nouvelle date de naissance (YYYY-MM-DD)",
            current_player.birthdate
        )

        new_national_id = self.get_input_with_default(
            "Nouvel identifiant national",
            current_player.national_id
        )

        modifications = {
            'last_name': new_last_name,
            'first_name': new_first_name,
            'birthdate': new_birthdate,
            'national_id': new_national_id
        }

        changes_made = []
        if new_last_name != current_player.last_name:
            changes_made.append(
                f"Nom: {current_player.last_name} → {new_last_name}"
            )
        if new_first_name != current_player.first_name:
            changes_made.append(
                f"Prénom: {current_player.first_name} → {new_first_name}"
            )
        if new_birthdate != current_player.birthdate:
            changes_made.append(
                f"Date: {current_player.birthdate} → {new_birthdate}"
            )
        if new_national_id != current_player.national_id:
            changes_made.append(
                f"ID: {current_player.national_id} → {new_national_id}"
            )

        if changes_made:
            print("\nModifications détectées :")
            for change in changes_made:
                print(f"  • {change}")
        else:
            print("\nAucune modification détectée.")

        return modifications

    def display_players_list(self, players: List[Player],
                             title: str = "LISTE DES JOUEURS"):
        if not players:
            self.display_info("Aucun joueur enregistré.")
            return

        self.display_title(title)

        print(f"Nombre total de joueurs : {len(players)}")
        self.display_separator()

        headers = ["#", "Nom", "Prénom", "ID National", "Âge"]
        col_widths = [3, 20, 15, 12, 5]

        header_line = ""
        for i, header in enumerate(headers):
            header_line += header.ljust(col_widths[i])
        print(header_line)
        self.display_separator()

        for i, player in enumerate(players, 1):
            age = None
            if hasattr(player, 'calculate_age'):
                age = player.calculate_age()
            age_str = str(age) if age is not None else "N/A"

            num = str(i).ljust(col_widths[0])

            last_name = player.last_name
            if len(last_name) > col_widths[1] - 1:
                last_name = last_name[:col_widths[1] - 4] + "..."
            last_name = last_name.ljust(col_widths[1])

            first_name = player.first_name
            if len(first_name) > col_widths[2] - 1:
                first_name = first_name[:col_widths[2] - 4] + "..."
            first_name = first_name.ljust(col_widths[2])

            national_id = player.national_id.ljust(col_widths[3])
            age_col = age_str.ljust(col_widths[4])

            print(f"{num}{last_name}{first_name}{national_id}{age_col}")

        self.display_separator()
        print(f"Total : {len(players)} joueur(s)")

    def display_player_details(self, player: Player):
        self.display_title("DÉTAILS DU JOUEUR")

        print(f"Nom complet           : {format_player_name(player)}")
        print(f"Nom de famille        : {player.last_name}")
        print(f"Prénom                : {player.first_name}")
        print(f"Date de naissance     : {format_date_display(player.birthdate)}")
        print(f"Identifiant national  : {player.national_id}")

        age = None
        if hasattr(player, 'calculate_age'):
            age = player.calculate_age()
        if age is not None:
            print(f"Âge                   : {age} ans")
        else:
            print("Âge                   : Non calculable")

        print("\nNote : Les scores sont affichés dans le contexte des tournois")

        if hasattr(player, 'tournaments_played'):
            print(f"Tournois joués        : {player.tournaments_played}")
        if hasattr(player, 'total_matches'):
            print(f"Matchs joués          : {player.total_matches}")
        if hasattr(player, 'win_rate'):
            print(f"Taux de victoire      : {player.win_rate:.1f}%")

    def select_player_from_list(self, players: List,
                                title: str = "SÉLECTIONNER UN JOUEUR") -> Optional[Player]:
        if not players:
            self.display_info("Aucun joueur disponible.")
            return None

        self.display_title(title)

        for i, player in enumerate(players, 1):
            age = None
            if hasattr(player, 'calculate_age'):
                age = player.calculate_age()
            age_str = f" ({age} ans)" if age else ""

            print(f"{i:>2}. {format_player_name(player)}{age_str}")
            print(f"     ID: {player.national_id}")

        print("\n 0. Annuler la sélection")
        self.display_separator()

        while True:
            try:
                choice = int(self.get_input("Numéro du joueur"))

                if choice == 0:
                    return None
                elif 1 <= choice <= len(players):
                    selected_player = players[choice - 1]
                    print(
                        f"Joueur sélectionné : "
                        f"{format_player_name(selected_player)}"
                    )
                    return selected_player
                else:
                    self.display_error(
                        f"Numéro invalide. Entrez un nombre entre 0 et "
                        f"{len(players)}."
                    )

            except ValueError:
                self.display_error("Veuillez entrer un numéro valide.")

    def confirm_player_deletion(self, player) -> bool:
        self.display_title("CONFIRMATION DE SUPPRESSION")

        print(
            "ATTENTION : Vous êtes sur le point de supprimer "
            "définitivement ce joueur !"
        )
        self.display_separator()

        self.display_player_details(player)

        self.display_warning("Cette action est IRRÉVERSIBLE !")
        print("Le joueur sera retiré de tous les tournois et statistiques.")
        print("Toutes ses données seront perdues définitivement.")

        self.display_separator()

        first_confirm = self.confirm_action(
            "Êtes-vous vraiment sûr de vouloir supprimer ce joueur"
        )
        if not first_confirm:
            return False

        print("\nPour confirmer, tapez le nom complet du joueur :")
        expected_name = format_player_name(player).lower()
        typed_name = self.get_input("Nom complet du joueur").lower()

        if typed_name == expected_name:
            final_confirm = self.confirm_action(
                "DERNIÈRE CONFIRMATION - Supprimer définitivement"
            )
            return final_confirm
        else:
            self.display_error(
                "Le nom saisi ne correspond pas. Suppression annulée."
            )
            return False
