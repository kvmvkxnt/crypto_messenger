import threading
import time
import utils.logger as logger
log = logger.Logger("p2p")


class P2PNetwork:
    def __init__(self, node, host, port, broadcast_port: int, public_key,
                 key_manager, encryptor):
        """Инициализация P2P сети."""
        self.host = host
        self.port = port
        self.broadcast_port = broadcast_port
        self.node = node(self.host, self.port, self.main_handler)
        self.peers = set()  # Список известных узлов
        self.public_key = public_key
        self.key_manager = key_manager
        self.encryptor = encryptor

    def start(self):
        """Запуск узла в режиме сервера."""
        threading.Thread(target=self.node.start_server, daemon=True).start()
        log.debug(f"Node started at {self.host}:{self.port}")

    def connect_to_peer(self, peer_host: str, peer_port: int, peer_public_key):
        """Подключение к новому узлу."""
        if (peer_host, peer_port, peer_public_key) not in self.peers:
            self.peers.add((peer_host, peer_port, peer_public_key))
        self.node.connect_to_peer(peer_host, peer_port)
        log.info(f"Connected to peer: {peer_host}:{peer_port}")

    def broadcast_message(self, message: str):
        """Рассылка сообщения всем подключенным узлам."""
        log.debug(f"Broadcasting message: {message}")
        for conn in self.node.connections:
            try:
                conn.send(message.encode())
            except Exception as e:
                log.error(f"Error broadcasting message: {e}")

    def main_handler(self, data, conn, addr):
        peer = ()
        for i in self.peers:
            if i[0] == addr[0]:
                peer = i

        peer_public_key = peer[2]
        chat_shared_key = self.key_manager.generate_shared_key(peer_public_key)
        peer_id = list(self.peers).index(peer)
        self.peers = list(self.peers)
        self.peers[peer_id] = (addr[0], self.peers[peer_id][1],
                               peer_public_key, chat_shared_key)
        self.peers = set(self.peers)
        encryptor = self.encryptor(chat_shared_key)
        got_message = encryptor.decrypt(bytes.fromhex(data.decode()))
        print(got_message)
        # message = input("Message: ")
        # conn.send(encryptor.encrypt(message).hex().encode())

    def discover_peers(self, discoverer: set, public_key):
        """Механизм обнаружения новых узлов."""
        self.peers = discoverer(self.host, self.port, self.broadcast_port,
                                public_key)

    def sync_with_peers(self, sync_manager, blockchain, block_generator,
                        transaction_generator):
        """Синхронизация данных с подключенными узлами."""
        return sync_manager(self, blockchain, block_generator,
                            transaction_generator)


if __name__ == "__main__":
    from discovery import discover_peers
    from sync import SyncManager
    import os
    import sys

    parent_dir = os.path.dirname(os.path.realpath(__file__)) + "/.."
    sys.path.append(parent_dir)
    from blockchain.blockchain import Blockchain, Block

    host = "10.255.196.200"
    port = 12345

    blockchain = Blockchain()
    new_block = Block(1, "ahfjdlasf", 0.2, [])
    blockchain.chain.append(new_block)

    p2p = P2PNetwork(host, port)
    p2p.start()

    while True:
        command = input("Enter command \
        (connect, broadcast, discover, sync, list peers, exit): ")
        if command == "connect":
            peer_host = input("Enter peer host: ")
            peer_port = int(input("Enter peer port: "))
            p2p.connect_to_peer(peer_host, peer_port)
        elif command == "broadcast":
            message = input("Enter message to broadcast: ")
            p2p.broadcast_message(message)
        elif command == "discover":
            p2p.discover_peers(discover_peers)
        elif command == "sync":
            sm = p2p.sync_with_peers(SyncManager, blockchain)
            sm.start_sync_loop()
            sm.broadcast_block(new_block.__repr__())
        elif command == "list peers":
            print(f"known peers: {list(p2p.peers)}")
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("No such command")
