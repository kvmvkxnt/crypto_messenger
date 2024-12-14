import threading
import time
import utils.logger as logger
log = logger.Logger("p2p")


class P2PNetwork:
    def __init__(self, node):
        """Инициализация P2P сети."""
        self.host = node.host
        self.port = node.port
        self.node = node
        self.peers = set()  # Список известных узлов

    def start(self):
        """Запуск узла в режиме сервера."""
        threading.Thread(target=self.node.start_server, daemon=True).start()
        log.debug(f"Node started at {self.host}:{self.port}")

    def connect_to_peer(self, peer_host: str, peer_port: int):
        """Подключение к новому узлу."""
        self.node.connect_to_peer(peer_host, peer_port)
        self.peers.add((peer_host, peer_port))
        log.info(f"Connected to peer: {peer_host}:{peer_port}")

    def broadcast_message(self, message: str):
        """Рассылка сообщения всем подключенным узлам."""
        print(f"Broadcasting message: {message}")
        for conn in self.node.connections:
            try:
                conn.send(message.encode())
            except Exception as e:
                log.error(f"Error broadcasting message: {e}")

    def discover_peers(self, discoverer: set):
        """Механизм обнаружения новых узлов."""
        # Заглушка: этот метод будет доработан в файле discovery.py
        # print("Discovering peers...")
        # time.sleep(2)
        # # Имитация обнаружения нового узла
        # new_peer = ("127.0.0.1", 54321)
        # self.peers.add(new_peer)
        # print(f"Discovered new peer: {new_peer}")
        # for item in discoverer(self.host, self.port):
        #    if item not in self.peers:
        #        self.peers.add(item)
        self.peers = discoverer(self.host, self.port)

    def sync_with_peers(self, sync_manager, blockchain):
        """Синхронизация данных с подключенными узлами."""
        # Заглушка: функциональность будет доработана в файле sync.py
        # print("Synchronizing with peers...")
        # time.sleep(1)
        # print("Synchronization complete.")
        return sync_manager(self, blockchain)


if __name__ == "__main__":
    from discovery import discover_peers
    from sync import SyncManager
    import os
    import sys

    parent_dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
    sys.path.append(parent_dir)
    from blockchain.blockchain import Blockchain, Block

    host = "10.255.196.200"
    port = 12345

    blockchain = Blockchain()
    new_block = Block(1, "ahfjdlasf", 0.2, [])
    blockchain.chain.append(new_block)

    p2p = P2PNetwork(host, port)
    p2p.start()

    while True:
        command = input("Enter command \
        (connect, broadcast, discover, sync, list peers, exit): ")
        if command == "connect":
            peer_host = input("Enter peer host: ")
            peer_port = int(input("Enter peer port: "))
            p2p.connect_to_peer(peer_host, peer_port)
        elif command == "broadcast":
            message = input("Enter message to broadcast: ")
            p2p.broadcast_message(message)
        elif command == "discover":
            p2p.discover_peers(discover_peers)
        elif command == "sync":
            sm = p2p.sync_with_peers(SyncManager, blockchain)
            sm.start_sync_loop()
            sm.broadcast_block(new_block.__repr__())
        elif command == "list peers":
            print(f"known peers: {list(p2p.peers)}")
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("No such command")
