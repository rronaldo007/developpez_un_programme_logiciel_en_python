from controllers.tournament_controller import TournamentController
from controllers.player_controller import PlayerController


class TournamentView:
    """
    Vue pour la gestion des tournois - MVC Pattern
    """

    def display_tournament_menu(self):
        """Affiche le menu de gestion des tournois"""
        while True:
            print("\n=== GESTION DES TOURNOIS ===")
            print("1. Créer un tournoi")
            print("2. Modifier un tournoi")
            print("3. Afficher tous les tournois")
            print("4. Afficher détails d'un tournoi")
            print("5. Gérer un tournoi")
            print("0. Retour au menu principal")
            
            choice = input("\nVotre choix: ").strip()
            
            if choice == "1":
                self.create_tournament_interface()
            elif choice == "2":
                self.modify_tournament_interface()
            elif choice == "3":
                self.show_all_tournaments_interface()
            elif choice == "4":
                self.show_tournament_details_only_interface()
            elif choice == "5":
                self.show_tournament_details_interface()
            elif choice == "0":
                break
            else:
                self.show_error("Choix invalide")

    def show_tournament_details_only_interface(self):
        """Interface pour voir les détails d'un tournoi (consultation seulement)"""
        print("\n=== DÉTAILS D'UN TOURNOI ===")
        
        try:
            # Afficher la liste des tournois
            tournaments = TournamentController.get_all_tournaments()
            if not tournaments:
                print("Aucun tournoi disponible.")
                return
            
            self.show_tournaments_list(tournaments)
            
            # Demander l'ID du tournoi
            tournament_id = input("\nID du tournoi: ").strip()
            if not tournament_id:
                return
            
            try:
                tournament_id = int(tournament_id)
            except ValueError:
                self.show_error("L'ID doit être un nombre.")
                return
            
            # Afficher les détails seulement (pas de menu d'actions)
            TournamentController.show_tournament_details(tournament_id)
            input("\nAppuyez sur Entrée pour continuer...")
            
        except KeyboardInterrupt:
            print("\nConsultation annulée.")

    def create_tournament_interface(self):
        """Interface pour créer un tournoi"""
        print("\n=== CRÉATION D'UN NOUVEAU TOURNOI ===")
        
        try:
            # Collecter les données
            name = input("Nom du tournoi: ").strip()
            if not name:
                self.show_error("Le nom du tournoi ne peut pas être vide.")
                return
            
            location = input("Lieu: ").strip()
            if not location:
                self.show_error("Le lieu ne peut pas être vide.")
                return
            
            start_date = input("Date de début (YYYY-MM-DD): ").strip()
            if not start_date:
                self.show_error("La date de début ne peut pas être vide.")
                return
            
            end_date = input("Date de fin (YYYY-MM-DD): ").strip()
            if not end_date:
                self.show_error("La date de fin ne peut pas être vide.")
                return
            
            description = input("Description (optionnel): ").strip()
            
            number_of_rounds = input("Nombre de rounds [4]: ").strip()
            if not number_of_rounds:
                number_of_rounds = 4
            else:
                try:
                    number_of_rounds = int(number_of_rounds)
                except ValueError:
                    self.show_error("Le nombre de rounds doit être un nombre.")
                    return
            
            # Appeler le contrôleur
            TournamentController.create_tournament(name, location, start_date, end_date, description, number_of_rounds)
            
        except KeyboardInterrupt:
            self.show_error("Création annulée.")

    def modify_tournament_interface(self):
        """Interface pour modifier un tournoi"""
        print("\n=== MODIFICATION D'UN TOURNOI ===")
        
        try:
            # Afficher la liste des tournois
            tournaments = TournamentController.get_all_tournaments()
            if not tournaments:
                print("Aucun tournoi disponible.")
                return
            
            self.show_tournaments_list(tournaments)
            
            # Demander l'ID du tournoi
            tournament_id = input("\nID du tournoi à modifier: ").strip()
            if not tournament_id:
                self.show_error("L'ID ne peut pas être vide.")
                return
            
            try:
                tournament_id = int(tournament_id)
            except ValueError:
                self.show_error("L'ID doit être un nombre.")
                return
            
            # Récupérer le tournoi
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament:
                self.show_error(f"Aucun tournoi trouvé avec l'ID {tournament_id}")
                return
            
            # Afficher les données actuelles
            print(f"\nTournoi actuel: {tournament.name}")
            print("Laissez vide pour conserver la valeur actuelle\n")
            
            # Collecter les nouvelles données
            new_name = input(f"Nouveau nom [{tournament.name}]: ").strip()
            if not new_name:
                new_name = tournament.name
            
            new_location = input(f"Nouveau lieu [{tournament.location}]: ").strip()
            if not new_location:
                new_location = tournament.location
            
            new_start_date = input(f"Nouvelle date début [{tournament.start_date}]: ").strip()
            if not new_start_date:
                new_start_date = tournament.start_date
            
            new_end_date = input(f"Nouvelle date fin [{tournament.end_date}]: ").strip()
            if not new_end_date:
                new_end_date = tournament.end_date
            
            new_description = input(f"Nouvelle description [{tournament.description}]: ").strip()
            if not new_description:
                new_description = tournament.description
            
            # Appeler le contrôleur
            TournamentController.modify_tournament(tournament_id, new_name, new_location, new_start_date, new_end_date, new_description)
            
        except KeyboardInterrupt:
            self.show_error("Modification annulée.")

    def show_all_tournaments_interface(self):
        """Interface pour afficher tous les tournois"""
        print("\n=== LISTE DE TOUS LES TOURNOIS ===")
        
        tournaments = TournamentController.get_all_tournaments()
        if not tournaments:
            print("Aucun tournoi disponible.")
            return
        
        self.show_tournaments_list(tournaments)

    def show_tournament_details_interface(self):
        """Interface pour gérer un tournoi spécifique"""
        print("\n=== GÉRER UN TOURNOI ===")
        
        try:
            # Afficher la liste des tournois
            tournaments = TournamentController.get_all_tournaments()
            if not tournaments:
                print("Aucun tournoi disponible.")
                return
            
            self.show_tournaments_list(tournaments)
            
            # Demander l'ID du tournoi
            tournament_id = input("\nID du tournoi: ").strip()
            if not tournament_id:
                self.show_error("L'ID ne peut pas être vide.")
                return
            
            try:
                tournament_id = int(tournament_id)
            except ValueError:
                self.show_error("L'ID doit être un nombre.")
                return
            
            # Vérifier que le tournoi existe
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament:
                self.show_error(f"Tournoi avec l'ID {tournament_id} non trouvé")
                return
                
            # Afficher les détails du tournoi
            TournamentController.show_tournament_details(tournament_id)
            
            # Menu d'actions pour ce tournoi spécifique
            self.show_tournament_actions_menu(tournament_id)
            
        except KeyboardInterrupt:
            print("\nGestion annulée.")

    def show_tournament_actions_menu(self, tournament_id):
        """Affiche le menu d'actions pour un tournoi spécifique"""
        while True:
            # Vérifier l'état du tournoi pour afficher le bon menu
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament:
                self.show_error(f"Tournoi avec l'ID {tournament_id} non trouvé")
                break
            
            print(f"\n=== ACTIONS POUR LE TOURNOI (ID: {tournament_id}) ===")
            print("1. Ajouter un joueur")
            
            # Afficher l'option appropriée selon l'état du tournoi
            if tournament.rounds and not tournament.rounds[-1].is_finished:
                # Il y a un round en cours
                print("2. Continuer le round en cours")
            elif tournament.current_round < tournament.number_of_rounds:
                # Pas de round en cours, on peut en démarrer un nouveau
                print("2. Démarrer un nouveau round")
            else:
                # Tournoi terminé
                print("2. Tournoi terminé")
            
            print("3. Voir matchs et rounds")
            print("4. Voir détails du tournoi")
            print("0. Retour au menu tournois")
            
            choice = input("\nVotre choix: ").strip()
            
            if choice == "1":
                self.add_player_to_specific_tournament(tournament_id)
            elif choice == "2":
                if tournament.rounds and not tournament.rounds[-1].is_finished:
                    # Continuer le round en cours
                    self.continue_current_round_interface(tournament_id)
                elif tournament.current_round < tournament.number_of_rounds:
                    # Démarrer un nouveau round
                    self.start_round_with_results_interface(tournament_id)
                else:
                    print("Le tournoi est terminé. Aucun nouveau round ne peut être démarré.")
            elif choice == "3":
                self.show_matches_and_rounds(tournament_id)
            elif choice == "4":
                TournamentController.show_tournament_details(tournament_id)
            elif choice == "0":
                break
            else:
                self.show_error("Choix invalide")

    def continue_current_round_interface(self, tournament_id):
        """Interface pour continuer un round en cours"""
        print("\n=== CONTINUER LE ROUND EN COURS ===")
        
        try:
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament or not tournament.rounds:
                self.show_error("Aucun round en cours")
                return
            
            current_round = tournament.rounds[-1]
            if current_round.is_finished:
                self.show_error("Le round actuel est déjà terminé")
                return
            
            print(f"Round en cours: {current_round.name}")
            
            # Afficher l'état des matchs
            finished_matches = sum(1 for match in current_round.matches if match.is_finished)
            total_matches = len(current_round.matches)
            print(f"Progression: {finished_matches}/{total_matches} matchs terminés")
            
            if finished_matches == total_matches:
                print("Tous les matchs sont terminés. Le round peut être clôturé.")
                choice = input("Clôturer le round ? (oui/non): ").strip().lower()
                if choice in ['oui', 'o', 'yes', 'y']:
                    current_round.end_round()
                    TournamentController._save_tournament(tournament, tournament_id)
                    print(f"SUCCÈS: {current_round.name} terminé!")
                return
            
            while True:
                print(f"\n=== {current_round.name.upper()} ===")
                print("1. Entrer les résultats des matchs")
                print("2. Voir l'état des matchs")
                print("0. Retour au menu du tournoi")
                
                choice = input("\nVotre choix: ").strip()
                
                if choice == "1":
                    TournamentController.enter_match_results(tournament_id)
                    break
                elif choice == "2":
                    self.show_current_round_status(tournament_id)
                elif choice == "0":
                    break
                else:
                    self.show_error("Choix invalide")
                    
        except Exception as e:
            self.show_error(f"Erreur: {e}")

    def show_current_round_status(self, tournament_id):
        """Affiche l'état du round en cours"""
        try:
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament or not tournament.rounds:
                self.show_error("Aucun round trouvé")
                return
            
            current_round = tournament.rounds[-1]
            print(f"\n=== ÉTAT DU {current_round.name.upper()} ===")
            print(f"Début: {current_round.start_time}")
            if current_round.end_time:
                print(f"Fin: {current_round.end_time}")
            
            print("-" * 70)
            print(f"{'Match':<8} {'Joueur 1':<20} {'Score':<6} {'Joueur 2':<20} {'Score':<6} {'Statut':<8}")
            print("-" * 70)
            
            for i, match in enumerate(current_round.matches, 1):
                player1 = PlayerController.get_player(match.player1_national_id)
                player2 = PlayerController.get_player(match.player2_national_id)
                
                p1_name = f"{player1.first_name} {player1.last_name}" if player1 else match.player1_national_id
                p2_name = f"{player2.first_name} {player2.last_name}" if player2 else match.player2_national_id
                
                status = "Terminé" if match.is_finished else "En cours"
                
                print(f"{i:<8} "
                      f"{p1_name:<20} "
                      f"{match.player1_score:<6} "
                      f"{p2_name:<20} "
                      f"{match.player2_score:<6} "
                      f"{status:<8}")
            
            print("-" * 70)
            
            finished = sum(1 for match in current_round.matches if match.is_finished)
            total = len(current_round.matches)
            print(f"Progression: {finished}/{total} matchs terminés")
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        except Exception as e:
            self.show_error(f"Erreur lors de l'affichage: {e}")

    def start_round_with_results_interface(self, tournament_id):
        """Interface pour démarrer un round et entrer les résultats"""
        print("\n=== DÉMARRER UN ROUND ===")
        
        # D'abord, démarrer le round
        if TournamentController.start_round(tournament_id):
            # Si le round a démarré avec succès, proposer d'entrer les résultats
            print("\nLe round a été créé avec succès!")
            
            while True:
                print("\nQue souhaitez-vous faire maintenant ?")
                print("1. Entrer les résultats des matchs")
                print("2. Voir matchs et rounds")
                print("0. Retour au menu du tournoi")
                
                choice = input("\nVotre choix: ").strip()
                
                if choice == "1":
                    TournamentController.enter_match_results(tournament_id)
                    break
                elif choice == "2":
                    self.show_matches_and_rounds(tournament_id)
                elif choice == "0":
                    break
                else:
                    self.show_error("Choix invalide")

    def show_matches_and_rounds(self, tournament_id):
        """Affiche les matchs et rounds du tournoi"""
        try:
            tournament = TournamentController.get_tournament(tournament_id)
            if not tournament:
                self.show_error(f"Tournoi avec l'ID {tournament_id} non trouvé")
                return
            
            if not tournament.rounds:
                print("Aucun round joué dans ce tournoi.")
                return
            
            print(f"\n=== MATCHS ET ROUNDS: {tournament.name} ===")
            
            for round_obj in tournament.rounds:
                status = "Terminé" if round_obj.is_finished else "En cours"
                print(f"\n{round_obj.name} [{status}]")
                print(f"Début: {round_obj.start_time}")
                if round_obj.end_time:
                    print(f"Fin: {round_obj.end_time}")
                
                print("-" * 60)
                print(f"{'Match':<8} {'Joueur 1':<20} {'Score':<6} {'Joueur 2':<20} {'Score':<6}")
                print("-" * 60)
                
                for i, match in enumerate(round_obj.matches, 1):
                    player1 = PlayerController.get_player(match.player1_national_id)
                    player2 = PlayerController.get_player(match.player2_national_id)
                    
                    p1_name = f"{player1.first_name} {player1.last_name}" if player1 else match.player1_national_id
                    p2_name = f"{player2.first_name} {player2.last_name}" if player2 else match.player2_national_id
                    
                    print(f"{i:<8} "
                          f"{p1_name:<20} "
                          f"{match.player1_score:<6} "
                          f"{p2_name:<20} "
                          f"{match.player2_score:<6}")
                
                print("-" * 60)
            
            input("\nAppuyez sur Entrée pour continuer...")
            
        except Exception as e:
            self.show_error(f"Erreur lors de l'affichage: {e}")

    def add_player_to_specific_tournament(self, tournament_id):
        """Ajoute un joueur à un tournoi spécifique"""
        print("\n=== AJOUTER JOUEUR AU TOURNOI ===")
        
        while True:
            print("\n1. Choisir un joueur existant")
            print("2. Créer un nouveau joueur")
            print("0. Annuler")
            
            choice = input("\nVotre choix: ").strip()
            
            if choice == "1":
                self.add_existing_player_to_tournament(tournament_id)
                break
            elif choice == "2":
                self.create_and_add_player_to_tournament(tournament_id)
                break
            elif choice == "0":
                break
            else:
                self.show_error("Choix invalide")

    def add_existing_player_to_tournament(self, tournament_id):
        """Ajoute un joueur existant au tournoi"""
        try:
            from controllers.player_controller import PlayerController
            
            # Afficher tous les joueurs disponibles
            all_players = PlayerController.get_all_players()
            if not all_players:
                print("Aucun joueur disponible. Créez d'abord des joueurs.")
                return
            
            # Récupérer le tournoi pour voir qui est déjà inscrit
            tournament = TournamentController.get_tournament(tournament_id)
            inscribed_ids = {p.national_id for p in tournament.players} if tournament else set()
            
            # Filtrer les joueurs non inscrits
            available_players = [p for p in all_players if p.national_id not in inscribed_ids]
            
            if not available_players:
                print("Tous les joueurs sont déjà inscrits dans ce tournoi.")
                return
            
            print(f"\n=== JOUEURS DISPONIBLES ({len(available_players)}) ===")
            print("-" * 80)
            print(f"{'#':<3} {'Nom':<20} {'Prénom':<15} {'Identifiant':<12} {'Naissance':<12}")
            print("-" * 80)
            
            for i, player in enumerate(available_players, 1):
                print(f"{i:<3} "
                      f"{player.last_name:<20} "
                      f"{player.first_name:<15} "
                      f"{player.national_id:<12} "
                      f"{player.birthdate:<12}")
            
            print("-" * 80)
            
            # Demander le choix
            while True:
                choice = input(f"\nChoisissez un joueur (1-{len(available_players)}) ou 0 pour annuler: ").strip()
                
                if choice == "0":
                    return
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(available_players):
                        selected_player = available_players[choice_num - 1]
                        
                        # Confirmer le choix
                        print(f"\nJoueur sélectionné: {selected_player.first_name} {selected_player.last_name} ({selected_player.national_id})")
                        confirm = input("Confirmer l'ajout ? (oui/non): ").strip().lower()
                        
                        if confirm in ['oui', 'o', 'yes', 'y']:
                            # Appeler le contrôleur
                            TournamentController.add_player_to_tournament(tournament_id, selected_player.national_id)
                        else:
                            print("Ajout annulé.")
                        break
                    else:
                        print(f"Veuillez entrer un nombre entre 1 et {len(available_players)}")
                except ValueError:
                    print("Veuillez entrer un nombre valide")
            
        except KeyboardInterrupt:
            self.show_error("Ajout annulé.")

    def create_and_add_player_to_tournament(self, tournament_id):
        """Crée un nouveau joueur et l'ajoute au tournoi"""
        print("\n=== CRÉER UN NOUVEAU JOUEUR ===")
        
        try:
            from controllers.player_controller import PlayerController
            
            # Collecter les données du nouveau joueur
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
            
            # Créer le joueur
            if PlayerController.create_player(last_name, first_name, birthdate, national_id):
                # Si la création réussit, ajouter au tournoi
                print(f"\nAjout du joueur {first_name} {last_name} au tournoi...")
                TournamentController.add_player_to_tournament(tournament_id, national_id)
            
        except KeyboardInterrupt:
            self.show_error("Création annulée.")

    def add_player_to_tournament_interface(self):
        """Interface pour ajouter un joueur à un tournoi - SUPPRIMÉE du menu principal"""
        pass

    def start_round_interface(self):
        """Interface pour démarrer un round - SUPPRIMÉE du menu principal"""
        pass

    def enter_match_results_interface(self):
        """Interface pour entrer les résultats des matchs - SUPPRIMÉE du menu principal"""
        pass

    def show_tournaments_list(self, tournaments):
        """Affiche la liste formatée des tournois"""
        print(f"\nNombre total de tournois: {len(tournaments)}")
        print("-" * 100)
        print(f"{'ID':<5} {'Nom':<25} {'Lieu':<20} {'Date début':<12} {'Round':<8} {'Joueurs':<8}")
        print("-" * 100)
        
        for tournament in tournaments:
            print(f"{tournament.id:<5} "
                  f"{tournament.name:<25} "
                  f"{tournament.location:<20} "
                  f"{tournament.start_date:<12} "
                  f"{tournament.current_round}/{tournament.number_of_rounds:<7} "
                  f"{len(tournament.players):<8}")
        
        print("-" * 100)

    def show_success(self, message):
        """Affiche un message de succès"""
        print(f"SUCCÈS: {message}")

    def show_error(self, message):
        """Affiche un message d'erreur"""
        print(f"ERREUR: {message}")
