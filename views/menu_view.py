from .base_view import BaseView


class MenuView(BaseView):

    def display_main_menu(self):
        self.display_title("CENTRE D'ÉCHECS - MENU PRINCIPAL")

        print("Bienvenue dans le système de gestion de tournois d'échecs !")
        print("Sélectionnez une option pour commencer :")
        self.display_separator()

        print("1. Gestion des joueurs")
        print("   - Ajouter, modifier, supprimer des joueurs")
        print("   - Consulter les profils et statistiques")
        print()
        print("2. Gestion des tournois")
        print("   - Créer et organiser des tournois")
        print("   - Gérer les tours et saisir les résultats")
        print()
        print("3. Rapports et statistiques")
        print("   - Consulter les analyses de performance")
        print("   - Générer des rapports détaillés")
        print()
        print("0. Quitter l'application")

        self.display_separator()