import hashlib
import time
from typing import List, Dict
from .consensus import ProofOfWork, Validator
from .transaction import Transaction
from cryptography.hazmat.primitives.asymmetric import rsa
import json5 as json


class Block:
    """
    Block class

    :ivar index: index (id) of the block
    :type index: int
    :ivar previous_hash: hash of the block before the specific block
    :type previous_hash: str
    :ivar timestamp: time when block was created (mined)
    :type timestamp: float
    :ivar transactions: list of transactions in the block
    :type transactions: List[Transaction]
    :ivar nonce: number used once only for this block
    :type nonce: int
    :ivar hash: hash of the block
    :type hash: str
    """

    def __init__(
        self,
        index: int,
        previous_hash: str,
        timestamp: float,
        transactions: List[Transaction],
        nonce: int = 0,
        hash: str = None,
    ) -> None:
        """Initiates the block class"""
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.calculate_hash() if not hash else hash

    def calculate_hash(self) -> str:
        """
        Calculates block hash by adding and hashing block's content

        :return: hash of the block
        :rtype: str
        """
        transactions = [transaction.to_dict() for transaction in self.transactions]
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}\
                         {transactions}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> dict:
        """
        Returns block content as a string

        :returns: block content
        :rtype: str
        """
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "timestamp": self.timestamp,
            "transactions": [
                transaction.to_dict() for transaction in self.transactions
            ],
            "nonce": self.nonce,
        }


class Blockchain:
    """
    The basic blockchain class

    :ivar difficulty: difficulty of getting the right hash
    :type difficulty: int
    :ivar pending_transactions: list of pending transactions
    :type pending_transactions: List[Transaction]
    :ivar chain: chain of the blocks (obvious)
    :type chain: List[Block]
    """

    def __init__(self, difficulty: int = 4) -> None:
        """
        Initiates the blockchain with its own difficulty

        :param difficulty: difficulty of getting the right hash
        :type difficulty: int
        """
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self.validator = Validator()

    def __len__(self):
        return len(self.chain)

    def create_genesis_block(self) -> Block:
        """
        Creates genesis-block (blockchain's first block)

        :return: absolutely empty block
        :rtype: Block
        """
        return Block(0, "0", 0, [])

    def get_latest_block(self) -> Block:
        """
        Gets the last block from the chain (obvious)

        :return: last block of the chain
        :rtype: Block
        """
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> None:
        """
        Adds transaction to pending list, previously signing it

        :param transaction: transaction that needs to be added to list
        :type transaction: Transaction
        """
        if self.is_transaction_valid(transaction):
            self.pending_transactions.append(transaction)
        else:
            print("Transaction is invalid")

    def is_transaction_valid(self, transaction: Transaction):
        if transaction.sender:
            if not transaction.is_valid(transaction.sign_public_key):
                return False

            sender_balance = self.get_balance(transaction.sender)
            if sender_balance < transaction.amount:
                return False

        return True

    def get_balance(self, address: bytes) -> float:
        """
        Calculates balance of specific address.
        """
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == address:
                    balance -= transaction.amount
                if transaction.recipient == address:
                    balance += transaction.amount
        return balance

    def mine_pending_transactions(self, miner, miner_address: str) -> None:
        """
        Creates new block using pending transactions and adds it to chain

        :param miner: miner that will mine the block
        :type miner: ProofOfWork
        :param miner_address: miner's adderss
        :type miner_address: str
        :return: only if there are no pending transactions
        :rtype: None
        """
        if not self.pending_transactions:
            print("No transactions to mine.")
            return

        new_block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            timestamp=time.time(),
            transactions=self.pending_transactions,
        )

        reward_transaction = Transaction(None, miner_address, 1, "Mining Reward")

        miner(self.difficulty).mine(new_block)
        miner(self.difficulty).validate(new_block)

        if self.validator.validate_block(new_block, self.chain[-1]):
            self.chain.append(new_block)
            self.pending_transactions = [reward_transaction]
            return new_block, reward_transaction
        else:
            print("Invalid block. Block was not added to the chain")
            return None, None

    def is_chain_valid(self):
        """
        Validates the blockchain using given validator

        :return: return's chain state
        :rtype: bool
        """
        return self.validator.validate_blockchain(self)

    def contains_block(self, target_block: Block) -> bool:
        """Checks if the blockchain already contains the given block."""
        for block in self.chain:
            if block.hash == target_block.hash:
                return True
        return False


if __name__ == "__main__":

    blockchain = Blockchain(difficulty=4)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    transaction1 = Transaction("Alice", "Bob", 50, "test transaction 1")
    transaction1.sender = public_key
    transaction1.sign_transaction(private_key)

    transaction2 = Transaction("Bob", "Alice", 25, "test transaction 2")
    transaction2.sender = public_key
    transaction2.sign_transaction(private_key)

    blockchain.add_transaction(transaction1)
    blockchain.add_transaction(transaction2)

    blockchain.mine_pending_transactions(ProofOfWork, miner_address="Miner1")
    blockchain.mine_pending_transactions(ProofOfWork, miner_address="Miner1")

    print("Blockchain valid:", blockchain.is_chain_valid())

    for block in blockchain.chain:
        print(block)
