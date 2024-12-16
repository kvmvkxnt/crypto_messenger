"""
    This module represents message encryption / decryption.\
    In project dh shared key will be used with this module \
    to encrypt / decrypt messages.
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
from typing import Optional
from ..utils.logger import Logger

log = Logger("encryption")


class SymmetricEncryption:
    """
    Encryption class

    :ivar key: key that will be used to encrypt message
    :type key: bytes
    """

    def __init__(self, key: bytes, algorithm="AES", mode="CBC"):
        """
        Initiates with the given key

        :param key: key that will be used to encrypt message
        :type key: bytes
        """
        if not isinstance(key, bytes):
            raise TypeError("Key must be bytes")
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes long")

        self.key = key
        self.algorithm = algorithm
        self.mode = mode

    def encrypt(self, plaintext: str) -> Optional[bytes]:
        """
        Encrypts the message

        :param plaintext: message to be encrypted
        :type plaintext: str
        :return: encrypted message
        :rtype: bytes
        """
        if not plaintext:
            return None

        plaintext_bytes = plaintext.encode()

        if self.algorithm == "AES" and self.mode == "CBC":
            iv = os.urandom(16)  # Random initialization vector
            cipher = Cipher(
                algorithms.AES(self.key), modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()

            # Padding data before ciphering
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(plaintext_bytes) + padder.finalize()

            # Encrypting data
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            return iv + ciphertext
        elif self.algorithm == "AES" and self.mode == "GCM":
            nonce = os.urandom(12)
            aesgcm = AESGCM(self.key)
            ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
            return nonce + ciphertext
        else:
            log.error("Unsupported algorithm or mode")
            return None

    def decrypt(self, ciphertext: bytes) -> Optional[str]:
        """
        Decrypts the message

        :param ciphertext: the message to be decrypted
        :type ciphertext: bytes
        :return: the decrypted message
        :rtype: str
        """
        if not ciphertext:
            return None

        if self.algorithm == "AES" and self.mode == "CBC":
            if len(ciphertext) < 16:
                print("Ciphertext too short for CBC mode")
                return None
            iv = ciphertext[:16]  # Extrcating intialization vector
            actual_ciphertext = ciphertext[16:]

            cipher = Cipher(
                algorithms.AES(self.key), modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # Decrypting data
            try:
                padded_data = decryptor.update(actual_ciphertext) + \
                    decryptor.finalize()

                # Deleting padding
                unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
                plaintext = unpadder.update(padded_data) + unpadder.finalize()
                return plaintext.decode()
            except Exception as e:
                print(f"Error during decryption in CBC mode: {e}")
                return None
        elif self.algorithm == "AES" and self.mode == "GCM":
            if len(ciphertext) < 12:
                print("Ciphertext too short for GCM mode")
                return None
            nonce = ciphertext[:12]
            actual_ciphertext = ciphertext[12:]
            aesgcm = AESGCM(self.key)
            try:
                plaintext = aesgcm.decrypt(nonce, actual_ciphertext, None)
                return plaintext.decode()
            except Exception as e:
                print(f"Error during decryption in GCM mode: {e}")
                return None
        else:
            print("Unsupported algorithm or mode")
            return None


if __name__ == "__main__":
    # Example of usage

    key = os.urandom(32)

    # Encryption and decryption
    encryptor = SymmetricEncryption(key, algorithm="AES", mode="GCM")
    plaintext = "This is a secret message."

    encrypted = encryptor.encrypt(plaintext)
    print("Encrypted:", encrypted.hex() if encrypted else "None")

    decrypted = encryptor.decrypt(encrypted)
    print("Decrypted:", decrypted if decrypted else "None")
