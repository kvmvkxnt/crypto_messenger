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
from cryptography.hazmat.primitives.asymmetric import rsa

log = logger.Logger("main")
blockchain = Blockchain(Validator.validate_blockchain, cfg.BLOCK_DIFFICULTY)


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


# sm = SyncManager
# syncronizer = network.sync_with_peers(sm, blockchain, Block, Transaction)
# syncronizer.start_sync_broad()
# new_block = Block(blockchain.get_latest_block().index + 1,
#                   blockchain.get_latest_block().hash,
#                   blockchain.get_latest_block().timestamp + 1,
#                   [])
# blockchain.chain.append(new_block)
# syncronizer.add_block(new_block)
# new_transaction1 = Transaction("bob", "alex", 100, "hello")
# private_key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=2048
# )
# public_key = private_key.public_key()
# new_transaction1.sign_transaction(private_key)
# blockchain.add_transaction(new_transaction1)
# syncronizer.add_transaction(new_transaction1)
# new_transaction2 = Transaction("alex", "bob", 50, "hi")
# new_transaction2.sign_transaction(private_key)
# blockchain.add_transaction(new_transaction2)
# syncronizer.add_transaction(new_transaction2)

host = input(f"Enter your host(default={get_ip()}): ") or get_ip()
log.debug(f"Got host: {host}")

port = input(f"Enter your port(default={cfg.DEFAULT_PORT}): ") or \
    cfg.DEFAULT_PORT
log.debug(f"Selected port: {port}")

broadcast_port = input(f"Enter your broadcast \
port(default={cfg.BROADCAST_PORT}): ") or cfg.BROADCAST_PORT
log.debug(f"Selected broadcast port: {broadcast_port}")

key_manager = DiffieHellmanKeyExchange()
user_public_key = key_manager.get_public_key()
network = P2PNetwork(P2PSocket(host, int(port)), int(broadcast_port), user_public_key)
network.start()

print(f"This is your public key: {user_public_key}")
network.discover_peers(discover_peers, user_public_key)


def startChat(peer):
    network.connect_to_peer(peer[0], peer[1], peer[2])
    chat_shared_key = key_manager.generate_shared_key(peer[2])
    print('break')
    encryptor = SymmetricEncryption(chat_shared_key)
    while True:
        message = input("Message: ")
        encrypted_message = encryptor.encrypt(message)
        network.broadcast_message(encrypted_message)


while True:
    user_input = input("Command (start_chat, list_peers, list_full): ")

    if user_input == "list_full":
        for i, val in enumerate(network.peers):
            print("ID:", i, "    IP:", val[0], "    PORT:", val[1], "    PUBLIC_KEY:",
                  val[2].decode())
    elif user_input == "start_chat":
        chat = input("Input peer id or peer public_key: ")
        try:
            if len(network.peers) and len(network.peers) >= int(chat):
                startChat(list(network.peers)[int(chat)])
        except ValueError:
            peer_public_key = str.encode(chat)

            try:
                peer = [p for p in network.peers if peer_public_key == p[2]]
                if len(peer) != 0:
                    startChat(peer[0])
            except Exception as e:
                print(f"error ocured: {e}")

    elif user_input == "list_peers":
        for i, val in enumerate(network.peers):
            print("ID:", i, "    IP:", val[0], "    PORT:", val[1], "    PUBLIC_KEY:",
                  val[2].decode()[27:37] + "..." + val[2].decode()[-36:-26])

# print("""
#     If you're using any vpn or proxy, please turn it off
#     1. Connect to peer
#     2. Broadcast message (public, manual)
#     3. Sync with other peers (manual)
#     4. Discover other peers (manual)
#     5. List peers
#     6. Show chain
#     7. Show pending transactions
#     8. Exit
# """)
#
# while True:
#     try:
#         user_input = int(input("Choice: "))
#     except ValueError:
#         print("Not an option. Please, choose another")
#         continue
#
#     if user_input > 8 or user_input < 1:
#         print("Not an option. Please, choose another")
#     elif user_input == 8:
#         break
#     elif user_input == 7:
#         print(blockchain.pending_transactions)
#     elif user_input == 6:
#         print(blockchain.chain)
#     elif user_input == 5:
#         if len(network.peers):
#             print(network.peers)
#         else:
#             print("No peers")
#     elif user_input == 4:
#         message = input("Enter a message: ")
#         network.broadcast_message(message)
#     elif user_input == 1:
#         peer_host = input("Enter peer's ip: ")
#         peer_port = int(input("Enter peer's port: "))
#         network.connect_to_peer(peer_host, peer_port)
