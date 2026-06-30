from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessageChunk

from src.llm import OllamaModel
from src.agent.state import State


class LangGraphAgent:
    def __init__(self, config):
        self.config = config
        self.tools = None # TODO
        self.llm = OllamaModel(config['model']['name'], config['model']['reasoning'])
        # self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.graph = self.build_graph()

    def llm_invoke(self, state: State):
        return {"messages": [self.llm.generate(state["messages"])]}

    def build_graph(self):
        graph = StateGraph(State)
        graph.add_node("agent", self.llm_invoke)
        graph.set_entry_point("agent")
        graph.add_edge("agent", END)
        return graph.compile()

    def invoke(self, messages: list):
        result = self.graph.invoke({"messages": messages})
        return result["messages"][-1].content
    
    async def stream(self, messages: list):
        """Yield text chunks from the final agent response."""
        async for event in self.graph.astream_events(
            {"messages": messages}, version="v2"
        ):
            if (event["event"] == "on_chat_model_stream") \
                and (event["metadata"].get("langgraph_node") == "agent"):
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield chunk.content
    
    def visualize_graph(self):
        pass