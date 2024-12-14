import os

# Основные настройки
HOST = "127.0.0.1"  # Локальный хост
DEFAULT_PORT = 12345  # Порт по умолчанию
BROADCAST_PORT = 5000  # Порт для широковещательных сообщений

# Параметры блокчейна
BLOCK_DIFFICULTY = 4  # Сложность PoW (количество ведущих нулей в хеше)

# Параметры криптографии
KEY_SIZE = 2048  # Размер ключа для алгоритма DH
ENCRYPTION_ALGORITHM = "AES-256-CBC"  # Алгоритм шифрования
SIGNATURE_ALGORITHM = "ECDSA"  # Алгоритм подписей

# Логирование
LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL") or "INFO"
# Уровень логирования: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Время между синхронизациями
SYNC_INTERVAL = 10  # Интервал в секундах

# Функция для проверки и создания директорий
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

if __name__ == "__main__":
    print("Configuration loaded successfully:")
    print(f"Host: {HOST}")
    print(f"Default Port: {DEFAULT_PORT}")
    print(f"Broadcast Port: {BROADCAST_PORT}")
    print(f"Blockchain Difficulty: {BLOCK_DIFFICULTY}")
    print(f"Encryption Algorithm: {ENCRYPTION_ALGORITHM}")
    print(f"Signature Algorithm: {SIGNATURE_ALGORITHM}")
    print(f"Log Directory: {LOG_DIR}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Sync Interval: {SYNC_INTERVAL}s")
