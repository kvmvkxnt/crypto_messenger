import socket
import json

# Константы
SERVER_HOST = "85.234.107.233"
SERVER_PORT = 5050
BUFFER_SIZE = 1024


def request_peers():
    """
    Отправляет запрос get_peers на сервер и выводит полученный список.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            client_socket.sendall("get_peers".encode())
            response = client_socket.recv(BUFFER_SIZE)
            if response:
                peers_list = json.loads(response.decode())
                print("Received peers list:")
                for peer in peers_list:
                    print(peer)
            else:
                print("No response from server.")

    except Exception as e:
        print(f"Error requesting peers: {e}")

def new_peer():
    """
    Отправляет запрос new_peer на сервер и выводит полученный список.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            client_socket.sendall("new_peer".encode())
            response = client_socket.recv(BUFFER_SIZE)
            if response:
                if response == 'success':
                    print('Successfully added to peers')
            else:
                print("No response from server.")

    except Exception as e:
        print(f"Error requesting peers: {e}")


if __name__ == "__main__":
    request_peers()