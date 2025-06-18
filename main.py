
import sys
import os
from controllers.main_controller import MainController



def main():
    """
    Point d'entrée principal de l'application
    
    Initialise et lance le contrôleur principal avec gestion d'erreurs globale.
    """
    try:
        
        # Initialisation et lancement de l'application
        app = MainController()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nApplication interrompue par l'utilisateur.")
        print("Au revoir !")
        

    except Exception as e:
        print(f"\nErreur critique: {e}")
        print("L'application va se fermer.")
        sys.exit(1)


if __name__ == "__main__":
    main()