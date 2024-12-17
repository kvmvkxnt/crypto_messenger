"""
    Consensus module

    Base of PoW algorithm and validations
"""

import time
from typing import List


class ProofOfWork:
    """
    ProofOfWork class used to mine and find hash.

    :ivar int difficulty: The difficulty of finding a valid hash.
    """

    def __init__(self, difficulty: int):
        """
        Initializes the ProofOfWork class.

        :param int difficulty: The mining difficulty level.
        """
        self.difficulty = difficulty

    def mine(self, block) -> str:
        """
        Processes block mining by finding a hash that meets the difficulty criteria.

        It modifies the block.nonce and block.hash attribute.

        :param Block block: The block to be mined.
        :return: The hash of the mined block.
        :rtype: str
        """
        target = self.get_target()

        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()
        print(f"Block mined: {block.hash}")
        return block.hash

    def validate(self, block) -> bool:
        """
        Validates that a block's hash meets the difficulty criteria.

        :param Block block: The block to be validated.
        :return: True if the block's hash is valid, False otherwise.
        :rtype: bool
        """
        target = self.get_target()
        return block.hash.startswith(target)

    def get_target(self) -> str:
        """
        Returns the target string based on the difficulty.

        The target is a string of zeros equal to the difficulty.

        :return: A string of zeros representing the mining target.
        :rtype: str
        """
        return "0" * self.difficulty


class Validator:
    """
    Validator class to check the integrity of the blockchain.
    """

    def validate_blockchain(self, blockchain) -> bool:
        """
        Checks the integrity of the entire blockchain.

        :param blockchain: The blockchain to be validated.
        :type blockchain: Blockchain or List[Block]
        :return: True if the blockchain is valid, False otherwise.
        :rtype: bool
        """
        for i in range(1, len(blockchain.chain)):
            current_block = blockchain.chain[i]
            previous_block = blockchain.chain[i - 1]
            if not self.validate_block(current_block, previous_block):
                return False

        return True

    def validate_block(self, current_block, previous_block) -> bool:
        """
        Validates a single block in relation to the previous block.

        :param Block current_block: The block to be validated.
        :param Block previous_block: The previous block in the chain.
        :return: True if the block is valid, False otherwise.
        :rtype: bool
        """
        if current_block.hash != current_block.calculate_hash():
            print(f"Block {current_block.index} has invalid hash.")
            return False

        if current_block.previous_hash != previous_block.hash:
            print(f"Block {current_block.index} has invalid previous hash.")
            return False

        if current_block.timestamp <= previous_block.timestamp:
            print(f"Block {current_block.index} has invalid timestamp")
            return False

        return True

    def adjust_difficulty(self, blockchain, last_block):
        """
        Adjusts the difficulty of mining based on the time it took to mine the previous block.

        :param Blockchain blockchain: The blockchain to adjust difficulty for.
        :param Block last_block: The last block of the chain.
        :return: The adjusted difficulty level.
        :rtype: int
        """
        if len(blockchain.chain) < 2:
            return blockchain.difficulty

        time_diff = time.time() - last_block.timestamp
        expected_time = 10

        if time_diff < expected_time / 2:
            blockchain.difficulty += 1
        elif time_diff > expected_time * 2 and blockchain.difficulty > 1:
            blockchain.difficulty -= 1

        print(f"Difficulty adjusted to: {blockchain.difficulty}")
        return blockchain.difficulty


if __name__ == "__main__":
    from transaction import Transaction
    from blockchain import Blockchain, Block

    blockchain = Blockchain(difficulty=4)
    pow = ProofOfWork(difficulty=4)

    transaction1 = Transaction("Alice", "Bob", 10, "Hi")
    transaction2 = Transaction("Charlie", "Dave", 20, "Hello")

    blockchain.add_transaction(transaction1)
    blockchain.add_transaction(transaction2)

    new_block = Block(
        index=len(blockchain.chain),
        previous_hash=blockchain.get_latest_block().hash,
        timestamp=time.time(),
        transactions=blockchain.pending_transactions,
    )

    pow.mine(new_block)

    blockchain.chain.append(new_block)

    validator = Validator()
    print("Blockchain valid:", validator.validate_blockchain(blockchain))