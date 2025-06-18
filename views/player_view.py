
from typing import List, Dict, Optional
from .base_view import BaseView
from utils.formatters import format_player_name, format_date_display


class PlayerView(BaseView):
    """
    Vue pour la gestion des joueurs
    Gère l'affichage et la saisie pour toutes les opérations sur les joueurs
    
    Responsabilités :
    - Interface CRUD pour les joueurs
    - Affichage des listes et détails
    - Formulaires de saisie et modification
    - Recherche et sélection
    """
    
    def display_player_menu(self):
        """Affiche le menu de gestion des joueurs"""
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
        """
        Collecte les informations d'un nouveau joueur
        
        Returns:
            Dict[str, str]: Données du joueur saisies
        """
        self.display_title("NOUVEAU JOUEUR")
        
        print("Veuillez saisir les informations du nouveau joueur :")
        print("(Tous les champs sont obligatoires)")
        self.display_separator()
        
        # Collecte des données avec aide contextuelle
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
        
        # Récapitulatif avant validation
        print("\nRécapitulatif des informations saisies :")
        print(f"  Nom complet    : {first_name} {last_name}")
        print(f"  Date naissance : {birthdate}")
        print(f"  Identifiant    : {national_id}")
        
        return player_data
        
    def get_player_modification_info(self, current_player) -> Dict[str, str]:
        """
        Collecte les modifications pour un joueur existant
        
        Args:
            current_player: Joueur à modifier
            
        Returns:
            Dict[str, str]: Nouvelles données du joueur
        """
        self.display_title("MODIFIER JOUEUR")
        
        # Afficher les informations actuelles
        print("Informations actuelles :")
        self.display_player_details(current_player)
        
        print("\nSaisie des nouvelles informations :")
        print("(Laissez vide pour conserver la valeur actuelle)")
        self.display_separator()
        
        # Saisie avec valeurs par défaut
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
        
        # Afficher un récapitulatif des changements
        changes_made = []
        if new_last_name != current_player.last_name:
            changes_made.append(f"Nom: {current_player.last_name} → {new_last_name}")
        if new_first_name != current_player.first_name:
            changes_made.append(f"Prénom: {current_player.first_name} → {new_first_name}")
        if new_birthdate != current_player.birthdate:
            changes_made.append(f"Date: {current_player.birthdate} → {new_birthdate}")
        if new_national_id != current_player.national_id:
            changes_made.append(f"ID: {current_player.national_id} → {new_national_id}")
        
        if changes_made:
            print("\nModifications détectées :")
            for change in changes_made:
                print(f"  • {change}")
        else:
            print("\nAucune modification détectée.")
        
        return modifications
        
    def display_players_list(self, players: List, title: str = "LISTE DES JOUEURS"):
        """
        Affiche la liste des joueurs avec formatage avancé - SANS SCORE
        
        Args:
            players (List): Liste des joueurs à afficher
            title (str): Titre de la liste
        """
        if not players:
            self.display_info("Aucun joueur enregistré.")
            return
            
        self.display_title(title)
        
        print(f"Nombre total de joueurs : {len(players)}")
        self.display_separator()
        
        # En-tête du tableau avec largeurs fixes (sans colonne Score)
        headers = ["#", "Nom", "Prénom", "ID National", "Âge"]
        col_widths = [3, 20, 15, 12, 5]
        
        # Ligne d'en-tête
        header_line = ""
        for i, header in enumerate(headers):
            header_line += header.ljust(col_widths[i])
        print(header_line)
        self.display_separator()
        
        # Lignes de données
        for i, player in enumerate(players, 1):
            # Calcul de l'âge
            age = player.calculate_age() if hasattr(player, 'calculate_age') else None
            age_str = str(age) if age is not None else "N/A"
            
            # Formatage des données avec troncature si nécessaire
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
                  
    def display_player_details(self, player):
        """
        Affiche les détails complets d'un joueur - SANS SCORE
        
        Args:
            player: Joueur à afficher
        """
        self.display_title("DÉTAILS DU JOUEUR")
        
        # Informations de base
        print(f"Nom complet           : {format_player_name(player)}")
        print(f"Nom de famille        : {player.last_name}")
        print(f"Prénom                : {player.first_name}")
        print(f"Date de naissance     : {format_date_display(player.birthdate)}")
        print(f"Identifiant national  : {player.national_id}")
        
        # Informations calculées
        age = player.calculate_age() if hasattr(player, 'calculate_age') else None
        if age is not None:
            print(f"Âge                   : {age} ans")
        else:
            print(f"Âge                   : Non calculable")
            
        # Note : Le score est maintenant géré au niveau des tournois
        print(f"\nNote : Les scores sont affichés dans le contexte des tournois")
        
        # Informations supplémentaires si disponibles
        if hasattr(player, 'tournaments_played'):
            print(f"Tournois joués        : {player.tournaments_played}")
        if hasattr(player, 'total_matches'):
            print(f"Matchs joués          : {player.total_matches}")
        if hasattr(player, 'win_rate'):
            print(f"Taux de victoire      : {player.win_rate:.1f}%")
            
        
    def select_player_from_list(self, players: List, title: str = "SÉLECTIONNER UN JOUEUR") -> Optional:
        """
        Permet de sélectionner un joueur dans une liste avec détails - SANS SCORE
        
        Args:
            players (List): Liste des joueurs
            title (str): Titre de la sélection
            
        Returns:
            Optional: Joueur sélectionné ou None
        """
        if not players:
            self.display_info("Aucun joueur disponible.")
            return None
            
        self.display_title(title)
        
        # Affichage des joueurs avec numérotation et informations utiles
        for i, player in enumerate(players, 1):
            age = player.calculate_age() if hasattr(player, 'calculate_age') else None
            age_str = f" ({age} ans)" if age else ""
            
            print(f"{i:>2}. {format_player_name(player)}{age_str}")
            print(f"     ID: {player.national_id}")
            
        print(f"\n 0. Annuler la sélection")
        self.display_separator()
        
        while True:
            try:
                choice = int(self.get_input("Numéro du joueur"))
                
                if choice == 0:
                    return None
                elif 1 <= choice <= len(players):
                    selected_player = players[choice - 1]
                    print(f"Joueur sélectionné : {format_player_name(selected_player)}")
                    return selected_player
                else:
                    self.display_error(f"Numéro invalide. Entrez un nombre entre 0 et {len(players)}.")
                    
            except ValueError:
                self.display_error("Veuillez entrer un numéro valide.")
                
        
    def confirm_player_deletion(self, player) -> bool:
        """
        Demande confirmation pour la suppression d'un joueur
        
        Args:
            player: Joueur à supprimer
            
        Returns:
            bool: True si confirmé, False sinon
        """
        self.display_title("CONFIRMATION DE SUPPRESSION")
        
        print("ATTENTION : Vous êtes sur le point de supprimer définitivement ce joueur !")
        self.display_separator()
        
        self.display_player_details(player)
        
        self.display_warning("Cette action est IRRÉVERSIBLE !")
        print("Le joueur sera retiré de tous les tournois et statistiques.")
        print("Toutes ses données seront perdues définitivement.")
        
        self.display_separator()
        
        # Double confirmation
        first_confirm = self.confirm_action("Êtes-vous vraiment sûr de vouloir supprimer ce joueur")
        if not first_confirm:
            return False
            
        print(f"\nPour confirmer, tapez le nom complet du joueur :")
        expected_name = format_player_name(player).lower()
        typed_name = self.get_input("Nom complet du joueur").lower()
        
        if typed_name == expected_name:
            final_confirm = self.confirm_action("DERNIÈRE CONFIRMATION - Supprimer définitivement")
            return final_confirm
        else:
            self.display_error("Le nom saisi ne correspond pas. Suppression annulée.")
            return False
            
        