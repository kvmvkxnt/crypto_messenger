import unittest
from transaction import Transaction
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PublicFormat,
)


class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key().public_bytes(
                encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
            )
        self.transaction = Transaction(
            sender=b"Alice",
            recipient=b"Bob",
            amount=10.0,
            content="Test transaction",
            sign_public_key=self.public_key
        )

    def test_to_dict(self):
        """ Test if transaction can be correctly converted to dict."""
        transaction_dict = self.transaction.to_dict()
        self.assertEqual(transaction_dict['sender'], self.transaction.sender.hex())
        self.assertEqual(transaction_dict['recipient'], self.transaction.recipient.hex())
        self.assertEqual(transaction_dict['amount'], self.transaction.amount)
        self.assertEqual(transaction_dict['content'], "Test transaction")
        self.assertIsNone(transaction_dict['signature'])


    def test_calculate_hash(self):
        """ Test if the hash is calculated correctly. """
        expected_hash = self.transaction.calculate_hash()
        self.assertIsNotNone(expected_hash)
        self.assertEqual(len(expected_hash), 64)

    def test_sign_transaction(self):
        """ Test transaction can be correctly signed."""
        self.transaction.sign_transaction(self.private_key)
        self.assertIsNotNone(self.transaction.signature)
    
    def test_sign_transaction_invalid(self):
        """ Test if sign transaction raises correct value error."""
        invalid_transaction = Transaction()
        with self.assertRaises(ValueError):
            invalid_transaction.sign_transaction(self.private_key)
        invalid_transaction2 = Transaction(sender=b"Alice")
        with self.assertRaises(ValueError):
            invalid_transaction2.sign_transaction(self.private_key)


    def test_is_valid_signature(self):
        """ Test that only valid transaction can be verified."""
        self.transaction.sign_transaction(self.private_key)
        is_valid = self.transaction.is_valid(self.public_key)
        self.assertTrue(is_valid)

    def test_is_invalid_signature(self):
        """ Test that invalid transaction can't be verified."""
        invalid_public_key = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key().public_bytes(
            encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
        )
        self.transaction.sign_transaction(self.private_key)
        is_valid = self.transaction.is_valid(invalid_public_key)
        self.assertFalse(is_valid)
        
        invalid_transaction = Transaction(
            sender=b"Alice",
            recipient=b"Bob",
            amount=10.0,
            content="Test transaction",
        )
        is_valid = invalid_transaction.is_valid(self.public_key)
        self.assertFalse(is_valid)

if __name__ == '__main__':
    unittest.main()