import logging.config
import os


class LoggingConfig:
    @staticmethod
    def setup_logging():
        os.makedirs('logs', exist_ok=True)  # Ensure 'logs/' directory exists
        logging.config.fileConfig('logging_config.ini', disable_existing_loggers=False)
