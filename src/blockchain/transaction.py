'''
    Transaction module represents all of the thing with transactions
'''
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from typing import Dict


class Transaction:
    '''
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
    '''

    def __init__(self, sender: str,
                 recipient: str,
                 amount: float,
                 content: any = ""):
        '''Initializes transaction'''
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.content = content
        self.signature = None

    def to_dict(self) -> Dict[str, str]:
        '''
            Returns transaction content as a dictionary

            :return: transaction content
            :rtype: Dict[str, str]
        '''
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "conent": str(self.content)
        }

    def calculate_hash(self) -> str:
        '''
            Returns transaction hash

            :return: transaction hash
            :rtype: str
        '''
        # Calculating hash just like block's hash
        transaction_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign_transaction(self, private_key: rsa.RSAPrivateKey) -> None:
        '''
            Signs transaction with private key

            :param private_key: private_key needed to sign transaction
            :type private_key: rsa.RSAPrivateKey
        '''
        # Raise error if no full info
        if not self.sender or not self.recipient:
            raise ValueError("Transaction must include sender and recipient")

        # Signing using private_key and transaction's hash
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
        '''
            Checks transaction signature

            :param public_key: key needed to validate signature
            :type public_key: rsa.RSAPublicKey
            :return: if signature is valid or not
            :rtype: bool
        '''
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


# Example of generating keys
if __name__ == "__main__":
    # Creating keys
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    # Creating trasnaction
    transaction = Transaction(sender="Alice", recipient="Bob", amount=100)
    print("Transaction hash before signing:", transaction.calculate_hash())

    # Signing transaction
    transaction.sign_transaction(private_key)
    print("Transaction signed.")

    # Validating signature
    is_valid = transaction.is_valid(public_key)
    print("Is transaction valid?:", is_valid)
