import threading
import time
import utils.logger as logger
from .sockets import P2PSocket
from blockchain.transaction import Transaction
import json
import socket
from .discovery import discover_peers
from .sync import SyncManager
import os
import sys

parent_dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
sys.path.append(parent_dir)
from blockchain.blockchain import Blockchain, Block

log = logger.Logger("p2p")


class P2PNetwork:
    def __init__(
        self,
        node: P2PSocket,
        blockchain: Blockchain,
        broadcast_port: int,
        sync_interval: int = 5,
        broadcast_interval: int = 1,
        discovery_timeout: int = 5,
    ):
        """Инициализация P2P сети."""
        if not isinstance(node, P2PSocket):
            raise TypeError("Node must be an instance of P2PSocket")
        self.blockchain = blockchain
        self.host = node.host
        self.port = node.port
        self.broadcast_port = broadcast_port
        self.node = node
        self.peers = set()  # Список известных узлов
        self.sync_interval = sync_interval
        self.broadcast_interval = broadcast_interval
        self.discovery_timeout = discovery_timeout
        self.signer = None

    def start(self):
        self.node.blockchain = self.blockchain  # Добавляем blockchain в node
        threading.Thread(target=self.node.start_server, daemon=True).start()
        log.info(f"Node started at {self.host}:{self.port}")

    def connect_to_peer(self, peer_host: str, peer_port: int):
        """Подключение к новому узлу."""
        try:
            self.node.connect_to_peer(peer_host, peer_port)
            self.peers.add((peer_host, peer_port))
        except Exception as e:
            log.error(f"Error connecting to peer: {e}")

    def broadcast_message(self, message: str):
        """Рассылка сообщения всем подключенным узлам."""
        log.debug(f"Broadcasting message: {message}")
        for conn in self.node.connections:
            try:
                conn.send(message.encode())
            except Exception as e:
                log.error(f"Error broadcasting message: {e}")

    def broadcast_transaction(self, transaction: Transaction):
        """Рассылает транзакцию всем подключенным узлам."""
        transaction_data = json.dumps(transaction.to_dict()).encode()
        log.debug(f"Broadcasting transaction: {transaction.calculate_hash()}")
        for conn in self.node.connections:
            try:
                conn.sendall(b"NEW_TRANSACTION" + transaction_data)
            except socket.error as e:
                log.error(f"Error broadcasting transaction: {e}")

    def discover_peers(self):
        """Механизм обнаружения новых узлов."""
        discovered = discover_peers(
            self.host,
            self.port,
            self.broadcast_port,
            self.broadcast_interval,
            self.discovery_timeout,
        )
        self.peers.update(discovered)
        log.info(f"Discovered peers: {list(self.peers)}")

    def sync_with_peers(self):
        """Синхронизация данных с подключенными узлами."""
        sync_manager = SyncManager(
            self, self.blockchain
        )  # Используем blockchain из self
        sync_manager.start_sync_loop()
        return sync_manager


if __name__ == "__main__":

    host = "127.0.0.1"
    port = 12345
    broadcast_port = 5000
    sync_interval = 10
    broadcast_interval = 2
    discovery_timeout = 5

    node = P2PSocket(host, port)
    blockchain = Blockchain()
    new_block = Block(1, "ahfjdlasf", 0.2, [])
    blockchain.chain.append(new_block)

    p2p = P2PNetwork(
        node, broadcast_port, sync_interval, broadcast_interval, discovery_timeout
    )
    p2p.start()

    while True:
        command = input(
            "Enter command \
        (connect, broadcast, discover, sync, list peers, exit): "
        )
        if command == "connect":
            peer_host = input("Enter peer host: ")
            peer_port = int(input("Enter peer port: "))
            p2p.connect_to_peer(peer_host, peer_port)
        elif command == "broadcast":
            message = input("Enter message to broadcast: ")
            p2p.broadcast_message(message)
        elif command == "discover":
            p2p.discover_peers()
        elif command == "sync":
            sm = p2p.sync_with_peers(blockchain)
            sm.broadcast_block(new_block.__repr__())
        elif command == "list peers":
            print(f"known peers: {list(p2p.peers)}")
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command.")
