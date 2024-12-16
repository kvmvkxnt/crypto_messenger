import unittest
import crypto.diffie_hellman as dh


class TestDiffieHellman(unittest.TestCase):
    def test_getPublicKey_success(self):
        dhc = dh.DiffieHellmanKeyExchange()
        self.assertEqual(dhc.get_public_key()[0:27].decode('utf-8'), "-----BEGIN PUBLIC KEY-----\n")

    def test_getPublicKey_fail(self):
        dhc = dh.DiffieHellmanKeyExchange()
        with self.assertRaises(AssertionError):
            self.assertEqual(dhc.get_public_key().decode('utf-8'), "")


if __name__ == '__main__':
    unittest.main()
