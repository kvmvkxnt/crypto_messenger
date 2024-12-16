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
