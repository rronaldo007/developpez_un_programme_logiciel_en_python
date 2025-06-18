
from typing import List, Optional


class BaseView:
    """
    Classe de base pour toutes les vues
    Fournit les méthodes communes d'affichage et de saisie

    Responsabilités :
    - Affichage de messages (succès, erreur, info, warning)
    - Saisie utilisateur de base
    - Formatage et séparateurs visuels
    - Confirmations et choix dans les listes
    """

    @staticmethod
    def display_title(title: str):
        """
        Affiche un titre avec séparateurs

        Args:
            title (str): Titre à afficher
        """
        print(f"\n{'='*60}")
        print(f"  {title.upper()}")
        print(f"{'='*60}")

    @staticmethod
    def display_separator(char: str = "-", length: int = 60):
        """
        Affiche un séparateur

        Args:
            char (str): Caractère pour le séparateur
            length (int): Longueur du séparateur
        """
        print(char * length)

    @staticmethod
    def display_success(message: str):
        """
        Affiche un message de succès

        Args:
            message (str): Message de succès
        """
        print(f"\nSUCCÈS: {message}")

    @staticmethod
    def display_error(message: str):
        """
        Affiche un message d'erreur

        Args:
            message (str): Message d'erreur
        """
        print(f"\nERREUR: {message}")

    @staticmethod
    def display_warning(message: str):
        """
        Affiche un avertissement

        Args:
            message (str): Message d'avertissement
        """
        print(f"\nATTENTION: {message}")

    @staticmethod
    def display_info(message: str):
        """
        Affiche une information

        Args:
            message (str): Message d'information
        """
        print(f"\nINFO: {message}")

    @staticmethod
    def get_input(prompt: str) -> str:
        """
        Demande une saisie utilisateur avec prompt

        Args:
            prompt (str): Message à afficher

        Returns:
            str: Saisie de l'utilisateur (nettoyée)
        """
        return input(f"{prompt}: ").strip()

    @staticmethod
    def get_input_with_default(prompt: str, default: str) -> str:
        """
        Demande une saisie avec valeur par défaut

        Args:
            prompt (str): Message à afficher
            default (str): Valeur par défaut

        Returns:
            str: Saisie ou valeur par défaut
        """
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default

    @staticmethod
    def get_user_choice(prompt: str = "Votre choix") -> str:
        """
        Récupère un choix utilisateur

        Args:
            prompt (str): Message pour la saisie

        Returns:
            str: Choix de l'utilisateur
        """
        return input(f"\n{prompt}: ").strip()

    @staticmethod
    def confirm_action(prompt: str) -> bool:
        """
        Demande une confirmation (oui/non)

        Args:
            prompt (str): Question à poser

        Returns:
            bool: True si oui, False si non
        """
        while True:
            response = input(f"\n{prompt} (oui/non): ").strip().lower()
            if response in ['o', 'oui', 'y', 'yes', '1']:
                return True
            elif response in ['n', 'non', 'no', '0']:
                return False
            else:
                print("Répondez par 'o' (oui) ou 'n' (non)")

    @staticmethod
    def wait_for_user(message: str = "Appuyez sur Entrée pour continuer..."):
        """
        Attend que l'utilisateur appuie sur Entrée

        Args:
            message (str): Message à afficher
        """
        input(f"\n{message}")

    @staticmethod
    def get_choice_from_list(items: List[str], title: str = "SÉLECTION") -> int:
        """
        Affiche une liste numérotée et demande un choix

        Args:
            items (List[str]): Liste des éléments à afficher
            title (str): Titre de la liste

        Returns:
            int: Index choisi (0-based) ou -1 pour annuler
        """
        if not items:
            BaseView.display_info("Aucun élément disponible.")
            return -1

        BaseView.display_title(title)

        # Afficher les éléments avec numérotation
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")
        print("0. Annuler")
        BaseView.display_separator()

        while True:
            try:
                choice = int(input("Votre choix: "))
                if choice == 0:
                    return -1
                elif 1 <= choice <= len(items):
                    return choice - 1
                else:
                    BaseView.display_error(f"Choix invalide. Entrez un nombre entre 0 et {len(items)}")
            except ValueError:
                BaseView.display_error("Veuillez entrer un nombre valide.")

    @staticmethod
    def get_integer_input(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
        """
        Demande une saisie d'entier avec validation

        Args:
            prompt (str): Message à afficher
            min_val (Optional[int]): Valeur minimale
            max_val (Optional[int]): Valeur maximale

        Returns:
            Optional[int]: Nombre saisi ou None si annulé
        """
        while True:
            try:
                user_input = input(f"{prompt}: ").strip()
                if user_input.lower() in ['q', 'quit', 'annuler', '']:
                    return None

                value = int(user_input)

                if min_val is not None and value < min_val:
                    BaseView.display_error(f"La valeur doit être supérieure ou égale à {min_val}")
                    continue

                if max_val is not None and value > max_val:
                    BaseView.display_error(f"La valeur doit être inférieure ou égale à {max_val}")
                    continue

                return value

            except ValueError:
                BaseView.display_error("Veuillez entrer un nombre entier valide.")

    @staticmethod
    def get_float_input(prompt: str, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Optional[float]:
        """
        Demande une saisie de nombre décimal avec validation

        Args:
            prompt (str): Message à afficher
            min_val (Optional[float]): Valeur minimale
            max_val (Optional[float]): Valeur maximale

        Returns:
            Optional[float]: Nombre saisi ou None si annulé
        """
        while True:
            try:
                user_input = input(f"{prompt}: ").strip()
                if user_input.lower() in ['q', 'quit', 'annuler', '']:
                    return None

                value = float(user_input)

                if min_val is not None and value < min_val:
                    BaseView.display_error(f"La valeur doit être supérieure ou égale à {min_val}")
                    continue

                if max_val is not None and value > max_val:
                    BaseView.display_error(f"La valeur doit être inférieure ou égale à {max_val}")
                    continue

                return value

            except ValueError:
                BaseView.display_error("Veuillez entrer un nombre décimal valide.")

    @staticmethod
    def display_table(headers: List[str], rows: List[List[str]], title: str = ""):
        """
        Affiche un tableau formaté

        Args:
            headers (List[str]): En-têtes des colonnes
            rows (List[List[str]]): Lignes de données
            title (str): Titre optionnel du tableau
        """
        if title:
            BaseView.display_title(title)

        if not headers or not rows:
            BaseView.display_info("Aucune donnée à afficher.")
            return

        # Calculer les largeurs des colonnes
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Afficher les en-têtes
        header_line = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        print(header_line)
        BaseView.display_separator("-", len(header_line))

        # Afficher les lignes
        for row in rows:
            row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
            print(row_line)

    @staticmethod
    def display_list_with_numbers(items: List[str], title: str = ""):
        """
        Affiche une liste avec numérotation

        Args:
            items (List[str]): Éléments à afficher
            title (str): Titre optionnel
        """
        if title:
            BaseView.display_title(title)

        if not items:
            BaseView.display_info("Aucun élément à afficher.")
            return

        for i, item in enumerate(items, 1):
            print(f"{i:>3}. {item}")

    @staticmethod
    def clear_screen():
        """Efface l'écran (compatible Windows/Unix)"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def display_progress(current: int, total: int, message: str = "Progression"):
        """
        Affiche une barre de progression simple

        Args:
            current (int): Valeur actuelle
            total (int): Valeur totale
            message (str): Message à afficher
        """
        if total <= 0:
            return

        percentage = min(100, int((current / total) * 100))
        bar_length = 30
        filled_length = int((current / total) * bar_length)

        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"\r{message}: [{bar}] {percentage}% ({current}/{total})", end="", flush=True)

        if current >= total:
            print()  # Nouvelle ligne à la fin