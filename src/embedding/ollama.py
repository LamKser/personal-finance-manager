from typing import List
from logging import getLogger

from langchain_ollama import OllamaEmbeddings

log = getLogger(__name__)


class OllamaEmbedding:
    def __init__(self, model_name: str, dimension: int = 256):
        self.embedding_model = OllamaEmbeddings(model=model_name, dimensions=dimension)
        log.info(f"[Embedding] Using Provider: 'Ollama' - Model: '{model_name}' - dimension: '{dimension}'")
        
    def get_embedding(self, text: str) -> List[float]:
        return self.embedding_model.embed_query(text)
        