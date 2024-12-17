import unittest
import time
from unittest.mock import patch
from blockchain import Blockchain, Block
from transaction import Transaction
from consensus import ProofOfWork
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    Encoding,
    PublicFormat,
)

class TestBlock(unittest.TestCase):

    def setUp(self):
        self.transactions = [
            Transaction(b"Alice", b"Bob", 0, "Test Transaction"),
            Transaction(b"Bob", b"Alice", 0, "Test Transaction 2")
        ]
        self.block = Block(
            index=1,
            previous_hash="0000",
            timestamp=time.time(),
            transactions=self.transactions
        )

    def test_calculate_hash(self):
        """ Test if the hash is generated correctly."""
        expected_hash = self.block.calculate_hash()
        self.assertEqual(self.block.hash, expected_hash)

    def test_to_dict(self):
        """ Test if the block can be represented as dict."""
        block_dict = self.block.to_dict()
        self.assertEqual(block_dict["index"], self.block.index)
        self.assertEqual(block_dict["previous_hash"], self.block.previous_hash)
        self.assertEqual(block_dict["hash"], self.block.hash)
        self.assertEqual(len(block_dict["transactions"]), len(self.block.transactions))

class TestBlockchain(unittest.TestCase):

    def setUp(self):
        self.blockchain = Blockchain(difficulty=4)
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key().public_bytes(
                encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
            )

        self.transaction1 = Transaction(b"Alice", b"Bob", 0, "Transaction 1", self.public_key)
        self.transaction1.sign_transaction(self.private_key)
        self.transaction2 = Transaction(b"Bob", b"Charlie", 0, "Transaction 2", self.public_key)
        self.transaction2.sign_transaction(self.private_key)

    def test_create_genesis_block(self):
        """Test the genesis block is created properly"""
        self.assertEqual(len(self.blockchain.chain), 1)
        self.assertEqual(self.blockchain.chain[0].index, 0)

    def test_add_transaction(self):
        """ Test transaction can be added to pending transactions"""
        self.blockchain.add_transaction(self.transaction1)
        self.assertEqual(len(self.blockchain.pending_transactions), 1)
        self.assertEqual(self.blockchain.pending_transactions[0].sender, self.transaction1.sender)

        invalid_transaction = Transaction(b"Invalid", b"Bob", 0, "Fake")
        self.blockchain.add_transaction(invalid_transaction)
        self.assertEqual(len(self.blockchain.pending_transactions), 1)

    def test_get_latest_block(self):
        """ Test returns latest block"""
        latest_block = self.blockchain.get_latest_block()
        self.assertEqual(latest_block.index, 0)
    
    # def test_get_balance(self):
    #     """ Test get balance method """
    #     self.blockchain.add_transaction(self.transaction1)
    #     self.blockchain.mine_pending_transactions(ProofOfWork, "Miner1")

    #     balance_alice = self.blockchain.get_balance(b"Alice")
    #     balance_bob = self.blockchain.get_balance(b"Bob")
    #     balance_miner = self.blockchain.get_balance(b"Miner1")
        
    #     self.assertEqual(balance_alice, -10)
    #     self.assertEqual(balance_bob, 10)
    #     self.assertEqual(balance_miner, 1)

    def test_mine_pending_transactions(self):
        """ Test if mine transaction method correctly mines new block"""
        self.blockchain.add_transaction(self.transaction1)
        mined_block, mined_transaction = self.blockchain.mine_pending_transactions(ProofOfWork, "Miner1")

        self.assertIsNotNone(mined_block)
        self.assertIsNotNone(mined_transaction)
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(len(self.blockchain.pending_transactions), 1)
        self.assertEqual(self.blockchain.pending_transactions[0].amount, 1)
        self.assertIn(mined_block, self.blockchain.chain)


    def test_is_chain_valid(self):
        """ Test if chain validation methods is working properly"""
        self.blockchain.add_transaction(self.transaction1)
        self.blockchain.mine_pending_transactions(ProofOfWork, "Miner1")

        self.assertTrue(self.blockchain.is_chain_valid())

        self.blockchain.chain[1].hash = "invalid hash"
        self.assertFalse(self.blockchain.is_chain_valid())

    def test_contains_block(self):
        """ Test if block is correctly recognized as part of the chain."""
        self.blockchain.add_transaction(self.transaction1)
        mined_block, _ = self.blockchain.mine_pending_transactions(ProofOfWork, "Miner1")

        self.assertTrue(self.blockchain.contains_block(mined_block))

        fake_block = Block(1, "0000", time.time(), [])
        self.assertFalse(self.blockchain.contains_block(fake_block))

    def test_len(self):
         """ Test if __len__ method is returning correct length"""
         self.assertEqual(len(self.blockchain), 1)
         self.blockchain.add_transaction(self.transaction1)
         self.blockchain.mine_pending_transactions(ProofOfWork, "Miner1")
         self.assertEqual(len(self.blockchain), 2)

if __name__ == '__main__':
    unittest.main()