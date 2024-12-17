import json5 as json
from utils.logger import Logger
from blockchain.transaction import Transaction
from blockchain.blockchain import Block
import socket
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
        try:
            conn = self.p2p_network.node.get_connection(peer_host)
            if not conn:
                conn = None
            self.p2p_network.broadcast_message(b"REQUEST_CHAIN", conn)  # Ensure all data is sent
            log.info(f"Requesting blockchain from {peer_host}:{peer_port}")
            return

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

    def broadcast_chain(self, conn) -> None:
        if not self.blockchain.chain:
            log.debug("Cannot broadcast empty chain")
            return
        log.debug("Broadcasting chain...")

        chain_bytes = json.dumps([block.to_dict() for block in self.blockchain.chain],
                                 ensure_ascii=False).encode()
        self.p2p_network.broadcast_message(b"BLOCKCHAIN" + chain_bytes, conn)

    def start_sync_loop(self) -> None:
        """
        Цикл автоматической синхронизации с известными узлами.
        """

        log.debug("Starting synchronization loop...")
        if len(self.p2p_network.peers):
            for peer in self.p2p_network.peers:
                try:
                    self.request_chain(peer[0], peer[1])
                except Exception as e:
                    log.error(f"Error syncing with peer {peer}: {e}")


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

    def handle_blockchain(self, blockchain):
        blockchain = json.loads(blockchain.decode())
        print(blockchain)
        chain = []

        for block_data in blockchain:
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
            block_data["transacti, connons"] = transactions
            chain.append(Block(**block_data))
        self.merge_chain(chain)
