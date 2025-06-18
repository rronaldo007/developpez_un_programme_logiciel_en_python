#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entrée principal de l'application de gestion de tournois d'échecs

Ce module lance l'application en initialisant le contrôleur principal
et en gérant les erreurs globales.
"""

import sys
import os


def main():
    """
    Point d'entrée principal de l'application
    
    Initialise et lance le contrôleur principal avec gestion d'erreurs globale.
    """
    try:
        # Ajouter le répertoire courant au path pour les imports
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import du contrôleur principal
        from controllers.main_controller import MainController
        
        # Initialisation et lancement de l'application
        app = MainController()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nApplication interrompue par l'utilisateur.")
        print("Au revoir !")
        
    except ImportError as e:
        print(f"\nErreur d'importation: {e}")
        print("Vérifiez que tous les modules sont présents.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\nErreur critique: {e}")
        print("L'application va se fermer.")
        sys.exit(1)


if __name__ == "__main__":
    main()