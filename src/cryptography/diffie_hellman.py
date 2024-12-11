from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PublicFormat
)


class DiffieHellmanKeyExchange:
    def __init__(self):
        # Генерация параметров для DH
        self.parameters = dh.generate_parameters(generator=2, key_size=2048)
        self.private_key = self.parameters.generate_private_key()
        self.public_key = self.private_key.public_key()

    def get_public_key(self):
        """Возвращает публичный ключ в сериализованном формате."""
        return self.public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        )

    def generate_shared_key(self, peer_public_key_bytes: bytes) -> bytes:
        """
            Создает общий секретный ключ
            на основе публичного ключа другой стороны.
        """
        peer_public_key = load_pem_public_key(peer_public_key_bytes)
        shared_key = self.private_key.exchange(peer_public_key)

        # Применяем KDF для усиления ключа
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'dh key exchange'
        ).derive(shared_key)

        return derived_key


if __name__ == "__main__":
    # Симуляция обмена ключами
    alice = DiffieHellmanKeyExchange()
    bob = DiffieHellmanKeyExchange()

    # Получение публичных ключей
    alice_public_key = alice.get_public_key()
    bob_public_key = bob.get_public_key()

    # Генерация общего секрета
    alice_shared_key = alice.generate_shared_key(bob_public_key)
    bob_shared_key = bob.generate_shared_key(alice_public_key)

    # Проверка совпадения
    print("Alice's shared key:", alice_shared_key.hex())
    print("Bob's shared key:", bob_shared_key.hex())
    print("Keys match:", alice_shared_key == bob_shared_key)
