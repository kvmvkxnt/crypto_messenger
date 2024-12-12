import threading
import time
from sockets import P2PSocket


class P2PNetwork:
    def __init__(self, host: str, port: int):
        """Инициализация P2P сети."""
        self.host = host
        self.port = port
        self.node = P2PSocket(host, port)
        self.peers = set()  # Список известных узлов

    def start(self):
        """Запуск узла в режиме сервера."""
        threading.Thread(target=self.node.start_server, daemon=True).start()
        print(f"Node started at {self.host}:{self.port}")

    def connect_to_peer(self, peer_host: str, peer_port: int):
        """Подключение к новому узлу."""
        self.node.connect_to_peer(peer_host, peer_port)
        self.peers.add((peer_host, peer_port))
        print(f"Connected to peer: {peer_host}:{peer_port}")

    def broadcast_message(self, message: str):
        """Рассылка сообщения всем подключенным узлам."""
        print(f"Broadcasting message: {message}")
        for conn in self.node.connections:
            try:
                conn.send(message.encode())
            except Exception as e:
                print(f"Error broadcasting message: {e}")

    def discover_peers(self):
        """Механизм обнаружения новых узлов."""
        # Заглушка: этот метод будет доработан в файле discovery.py
        print("Discovering peers...")
        time.sleep(2)
        # Имитация обнаружения нового узла
        new_peer = ("127.0.0.1", 54321)
        self.peers.add(new_peer)
        print(f"Discovered new peer: {new_peer}")

    def sync_with_peers(self):
        """Синхронизация данных с подключенными узлами."""
        # Заглушка: функциональность будет доработана в файле sync.py
        print("Synchronizing with peers...")
        time.sleep(1)
        print("Synchronization complete.")


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 12345

    p2p = P2PNetwork(host, port)
    p2p.start()

    while True:
        command = input("Enter command \
        (connect, broadcast, discover, sync, exit): ")
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
            p2p.sync_with_peers()
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command.")
