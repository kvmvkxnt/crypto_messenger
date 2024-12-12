'''
    This module represents digital signatures and handles message signing.
'''
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
    '''
        Class that handles all signature methods

        :ivar private_key: private key of the signature
        :type private_key: RSAPrivateKey
        :ivar public_key: public key of the signature based on its private key
        :type public_key: RSAPublicKey
    '''

    def __init__(self):
        '''Generating RSA key pair'''
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def get_private_key(self) -> bytes:
        '''
            Returns private key in PEM format

            :return: private key as PEM
            :rtype: bytes
        '''
        return self.private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )

    def get_public_key(self) -> bytes:
        '''
            Returns public key in PEM format

            :return: public key as PEM
            :rtype: bytes
        '''
        return self.public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )

    def sign(self, message: str) -> bytes:
        '''
            Creates digital signature of a message

            :return: signature
            :rtype: bytes
        '''
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
        '''
            Verifys digital signature

            :param public_key_pem: signer's public key
            :type public_key_pem: bytes
            :param message: message's sign to be checked
            :type message: str
            :param signature: the actual signature of message
            :type signature: bytes
            :return: if signature is valid or not
            :rtype: bool
        '''
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


# Example usage
if __name__ == "__main__":
    # Creating example for signature
    signer = DigitalSignature()

    # Generating keys
    private_key_pem = signer.get_private_key()
    public_key_pem = signer.get_public_key()

    # Signing message
    message = "This is a secure message."
    signature = signer.sign(message)
    print("Signature:", signature.hex())

    # Validating sign
    is_valid = DigitalSignature.verify(public_key_pem, message, signature)
    print("Is signature valid?:", is_valid)
