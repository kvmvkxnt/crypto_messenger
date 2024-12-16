import unittest
import diffie_hellman as dh


class TestDiffieHellman(unittest.TestCase):
    def test_getPublicKey(self):
        dhc = dh.DiffieHellmanKeyExchange()
        self.assertEqual(dhc.get_public_key(), "test")


if __name__ == '__main__':
    unittest.main()
