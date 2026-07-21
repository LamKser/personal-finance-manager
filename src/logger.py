import logging
from os import getenv
import os

def get_logger(level: str = getenv("LOG_LEVEL", "INFO"),
               name: str = __name__,
               file_name: str = getenv("LOG_FILE", "logs/app.log")):
    
    parent_dir = os.path.dirname(file_name)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
        
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(file_name, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "{asctime} - {name} - {levelname} - {message}", # 2025-07-22 15:58 - WARNING - Messages
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    if name == __name__: logger.info(f"[LOG]: Logs are saved at '{file_name}'")
    return logger