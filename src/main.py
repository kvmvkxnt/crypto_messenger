from blockchain.blockchain import Block, Blockchain
from blockchain.consensus import ProofOfWork, Validator
from blockchain.transaction import Transaction
from crypto.diffie_hellman import DiffieHellmanKeyExchange
from crypto.encryption import SymmetricEncryption
from crypto.signatures import DigitalSignature
from network.p2p import P2PNetwork
from network.sockets import P2PSocket
from network.discovery import discover_peers
from network.sync import SyncManager
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


host = input(f"Enter your host(default={get_ip()}): ") or get_ip()
log.debug(f"Got host: {host}")

port = input(f"Enter your port(default={cfg.DEFAULT_PORT}): ") or \
    cfg.DEFAULT_PORT
log.debug(f"Selected port: {port}")

broadcast_port = input(f"Enter your broadcast \
port(default={cfg.BROADCAST_PORT}): ") or cfg.BROADCAST_PORT
log.debug(f"Selected broadcast port: {broadcast_port}")

network = P2PNetwork(P2PSocket(host, int(port)), int(broadcast_port))
sync_manager = SyncManager(network, blockchain)

network.start()

print("""
    If you're using any vpn or proxy, please turn it off
    1. Connect to peer
    2. Broadcast message (public, manual)
    3. Sync with other peers (manual)
    4. Discover other peers (manual)
    5. List peers
    6. Exit
""")

while True:
    try:
        user_input = int(input("Choice: "))
    except ValueError:
        print("Not an option. Please, choose another")
        continue

    if user_input > 6 or user_input < 1:
        print("Not an option. Please, choose another")
    elif user_input == 6:
        break
    elif user_input == 5:
        print(network.peers)
        if len(network.peers):
            for i in network.peers:
                print(i)
        else:
            print("No peers")
    elif user_input == 4:
        network.discover_peers(discover_peers)
    elif user_input == 2:
        message = input("Enter a message: ")
        network.broadcast_message(message)
    elif user_input == 1:
        peer_host = input("Enter peer's ip: ")
        peer_port = int(input("Enter peer's port: "))
        network.connect_to_peer(peer_host, peer_port)
