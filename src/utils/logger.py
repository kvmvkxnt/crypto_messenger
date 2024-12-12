import logging
import os
from utils.config import LOG_DIR, LOG_LEVEL


class Logger:
    """
    Утилита для централизованного логирования событий.
    """

    def __init__(self, name: str):
        """
        Инициализация логгера.

        :param name: Имя логгера, обычно имя модуля или класса.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL)

        # Формат вывода логов
        log_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)

        # Файловый обработчик
        log_file = os.path.join(LOG_DIR, f"{name}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)


# Пример использования
if __name__ == "__main__":
    log = Logger("example")
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")
