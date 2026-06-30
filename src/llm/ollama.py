from langchain_ollama import ChatOllama


class OllamaModel:
    def __init__(self, model_name: str, reasoning: bool | str | None = None):
        self.llm = ChatOllama(model=model_name, reasoning=reasoning)
        
    def generate(self, messages):
        return self.llm.invoke(messages)

    # def generate_stream(self, messages):
    #     for response in self.llm.stream(messages):
    #         yield response
    
    # async def async_generate_stream(self, messages):
    #     async for response in self.llm.astream(messages):
    #         yield response
            
    # async def async_generate(self, messages):
    #     await self.llm.ainvoke(messages)