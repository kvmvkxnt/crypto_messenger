import json5 as json
import threading
import time
from utils.logger import Logger
from typing import Optional
from blockchain.transaction import Transaction
from blockchain.blockchain import Block
import socket
from cryptography.hazmat.primitives.serialization import load_pem_public_key


log = Logger("sync")


class SyncManager:
    def __init__(self, p2p_network, blockchain, sync_interval: int = 5):
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
            conn = self.p2p_network.node.get_connection(peer_host)
            if not conn:
                conn = self.p2p_network.connect_to_peer(peer_host, peer_port)
                # conn.send(b"INCOME_PORT" + str(self.p2p_network.port).encode())
                if not conn:
                    log.error(f"Failed to connect to peer {peer_host}:{peer_port}")
                    return
            if conn:
                conn.send(b"REQUEST_CHAIN")
                response = conn.recv(4096)

                received_chain = json.loads(response.decode())

                for block in received_chain:
                    for transaction in block["transactions"]:
                        transaction["signature"] = (
                            bytes.fromhex(transaction["signature"])
                            if transaction["signature"]
                            else None
                        )
                        transaction["sender"] = (
                            bytes.fromhex(transaction["sender"]).encode()
                            if transaction["sender"]
                            else None
                        )
                        transaction["recipient"] = bytes.fromhex(
                            transaction["recipient"]
                        ).encode()
                    block["transactions"] = [
                        Transaction(**transaction)
                        for transaction in block["transactions"]
                    ]
                received_chain = [Block(**block) for block in received_chain]
                log.debug(f"Received chain from {peer_host}:{peer_port}")
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
            log.info("Received empty chain")
            return

        if len(received_chain) > len(self.blockchain.chain):
            if self.blockchain.validator.validate_blockchain(self.blockchain):
                self.blockchain.chain = received_chain
                log.info("Local blockchain updated.")
            else:
                log.warning("Received blockchain is not valid")
        else:
            log.debug("Received chain is not longer than the local chain.")

    def broadcast_block(self, block: Block) -> None:
        """
        Рассылает новый блок всем известным узлам.

        :param block: Новый блок для добавления в цепочку
        """
        if not block:
            log.debug("Cannot broadcast empty block")
            return
        log.debug("Broadcasting new block...")

        block_bytes = json.dumps(block.to_dict(), ensure_ascii=False).encode()

        for conn, _ in self.p2p_network.node.connections:
            try:
                conn.sendall(b"NEW_BLOCK" + block_bytes)
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
            block_dict = json.loads(block_data.decode())
            for transaction in block_dict["transactions"]:
                transaction["signature"] = (
                    bytes.fromhex(transaction["signature"])
                    if transaction["signature"]
                    else None
                )
                transaction["sender"] = (
                    bytes.fromhex(transaction["sender"]).encode()
                    if transaction["sender"]
                    else None
                )
                transaction["recipient"] = bytes.fromhex(
                    transaction["recipient"]
                ).encode()
            block_dict["transactions"] = [
                Transaction(**transaction) for transaction in block_dict["transactions"]
            ]
            block = Block(**block_dict)
            if self.blockchain.contains_block(block):
                return

            if self.blockchain.validator.validate_block(block, self.blockchain.get_latest_block()):
                self.blockchain.chain.append(block)
                log.info(f"Added new block with index {block.index}")
                # self.broadcast_block(block)
            else:
                log.warning("Invalid block received")

        except json.JSONDecodeError as e:
            log.error(f"Error decoding block data: {e}")
        except Exception as e:
            log.error(f"Error during block handling: {e}")

    def handle_new_transaction(self, transaction_data: bytes, conn) -> None:
        """
        Обрабатывает новую транзакцию, полученную от другого узла.
        """
        try:
            transaction_string = transaction_data.decode()
            transaction_dict = json.loads(transaction_string)
            transaction_dict["sender"] = (
                bytes.fromhex(transaction_dict["sender"])
                if transaction_dict["sender"]
                else None
            )
            transaction_dict["recipient"] = bytes.fromhex(
                transaction_dict["recipient"]
            )
            transaction_dict["signature"] = (
                bytes.fromhex(transaction_dict["signature"])
                if transaction_dict["signature"]
                else None
            )
            transaction = Transaction(**transaction_dict)
            if transaction in self.blockchain.pending_transactions:
                return

            log.debug(f"Received transaction {transaction.calculate_hash()}")
            if self.blockchain.is_transaction_valid(transaction):
                self.blockchain.pending_transactions.append(transaction)
                self.p2p_network.broadcast_transaction(transaction, conn)
                log.info(f"Added new transaction from network")
            else:
                log.warning("Invalid transaction received")
        except json.JSONDecodeError as e:
            log.error(f"Error decoding transaction data: {e}")
        except Exception as e:
            log.error(f"Error during transaction handling: {e}")
