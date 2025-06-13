import logging.config
import os


class LoggingConfig:
    @staticmethod
    def setup_logging():
        # Ensure data and logs directories exist
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        logging.config.fileConfig('logging_config.ini', disable_existing_loggers=False)
