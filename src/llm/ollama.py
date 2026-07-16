from langchain_ollama import ChatOllama


class OllamaModel:
    def __init__(self, model_name: str, reasoning: bool | str | None = None):
        self.llm = ChatOllama(model=model_name, reasoning=reasoning)
        
    def get_llm(self):
        return self.llm