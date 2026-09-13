from langchain_openai import ChatOpenAI


class VLLMModel:
    def __init__(self, model_name: str, base_url: str, reasoning: bool | str | None = None):
        self.llm = ChatOpenAI(
            model=model_name,
            base_url=base_url,
            api_key="EMPTY"
        )
        
    def get_llm(self):
        return self.llm