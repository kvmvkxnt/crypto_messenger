import socket
import threading
import time
import utils.logger as logger

log = logger.Logger("discovery")


def discover_peers(local_host: str, local_port: int,
                   broadcast_port: int):
    """
    Обнаружение новых узлов в сети через UDP широковещательные сообщения.

    :param local_host: Локальный хост узла
    :param local_port: Локальный порт узла для приема сообщений
    :param broadcast_port: Порт для широковещательной рассылки
    """
    peers = set()

    def listen_for_broadcast():
        """Слушает широковещательные сообщения для обнаружения новых узлов."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind((local_host, broadcast_port))

            log.debug(f"Listening for broadcasts on {local_host}:{broadcast_port}")

            while True:
                try:
                    data, addr = udp_socket.recvfrom(1024)
                    peer_info = data.decode()
                    if addr not in peers:
                        peers.add(addr)
                        print(f"Discovered new peer: {peer_info} at {addr}")
                except Exception as e:
                    print(f"Error in receiving broadcast: {e}")

    def send_broadcast():
        """
            Отправляет широковещательное сообщение
            для оповещения о своем узле.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            message = f"Node at {local_host}:{local_port}"
            broadcast_address = ("<broadcast>", broadcast_port)

            while True:
                try:
                    udp_socket.sendto(message.encode(), broadcast_address)
                    log.debug(f"Broadcasting: {message}")
                except Exception as e:
                    print(f"Error in sending broadcast: {e}")
                finally:
                    time.sleep(1)  # Повторение каждые 5 секунд

    threading.Thread(target=listen_for_broadcast, daemon=True).start()
    threading.Thread(target=send_broadcast, daemon=True).start()

    return peers


#if __name__ == "__main__":
#    local_host = "127.0.0.1"
#    local_port = 12345
#    broadcast_port = 5000
#
#    discovered_peers = discover_peers(local_host, local_port, broadcast_port)
#
#    while True:
#        command = input("Enter command (list, exit): ")
#        if command == "list":
#            print(f"Known peers: {list(discovered_peers)}")
#        elif command == "exit":
#            print("Exiting...")
#            break
#        else:
#            print("Unknown command.")
