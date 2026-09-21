from logging import getLogger

from src.llm.ollama import OllamaModel
from src.llm.vllm import VllmModel
from src.llm.nvidia import NvidiaModel
from src.settings import settings

log = getLogger(__name__)


class LLM:
    def __init__(self, provider: str) -> None:
        if provider == "ollama":
            self.model = OllamaModel(settings.ollama_model, settings.ollama_reasoning)
            log.info("[LLM] - Using Provider: 'ollama' - Model: '%s' - think_mode: '%s'", settings.ollama_model, settings.ollama_reasoning)
        elif provider == "vllm":
            self.model = VllmModel(settings.vllm_model, settings.vllm_url, settings.vllm_api_key)
            log.info("[LLM] - Using Provider: 'vllm' - Model: '%s'", settings.vllm_model)
        elif provider == "nvidia":
            self.model = NvidiaModel(settings.nvidia_model, settings.nvidia_api_key)
            log.info("[LLM] - Using Provider: 'nvidia' - Model: '%s'", settings.nvidia_model)
        else:
            log.info("[LLM] Provider '{provider}' is not supported")

    def get_llm(self):
        return self.model.get_llm()
