from logging import getLogger

from src.llm.ollama import OllamaModel
from src.llm.vllm import VLLMModel


log = getLogger(__name__)


class LLM:
    def __init__(self, provider: str, vllm_url: str, model: str, reasoning: bool | str | None = None) -> None:
        if provider == "ollama":
            self.model = OllamaModel(model, reasoning)
        elif provider == "vllm":
            self.model = VLLMModel(model, vllm_url, reasoning)
        else:
            log.info("[LLM] Provider '{provider}' is not supported")

    def get_llm(self):
        return self.model.get_llm()
