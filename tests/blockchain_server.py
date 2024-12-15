import socket
import threading
import json

# Константы
HOST = "0.0.0.0"  # Замените на свой IP-адрес, если необходимо
PORT = 5050
BUFFER_SIZE = 4096


class PeerServer:
    def __init__(self, host, port):
        """
        Инициализация сервера для обработки запросов о пирах.
        """
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peers = set()

    def start_server(self):
        """Запуск сервера."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Peer server listening on {self.host}:{self.port}")

            while True:
                conn, addr = self.server_socket.accept()
                # print(f"Connection from {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
        except Exception as e:
            print(f"Error starting peer server: {e}")
        finally:
            self.server_socket.close()

    def handle_client(self, conn, addr):
        """
        Обработка подключения клиента.
        """
        try:
            while True:
                message = conn.recv(BUFFER_SIZE)
                if not message:
                    break
                if message.startswith(b"GET_PEERS"):
                    self.send_peers(conn)
                elif message.startswith(b"NEW_PEER"):
                    port = message[len(b"NEW_PEER") :].decode()
                    self.add_peer(addr, port, conn)
                elif message.startswith(b"INVALID_PEER"):
                    peer = message[len(b"INVALID_PEER") :].decode()
                    address = (peer.split(':')[0], int(peer.split(':')[1]))
                    self.remove_peer(address)
                else:
                    print(f"Unknown message from {addr}: {message}")
        except Exception as e:
            pass
        finally:
            conn.close()

    def add_peer(self, peer, port):
        """
        Добавляет пира в список
        """
        self.peers.add((peer[0], port))
        print(f'New peer added: {(peer[0])}:{port}')

    def remove_peer(self, peer):
        """
        Удаляет пира из списка.
        """
        if peer in self.peers:
            if not self.is_peer_online(peer[0], peer[1]):
                self.peers.remove(peer)
        print(f'Removed invalid peer: {peer}')

    def send_peers(self, conn):
        """
        Отправляет список пиров клиенту.

        :param conn: сокетное соединение с клиентом
        """
        try:
            peers_list = list(self.peers)
            response = json.dumps(peers_list).encode()
            conn.sendall(response)
            print("Sent peers list to client.")
        except Exception as e:
            print(f"Error sending peers list: {e}")
        finally:
            conn.close()

    def is_peer_online(peer_ip, peer_port, timeout=5):
        """
        Проверяет, доступен ли пир в сети.

        Args:
            peer_ip (str): IP-адрес пира.
            peer_port (int): Порт пира.
            timeout (int): Время ожидания в секундах.

        Returns:
            bool: True, если пир доступен, False в противном случае.
        """
        try:
            with socket.create_connection((peer_ip, peer_port), timeout=timeout) as sock:
                return True
        except (socket.error, socket.timeout):
            return False


if __name__ == "__main__":
    server = PeerServer(HOST, PORT)
    server.start_server()
