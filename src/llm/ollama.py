from os import getenv

from langchain_ollama import ChatOllama

from src.logger import get_logger

log = get_logger()

class OllamaModel:
    def __init__(self, model_name: str, reasoning: bool | str | None = None):
        self.llm = ChatOllama(model=model_name, reasoning=reasoning)
        log.info(f"Using Provider: 'Ollama' - Model: '{model_name}' - think_mode: '{reasoning}'")
        
    def get_llm(self):
        return self.llm