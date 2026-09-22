from langchain_openai import ChatOpenAI


class VllmModel:
    def __init__(self, model_name: str, base_url: str, api_key: str = "EMPTY"):
        self.llm = ChatOpenAI(
            model=model_name,
            base_url=base_url,
            api_key=api_key,
            stream_usage=True,
            stream=True
        )
        
    def get_llm(self):
        return self.llm