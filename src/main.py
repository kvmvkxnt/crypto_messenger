<<<<<<< HEAD
from blockchain.blockchain import Block, Blockchain
#from blockchain.consensus import ProofOfWork, Validator
#from blockchain.transaction import Transaction
#from crypto.diffie_hellman import DiffieHellmanKeyExchange
#from crypto.encryption import SymmetricEncryption
#from crypto.signatures import DigitalSignature
from network.p2p import P2PNetwork
#from network.discovery import discover_peers
#from network.sync import SyncManager
from utils import config as cfg
from utils import logger
import socket
=======
import os
import sys
import time
import hashlib
import json

parent_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(parent_dir)

from network.p2p import P2PNetwork
from blockchain.blockchain import Blockchain
from network.sockets import P2PSocket
from blockchain.transaction import Transaction
from blockchain.consensus import ProofOfWork
from crypto.diffie_hellman import DiffieHellmanKeyExchange
from crypto.signatures import DigitalSignature
from crypto.encryption import SymmetricEncryption
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives import hashes
from utils.logger import Logger
>>>>>>> f00be1e2a327c1ed23561c21e9daeeb8f233859c

log = Logger("main")


def generate_address(public_key_bytes: bytes) -> str:
    """Generates address based on public key."""
    address_hash = hashlib.sha256(public_key_bytes).hexdigest()
    return address_hash[:32]

def generate_keys():
    """Generates keys for both DH and signature."""
    dh_key_exchange = DiffieHellmanKeyExchange()
    public_key_bytes = dh_key_exchange.get_public_key()
    address = generate_address(public_key_bytes)

    signer = DigitalSignature()
    private_key_pem = signer.get_private_key()
    public_key_pem = signer.get_public_key()

<<<<<<< HEAD
port = input(f"Enter your port(default={cfg.DEFAULT_PORT}): ") or \
    cfg.DEFAULT_PORT
log.debug(f"Selected port: {port}")
action = input("Choose action (connect, start): ")
p2p = P2PNetwork(host, port)
while True:
    if action == "start":
        p2p.start_server()
    elif action == "connect":
        peer_host = input("Enter peer host: ")
        peer_port = int(input("Enter peer port: "))
        p2p.connect(peer_host, peer_port)
    else:
        print("No such action")
#
#broadcast_port = input(f"Enter your broadcast \
#port(default={cfg.BROADCAST_PORT}): ") or cfg.BROADCAST_PORT
#log.debug(f"Selected broadcast port: {broadcast_port}")
#
#network = P2PNetwork(host, port, broadcast_port)
#sync_manager = SyncManager(network, blockchain)
#
#network.start()
#network.peers.add(('10.255.196.46', 12345))

# sync_manager.start_sync_loop()


#print("""
#    If you're using any vpn or proxy, please turn it off
#    1. Connect to peer
#    2. Broadcast message (public, manual)
#    3. Sync with other peers (manual)
#    4. Discover other peers (manual)
#    5. List peers
#    6. Exit
#""")
#
#while True:
#    try:
#        user_input = int(input("Choice: "))
#    except ValueError:
#        print("Not an option. Please, choose another")
#        continue
#
#    if user_input > 6 or user_input < 1:
#        print("Not an option. Please, choose another")
#    elif user_input == 6:
#        break
#    elif user_input == 5:
#        print(network.peers)
#        if len(network.peers):
#            for i in network.peers:
#                print(i)
#        else:
#            print("No peers")
#    elif user_input == 4:
#        network.discover_peers(discover_peers)
#    elif user_input == 2:
#        message = input("Enter a message: ")
#        network.broadcast(message.encode())
#    elif user_input == 1:
#        peer_host = input("Enter peer's ip: ")
#        peer_port = int(input("Enter peer's port: "))
#        network.connect_to_peer(peer_host, peer_port)
=======
    return address, dh_key_exchange, signer, private_key_pem, public_key_pem

