# main.py
import os
import sys
import time
import hashlib
import json
import socket

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
from cryptography.hazmat.primitives.serialization import load_pem_public_key


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
    public_key = signer.public_key


    return address, dh_key_exchange, signer, private_key_pem, public_key

def main():
    rv_host = '85.234.107.233'
    rv_port = 5050
    peers_list = []

    host = "0.0.0.0"
    port = 12345
    broadcast_port = 5000
    sync_interval = 5
    max_connections = 5
    broadcast_interval = 2
    discovery_timeout = 5

    print('Generating keys...')
    address, dh_key_exchange, signer, private_key_pem, public_key = generate_keys()

    node = P2PSocket(host, port, max_connections)
    blockchain = Blockchain()
    p2p_network = P2PNetwork(node, blockchain, broadcast_port, sync_interval, broadcast_interval, discovery_timeout)
    sync_manager = p2p_network.sync_with_peers()
    node.sync_manager = sync_manager
    node.node = p2p_network
    node.blockchain = blockchain

    p2p_network.signer = signer
    p2p_network.start()
    # p2p_network.discover_peers() # <--- кривовато работает


    log.info(f"Your address: {address}")

    shared_keys = {}
    peers_public_keys = {}

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

    def request_peer_public_key(conn, peer_address):
        """Requests public key from peer"""
        try:
            with node.lock:
                conn.send(b"REQUEST_PUBLIC_KEY")
            response = conn.recv(4096)
            if response:
                try:
                    public_key = load_pem_public_key(response)
                    peers_public_keys[peer_address] = public_key # rsa.RSAPublicKey
                    log.info(f"Received public key from {peer_address}: {response.hex() if response else 'None'}")
                except Exception as e:
                    log.error(f"Error during loading peer public key: {e}")
            else:
                log.error(f"Cannot obtain public key from {peer_address}")

        except Exception as e:
            log.error(f"Error during obtaining public key: {e}")


    def request_peers():
        """
        Отправляет запрос get_peers на сервер и выводит полученный список.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((rv_host, rv_port))
                client_socket.sendall(b"GET_PEERS")
                response = client_socket.recv(4096)
                if response:
                    peers_list = json.loads(response.decode())
                    print(f"Received peers list: {peers_list}")
                    return peers_list
                else:
                    print("No response from rendez-vous server.")
                    return []

        except Exception as e:
            print(f"Error requesting peers: {e}")

    def new_peer():
        """
        Отправляет запрос new_peer на сервер и выводит полученный список.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((rv_host, rv_port))
                message = b"NEW_PEER" + str(port).encode()
                client_socket.sendall(message)
        except Exception as e:
            print(f"Error adding to peers: {e}")
    def invalid_peer(address, port):
        """
        Отправляет запрос new_peer на сервер и выводит полученный список.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((rv_host, rv_port))
                message = b"INVALID_PEER" + f'{address}:{port}'.encode()
                client_socket.sendall(message)
        except Exception as e:
            print(f"Error sending invalid peer: {e}")
    
    peers_list = request_peers()
    new_peer()
    for peer in peers_list:
        conn = p2p_network.connect_to_peer(peer[0], int(peer[1]))
        if not conn:
            invalid_peer(peer[0], int(peer[1]))
            continue
        with node.lock:
            conn.send(b"INCOME_PORT" + str(port).encode())  ## Для двустороннего подключения
            time.sleep(0.05)

    while True:
        command = input("Enter command (connect, message, send, mine, balance, peers, chain, exit): ")
        if command == "connect":
            peer_host = input("Enter peer host: ")
            peer_port = int(input("Enter peer port: "))

            p2p_network.connect_to_peer(peer_host, peer_port)
            conn = p2p_network.node.get_connection(peer_host, peer_port)
            if conn:
                with node.lock:
                    conn.send(b"INCOME_PORT" + str(port).encode())  ## Для двустороннего подключения
                    time.sleep(0.05)

            # peer_address = get_peer_address(peer_host, peer_port)
            # conn = p2p_network.node.get_connection(peer_host, peer_port)
            # if conn:
            #     request_peer_public_key(conn, peer_address)
            # else:
            #     log.error(f"Cannot obtain public key from {peer_address}") ### Обмен ключами - доделать

        elif command == "message":
            recipient = input("Enter recipient address: ")
            content = input("Enter message content: ")

            shared_key = get_shared_key(recipient)

            if shared_key:
                encryptor = SymmetricEncryption(shared_key, algorithm="AES", mode="GCM")
                encrypted_content = encryptor.encrypt(content)
                if encrypted_content:
                    log.debug("Creating signed encrypted transaction")
                    transaction = Transaction(address, recipient, 0, encrypted_content.hex(), public_key)
                    transaction.sign_transaction(signer.private_key)
                    blockchain.add_transaction(transaction, p2p_network)
                else:
                    log.error("Message was not encrypted")
            else:
                log.debug("Creating signed transaction")
                transaction = Transaction(address, recipient, 0, content, public_key)
                transaction.sign_transaction(signer.private_key)
                blockchain.add_transaction(transaction, p2p_network)

        elif command == "send":
            recipient = input("Enter recipient address: ")
            amount = float(input("Enter amount to send (MEM): "))
            transaction = Transaction(address, recipient, amount, "", public_key)
            transaction.sender_public_key = public_key
            transaction.sign_transaction(signer.private_key)
            blockchain.add_transaction(transaction, p2p_network)
        elif command == "mine":
            blockchain.mine_pending_transactions(ProofOfWork, address, sync_manager)
        elif command == "balance":
             balance = blockchain.get_balance(address)
             print(f"Your balance: {balance} MEM")
        elif command == "peers":
            print(f"Known peers: {list(p2p_network.peers)}")
        elif command == 'chain':
            for block in blockchain.chain:
                print(block.to_dict())
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()