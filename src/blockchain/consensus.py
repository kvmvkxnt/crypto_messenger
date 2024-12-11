from transaction import Transaction


class ProofOfWork:
    def __init__(self, difficulty: int):
        self.difficulty = difficulty

    def mine(self, block) -> str:
        """Реализует процесс майнинга для блока."""
        target = "0" * self.difficulty
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()
        print(f"Block mined: {block.hash}")
        return block.hash

    def validate(self, block) -> bool:
        """Проверяет, что блок удовлетворяет условиям сложности."""
        target = "0" * self.difficulty
        return block.hash.startswith(target)


class Validator:
    def validate_blockchain(self, blockchain) -> bool:
        """Проверяет целостность всей цепочки блоков."""
        for i in range(1, len(blockchain.chain)):
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
    from blockchain import Blockchain, Block

    # Инициализация блокчейна и ProofOfWork
    blockchain = Blockchain(difficulty=4)
    pow = ProofOfWork(difficulty=4)

    # Создание и майнинг блока
    blockchain.add_transaction(Transaction("Alice", "Bob", 10, "Hi"))
    blockchain.add_transaction(Transaction("Charlie", "Dave", 20, "Hello"))

    new_block = Block(
        index=len(blockchain.chain),
        previous_hash=blockchain.get_latest_block().hash,
        timestamp=blockchain.get_latest_block().timestamp + 1,
        transactions=blockchain.pending_transactions
    )

    pow.mine(new_block)

    # Добавление блока в цепочку
    blockchain.chain.append(new_block)

    # Валидация цепочки
    validator = Validator()
    print("Blockchain valid:", validator.validate_blockchain(blockchain))
