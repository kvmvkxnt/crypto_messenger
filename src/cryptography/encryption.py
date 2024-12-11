from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os


class SymmetricEncryption:
    def __init__(self, key: bytes):
        """Инициализация с заданным ключом."""
        self.key = key

    def encrypt(self, plaintext: str) -> bytes:
        """Шифрует сообщение."""
        iv = os.urandom(16)  # Случайный вектор инициализации
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv),
                        backend=default_backend())
        encryptor = cipher.encryptor()

        # Паддинг данных перед шифрованием
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext.encode()) + padder.finalize()

        # Шифрование данных
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext

    def decrypt(self, ciphertext: bytes) -> str:
        """Расшифровывает сообщение."""
        iv = ciphertext[:16]  # Извлечение вектора инициализации
        actual_ciphertext = ciphertext[16:]

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv),
                        backend=default_backend())
        decryptor = cipher.decryptor()

        # Расшифровка данных
        padded_data = decryptor.update(actual_ciphertext) + \
            decryptor.finalize()

        # Удаление паддинга
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext.decode()


# Пример использования
if __name__ == "__main__":
    # Генерация ключа (обычно берется из KDF на основе общего секрета)
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

    # Шифрование и расшифровка
    encryptor = SymmetricEncryption(key)
    plaintext = "This is a secret message."

    encrypted = encryptor.encrypt(plaintext)
    print("Encrypted:", encrypted.hex())

    decrypted = encryptor.decrypt(encrypted)
    print("Decrypted:", decrypted)
