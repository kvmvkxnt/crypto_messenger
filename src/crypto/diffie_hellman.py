"""
    This module represents basic Diffie Hellman's (DH) algorithm's usage
    to generate public, pravate and shared keys and to validate them.
"""

from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PublicFormat,
)
from cryptography.exceptions import InvalidKey
from typing import Optional


class DiffieHellmanKeyExchange:
    """
    Class manages all keys (private, public, shared)

    :ivar parameters: DH parameter group
    :type parameters: DHParameters
    :ivar private_key: DH private key
    :type private_key: DHPrivateKey
    :ivar public_key: public key associated with private key
    :type public_key: DHPublicKey
    """

    def __init__(self, parameters: Optional[dh.DHParameters] = None):
        """
            Initiates key exchange class

            :param parameters: DH parameter group which will be used to \
            generate keys
            :type parameters: DHParameters or None
        """

        self.parameters = parameters or dh.generate_parameters(
            generator=2, key_size=2048
        )
        self.private_key = self.parameters.generate_private_key()
        self.public_key = self.private_key.public_key()

    def get_public_key(self):
        """
        Returns public key in serialized format

        :return: public key in serialized format
        :rtype: Serialized key
        """
        return self.public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        )

    def generate_shared_key(self, peer_public_key_bytes: bytes) -> Optional[bytes]:
        """
        Generates shared key based on other peer's public key

        :param peer_public_key_bytes: other peer's public key in bytes
        :type peer_public_key_bytes: bytes
        :return: derived key
        :rtype: None or bytes
        """
        if peer_public_key_bytes is None:
            print("Error: Peer public key cannot be None.")
            return None

        try:
            peer_public_key = load_pem_public_key(peer_public_key_bytes)
        except InvalidKey as e:
            print(f"Error: Invalid Public Key Format: {e}")
            return None
        except Exception as e:
            print(f"Error during key loading: {e}")
            return None

        print("Received public key:", peer_public_key_bytes.decode())
        try:
            shared_key = self.private_key.exchange(peer_public_key)

            derived_key = HKDF(
                algorithm=hashes.SHA256(), length=32, salt=None, info=b"dh key exchange"
            ).derive(shared_key)

            return derived_key
        except Exception as e:
            print(f"Error during key exchange: {e}")
            return None


if __name__ == "__main__":
    shared_parameters = dh.generate_parameters(generator=2, key_size=2048)

    alice = DiffieHellmanKeyExchange(shared_parameters)
    bob = DiffieHellmanKeyExchange(shared_parameters)

    alice_public_key = alice.get_public_key()
    bob_public_key = bob.get_public_key()

    alice_shared_key = alice.generate_shared_key(bob_public_key)
    bob_shared_key = bob.generate_shared_key(alice_public_key)

    print("Alice's shared key:", alice_shared_key.hex() if alice_shared_key else "None")
    print("Bob's shared key:", bob_shared_key.hex() if bob_shared_key else "None")
    print(
        "Keys match:",
        (
            alice_shared_key == bob_shared_key
            if alice_shared_key and bob_shared_key
            else False
        ),
    )
