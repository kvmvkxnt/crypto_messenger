import hashlib
import time
from typing import List, Dict, Any


class Block:
    def __init__(self, index: int, previous_hash: str, timestamp: float,
                 transactions: List[Dict[str, Any]], nonce: int = 0) -> None:
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Возвращает хеш блока."""
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}\
                         {self.transactions}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __repr__(self) -> str:
        return (
            f"Block(index={self.index},\
            previous_hash={self.previous_hash[:10]}...,\
            hash={self.hash[:10]}..., \
            transactions={len(self.transactions)},\
            nonce={self.nonce})"
        )


class Blockchain:
    def __init__(self, difficulty: int = 4) -> None:
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions: List[Dict[str, Any]] = []

    def create_genesis_block(self) -> Block:
        """Создает генезис-блок (первый блок в цепочке)."""
        return Block(0, "0", time.time(), [])

    def get_latest_block(self) -> Block:
        """Возвращает последний блок в цепочке."""
        return self.chain[-1]

    def add_transaction(self, transaction: Dict[str, Any]) -> None:
        """Добавляет транзакцию в список ожидающих."""
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address: str) -> None:
        """
            Создает новый блок из ожидающих транзакций и
            добавляет его в цепочку.
        """
        if not self.pending_transactions:
            print("No transactions to mine.")
            return

        new_block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            timestamp=time.time(),
            transactions=self.pending_transactions
        )

        self.proof_of_work(new_block)
        self.chain.append(new_block)

        # Очистка списка транзакций и награда майнеру
        self.pending_transactions = [{"from": None, "to": miner_address,
                                      "amount": 1}]

    def proof_of_work(self, block: Block) -> None:
        """Ищет хеш, соответствующий сложности."""
        target = "0" * self.difficulty
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.calculate_hash()

        print(f"Block mined: {block.hash}")

    def is_chain_valid(self) -> bool:
        """Проверяет целостность цепочки."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                print(f"Invalid hash at block {i}")
                return False

            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash at block {i}")
                return False

        return True


if __name__ == "__main__":
    # Пример работы
    blockchain = Blockchain(difficulty=4)

    # Добавление транзакций
    blockchain.add_transaction({"from": "Alice", "to": "Bob", "amount": 50})
    blockchain.add_transaction({"from": "Bob", "to": "Charlie", "amount": 25})

    # Майнинг
    blockchain.mine_pending_transactions(miner_address="Miner1")
    blockchain.mine_pending_transactions(miner_address="Miner1")

    # Проверка цепочки
    print("Blockchain valid:", blockchain.is_chain_valid())

    # Печать цепочки
    for block in blockchain.chain:
        print(block)
