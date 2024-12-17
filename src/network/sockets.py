import socket
import threading
from utils import logger
import json5 as json
import time
import zlib

log = logger.Logger("sockets")


class P2PSocket:
    def __init__(self, host: str, port: int, blockchain, sync_manager, signature_manager, max_connections: int = 5):
        """Инициализация сокета для P2P соединений."""
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # Список активных подключений
        self.blockchain = blockchain
        self.sync_manager = sync_manager
        self.signature_manager = signature_manager
        self.lock = threading.Lock()



    def start_server(self):
        """Запуск сервера для приема подключений."""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.max_connections)
            log.debug(f"Server started at {self.host}:{self.port}")
        except socket.error as e:
            log.error(f"Could not bind socket: {e}")
            return

        while True:
            try:
                conn, addr = self.socket.accept()
                if len(self.connections) >= self.max_connections:
                    log.warning(
                        f"Maximum connections reached. Connection from {addr} rejected"
                    )
                    conn.close()
                    continue
                self.connections.append((conn, addr))
                log.info(f"Connection established with {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
            except socket.error as e:
                log.error(f"Error accepting connection: {e}")
                return

    def handle_client(self, conn, addr):
        """Обработка клиента."""
        try:
            while True:
                try:
                    chunks = []
                    while True:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break  # Соединение закрыто
                        chunks.append(chunk)
                        if len(chunk) < 4096:
                            break # последний чанк+m
                    if not chunks:
                        break # Выходим из цикла обработки, если нет данных

                    data = b"".join(chunks)

                    data = zlib.decompress(data)

                    log.debug(f"Received from {addr}: {data[:100].decode()}")

                    if data.startswith(b"NEW_BLOCK"):
                        block_data = data[len(b"NEW_BLOCK") :]
                        self.sync_manager.handle_new_block(block_data, conn)

                    elif data.startswith(b"REQUEST_CHAIN_LENGTH"):
                        length = str(len(self.blockchain.chain)).encode()
                        self.broadcast(length, conn)

                    elif data.startswith(b"REQUEST_CHAIN"):
                        print("break1")
                        chain_data = json.dumps(
                            [block.to_dict() for block in self.blockchain.chain]
                        ).encode()
                        print("break2")
                        try:
                            self.broadcast(b"BLOCKCHAIN" + chain_data, conn)
                            print("break3")
                        except socket.error as e:
                            log.error(f"Error sending blockchain to {addr}: {e}")
                            break
                        log.debug(f"Sent blockchain to {addr}")

                    elif data.startswith(b"BLOCKCHAIN"):
                        blockchain = data[len(b"BLOCKCHAIN") :]
                        self.sync_manager.handle_blockchain(blockchain)


                    elif data.startswith(b"NEW_TRANSACTION"):
                        transaction_data = data[len(b"NEW_TRANSACTION") :]
                        self.sync_manager.handle_new_transaction(transaction_data, conn)

                    elif data.startswith(b"NEW_MESSAGE"):
                        pass

                    else:  # Простое сообщение
                        self.broadcast(data, conn)

                except ConnectionResetError as e:
                    break # Выходим из цикла обработки клиента
                except socket.error as e:
                    log.error(f"Error receiving data from {addr}: {e}")
                    break

        except Exception as e:
            log.error(f"Error with client {addr}: {e}")
        finally:
            self.connections.remove((conn, addr))
            log.info(f"Connection closed with {addr}")
            conn.close()

    def broadcast(self, message: bytes, sender_conn):
        """Отправка сообщения всем подключенным клиентам, кроме отправителя."""
        for conn, _ in self.connections:
            if conn != sender_conn:
                try:
                    conn.sendall(zlib.compress(message))
                except socket.error as e:
                    log.error(f"Error broadcasting to a connection: {e}")

    def connect_to_peer(self, peer_host: str, peer_port: int):
        """Подключение к другому узлу."""
        try:
            conn = socket.create_connection((peer_host, peer_port))
            if len(self.connections) >= self.max_connections:
                log.warning(
                    f"Maximum connections reached. Connection to {peer_host}:{peer_port} rejected"
                )
                conn.close()
                return None
            self.connections.append((conn, (peer_host, peer_port)))
            threading.Thread(
                target=self.handle_client, args=(conn, (peer_host, peer_port))
            ).start()
            log.info(f"Connected to peer {peer_host}:{peer_port}")
            return conn
        except socket.error as e:
            log.error(f"Error connecting to peer {peer_host}:{peer_port}: {e}")
            # self.node.peers.remove((peer_host, peer_port))
            # log.info(f'Removed peer {peer_host}:{peer_port} due to connection error')
            return None

    def get_connection(self, peer_host: str):
        """Возвращает существующее соединение или None, если его нет."""
        for conn, addr in self.connections:
            if addr[0] == peer_host:
                return conn
        return None


if __name__ == "__main__":
    choice = input("Start as (s)erver or (c)lient? ")
    host = "127.0.0.1"
    port = 12345
    max_connections = 5

    if choice.lower() == "s":
        server = P2PSocket(host, port, max_connections)
        server.start_server()
    elif choice.lower() == "c":
        client = P2PSocket(host, port, max_connections)
        peer_host = input("Enter peer host: ")
        peer_port = int(input("Enter peer port: "))
        client.connect_to_peer(peer_host, peer_port)

        while True:
            message = input("Enter message: ")
            with client.lock:
                for conn in client.connections:
                    try:
                        conn.send(message.encode())
                    except socket.error as e:
                        log.error(f"Error sending message: {e}")
