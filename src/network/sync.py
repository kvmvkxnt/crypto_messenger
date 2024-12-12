import json
import threading
import time


class SyncManager:
    def __init__(self, p2p_network, blockchain):
        """
        Инициализация менеджера синхронизации.

        :param p2p_network: Экземпляр P2PNetwork для взаимодействия с узлами
        """
        self.p2p_network = p2p_network
        self.blockchain = blockchain  # Локальная копия блокчейна

    def request_chain(self, peer_host: str, peer_port: int):
        """
        Запрашивает копию блокчейна у указанного узла.

        :param peer_host: Хост узла
        :param peer_port: Порт узла
        """
        print(f"Requesting blockchain from {peer_host}:{peer_port}")
        try:
            conn = self.p2p_network.node.connect_to_peer(peer_host, peer_port)
            conn.send(b"REQUEST_CHAIN")
            response = conn.recv(4096).decode()
            received_chain = json.loads(response)
            print(f"Received chain from {peer_host}:{peer_port}")
            self.merge_chain(received_chain)
        except Exception as e:
            print(f"Error requesting chain: {e}")

    def merge_chain(self, received_chain):
        """
        Обновляет локальный блокчейн, если полученная цепочка длиннее.

        :param received_chain: Полученная цепочка блоков
        """
        if len(received_chain) > len(self.blockchain):
            self.blockchain = received_chain
            print("Local blockchain updated.")
        else:
            print("Received chain is not longer than the local chain.")

    def broadcast_block(self, block):
        """
        Рассылает новый блок всем известным узлам.

        :param block: Новый блок для добавления в цепочку
        """
        block_data = json.dumps(block.__repr__()).encode()
        print("Broadcasting new block...")
        for conn in self.p2p_network.node.connections:
            try:
                conn.send(b"NEW_BLOCK" + block_data)
            except Exception as e:
                print(f"Error broadcasting block: {e}")

    def start_sync_loop(self):
        """
        Цикл автоматической синхронизации с известными узлами.
        """
        def sync_loop():
            while True:
                print("Starting synchronization loop...")
                for peer in self.p2p_network.peers:
                    try:
                        self.request_chain(peer[0], peer[1])
                    except Exception as e:
                        print(f"Error syncing with peer {peer}: {e}")
                time.sleep(10)  # Интервал синхронизации

        threading.Thread(target=sync_loop, daemon=True).start()


if __name__ == "__main__":
    import os
    import sys

    parent_dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
    sys.path.append(parent_dir)
    from p2p import P2PNetwork
    from blockchain.blockchain import Blockchain, Block

    host = "10.255.196.200"
    port = 12345

    blockchain = Blockchain()
    p2p_network = P2PNetwork(host, port)
    sync_manager = SyncManager(p2p_network, blockchain)

    p2p_network.start()
    sync_manager.start_sync_loop()

    while True:
        command = input("Enter command (broadcast, request, exit): ")
        if command == "broadcast":
            new_block = Block(1, "hfjasklfashfjaslf", 0.2, [])
            sync_manager.broadcast_block(new_block)
        elif command == "request":
            peer_host = input("Enter peer host: ")
            peer_port = int(input("Enter peer port: "))
            sync_manager.request_chain(peer_host, peer_port)
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command.")
