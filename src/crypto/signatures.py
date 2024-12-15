"""
    This module represents digital signatures and handles message signing.
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PrivateFormat,
    NoEncryption,
    PublicFormat,
)
from cryptography import exceptions
from typing import Optional
from utils.logger import Logger

log = Logger("signatures")


class DigitalSignature:
    """
    Class that handles all signature methods

    :ivar private_key: private key of the signature
    :type private_key: RSAPrivateKey
    :ivar public_key: public key of the signature based on its private key
    :type public_key: RSAPublicKey
    """

    def __init__(self, key_size: int = 2048):
        """Generating RSA key pair"""
        self.key_size = key_size
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=self.key_size
        )
        self.public_key = self.private_key.public_key()
        self.padding = padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        )

    def get_private_key(self) -> bytes:
        """
        Returns private key in PEM format

        :return: private key as PEM
        :rtype: bytes
        """
        return self.private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )

    def get_public_key(self) -> bytes:
        """
        Returns public key in PEM format

        :return: public key as PEM
        :rtype: bytes
        """
        return self.public_key.public_bytes(
            encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
        )

    def sign(self, message: str) -> Optional[bytes]:
        """
        Creates digital signature of a message

        :return: signature
        :rtype: bytes
        """
        if not message:
            log.error("Cannot sign empty message")
            return None
        try:
            signature = self.private_key.sign(
                message.encode(), self.padding, hashes.SHA256()
            )
            log.debug(f"Signed message: {message}")
            return signature
        except Exception as e:
            log.error(f"Error during signing: {e}")
            return None

    def verify(self, public_key_pem: bytes, message: str, signature: bytes) -> bool:
        """
        Verifys digital signature

        :param public_key_pem: signer's public key
        :type public_key_pem: bytes
        :param message: message's sign to be checked
        :type message: str
        :param signature: the actual signature of message
        :type signature: bytes
        :return: if signature is valid or not
        :rtype: bool
        """
        if not public_key_pem:
            log.error("Public key cannot be None")
            return False
        if not message:
            log.error("Message cannot be None")
            return False
        if not signature:
            log.error("Signature cannot be None")
            return False
        try:
            log.debug(f"Loading public key")
            public_key = load_pem_public_key(public_key_pem)
        except Exception as e:
            log.error(f"Error loading public key during verification: {e}")
            return False
        try:
            log.debug(f"Verifying signature for message {message}")
            public_key.verify(
                signature, message.encode(), self.padding, hashes.SHA256()
            )
            log.debug("Signature is valid")
            return True
        except exceptions.InvalidSignature as e:
            log.error(f"Signature verification failed: {e}")
            return False
        except Exception as e:
            log.error(f"Unexpected error during signature verification: {e}")
            return False


if __name__ == "__main__":
    signer = DigitalSignature(key_size=2048)

    private_key_pem = signer.get_private_key()
    public_key_pem = signer.get_public_key()

    message = "This is a secure message."
    signature = signer.sign(message)
    print("Signature:", signature.hex() if signature else "None")

    is_valid = signer.verify(public_key_pem, message, signature)
    print("Is signature valid?:", is_valid)
