from langchain_nvidia_ai_endpoints import ChatNVIDIA


class NvidiaModel:
    def __init__(self, model_name: str, api_key: str):
        self.llm = ChatNVIDIA(model=model_name, api_key=api_key)
        
    def get_llm(self):
        return self.llm
