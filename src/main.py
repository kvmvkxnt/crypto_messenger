from blockchain.blockchain import Block, Blockchain
from blockchain.consensus import ProofOfWork, Validator
from blockchain.transaction import Transaction
from crypto.diffie_hellman import DiffieHellmanKeyExchange
from crypto.encryption import SymmetricEncryption
from crypto.signatures import DigitalSignature
from network.p2p import P2P
from network.discovery import discover_peers
# from network.sync import SyncManager
from utils import config as cfg
from utils import logger
import socket

log = logger.Logger("main")
blockchain = Blockchain(cfg.BLOCK_DIFFICULTY)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


port = input(f"Enter port to use(default={cfg.DEFAULT_PORT}): ") or cfg.DEFAULT_PORT
max_clients = input("Enter the max amount of clients that can connect \
to you (default=1): ") or 1

network = P2P(int(port), int(max_clients))
network.create_session("10.255.196.46")

print("""
    If you're using any vpn or proxy, please turn it off
    1. Connect to peer
    2. Broadcast message (public, manual)
    3. Sync with other peers (manual)
    4. Discover other peers (manual)
    5. List peers
    6. Exit
""")
