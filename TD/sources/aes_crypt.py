from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

backend = default_backend()

def aes_encrypt(data: bytes, key: bytes):
    iv = os.urandom(12)  # Génération d'un IV aléatoire de 12 octets
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=backend)
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(data) + encryptor.finalize()

    return iv, encryptor.tag, ciphertext

def aes_decrypt(iv: bytes, tag: bytes, ciphertext: bytes, key: bytes):
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=backend)
    decryptor = cipher.decryptor()

    return decryptor.update(ciphertext) + decryptor.finalize()

def aes_encrypt_file(filename: str, key: bytes):
    # Charger le fichier
    with open(filename, "rb") as f:
        data = f.read()

    # Chiffrer les données
    iv, tag, ciphertext = aes_encrypt(data, key)

    # Sauvegarder les données chiffrées dans le même fichier
    with open(filename, "wb") as f:
        f.write(iv + tag + ciphertext)

def aes_decrypt_file(filename: str, key: bytes):
    # Charger le fichier chiffré
    with open(filename, "rb") as f:
        encrypted_data = f.read()

    # Récupérer l'IV, le tag et le texte chiffré
    iv = encrypted_data[:12]
    tag = encrypted_data[12:28]
    ciphertext = encrypted_data[28:]

    # Déchiffrer les données
    decrypted_data = aes_decrypt(iv, tag, ciphertext, key)

    # Sauvegarder les données déchiffrées dans le même fichier
    with open(filename, "wb") as f:
        f.write(decrypted_data)