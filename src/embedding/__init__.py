from logging import getLogger

from src.embedding.ollama import OllamaEmbedding


log = getLogger(__name__)


class EmbeddingModel:
    def __init__(self, provider: str, model: str, dimension: int = None) -> None:
        if provider == "ollama":
            self.model = OllamaEmbedding(model, dimension)
        else:
            log.info("[EMBEDDING] Provider '{provider}' is not supported")

        log.info(f"[EMBEDDING] Using Provider: '{provider.upper()}' - Model: '{model}' - dimension: '{dimension}'")

    def get_embedding(self, query):
        return self.model.get_embedding(query)
