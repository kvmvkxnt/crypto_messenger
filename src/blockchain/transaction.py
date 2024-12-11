import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from typing import Dict


class Transaction:
    def __init__(self, sender: str, recipient: str, amount: float):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = None

    def to_dict(self) -> Dict[str, str]:
        """Возвращает словарь с данными транзакции."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
        }

    def calculate_hash(self) -> str:
        """Возвращает хеш транзакции."""
        transaction_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign_transaction(self, private_key: rsa.RSAPrivateKey) -> None:
        """Подписывает транзакцию приватным ключом."""
        if not self.sender or not self.recipient:
            raise ValueError("Transaction must include sender and recipient")

        hash_bytes = self.calculate_hash().encode()
        self.signature = private_key.sign(
            hash_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def is_valid(self, public_key: rsa.RSAPublicKey) -> bool:
        """Проверяет подпись транзакции."""
        if not self.signature:
            print("No signature in this transaction")
            return False

        try:
            public_key.verify(
                self.signature,
                self.calculate_hash().encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False


# Генерация ключей для примера
if __name__ == "__main__":
    # Создаем ключи
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Создаем транзакцию
    transaction = Transaction(sender="Alice", recipient="Bob", amount=100)
    print("Transaction hash before signing:", transaction.calculate_hash())

    # Подписываем транзакцию
    transaction.sign_transaction(private_key)
    print("Transaction signed.")

    # Проверяем подпись
    is_valid = transaction.is_valid(public_key)
    print("Is transaction valid?:", is_valid)
