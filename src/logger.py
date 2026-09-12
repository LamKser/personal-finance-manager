import logging
from os import getenv
import os

from src.settings import settings

class FolderFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("src.")


def logger(level: str = getenv("LOG_LEVEL", settings.log_level.upper()), file_name: str = getenv("LOG_FILE", settings.log_file)):
    
    parent_dir = os.path.dirname(file_name)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    folder_filter = FolderFilter()
    file_handler = logging.FileHandler(file_name, mode='a', encoding="utf-8")
    file_handler.addFilter(folder_filter)
    stream_handler = logging.StreamHandler()
    stream_handler.addFilter(folder_filter)

    logging.basicConfig(
        level=logging._nameToLevel[level],
        format="%(asctime)s | %(levelname)-10s | %(name)-35s | %(message)s",
        handlers=[
            file_handler,
            stream_handler,
        ],
        datefmt="%Y-%m-%d %H:%M"
    )
    return