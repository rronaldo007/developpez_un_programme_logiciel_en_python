from typing import List


class BaseView:

    @staticmethod
    def display_title(title: str):
        print(f"\n{'='*60}")
        print(f"  {title.upper()}")
        print(f"{'='*60}")

    @staticmethod
    def display_separator(char: str = "-", length: int = 60):
        print(char * length)

    @staticmethod
    def display_success(message: str):
        print(f"\nSUCCÈS: {message}")

    @staticmethod
    def display_error(message: str):
        print(f"\nERREUR: {message}")

    @staticmethod
    def display_warning(message: str):
        print(f"\nATTENTION: {message}")

    @staticmethod
    def display_info(message: str):
        print(f"\nINFO: {message}")

    @staticmethod
    def get_input(prompt: str) -> str:
        return input(f"{prompt}: ").strip()

    @staticmethod
    def get_input_with_default(prompt: str, default: str) -> str:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default

    @staticmethod
    def get_user_choice(prompt: str = "Votre choix") -> str:
        return input(f"\n{prompt}: ").strip()

    @staticmethod
    def confirm_action(prompt: str) -> bool:
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
        input(f"\n{message}")

    @staticmethod
    def get_choice_from_list(items: List[str], title: str = "SÉLECTION") -> int:
        if not items:
            BaseView.display_info("Aucun élément disponible.")
            return -1

        BaseView.display_title(title)

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
                    BaseView.display_error(
                        f"Choix invalide. Entrez un nombre entre 0 et "
                        f"{len(items)}"
                    )
            except ValueError:
                BaseView.display_error("Veuillez entrer un nombre valide.")
