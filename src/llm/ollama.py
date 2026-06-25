from langchain_ollama import ChatOllama


class OllamaModel:
    def __init__(self, model_name: str, reasoning: bool | str | None = None):
        self.llm = ChatOllama(model=model_name, reasoning=reasoning)
        
    def generate(self, messages):
        return self.llm.invoke(messages)

    def generate_stream(self, messages):
        stream_response = self.llm.stream(messages)
        for response in stream_response:
            yield response