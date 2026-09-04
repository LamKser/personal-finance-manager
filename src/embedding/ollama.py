from typing import List
from logging import getLogger

from langchain_ollama import OllamaEmbeddings


DEFAULT_DIMENSION = {
    "nomic-embed-text-v2-moe:latest": 768,
    "qwen3-embedding:0.6b": 1024
}


log = getLogger(__name__)


class OllamaEmbedding:
    def __init__(self, model: str, dimension: int = None):
        self.dimension = dimension if dimension else DEFAULT_DIMENSION[model]
        self.embedding_model = OllamaEmbeddings(model=model, dimensions=self.dimension)
        
    def get_embedding(self, text: str) -> List[float]:
        return self.embedding_model.embed_query(text)
        