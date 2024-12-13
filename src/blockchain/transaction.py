"""
    Transaction module represents all of the thing with transactions
"""

import hashlib
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from typing import Dict
from crypto.signatures import DigitalSignature  # Import DigitalSignature
from utils.logger import Logger
from cryptography import exceptions

log = Logger("transaction")


class Transaction:
    """
    Defines transaction and its content

    :ivar sender: initiator of the transaction
    :type sender: str
    :ivar recipient: recipient of the transaction
    :type recipient: str
    :ivar amount: amount of coins recipient gets
    :type amount: float
    :ivar content: content (comment) sender sends !?
    :type content: str
    :ivar signature: encrypted signature to secure the transaction
    :type signature: bytes
    :ivar sender_public_key: public key of sender in bytes
    :type sender_public_key: str
    """

    def __init__(self, sender: str, recipient: str, amount: float, content: str = ""):
        """Initializes transaction"""
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.content = content
        self.signature = None
        self.sender_public_key = None

    def to_dict(self) -> Dict[str, str]:
        """
        Returns transaction content as a dictionary

        :return: transaction content
        :rtype: Dict[str, str]
        """
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "content": str(self.content),
            "signature": self.signature.hex() if self.signature else None,
            "sender_public_key": (
                self.sender_public_key.decode("utf-8")
                if self.sender_public_key
                else None
            ),  # save public key as string
        }

    def calculate_hash(self) -> str:
        """
        Returns transaction hash

        :return: transaction hash
        :rtype: str
        """
        # Calculating hash just like block's hash
        transaction_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign_transaction(self, private_key_pem: bytes) -> None:
        """
        Signs transaction with private key

        :param private_key_pem: private_key needed to sign transaction
        :type private_key: bytes
        """
        # Raise error if no full info
        if not self.sender or not self.recipient:
            raise ValueError("Transaction must include sender and recipient")
        if self.amount > 0:
            if self.amount <= 0:
                raise ValueError("Transaction amount must be positive")

        # Signing using private_key and transaction's hash
        signer = DigitalSignature()
        self.signature = signer.sign(self.calculate_hash())
        if not self.signature:
            raise ValueError("Error signing transaction")

    def is_valid(self, public_key_pem: bytes) -> bool:
        """
        Checks transaction signature
        :param public_key_pem: key needed to validate signature
        :type public_key_pem: bytes
        :return: if signature is valid or not
        :rtype: bool
        """
        if not self.signature:
            log.debug("No signature in this transaction")
            return False
        if not public_key_pem:
            log.debug("No public key provided")
            return False

        signer = DigitalSignature()
        is_valid = signer.verify(public_key_pem, self.calculate_hash(), self.signature)

        if not is_valid:
            log.error("Signature is invalid")
            return False
        return True


def generate_keys():
    """Generates RSA key pair"""
    signer = DigitalSignature()
    private_key = signer.get_private_key()
    public_key = signer.get_public_key()
    return private_key, public_key


# Example of generating keys
if __name__ == "__main__":
    # Creating keys
    private_key, public_key = generate_keys()

    # Creating trasnaction
    transaction = Transaction(
        sender="Alice", recipient="Bob", amount=100, content="test content"
    )
    print("Transaction hash before signing:", transaction.calculate_hash())

    # Signing transaction
    transaction.sender_public_key = public_key
    transaction.sign_transaction(private_key)
    print("Transaction signed.")

    # Validating signature
    is_valid = transaction.is_valid(public_key)
    print("Is transaction valid?:", is_valid)
