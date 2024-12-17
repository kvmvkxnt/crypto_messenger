import unittest
import time
from unittest.mock import patch
from consensus import ProofOfWork, Validator
from blockchain import Block, Blockchain
from transaction import Transaction
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PublicFormat,
)


class TestProofOfWork(unittest.TestCase):

    def setUp(self):
        self.pow = ProofOfWork(difficulty=4)
        self.block = Block(
            index=1,
            previous_hash="0000",
            timestamp=time.time(),
            transactions=[]
        )

    def test_mine(self):
        """Test if mine method mines block correctly"""
        mined_hash = self.pow.mine(self.block)
        self.assertTrue(mined_hash.startswith("0000"))

    def test_validate(self):
        """ Test that only correctly mined blocks pass the validation."""
        self.pow.mine(self.block)
        is_valid = self.pow.validate(self.block)
        self.assertTrue(is_valid)

        invalid_block = Block(
            index=1,
            previous_hash="0000",
            timestamp=time.time(),
            transactions=[],
            hash="invalid hash"
        )
        is_valid = self.pow.validate(invalid_block)
        self.assertFalse(is_valid)
    
    def test_get_target(self):
         """ Test target string is calculated correctly."""
         target = self.pow.get_target()
         self.assertEqual(target, "0000")


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.validator = Validator()
        self.blockchain = Blockchain(difficulty=4)
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key().public_bytes(
                encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
            )

        self.transaction1 = Transaction(b"Alice", b"Bob", 0, "Transaction 1", self.public_key)
        self.transaction1.sign_transaction(self.private_key)
        self.transaction2 = Transaction(b"Bob", b"Charlie", 0, "Transaction 2", self.public_key)
        self.transaction2.sign_transaction(self.private_key)

    def test_validate_block(self):
        """ Test if block validation method correctly validate block in relation to previous."""
        self.blockchain.add_transaction(self.transaction1)
        mined_block, _ = self.blockchain.mine_pending_transactions(ProofOfWork, "Miner1")

        previous_block = self.blockchain.chain[0]
        is_valid = self.validator.validate_block(mined_block, previous_block)
        self.assertTrue(is_valid)

        invalid_block = Block(
            index=2,
            previous_hash=previous_block.hash,
            timestamp=time.time(),
            transactions=[],
            hash="invalid hash"
        )

        is_valid = self.validator.validate_block(invalid_block, previous_block)
        self.assertFalse(is_valid)
    
    def test_validate_block_with_invalid_timestamp(self):
        """ Test if block validation method correctly validate block with invalid timestamp."""
        self.blockchain.add_transaction(self.transaction1)
        mined_block, _ = self.blockchain.mine_pending_transactions(ProofOfWork, "Miner1")

        previous_block = self.blockchain.chain[0]
        mined_block.timestamp = 0
        is_valid = self.validator.validate_block(mined_block, previous_block)
        self.assertFalse(is_valid)
    

    def test_validate_blockchain(self):
         """ Test if full chain validation method validates correctly."""
         self.blockchain.add_transaction(self.transaction1)
         self.blockchain.mine_pending_transactions(ProofOfWork, "Miner1")
         is_valid = self.validator.validate_blockchain(self.blockchain)
         self.assertTrue(is_valid)

         self.blockchain.chain[1].hash = "invalid hash"
         is_valid = self.validator.validate_blockchain(self.blockchain)
         self.assertFalse(is_valid)
        

        
if __name__ == '__main__':
    unittest.main()