from logging import getLogger

from src.llm.ollama import OllamaModel


log = getLogger(__name__)


class LLM:
    def __init__(self, provider: str, model: str, reasoning: bool | str | None = None) -> None:
        if provider == "ollama":
            self.model = OllamaModel(model, reasoning)
        else:
            log.info("[LLM] Provider '{provider}' is not supported")

    def get_llm(self):
        return self.model.get_llm()
