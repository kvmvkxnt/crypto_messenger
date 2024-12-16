import threading
import utils.logger as logger
from .sockets import P2PSocket
from blockchain.transaction import Transaction
import json
from .discovery import discover_peers
from .sync import SyncManager

from blockchain.blockchain import Blockchain

log = logger.Logger("p2p")


class P2PNetwork:
    def __init__(
        self,
        host: str,
        port: int,
        node: P2PSocket,
        sync_manager,
        blockchain: Blockchain,
        broadcast_port: int,
        username: str,
        public_key: str,
        sync_interval: int = 5,
        broadcast_interval: int = 1,
        max_connections: int = 5
    ):
        """Инициализация P2P сети."""
        if not isinstance(node, P2PSocket):
            raise TypeError("Node must be an instance of P2PSocket")
        self.blockchain = blockchain
        self.host = host
        self.port = port
        self.username = username
        self.public_key = public_key
        self.broadcast_port = broadcast_port
        self.peers = set()  # Список известных узлов
        self.sync_interval = sync_interval
        self.broadcast_interval = broadcast_interval
        self.sync_manager = sync_manager
        self.node = node(self.host, self.port, self.blockchain, self.sync_manager, max_connections)


    def start(self):
        self.node.blockchain = self.blockchain  # Добавляем blockchain в node
        threading.Thread(target=self.node.start_server, daemon=True).start()
        log.info(f"Node started at {self.host}:{self.port}")

    def connect_to_peer(self, peer_host: str, peer_port: int):
        """Подключение к новому узлу."""
        try:
            if (
                self.host == peer_host or peer_host == "127.0.0.1"
            ) and self.port == peer_port:
                log.warning("Cannot connect to self")
                raise Exception("Cannot connect to self")
            conn = self.node.connect_to_peer(peer_host, peer_port)
            return conn
        except Exception as e:
            log.error(f"Error connecting to peer: {e}")

    def broadcast_message(self, message: str):
        """Рассылка сообщения всем подключенным узлам."""
        log.debug(f"Broadcasting message: {message}")
        self.node.broadcast(message.encode())

    def broadcast_transaction(self, transaction: Transaction):
        """Рассылает транзакцию всем подключенным узлам."""
        transaction_data = json.dumps(
            transaction.to_dict(), ensure_ascii=False
        ).encode()
        log.debug(f"Broadcasting transaction: {transaction.calculate_hash()}")
        self.broadcast_message(b"NEW_TRANSACTION" + transaction_data)

    def discover_peers(self):
        """Механизм обнаружения новых узлов."""
        self.peers = discover_peers(
            self.host,
            self.port,
            self.broadcast_port,
            self.username,
            self.public_key,
            self.broadcast_interval,
        )
        log.info(f"Discovered peers: {list(self.peers)}")

    def sync_with_peers(self):
        """Синхронизация данных с подключенными узлами."""
        self.sync_manager(self, self.blockchain, self.sync_interval).start_sync_loop()


if __name__ == "__main__":
    from blockchain.blockchain import Block
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
