"""
    Transaction module represents all of the thing with transactions
"""

import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from typing import Dict
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PublicFormat,
)
import base64


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
        sender: str,
        recipient: str,
        amount: float,
        content: any = "",
        sender_public_key: rsa.RSAPublicKey = None,
        signature: bytes = None,
    ):
        """Initializes transaction"""
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.content = content
        self.signature = signature
        if sender:
            self.sender_public_key = (
                sender_public_key
                if isinstance(sender_public_key, rsa.RSAPublicKey)
                else load_pem_public_key(sender_public_key.encode("utf-8"))
            )
        else:
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
            "signature": (
                base64.b64encode(self.signature).decode("utf-8")
                if self.signature
                else None
            ),
            "sender_public_key": (
                self.sender_public_key.public_bytes(
                    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
                ).decode("utf-8")
                if self.sender_public_key
                else None
            ),
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

    def sign_transaction(self, private_key: rsa.RSAPrivateKey) -> None:
        """
        Signs transaction with private key

        :param private_key: private_key needed to sign transaction
        :type private_key: rsa.RSAPrivateKey
        """
        if not self.sender or not self.recipient:
            raise ValueError("Transaction must include sender and recipient")

        hash_bytes = self.calculate_hash().encode()
        self.signature = private_key.sign(
            hash_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

    def is_valid(self, public_key: rsa.RSAPublicKey) -> bool:
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
            public_key.verify(
                self.signature,
                self.calculate_hash().encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
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
