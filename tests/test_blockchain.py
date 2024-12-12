import unittest
import os
import sys

parent_dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(parent_dir)
from src.blockchain.blockchain import Block, Blockchain
from src.blockchain.consensus import ProofOfWork, Validator
from src.blockchain.transaction import Transaction


class BlockchainTest(unittest.TestCase):
    def test_calculating_hash(self):
        test_block = Block(0, "123", 14.23423, [])
        test_hash = "83b1c99f5060b8576871e8676b1e2928953d3ff5592cbcc921b34cacae02df38"
        self.assertEqual(test_block.calculate_hash(), test_hash)


if __name__ == "__main__":
    unittest.main()
