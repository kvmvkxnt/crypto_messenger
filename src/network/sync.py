import json5 as json
import threading
import time
from utils.logger import Logger
from typing import Optional
from blockchain.transaction import Transaction
from blockchain.blockchain import Block
import socket
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import zlib



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
        log.info(f"Requesting blockchain from {peer_host}:{peer_port}")
        try:
            conn = self.p2p_network.node.get_connection(peer_host)
            if not conn:
                log.warning(f"No connection to peer {peer_host}:{peer_port}")  # More informative log
                return

            conn.sendall(b"REQUEST_CHAIN")  # Ensure all data is sent

            # Receive data in chunks
            chunks = []
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break  # Connection closed
                chunks.append(chunk)
                if len(chunk) < 4096:
                    break  # Last chunk

            data = b"".join(chunks)

            if not data:
                log.warning(f"Received empty data from {peer_host}:{peer_port}") # Check for no data
                return

            received_chain_data = json.loads(data.decode())


            received_chain = []
            for block_data in received_chain_data:
                transactions = []
                for transaction_data in block_data["transactions"]:
                    if transaction_data["signature"]:
                        transaction_data["signature"] = bytes.fromhex(transaction_data["signature"])
                    if transaction_data["sender"]:
                        transaction_data["sender"] = bytes.fromhex(transaction_data["sender"])
                    if transaction_data["recipient"]:
                        transaction_data["recipient"] = bytes.fromhex(transaction_data["recipient"])
                    if transaction_data["sign_public_key"]:
                        transaction_data["sign_public_key"] = bytes.fromhex(transaction_data["sign_public_key"])

                    transactions.append(Transaction(**transaction_data))
                block_data["transactions"] = transactions  # update dict with transaction objs
                received_chain.append(Block(**block_data))

            log.info(f"Received chain from {peer_host}:{peer_port}")
            self.merge_chain(received_chain)

        except socket.error as e:
            log.error(f"Error requesting chain: {e}")
        # except json.JSONDecodeError as e:
        #     log.error(f"Error decoding chain data: {e}")
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

    def broadcast_block(self, block: Block, conn) -> None:
        """
        Рассылает новый блок всем известным узлам.

        :param block: Новый блок для добавления в цепочку
        """
        if not block:
            log.debug("Cannot broadcast empty block")
            return
        log.debug("Broadcasting new block...")

        block_bytes = json.dumps(block.to_dict(), ensure_ascii=False).encode()

        self.p2p_network.broadcast_message(b"NEW_BLOCK" + block_bytes, conn)
        


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

    def handle_new_block(self, block_data: bytes, conn) -> None:
        """
        Обрабатывает новый блок, полученный от другого узла.
        """
        try:
            block_dict = json.loads(block_data.decode())
            for transaction in block_dict["transactions"]:
                if transaction["signature"]:
                    transaction["signature"] = (
                        bytes.fromhex(transaction["signature"])
                        if transaction["signature"]
                        else None
                    )
                if transaction["sender"]:
                    transaction["sender"] = (
                        bytes.fromhex(transaction["sender"])
                        if transaction["sender"]
                        else None
                    )
                transaction["recipient"] = bytes.fromhex(
                    transaction["recipient"]
                )
                if transaction["sign_public_key"]:
                    transaction["sign_public_key"] = bytes.fromhex(
                        transaction["sign_public_key"]
                    )
            block_dict["transactions"] = [
                Transaction(**transaction) for transaction in block_dict["transactions"]
            ]
            block = Block(**block_dict)
            if self.blockchain.contains_block(block):
                return

            if self.blockchain.validator.validate_block(block, self.blockchain.get_latest_block()):
                self.blockchain.chain.append(block)
                self.broadcast_block(block, conn)
                log.info(f"Added new block with index {block.index}")
            else:
                log.warning("Invalid block received")

        # except json.JSONDecodeError as e:
        #     log.error(f"Error decoding block data: {e}")
        except Exception as e:
            log.error(f"Error during block handling: {e}")

    def handle_new_transaction(self, transaction_data: bytes, conn) -> None:
        """
        Обрабатывает новую транзакцию, полученную от другого узла.
        """
        try:
            transaction_string = transaction_data.decode()
            transaction_dict = json.loads(transaction_string)
            if transaction_dict["sender"]:
                transaction_dict["sender"] = (
                    bytes.fromhex(transaction_dict["sender"])
                    if transaction_dict["sender"]
                    else None
                )
            transaction_dict["recipient"] = bytes.fromhex(
                transaction_dict["recipient"]
            )
            if transaction_dict["signature"]:
                transaction_dict["signature"] = (
                    bytes.fromhex(transaction_dict["signature"])
                    if transaction_dict["signature"]
                    else None
                )
            if transaction_dict["sign_public_key"]:
                transaction_dict["sign_public_key"] = bytes.fromhex(
                    transaction_dict["sign_public_key"]
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
        # except json.JSONDecodeError as e:
        #     log.error(f"Error decoding transaction data: {e}")
        except Exception as e:
            log.error(f"Error during transaction handling: {e}")


    def handle_block_sync(self, block_data: bytes) -> None:
        """
        Обрабатывает новый блок, полученный от другого узла.
        """
        try:
            block_dict = json.loads(block_data.decode())
            for transaction in block_dict["transactions"]:
                if transaction["signature"]:
                    transaction["signature"] = (
                        bytes.fromhex(transaction["signature"])
                        if transaction["signature"]
                        else None
                    )
                if transaction["sender"]:
                    transaction["sender"] = (
                        bytes.fromhex(transaction["sender"])
                        if transaction["sender"]
                        else None
                    )
                transaction["recipient"] = bytes.fromhex(
                    transaction["recipient"]
                )
                if transaction["sign_public_key"]:
                    transaction["sign_public_key"] = bytes.fromhex(
                        transaction["sign_public_key"]
                    )
            block_dict["transactions"] = [
                Transaction(**transaction) for transaction in block_dict["transactions"]
            ]
            block = Block(**block_dict)
            if self.blockchain.contains_block(block):
                return

            if self.blockchain.validator.validate_block(block, self.blockchain.get_latest_block()):
                self.blockchain.chain.append(block)
                log.info(f"Added new block with index {block.index}")
            else:
                log.warning("Invalid block received")

        # except json.JSONDecodeError as e:
        #     log.error(f"Error decoding block data: {e}")
        except Exception as e:
            log.error(f"Error during block handling: {e}")