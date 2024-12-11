from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PrivateFormat,
    NoEncryption,
    PublicFormat
)


class DigitalSignature:
    def __init__(self):
        """Генерация пары ключей RSA."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def get_private_key(self) -> bytes:
        """Возвращает приватный ключ в PEM формате."""
        return self.private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )

    def get_public_key(self) -> bytes:
        """Возвращает публичный ключ в PEM формате."""
        return self.public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )

    def sign(self, message: str) -> bytes:
        """Создает цифровую подпись сообщения."""
        return self.private_key.sign(
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    @staticmethod
    def verify(public_key_pem: bytes, message: str, signature: bytes) -> bool:
        """Проверяет цифровую подпись."""
        public_key = load_pem_public_key(public_key_pem)
        try:
            public_key.verify(
                signature,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Verification failed: {e}")
            return False


# Пример использования
if __name__ == "__main__":
    # Создание экземпляра для подписи
    signer = DigitalSignature()

    # Генерация ключей
    private_key_pem = signer.get_private_key()
    public_key_pem = signer.get_public_key()

    # Подписываем сообщение
    message = "This is a secure message."
    signature = signer.sign(message)
    print("Signature:", signature.hex())

    # Проверяем подпись
    is_valid = DigitalSignature.verify(public_key_pem, message, signature)
    print("Is signature valid?:", is_valid)
