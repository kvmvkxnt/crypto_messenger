import socket

class P2PNetwork:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
        with self.socket as sock:
            sock.bind((self.host, self.port))
            sock.listen()
            conn, addr = sock.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.sendall(data)

    def connect(self, peer_host: str, peer_port: int):
        with self.socket as sock:
            sock.connect((peer_host, peer_port))
            sock.sendall(b"Hello world")
            data = sock.recv(1024)

        print(f"Recieved: {data}")

