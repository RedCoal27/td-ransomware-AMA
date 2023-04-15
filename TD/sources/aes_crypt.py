from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Utilisation du backend par défaut pour les opérations cryptographiques
BACKEND = default_backend()

def aes_encrypt(data: bytes, key: bytes):
    # Génère un vecteur d'initialisation (IV) aléatoire de 12 octets
    iv = os.urandom(12)
    # Crée un chiffrement AES-GCM avec la clé donnée et l'IV
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=BACKEND)
    encryptor = cipher.encryptor()

    # Chiffre les données et finalise le chiffrement
    ciphertext = encryptor.update(data) + encryptor.finalize()

    # Retourne l'IV, le tag d'authentification et le texte chiffré
    return iv, encryptor.tag, ciphertext

def aes_decrypt(iv: bytes, tag: bytes, ciphertext: bytes, key: bytes):
    # Crée un déchiffrement AES-GCM avec la clé donnée, l'IV et le tag
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=BACKEND)
    decryptor = cipher.decryptor()

    # Déchiffre les données et finalise le déchiffrement
    return decryptor.update(ciphertext) + decryptor.finalize()

def aes_encrypt_file(filename: str, key: bytes):
    # Charger le contenu du fichier
    with open(filename, "rb") as f:
        data = f.read()

    # Chiffrer les données avec AES-GCM
    iv, tag, ciphertext = aes_encrypt(data, key)

    # Sauvegarder les données chiffrées (IV + tag + texte chiffré) dans le même fichier
    with open(filename, "wb") as f:
        f.write(iv + tag + ciphertext)

def aes_decrypt_file(filename: str, key: bytes):
    # Charger le contenu du fichier chiffré
    with open(filename, "rb") as f:
        encrypted_data = f.read()

    # Récupérer l'IV, le tag et le texte chiffré depuis les données chiffrées
    iv = encrypted_data[:12]
    tag = encrypted_data[12:28]
    ciphertext = encrypted_data[28:]

    # Déchiffrer les données avec AES-GCM
    decrypted_data = aes_decrypt(iv, tag, ciphertext, key)

    # Sauvegarder les données déchiffrées dans le même fichier
    with open(filename, "wb") as f:
        f.write(decrypted_data)
