from logging import getLogger

log = getLogger(__name__)

from src.embedding.ollama import OllamaEmbedding


class EmbeddingModel:
    def __init__(self, provider: str, model: str, dimension: int = None) -> None:
        self.provider = provider
        self.model = model
        self.dimension = dimension
        if provider == "ollama":
            self.model = OllamaEmbedding(model, dimension)
        else:
            log.info("[EMBEDDING] Provider '%s' is not supported", provider)

    def get_embedding(self, query):
        return self.model.get_embedding(query)
