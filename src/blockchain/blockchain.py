'''
    Blockchain module

    Base of blockchain module which contains most os the basic things sush as
    Block class or Blockchain class with basic functions
'''

import hashlib
import time
from typing import List


class Block:
    '''
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
    '''

    def __init__(self, index: int, previous_hash: str, timestamp: float,
                 transactions: List, nonce: int = 0) -> None:
        '''Initiates the block class'''
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        '''
            Calculates block hash by adding and hashing block's content

            :return: hash of the block
            :rtype: str
        '''
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}\
                         {self.transactions}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __repr__(self) -> str:
        '''
            Returns block content as a string

            :returns: block content
            :rtype: str
        '''
        return (
            f"Block(index={self.index},\
            previous_hash={self.previous_hash},\
            hash={self.hash}, \
            transactions={self.transactions},\
            nonce={self.nonce})"
        )


class Blockchain:
    '''
        The basic blockchain class

        :ivar difficulty: difficulty of getting the right hash
        :type difficulty: float
        :ivar pending_transactions: list of pending transactions
        :type pending_transactions: List[Transaction]
        :ivar chain: chain of the blocks (obvious)
        :type chain: List[Block]
    '''

    def __init__(self, difficulty: float = 4) -> None:
        '''
            Initiates the blockchain with its own difficulty

            :param difficulty: difficulty of geting the right hash
            :type difficulty: float
        '''
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions: List = []

    def __len__(self):
        return len(self.chain)

    def create_genesis_block(self) -> Block:
        '''
            Creates genesis-block (blockchain's first block)

            :return: absolutely empty block
            :rtype: Block
        '''
        return Block(0, "0", time.time(), [])

    def get_latest_block(self) -> Block:
        '''
            Gets the last block from the chain (obvious)

            :return: last block of the chain
            :rtype: Block
        '''
        return self.chain[-1]

    def add_transaction(self, transaction) -> None:
        '''
            Adds transaction to pending list, previously signing it

            :param transaction: transaction that needs to be added to list
            :type transaction: Transaction
        '''
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner, miner_address: str) -> None:
        '''
            Creates new block using pending transactions and adds it to chain

            :param miner: miner that will mine the block
            :type miner: ProofOfWork
            :param miner_address: miner's adderss
            :type miner_address: str
            :return: only if there are no pending transactions
            :rtype: None
        '''
        if not self.pending_transactions:
            print("No transactions to mine.")
            return

        # creating a new block
        new_block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            timestamp=time.time(),
            transactions=self.pending_transactions
        )

        # Mining and validating new block
        miner(self.difficulty).mine(new_block)
        miner(self.difficulty).validate(new_block)
        self.chain.append(new_block)

        # Clearing pending transactions list after successful mining
        self.pending_transactions = [{"sender": None,
                                      "recipient": miner_address,
                                      "amount": 1}]

    def is_chain_valid(self, validator):
        '''
            Validates the blockchain using given validator

            :param validator: validator which vill used to validate chain
            :type validator: Validator
            :return: return's chain state
            :rtype: bool
        '''
        return validator(self)


if __name__ == "__main__":
    from consensus import ProofOfWork, Validator
    from transaction import Transaction

    # Usage example
    blockchain = Blockchain(difficulty=4)

    # Adding transactions
    blockchain.add_transaction(Transaction("Alice", "Bob", 50))
    blockchain.add_transaction(Transaction("Bob", "Alice", 25))

    # Mining
    blockchain.mine_pending_transactions(ProofOfWork,
                                         miner_address="Miner1")
    blockchain.mine_pending_transactions(ProofOfWork,
                                         miner_address="Miner1")

    # Chain validation
    print(Block(0, "123", 14.23423, []).calculate_hash())
    print("Blockchain valid:", Validator().validate_blockchain(blockchain))

    # Printing chain
    for block in blockchain.chain:
        print(block)
