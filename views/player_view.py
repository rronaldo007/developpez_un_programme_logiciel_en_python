from controllers.player_controller import PlayerController

class PlayerView:


    def display_player_menu(self):
        """Affiche le menu de gestion des joueurs et gère les choix"""
        
        while True:
            print("\n=== GESTION DES JOUEURS ===")
            print("1. Créer un joueur")
            print("2. Modifier un joueur")
            print("3. Supprimer un joueur")
            print("4. Voir détails d'un joueur")
            print("5. Afficher tous les joueurs")
            print("0. Retour au menu principal")
            
            choice = input("\nVotre choix: ").strip()
            
            if choice == "1":
                self.create_player_interface()
            elif choice == "2":
                self.modify_player_interface()
            elif choice == "3":
                self.delete_player_interface()
            elif choice == "4":
                self.view_player_details_interface()
            elif choice == "5":
                self.view_all_players_interface()
            elif choice == "0":
                break
            else:
                self.show_error("Choix invalide")

    def create_player_interface(self):
        """Interface pour créer un joueur - appelle le contrôleur"""
        print("\n=== CRÉATION D'UN NOUVEAU JOUEUR ===")
        
        try:
            # Collecter les données
            last_name = input("Nom de famille: ").strip()
            if not last_name:
                self.show_error("Le nom de famille ne peut pas être vide.")
                return
            
            first_name = input("Prénom: ").strip()
            if not first_name:
                self.show_error("Le prénom ne peut pas être vide.")
                return
            
            birthdate = input("Date de naissance (YYYY-MM-DD): ").strip()
            if not birthdate:
                self.show_error("La date de naissance ne peut pas être vide.")
                return
            
            national_id = input("Identifiant national (ex: AB12345): ").strip().upper()
            if not national_id:
                self.show_error("L'identifiant national ne peut pas être vide.")
                return
            
            # Appeler le contrôleur
            PlayerController.create_player(last_name, first_name, birthdate, national_id)
            
        except KeyboardInterrupt:
            self.show_error("Création annulée.")

    def modify_player_interface(self):
        """Interface pour modifier un joueur - appelle le contrôleur"""
        print("\n=== MODIFICATION D'UN JOUEUR ===")
        
        try:
            # Demander l'identifiant
            national_id = input("Identifiant national du joueur à modifier: ").strip().upper()
            if not national_id:
                self.show_error("L'identifiant ne peut pas être vide.")
                return
            
            # Vérifier que le joueur existe via le contrôleur
            current_player = PlayerController.get_player(national_id)
            if not current_player:
                self.show_error(f"Aucun joueur trouvé avec l'identifiant {national_id}")
                return
            
            # Afficher les données actuelles
            print(f"\nJoueur actuel: {current_player.first_name} {current_player.last_name}")
            print("Laissez vide pour conserver la valeur actuelle\n")
            
            # Collecter les nouvelles données
            new_last_name = input(f"Nouveau nom [{current_player.last_name}]: ").strip()
            if not new_last_name:
                new_last_name = current_player.last_name
            
            new_first_name = input(f"Nouveau prénom [{current_player.first_name}]: ").strip()
            if not new_first_name:
                new_first_name = current_player.first_name
            
            new_birthdate = input(f"Nouvelle date [{current_player.birthdate}]: ").strip()
            if not new_birthdate:
                new_birthdate = current_player.birthdate
            
            new_national_id = input(f"Nouvel identifiant [{current_player.national_id}]: ").strip().upper()
            if not new_national_id:
                new_national_id = current_player.national_id
            
            # Appeler le contrôleur
            PlayerController.modify_player(national_id, new_last_name, new_first_name, new_birthdate, new_national_id)
            
        except KeyboardInterrupt:
            self.show_error("Modification annulée.")

    def delete_player_interface(self):
        """Interface pour supprimer un joueur - appelle le contrôleur"""
        print("\n=== SUPPRESSION D'UN JOUEUR ===")
        
        try:
            # Demander l'identifiant
            national_id = input("Identifiant national du joueur à supprimer: ").strip().upper()
            if not national_id:
                self.show_error("L'identifiant ne peut pas être vide.")
                return
            
            # Vérifier que le joueur existe via le contrôleur
            player = PlayerController.get_player(national_id)
            if not player:
                self.show_error(f"Aucun joueur trouvé avec l'identifiant {national_id}")
                return
            
            # Afficher les infos et demander confirmation
            print(f"\nJoueur à supprimer: {player.first_name} {player.last_name} ({player.national_id})")
            confirmation = input("Confirmer la suppression ? (oui/non): ").strip().lower()
            
            if confirmation in ['oui', 'o', 'yes', 'y']:
                # Appeler le contrôleur
                PlayerController.delete_player(national_id)
            else:
                self.show_error("Suppression annulée")
                
        except KeyboardInterrupt:
            self.show_error("Suppression annulée.")

    def view_player_details_interface(self):
        """Interface pour voir les détails complets d'un joueur"""
        print("\n=== DÉTAILS COMPLETS D'UN JOUEUR ===")
        
        # Demander l'identifiant
        national_id = input("Identifiant national du joueur: ").strip().upper()
        if not national_id:
            self.show_error("L'identifiant ne peut pas être vide.")
            return
        
        # Récupérer le joueur via le contrôleur
        player = PlayerController.get_player(national_id)
        if not player:
            self.show_error(f"Aucun joueur trouvé avec l'identifiant {national_id}")
            return
        
        # Récupérer les données de tournois, matchs et rounds via le contrôleur
        player_tournaments = PlayerController.get_player_tournaments(national_id)
        player_matches = PlayerController.get_player_matches(national_id)
        player_rounds = PlayerController.get_player_rounds(national_id)
        
        # Afficher les détails complets via le contrôleur
        PlayerController.show_complete_player_details(player, player_tournaments, player_matches, player_rounds)


    def view_all_players_interface(self):
        """Interface pour afficher tous les joueurs"""
        print("\n=== LISTE DE TOUS LES JOUEURS ===")
        
        # Récupérer tous les joueurs via le contrôleur
        players = PlayerController.get_all_players()
        
        if not players:
            print("Aucun joueur enregistré.")
            return
        
        # Trier par nom de famille puis prénom
        sorted_players = sorted(players, key=lambda p: (p.last_name.lower(), p.first_name.lower()))
        
        # Afficher la liste
        self.show_players_list(sorted_players)
            

    def show_player_details(self, player):
        """Affiche les détails complets d'un joueur"""
        print(f"\n--- DÉTAILS DU JOUEUR ---")
        print(f"Nom complet    : {player.first_name} {player.last_name}")
        print(f"Identifiant    : {player.national_id}")
        print(f"Date naissance : {player.birthdate}")
        print(f"Score actuel   : {player.score}")
        print("-" * 30)

    def show_players_list(self, players):
        """Affiche la liste formatée des joueurs"""
        print(f"\nNombre total de joueurs: {len(players)}")
        print("-" * 80)
        print(f"{'Nom':<20} {'Prénom':<15} {'Identifiant':<12} {'Naissance':<12} {'Score':<8}")
        print("-" * 80)
        
        for player in players:
            print(f"{player.last_name:<20} "
                  f"{player.first_name:<15} "
                  f"{player.national_id:<12} "
                  f"{player.birthdate:<12} "
                  f"{player.score:<8.1f}")
        
        print("-" * 80)

    def show_success(self, message):
        """Affiche un message de succès"""
        print(f"SUCCÈS: {message}")

    def show_error(self, message):
        """Affiche un message d'erreur"""
        print(f"ERREUR: {message}")

    def show_player_info(self, player):
        """Affiche les informations d'un joueur (version courte)"""
        print(f"Joueur: {player.first_name} {player.last_name}")
        print(f"Identifiant: {player.national_id}")
        print(f"Date de naissance: {player.birthdate}")
        print(f"Score: {player.score}")