def main():
    host = "127.0.0.1"
    port = int(input('Enter port: '))
    broadcast_port = 5000
    sync_interval = 10
    max_connections = 5
    broadcast_interval = 2
    discovery_timeout = 5

    node = P2PSocket(host, port, max_connections)
    blockchain = Blockchain()
    p2p_network = P2PNetwork(node, blockchain, broadcast_port, sync_interval, broadcast_interval, discovery_timeout)
    sync_manager = p2p_network.sync_with_peers()
    node.sync_manager = sync_manager
    node.node = p2p_network
    node.blockchain = blockchain

    p2p_network.start()
    p2p_network.discover_peers()

    # Generating keys using DH and signatures
    address, dh_key_exchange, signer, private_key_pem, public_key_pem = generate_keys()

    log.info(f"Your address: {address}")
    log.info(f"Your public key: {public_key_pem.hex()}")

    shared_keys = {}  # Stores shared keys with each peer
    peers_public_keys = {}  # Store public keys of known peers

    def get_shared_key(peer_address):
        """Retrieves existing shared key or generates new one."""
        if peer_address in shared_keys:
            return shared_keys[peer_address]

        peer_public_key_pem = peers_public_keys.get(peer_address)
        if peer_public_key_pem:
            derived_key = dh_key_exchange.generate_shared_key(peer_public_key_pem)
            if derived_key:
                shared_keys[peer_address] = derived_key
                return derived_key
        return None

    def get_peer_address(peer_host, peer_port):
        """Return peer address"""
        return f"{peer_host}:{peer_port}"

    def request_peer_public_key(conn, peer_address):
        """Requests public key from peer"""
        try:
            conn.send(b"REQUEST_PUBLIC_KEY")  # Request public key from peer
            response = conn.recv(4096)
            if response:
                peers_public_keys[peer_address] = response
                log.info(f"Received public key from {peer_address}: {response.hex() if response else 'None'}")
            else:
                log.error(f"Cannot obtain public key from {peer_address}")

        except Exception as e:
            log.error(f"Error during obtaining public key: {e}")

    while True:
        command = input("Enter command (connect, broadcast, message, send, mine, balance, list peers, exit): ")
        if command == "connect":
            peer_host = input("Enter peer host: ")
            peer_port = int(input("Enter peer port: "))

            p2p_network.connect_to_peer(peer_host, peer_port)
            peer_address = get_peer_address(peer_host, peer_port)

            conn = p2p_network.node.get_connection(peer_host, peer_port)
            if conn:
                request_peer_public_key(conn, peer_address)
            else:
                log.error(f"Cannot obtain public key from {peer_address}")

        elif command == "broadcast":
            message = input("Enter message to broadcast: ")
            p2p_network.broadcast_message(message)
        elif command == "message":
            recipient = input("Enter recipient address: ")
            content = input("Enter message content: ")

            shared_key = get_shared_key(recipient)

            if shared_key:
                encryptor = SymmetricEncryption(shared_key, algorithm="AES", mode="GCM")
                encrypted_content = encryptor.encrypt(content)
                if encrypted_content:
                    log.debug("Creating signed encrypted transaction")
                    transaction = Transaction(address, recipient, 0, encrypted_content.hex())
                    transaction.sender_public_key = public_key_pem
                    transaction.sign_transaction(private_key_pem)
                    blockchain.add_transaction(transaction, p2p_network)
                else:
                    log.error("Message was not encrypted")
            else:
                log.debug("Creating signed transaction")
                transaction = Transaction(address, recipient, 0, content)
                transaction.sender_public_key = public_key_pem
                transaction.sign_transaction(private_key_pem)
                blockchain.add_transaction(transaction, p2p_network)

        elif command == "send":
            recipient = input("Enter recipient address: ")
            amount = float(input("Enter amount to send: "))
            transaction = Transaction(address, recipient, amount)
            transaction.sender_public_key = public_key_pem
            transaction.sign_transaction(private_key_pem)
            blockchain.add_transaction(transaction, p2p_network)
        elif command == "mine":
            blockchain.mine_pending_transactions(ProofOfWork, address)
        elif command == "balance":
            balance = blockchain.get_balance(address)
            print(f"Your balance: {balance}")
        elif command == "list peers":
            print(f"Known peers: {list(p2p_network.peers)}")
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()
>>>>>>> f00be1e2a327c1ed23561c21e9daeeb8f233859c
