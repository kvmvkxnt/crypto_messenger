'''
    This module represents basic Diffie Hellman's (DH) algorithm's usage
    to generate public, pravate and shared keys and to validate them.
'''
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PublicFormat
)
from cryptography.exceptions import InvalidKey
import os


class DiffieHellmanKeyExchange:
    '''
        Class manages all keys (private, public, shared)

        :ivar parameters: DH parameter group
        :type parameters: DHParameters
        :ivar private_key: DH private key
        :type private_key: DHPrivateKey
        :ivar public_key: public key associated with private key
        :type public_key: DHPublicKey
    '''

    def __init__(self, parameters=None):
        '''
            Initiates key exchange class

            :param parameters: DH parameter group which will be used to \
            generate keys
            :type parameters: DHParameters or None
        '''
        # Getting parameters for DH or generating them
        self.parameters = parameters or \
            dh.generate_parameters(generator=2, key_size=2048)
        self.private_key = self.parameters.generate_private_key()
        self.public_key = self.private_key.public_key()

    def get_public_key(self):
        '''
            Returns public key in serialized format

            :return: public key in serialized format
            :rtype: Serialized key
        '''
        return self.public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        )

    def generate_shared_key(self, peer_public_key_bytes: bytes) -> bytes:
        '''
            Generates shared key based on other peer's public key

            :param peer_public_key_bytes: other peer's public key in bytes
            :type peer_public_key_bytes: bytes
            :return: derived key
            :rtype: None or bytes
        '''
        try:
            peer_public_key = load_pem_public_key(peer_public_key_bytes)
        except InvalidKey:
            print("Invalid Public Key Format")
            return

        print("Received public key:", peer_public_key_bytes.decode())
        shared_key = self.private_key.exchange(peer_public_key)
        print(shared_key)

        # Using KDF to strenghten key
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=os.urandom(16),
            info=b'dh key exchange'
        ).derive(shared_key)

        return derived_key


if __name__ == "__main__":
    shared_parameters = dh.generate_parameters(generator=2, key_size=2048)

    # Simulating key generation
    alice = DiffieHellmanKeyExchange(shared_parameters)
    bob = DiffieHellmanKeyExchange(shared_parameters)

    # Getting public keys
    alice_public_key = alice.get_public_key()
    bob_public_key = bob.get_public_key()

    # Generating shared key
    alice_shared_key = alice.generate_shared_key(bob_public_key)
    bob_shared_key = bob.generate_shared_key(alice_public_key)

    # Validating key equalness
    print("Alice's shared key:", alice_shared_key.hex())
    print("Bob's shared key:", bob_shared_key.hex())
    print("Keys match:", alice_shared_key == bob_shared_key)
