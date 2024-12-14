<<<<<<< HEAD
=======
import json
import threading
import time
from utils.logger import Logger
from typing import Optional
from blockchain.transaction import Transaction
import socket  # Import the socket module
from cryptography.hazmat.primitives.serialization import load_pem_public_key


log = Logger("sync")


class SyncManager:
    def __init__(self, p2p_network, blockchain, sync_interval: int = 10):
        """
        Инициализация менеджера синхронизации.

        :param p2p_network: Экземпляр P2PNetwork для взаимодействия с узлами
        :param sync_interval: интервал синхронизации
        """
        self.p2p_network = p2p_network
        self.blockchain = blockchain  # Локальная копия блокчейна
        self.sync_interval = sync_interval

    def request_chain(self, peer_host: str, peer_port: int) -> None:
        """
        Запрашивает копию блокчейна у указанного узла.

        :param peer_host: Хост узла
        :param peer_port: Порт узла
        """
        log.debug(f"Requesting blockchain from {peer_host}:{peer_port}")
        try:
            conn = self.p2p_network.node.get_connection(peer_host, peer_port)
            if not conn:
                conn = self.p2p_network.node.connect_to_peer(peer_host, peer_port)
                if not conn:
                    log.error(f"Failed to connect to peer {peer_host}:{peer_port}")
                    return
            if conn:
                conn.send(b"REQUEST_CHAIN")
                response = conn.recv(4096).decode()
                received_chain_data = json.loads(response)
                received_chain = [
                    self.block_from_dict(block_data)
                    for block_data in received_chain_data
                ]

                log.info(f"Received chain from {peer_host}:{peer_port}")
                self.merge_chain(received_chain)
            else:
                log.error(f"Failed to connect to peer {peer_host}:{peer_port}")

        except socket.error as e:
            log.error(f"Error requesting chain: {e}")
        except json.JSONDecodeError as e:
            log.error(f"Error decoding chain data: {e}")
        except Exception as e:
            log.error(f"Error during chain request: {e}")

    def merge_chain(self, received_chain: list) -> None:
        """
        Обновляет локальный блокчейн, если полученная цепочка длиннее и валидна.

        :param received_chain: Полученная цепочка блоков
        """
        if not received_chain:
            log.debug("Received empty chain")
            return

        if len(received_chain) > len(self.blockchain.chain):
            if self.blockchain.validator.validate_blockchain(self.blockchain):
                self.blockchain.chain = received_chain
                log.info("Local blockchain updated.")
            else:
                log.warning("Received blockchain is not valid")
        else:
            log.debug("Received chain is not longer than the local chain.")

    def broadcast_block(self, block: str) -> None:
        """
        Рассылает новый блок всем известным узлам.

        :param block: Новый блок для добавления в цепочку
        """
        if not block:
            log.debug("Cannot broadcast empty block")
            return
        block_data = json.dumps(block).encode()
        log.debug("Broadcasting new block...")
        for conn in self.p2p_network.node.connections:
            try:
                conn.send(b"NEW_BLOCK" + block_data)
            except socket.error as e:
                log.error(f"Error broadcasting block: {e}")

    def start_sync_loop(self) -> None:
        """
        Цикл автоматической синхронизации с известными узлами.
        """

        def sync_loop():
            while True:
                log.debug("Starting synchronization loop...")
                for peer in self.p2p_network.peers:
                    try:
                        self.request_chain(peer[0], peer[1])
                    except Exception as e:
                        log.error(f"Error syncing with peer {peer}: {e}")

                time.sleep(self.sync_interval)  # Интервал синхронизации

        threading.Thread(target=sync_loop, daemon=True).start()

    def handle_new_block(self, block_data: bytes) -> None:
        """
        Обрабатывает новый блок, полученный от другого узла.
        """
        try:
            block_string = block_data.decode()
            block_dict = json.loads(block_string)
            block = self.block_from_dict(block_dict)
            latest_block = self.blockchain.get_latest_block()

            if latest_block and self.blockchain.validator.validate_block(
                block, latest_block
            ):
                self.blockchain.chain.append(block)
                log.info(f"Added new block with index {block.index}")

                # broadcast validated block
                self.broadcast_block(block_string.encode())  # Рассылаем новый блок

            else:
                log.warning("Invalid block received")
        except json.JSONDecodeError as e:
            log.error(f"Error decoding block data: {e}")
        except Exception as e:
            log.error(f"Error during block handling: {e}")

    def handle_new_transaction(self, transaction_data: bytes) -> None:
        """
        Обрабатывает новую транзакцию, полученную от другого узла.
        """
        try:
            transaction_string = transaction_data.decode()
            transaction_dict = json.loads(transaction_string)
            transaction = Transaction(**transaction_dict)
            log.debug(f"Received transaction {transaction.calculate_hash()}")
            if self.blockchain.is_transaction_valid(transaction):
                self.blockchain.pending_transactions.append(transaction)
                log.info(f"Added new transaction from network")
            else:
                log.warning("Invalid transaction received")
        except json.JSONDecodeError as e:
            log.error(f"Error decoding transaction data: {e}")
        except Exception as e:
            log.error(f"Error during transaction handling: {e}")

    def block_from_dict(self, block_data: dict):
        from blockchain.blockchain import Block, Transaction

        transactions = []
        for trans in block_data["transactions"]:
            if trans["sender_public_key"]:
                try:
                    trans["sender_public_key"] = load_pem_public_key(
                        trans["sender_public_key"].encode()
                    )  # Loading key from string if available
                except Exception as e:
                    log.error(f"Error loading public key: {e}")
            transactions.append(Transaction(**trans))

        block = Block(
            index=block_data["index"],
            previous_hash=block_data["previous_hash"],
            timestamp=block_data["timestamp"],
            transactions=transactions,
            nonce=block_data["nonce"],
        )
        return block
>>>>>>> f00be1e2a327c1ed23561c21e9daeeb8f233859c
