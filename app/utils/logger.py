import os
import logging
from logging.handlers import RotatingFileHandler


class Logger:
    _instance = None 
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._logger = logging.getLogger("Journal-Daily")
            self._logger.setLevel(logging.DEBUG)

            if not os.path.exists("logs"):
                os.makedirs("logs")

            handler = RotatingFileHandler(
                "logs/log.log",
                mode="a",
                maxBytes=10*1024*1024,
                backupCount=5
            )

            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s"
            ))

            if not self._logger.handlers:
                self._logger.addHandler(handler)
            self._initialized = True

    @classmethod
    def get_logger(cls):
        return cls()._logger

    def set_logger_level(self, level):
        try:
            self._logger.setLevel(level)
        except Exception as e:
            error_string = (
                "Use a valid logging level "
                "(logging.DEBUG, logging.INFO, "
                "logging.WARNING, logging.ERROR, "
                "logging.CRITICAL)\n"
                f"{e}"
            )
            self._logger.error(error_string)

