import socket
import threading
from utils import logger

log = logger.Logger("sockets")


class P2PSocket:
    def __init__(self, host: str, port: int):
        """Инициализация сокета для P2P соединений."""
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # Список активных подключений
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.requests = []

    def start_server(self):
        """Запуск сервера для приема подключений."""
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        log.debug(f"Server started at {self.host}:{self.port}")

        while True:
            conn, addr = self.socket.accept()
            print(f"Connection established with {addr}")
            self.connections.append(conn)
            threading.Thread(target=self.handle_client,
                             args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        """Обработка клиента."""
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                self.requests.append(data.decode())
                print(f"Received from {addr}: {data.decode()}")
                break
                self.broadcast(data, conn)
        except Exception as e:
            print(f"Error with client {addr}: {e}")
        finally:
            print(f"Connection closed with {addr}")
            self.connections.remove(conn)
            conn.close()

    def broadcast(self, message: bytes, sender_conn):
        """Отправка сообщения всем подключенным клиентам, кроме отправителя."""
        for conn in self.connections:
            if conn != sender_conn:
                try:
                    conn.send(message)
                except Exception as e:
                    print(f"Error broadcasting to a connection: {e}")

    def connect_to_peer(self, peer_host: str, peer_port: int):
        """Подключение к другому узлу."""
        try:
            conn = socket.create_connection((peer_host, peer_port))
            self.connections.append(conn)
            threading.Thread(target=self.handle_client,
                             args=(conn, (peer_host, peer_port))).start()
            print(f"Connected to peer {peer_host}:{peer_port}")
            return conn
        except Exception as e:
            print(f"Error connecting to peer {peer_host}:{peer_port}: {e}")


if __name__ == "__main__":
    # Пример запуска сервера или клиента
    choice = input("Start as (s)erver or (c)lient? ")
    host = "10.255.196.200"
    port = 12345

    if choice.lower() == 's':
        server = P2PSocket(host, port)
        server.start_server()
    elif choice.lower() == 'c':
        client = P2PSocket(host, port)
        peer_host = input("Enter peer host: ")
        peer_port = int(input("Enter peer port: "))
        client.connect_to_peer(peer_host, peer_port)

        # Sending messages to peers
        while True:
            message = input("Enter message: ")
            for conn in client.connections:
                conn.send(message.encode())
