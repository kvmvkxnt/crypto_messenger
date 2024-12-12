import unittest
import os
import sys

class TestCryptography(unittest.TestCase):
    def test_cryptography_intialization(self):
        dh1 = dh.DiffieHellmanKeyExchange()
        self.assertEqual(dh1, True)


if __name__ == "__main__":
    unittest.main()
