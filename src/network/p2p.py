import threading
import socket
import utils.logger as logger

log = logger.Logger("p2p")


class P2PNetwork:
    def __init__(self, host, port, broadcast_port):
        """Инициализация P2P сети."""
        self.host = host
        self.port = port
        self.broadcast_port = broadcast_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # Acrive connections list
        self.peers = set()  # Список известных узлов

    def start(self):
        print(f"Node started at {self.host}:{self.port}")
        threading.Thread(target=self.start_server, daemon=True).start()

    def start_server(self):
        """Запуск узла в режиме сервера."""
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        log.debug(f"Server started at {self.host}:{self.port}")

        while True:
            conn, addr = self.socket.accept()
            print(f"Connection estabilished with {addr}")
            self.connections.append((conn, addr))
            threading.Thread(target=self.handle_client, args=(conn, addr)) \
                     .start()

    def handle_client(self, conn, addr):
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"Recieved from {addr}: {data.encode()}")
                self.broadcast(data, conn)
        except Exception as e:
            print(f"Error with client {addr}: {e}")
        finally:
            print(f"Connection closed with {addr}")
            self.connection.remove((conn, addr))
            conn.close()

    def broadcast(self, message: bytes, sender_conn):
        for conn in self.connections:
            if list(conn)[0] != sender_conn:
                try:
                    conn.send(message)
                except Exception as e:
                    print(f"Error broadcasting to a connection: {e}")

    def connect_to_peer(self, peer_host: str, peer_port: int):
        """Подключение к новому узлу."""
        try:
            if (peer_host, peer_port) not in self.peers:
                conn, addr = socket.create_connection((peer_host, peer_port))
                self.connections.append((conn, addr))
                self.peers.add((peer_host, peer_port))
                threading.Thread(target=self.handle_client,
                                 args=(conn, (peer_host, peer_port))).start()
                print(f"Connected to peer(addr={addr}): \
{peer_host}:{peer_port}")
            elif len(self.connections) and [conn for conn in self.connections if peer_host == conn[1].split(":")[0]][0]:
                return
            else:
                conn, addr = socket.create_connection((peer_host, peer_port))
                self.connections.append((conn, addr))
                threading.Thread(target=self.handle_client,
                                 args=(conn, (peer_host, peer_port))).start()
                print(f"Connected to peer(addr={addr}): \
{peer_host}:{peer_port}")

        except Exception as e:
            print(f"Error connecting to peer \
{peer_host}:{peer_port}: {e}")

    def discover_peers(self, discoverer: set):
        """Механизм обнаружения новых узлов."""
        # Заглушка: этот метод будет доработан в файле discovery.py
        self.peers = discoverer(self.host, self.port, self.broadcast_port)

    def sync_with_peers(self, sync_manager, blockchain):
        """Синхронизация данных с подключенными узлами."""
        # Заглушка: функциональность будет доработана в файле sync.py
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
            print("Unknown command.")
