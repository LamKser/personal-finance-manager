import logging
from os import getenv
import os

def logger(level: str = getenv("LOG_LEVEL", "INFO"),
               file_name: str = getenv("LOG_FILE", "logs/app.log")):
    
    parent_dir = os.path.dirname(file_name)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
        
    logging.basicConfig(
        level=logging._nameToLevel[level.upper()],
        format="%(asctime)s - [%(name)s][%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(file_name, mode='a', encoding="utf-8"),
            logging.StreamHandler()
        ],
        datefmt="%Y-%m-%d %H:%M"
    )
    return