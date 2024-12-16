import socket
import threading
import time
import utils.logger as logger
from typing import Set, Tuple
import json
import os

log = logger.Logger("discovery")


def discover_peers(
    local_host: str,
    local_port: int,
    broadcast_port: int,
    username: str,
    public_key: str,
    broadcast_interval: int = 1,
) -> Set[Tuple[str, int]]:
    """
    Обнаружение новых узлов в сети через UDP широковещательные сообщения.

    :param local_host: Локальный хост узла
    :param local_port: Локальный порт узла для приема сообщений
    :param broadcast_port: Порт для широковещательной рассылки
    :param broadcast_interval: Интервал отправки широковещательных сообщений
    :param timeout: таймаут
    """
    peers = set()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def listen_for_broadcast():
        """Слушает широковещательные сообщения для обнаружения новых узлов."""
        with sock as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                if os.name == "posix":
                    udp_socket.bind(('', broadcast_port))
                else:
                    udp_socket.bind((local_host, broadcast_port))
            except socket.error as e:
                log.error(f"Could not bind socket: {e}")
                return

            log.debug(f"Listening for broadcasts on {local_host}:{broadcast_port}")
            while True:
                try:
                    data, addr = udp_socket.recvfrom(4096)
                    peer_info = json.loads(data.decode())

                    peer_port = peer_info["port"]
                    try:
                        peer_port = int(peer_port)
                    except ValueError:
                        log.debug(f"Invalid peer port received: {peer_port}")
                        continue

                    peer = (addr[0], peer_port, peer_info["username"],
                            peer_info["public_key"])
                    if peer == (local_host, local_port, username, public_key):
                        log.debug(f"Ignoring self broadcast from {peer}")
                        continue

                    if peer not in peers:
                        peers.add(peer)
                        log.info(f"Discovered new peer: {peer_info} at {addr}")
                except socket.error as e:
                    log.error(f"Error in receiving broadcast: {e}")
                except UnicodeDecodeError as e:
                    log.error(f"Error decoding broadcast message: {e}")

    def send_broadcast():
        """
        Отправляет широковещательное сообщение
        для оповещения о своем узле.
        """
        with sock as udp_socket:
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            message = {"host": local_host, "port": local_port,
                       "public_key": public_key, "username": username}
            broadcast_address = ("<broadcast>", broadcast_port)

            while True:
                try:
                    udp_socket.sendto(json.dumps(message, ensure_ascii=False)
                                      .encode(), broadcast_address)
                    log.debug(f"Broadcasting: {message}")
                except socket.error as e:
                    log.error(f"Error in sending broadcast: {e}")
                finally:
                    time.sleep(
                        broadcast_interval
                    )  # Повторение каждые broadcast_interval секунд

    threading.Thread(target=listen_for_broadcast, daemon=True).start()
    threading.Thread(target=send_broadcast, daemon=True).start()

    return peers


if __name__ == "__main__":
    local_host = "127.0.0.1"
    local_port = 12345
    broadcast_port = 5000
    broadcast_interval = 2
    timeout = 10

    discovered_peers = discover_peers(
        local_host, local_port, broadcast_port, broadcast_interval, timeout
    )

    while True:
        command = input("Enter command (list, exit): ")
        if command == "list":
            print(f"Known peers: {list(discovered_peers)}")
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command.")
