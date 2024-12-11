import unittest
import src.blockchain.blockchain as blockchain


class BlockchainTest(unittest.TestCase):
    def test_calculating_hash(self):
        test_block = blockchain.Block(0, "123", 14.23423, [])
        test_hash = "83b1c99f5060b8576871e8676b1e2928953d3ff5592cbcc921b34cacae02df38"
        self.assertEqual(test_block.calculate_hash(), test_hash)


if __name__ == "__main__":
    unittest.main()
