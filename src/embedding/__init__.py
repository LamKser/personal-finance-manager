from logging import getLogger

log = getLogger(__name__)

from src.embedding.ollama import OllamaEmbedding

OLLAMA_DEFAULT_DIMENSION = {
    "nomic-embed-text-v2-moe:latest": 768,
    "qwen3-embedding:0.6b": 1024
}


class EmbeddingModel:
    def __init__(self, provider: str, model: str, dimension: int = None) -> None:
        self.provider = provider
        self.model = model
        self.dimension = dimension if dimension else OLLAMA_DEFAULT_DIMENSION[model]
        if provider == "ollama":
            self.model = OllamaEmbedding(model, self.dimension)
        else:
            log.info("[EMBEDDING] Provider '%s' is not supported", provider)

    def get_embedding(self, query):
        return self.model.get_embedding(query)
