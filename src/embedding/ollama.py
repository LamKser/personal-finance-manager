from typing import List
from logging import getLogger

from langchain_ollama import OllamaEmbeddings


log = getLogger(__name__)


class OllamaEmbedding:
    def __init__(self, model: str, dimension: int):
        self.embedding_model = OllamaEmbeddings(model=model, dimensions=dimension)
        
    def get_embedding(self, text: str) -> List[float]:
        return self.embedding_model.embed_query(text)
        