import base64
import os
import subprocess

class OpensslError(Exception):
    pass

def encrypt_with_public_key(data, public_key_file):
    """Encrypts data using OpenSSL pkeyutl command with a public key from a PEM file."""
    # Prépare les arguments pour appeler la commande pkeyutl
    args = [
        'openssl',
        'pkeyutl',
        '-encrypt',
        '-pubin',
        '-inkey',
        public_key_file
    ]

    # Ouvre le pipeline vers openssl. Envoie les données à chiffrer sur l'entrée standard de openssl, récupère la sortie
    result = subprocess.run(args, input=data.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Vérifie s'il y a des erreurs
    if result.returncode != 0:
        error_message = result.stderr.decode()
        raise RuntimeError(f"Error encrypting data: {error_message}")

    # Renvoie le résultat chiffré brut
    return result.stdout
# Exemple d'utilisation
data_to_encrypt = "I got it!"
public_key_file = "pki.pem"
encrypted_data = encrypt_with_public_key(data_to_encrypt, public_key_file)
print("Cipher text (hex):", encrypted_data.hex())

