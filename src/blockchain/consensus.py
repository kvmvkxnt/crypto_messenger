"""
    Consensus module

    Base of PoW algorithm and validations
"""

import time


class ProofOfWork:
    """
    ProofOfWork class used to mine and find hash

    :ivar difficulty: difficulty of finding hash
    :type difficulty: int
    """

    def __init__(self, difficulty: int):
        """Initializes the PoW class"""
        self.difficulty = difficulty

    def mine(self, block) -> str:
        """
        Proccesses block mining.

        :param block: block that should be mined
        :type block: Block
        :return: found hash of the block
        :rtype: str
        """
        target = self.get_target()
        # Mining block
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()
        print(f"Block mined: {block.hash}")
        return block.hash

    def validate(self, block) -> bool:
        """
        Validates that block corresponds to difficulty

        :param block: block that should be validated
        :type block: Block
        :return: if correct hash was found or not
        :rtype: bool
        """
        target = self.get_target()
        return block.hash.startswith(target)

    def get_target(self):
        return "0" * self.difficulty


class Validator:
    """
    Validator class checks the chain and validates its integrity
    """

    def validate_blockchain(self, blockchain) -> bool:
        """
        Checks integrity of the whole chain

        :param blockchain: chain that should be checked
        :type blockchain: Blockchain or List[Block]
        :return: if blockchain is corrupted or not
        :rtype: bool
        """
        for i in range(1, len(blockchain.chain)):
            current_block = blockchain.chain[i]
            previous_block = blockchain.chain[i - 1]
            if not self.validate_block(current_block, previous_block):
                return False

        return True

    def validate_block(self, current_block, previous_block) -> bool:
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
        """Adjust difficulty based on the time it took to mine the previous block"""
        if len(blockchain.chain) < 2:
            return blockchain.difficulty

        time_diff = time.time() - last_block.timestamp
        expected_time = 10  # Expected time for mining

        if time_diff < expected_time / 2:
            blockchain.difficulty += 1
        elif time_diff > expected_time * 2 and blockchain.difficulty > 1:
            blockchain.difficulty -= 1

        print(f"Difficulty adjusted to: {blockchain.difficulty}")
        return blockchain.difficulty


if __name__ == "__main__":
    from transaction import Transaction
    from blockchain import Blockchain, Block

    # Blockchain initialization and PoW
    blockchain = Blockchain(difficulty=4)
    pow = ProofOfWork(difficulty=4)

    # Creating and mining block
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

    # Adding block to the chain
    blockchain.chain.append(new_block)

    # Validating chain
    validator = Validator()
    print("Blockchain valid:", validator.validate_blockchain(blockchain))
