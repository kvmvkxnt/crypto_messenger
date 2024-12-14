<<<<<<< HEAD
=======
import socket
import threading
from utils import logger
import time
import json

log = logger.Logger("sockets")


class P2PSocket:
    def __init__(self, host: str, port: int, max_connections: int = 5):
        """Инициализация сокета для P2P соединений."""
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # Список активных подключений
        self.connections_info = []  # Список (connection, (host, port))
        self.lock = threading.Lock()
        self.node = None
        self.blockchain = None
        self.sync_manager = None

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
                with self.lock:
                    if len(self.connections) >= self.max_connections:
                        log.warning(
                            f"Maximum connections reached. Connection from {addr} rejected"
                        )
                        conn.close()
                        continue
                    self.connections.append(conn)
                log.info(f"Connection established with {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
            except socket.error as e:
                log.error(f"Error accepting connection: {e}")
                return

    def handle_client(self, conn, addr):
        """Обработка клиента."""

        with self.lock:
            if len(self.connections) >= self.max_connections:
                log.warning(
                    f"Maximum connections reached. Connection from {addr} rejected"
                )
                conn.close()
                return
            self.connections.append(conn)
            self.connections_info.append((conn, addr))

        self.node.peers.add(addr)  # <---- Добавляем пира в p2p.peers
        log.info(f"Connection established with {addr}")

        try:
            while True:
                try:
                    data = conn.recv(4096)
                    if not data:  # Соединение закрыто клиентом
                        break

                    log.debug(f"Received from {addr}: {data[:100].decode()}")

                    if data.startswith(b"NEW_BLOCK"):
                        block_data = data[len(b"NEW_BLOCK") :]
                        self.sync_manager.handle_new_block(block_data)

                    elif data.startswith(b"REQUEST_CHAIN"):
                        chain_data = json.dumps(
                            [block.__dict__ for block in self.blockchain.chain]
                        ).encode()

                        try:
                            conn.sendall(
                                chain_data
                            )  # Используем sendall для полной отправки
                            log.debug(f"Sent blockchain to {addr}")
                        except socket.error as e:
                            log.error(f"Error sending blockchain to {addr}: {e}")
                            break

                    elif data.startswith(b"NEW_TRANSACTION"):  # Обработка транзакций
                        transaction_data = data[len(b"NEW_TRANSACTION") :]
                        self.sync_manager.handle_new_transaction(transaction_data)

                    else:  # Простое сообщение
                        self.broadcast(data, conn)

                except socket.error as e:
                    log.error(f"Error receiving data from {addr}: {e}")
                    break

        except Exception as e:
            log.error(f"Error with client {addr}: {e}")

        finally:
            with self.lock:
                if conn in self.connections:
                    for i in range(len(self.connections_info)):
                        if self.connections_info[i][0] == conn:
                            del self.connections_info[i]
                            break
                    self.connections.remove(conn)

            log.info(f"Connection closed with {addr}")
            conn.close()

    def broadcast(self, message: bytes, sender_conn):
        """Отправка сообщения всем подключенным клиентам, кроме отправителя."""
        with self.lock:
            for conn in self.connections:
                if conn != sender_conn:
                    try:
                        conn.send(message)
                    except socket.error as e:
                        log.error(f"Error broadcasting to a connection: {e}")

    def connect_to_peer(self, peer_host: str, peer_port: int):
        """Подключение к другому узлу."""
        try:
            conn = socket.create_connection((peer_host, peer_port))
            with self.lock:
                if len(self.connections) >= self.max_connections:
                    log.warning(
                        f"Maximum connections reached. Connection to {peer_host}:{peer_port} rejected"
                    )
                    conn.close()
                    return None  # Возвращаем None, если не удалось подключиться
                self.connections.append(conn)
                self.connections_info.append(
                    (conn, (peer_host, peer_port))
                )  # Добавляем информацию о соединении
            threading.Thread(
                target=self.handle_client, args=(conn, (peer_host, peer_port))
            ).start()
            log.info(f"Connected to peer {peer_host}:{peer_port}")
            return conn  # Возвращаем соединение
        except socket.error as e:
            log.error(f"Error connecting to peer {peer_host}:{peer_port}: {e}")
            return None  # Возвращаем None при ошибке

    def get_connection(self, peer_host: str, peer_port: int):
        """Возвращает существующее соединение или None, если его нет."""
        with self.lock:
            for conn, addr in self.connections_info:
                if addr == (peer_host, peer_port):
                    return conn
            return None


if __name__ == "__main__":
    # Пример запуска сервера или клиента
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

        # Sending messages to peers
        while True:
            message = input("Enter message: ")
            with client.lock:
                for conn in client.connections:
                    try:
                        conn.send(message.encode())
                    except socket.error as e:
                        log.error(f"Error sending message: {e}")
>>>>>>> f00be1e2a327c1ed23561c21e9daeeb8f233859c
