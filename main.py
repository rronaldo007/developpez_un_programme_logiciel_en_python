from controllers.main_controller import MainController


def main():
    try:
        app = MainController()
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrompue par l'utilisateur.")
        print("Au revoir !")


if __name__ == "__main__":
    main()