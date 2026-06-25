import yaml
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_CONFIG_PATH = "src/config/telegram.yaml"
LLM_CONFIG_PATH = "src/config/llm.yaml"

with open(TELEGRAM_CONFIG_PATH, 'r') as f:
    telegram_config = yaml.safe_load(f)
    telegram_config["token"] = os.getenv("TELEGRAM_TOKEN")

with open(LLM_CONFIG_PATH, 'r') as f:
    llm_config = yaml.safe_load(f)