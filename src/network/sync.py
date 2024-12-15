import json
import threading
import time
from utils.logger import Logger
import pickle
log = Logger("sync")


class SyncManager:
    def __init__(self, p2p_network, blockchain, block_generator):
        """
        Инициализация менеджера синхронизации.
        :param p2p_network: Экземпляр P2PNetwork для взаимодействия с узлами
        """
        self.p2p_network = p2p_network
        self.blockchain = blockchain  # Локальная копия блокчейна
        self.block_generator = block_generator

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
            response = conn.recv(4096)
            print("breakpoint 1")
            recieved_chain = pickle.loads(response)
            log.debug(f"Received chain from {peer_host}:{peer_port}")
            self.merge_chain(recieved_chain)
        except Exception as e:
            log.error(f"Error requesting chain: {e}")

    def merge_chain(self, recieved_chain):
        """
        Обновляет локальный блокчейн, если полученная цепочка длиннее.
        :param received_chain: Полученная цепочка блоков
        """
        if len(recieved_chain) > len(self.blockchain):
            self.blockchain = recieved_chain
            log.info("Local blockchain updated.")
        else:
            log.debug("Received chain is not longer than the local chain.")

    def merge_block(self, recieved_block):
        new_block = self.block_generator(recieved_block["index"],
                                         recieved_block["previous_hash"],
                                         recieved_block["timestamp"],
                                         recieved_block["transactions"],
                                         recieved_block["nonce"])
        if self.blockchain.get_latest_block().timestamp < \
                new_block.timestamp:
            self.blockchain.chain.append(new_block)
            log.debug("Validating blockchain...")
            if not self.blockchain.is_chain_valid():
                log.error("Blockchain is invalid")
            else:
                log.debug("Blockchain is valid")
        else:
            print("huy")

    def request_block(self, peer_host: str, peer_port: int):
        log.debug(f"Requesting block from {peer_host}:{peer_port}")
        try:
            conn = self.p2p_network.node.connect_to_peer(peer_host, peer_port)
            conn.send(b"REQUEST_BLOCK")
            response = conn.recv(4096).decode()
            recieved_block = json.loads(response[9:])
            log.debug(f"Received block from {peer_host}:{peer_port}")
            self.merge_block(recieved_block)
        except Exception as e:
            log.error(f"Error requesting block: {e}")

    def broadcast_block(self, block):
        """
        Рассылает новый блок всем известным узлам.
        :param block: Новый блок для добавления в цепочку
        """
        block = {"index": block.index,
                 "previous_hash": block.previous_hash,
                 "timestamp": block.timestamp,
                 "transactions": block.transactions,
                 "nonce": block.nonce}
        block_data = json.dumps(block).encode()
        log.info("Broadcasting new block...")
        for conn in self.p2p_network.node.connections:
            try:
                conn.send(b"NEW_BLOCK" + block_data)
            except Exception as e:
                log.error(f"Error broadcasting block: {e}")

    def broadcast_chain(self):
        blockchain_data = pickle.dumps(self.blockchain.chain)
        log.info("Broadcasting chain...")
        for conn in self.p2p_network.node.connections:
            try:
                conn.send(b"NEW_CHAIN" + blockchain_data)
            except Exception as e:
                log.error(f"Error broadcasting blockchain: {e}")

    def start_sync_loop(self):
        """
        Цикл автоматической синхронизации с известными узлами.
        """
        def sync_loop():
            while True:
                log.debug("Starting synchronization loop...")
                for peer in self.p2p_network.peers:
                    try:
                        self.request_chain(peer[0], peer[1])
                        self.request_block(peer[0], peer[1])
                    except Exception as e:
                        log.error(f"Error syncing with peer {peer}: {e}")
                time.sleep(10)  # Интервал синхронизации

        threading.Thread(target=sync_loop, daemon=True).start()


if __name__ == "__main__":
    import os
    import sys

    parent_dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
    sys.path.append(parent_dir)
    from p2p import P2PNetwork
    from blockchain.blockchain import Blockchain, Block
    from sockets import P2PSocket

    host = input("HOST: ")
    port = 12345

    blockchain = Blockchain()
    p2p_network = P2PNetwork(P2PSocket(host, port))
    sync_manager = SyncManager(p2p_network, blockchain)

    p2p_network.start()
    sync_manager.start_sync_loop()

    while True:
        command = input("Enter command (broadcast, request, exit): ")
        if command == "broadcast":
            new_block = Block(1, "hfjasklfashfjaslf", 0.2, [])
            sync_manager.broadcast_block(new_block.__repr__())
        elif command == "request":
            peer_host = input("Enter peer host: ")
            peer_port = int(input("Enter peer port: "))
            sync_manager.request_chain(peer_host, peer_port)
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command.")
