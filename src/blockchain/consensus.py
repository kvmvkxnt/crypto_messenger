'''
    Consensus module

    Base of PoW algorithm and validations
'''


class ProofOfWork:
    '''
        ProofOfWork class used to mine and find hash

        :ivar difficulty: difficulty of finding hash
        :type difficulty: float
    '''

    def __init__(self, difficulty: float):
        '''Initializes the PoW class'''
        self.difficulty = difficulty

    def mine(self, block) -> str:
        '''
            Proccesses block mining.

            :param block: block that should be mined
            :type block: Block
            :return: found hash of the block
            :rtype: str
        '''
        target = "0" * self.difficulty
        # Mining block
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()
        print(f"Block mined: {block.hash}")
        return block.hash

    def validate(self, block) -> bool:
        '''
            Validates that block corresponds to difficulty

            :param block: block that should be validated
            :type block: Block
            :return: if correct hash was found or not
            :rtype: bool
        '''
        target = "0" * self.difficulty
        return block.hash.startswith(target)


class Validator:
    '''
        Validator class checks the chain and validates its integrity
    '''

    def validate_blockchain(self, blockchain) -> bool:
        '''
            Checks integrity of the whole chain

            :param blockchain: chain that should be checked
            :type blockchain: Blockchain or List[Block]
            :return: if blockchain is corrupted or not
            :rtype: bool
        '''
        for i in range(1, len(blockchain.chain)):
            print(i)
            current_block = blockchain.chain[i]
            previous_block = blockchain.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                print(f"Block {i} has invalid hash.")
                return False

            if current_block.previous_hash != previous_block.hash:
                print(f"Block {i} has invalid previous hash.")
                return False

        return True


if __name__ == "__main__":
    from transaction import Transaction
    from blockchain import Blockchain, Block

    # Blockchain initialization and PoW
    blockchain = Blockchain(difficulty=4)
    pow = ProofOfWork(difficulty=4)

    # Creating and mining block
    blockchain.add_transaction(Transaction("Alice", "Bob", 10, "Hi"))
    blockchain.add_transaction(Transaction("Charlie", "Dave", 20, "Hello"))

    new_block = Block(
        index=len(blockchain.chain),
        previous_hash=blockchain.get_latest_block().hash,
        timestamp=blockchain.get_latest_block().timestamp + 1,
        transactions=blockchain.pending_transactions
    )

    pow.mine(new_block)

    # Adding block to the chain
    blockchain.chain.append(new_block)

    # Validating chain
    validator = Validator()
    print("Blockchain valid:", validator.validate_blockchain(blockchain))
