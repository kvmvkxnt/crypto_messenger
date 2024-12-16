"""
    Transaction module represents all of the thing with transactions
"""

import hashlib
import json5 as json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from typing import Dict


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
    :type content: any
    :ivar signature: encrypted signature to secure the transaction
    :type signature: idk
    """

    def __init__(
        self,
        sender: bytes = None,
        recipient: bytes = None,
        amount: float = 0,
        content: any = "",
        signature: bytes = None,
    ):
        """Initializes transaction"""
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.content = content
        self.signature = signature

    def to_dict(self) -> Dict[str, str]:
        """
        Returns transaction content as a dictionary

        :return: transaction content
        :rtype: Dict[str, str]
        """
        return {
            "sender": (
                self.sender.hex()
                if self.sender
                else None
            ),
            "recipient": (
                self.recipient.hex()
                if self.recipient
                else None
            ),
            "amount": self.amount,
            "content": str(self.content),
            "signature": (
                self.signature.hex()
                if self.signature
                else None
            )
        }

    def calculate_hash(self) -> str:
        """
        Returns transaction hash

        :return: transaction hash
        :rtype: str
        """
        transaction_dict = self.to_dict()
        transaction_dict.pop("signature", None)
        transaction_string = json.dumps(transaction_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign_transaction(self, signer) -> None:
        """
        Signs transaction with private key

        :param private_key: private_key needed to sign transaction
        :type private_key: rsa.RSAPrivateKey
        """
        if not self.sender or not self.recipient:
            raise ValueError("Transaction must include sender and recipient")

        hash_bytes = self.calculate_hash().encode()
        self.signature = signer.sign(hash_bytes)

    def is_valid(self, public_key, signature_manager) -> bool:
        """
        Checks transaction signature

        :param public_key: key needed to validate signature
        :type public_key: rsa.RSAPublicKey
        :return: if signature is valid or not
        :rtype: bool
        """
        if not self.signature:
            print("No signature in this transaction")
            return False

        try:
            signature_manager.verify(public_key, self.calculate_hash(),
                           self.signature)
            return True
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False


if __name__ == "__main__":
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    transaction = Transaction(sender="Alice", recipient="Bob", amount=100)
    print("Transaction hash before signing:", transaction.calculate_hash())

    transaction.sign_transaction(private_key)
    print("Transaction signed.")

    is_valid = transaction.is_valid(public_key)
    print("Is transaction valid?:", is_valid)
