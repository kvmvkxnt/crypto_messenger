'''
    This module represents message encryption / decryption.\
    In project dh shared key will be used with this module \
    to encrypt / decrypt messages.
'''
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os


class SymmetricEncryption:
    '''
        Encryption class

        :ivar key: key that will be used to encrypt message
        :type key: bytes
    '''

    def __init__(self, key: bytes):
        '''
            Initiates with the given key

            :param key: key that will be used to encrypt message
            :type key: bytes
        '''
        self.key = key

    def encrypt(self, plaintext: str) -> bytes:
        '''
            Encrypts the message

            :param plaintext: message to be encrypted
            :type plaintext: str
            :return: encrypted message
            :rtype: bytes
        '''
        iv = os.urandom(16)  # Random initialization vector
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv),
                        backend=default_backend())
        encryptor = cipher.encryptor()

        # Padding data before ciphering
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()

        # Encrypting data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext

    def decrypt(self, ciphertext: bytes) -> str:
        '''
            Decrypts the message

            :param ciphertext: the message to be decrypted
            :type ciphertext: bytes
            :return: the decrypted message
            :rtype: str
        '''
        iv = ciphertext[:16]  # Extrcating intialization vector
        actual_ciphertext = ciphertext[16:]

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv),
                        backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypting data
        padded_data = decryptor.update(actual_ciphertext) + \
            decryptor.finalize()

        # Deleting padding
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext.decode()


# Usage example
if __name__ == "__main__":
    # Generating key (usually KDF is taken from shared key)
    password = b"my_secret_password"
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password)

    # Encryption and decryption
    encryptor = SymmetricEncryption(key)
    plaintext = "This is a secret message."

    encrypted = encryptor.encrypt(plaintext)
    print("Encrypted:", encrypted.hex())

    decrypted = encryptor.decrypt(encrypted)
    print("Decrypted:", decrypted)
