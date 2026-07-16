from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessageChunk
from langgraph.prebuilt import ToolNode, tools_condition

from src.llm import OllamaModel
from src.agent.state import State
from src.agent.tools.google_sheet import extract_transaction_information
from src.utils.visualization .graph_visualize import GraphVisualization


class LangGraphAgent:
    def __init__(self, config):
        self.config = config
        self.tools = list(extract_transaction_information) # TODO: implement tools
        self.llm = OllamaModel(config['model']['name'], config['model']['reasoning']).get_llm()
        
        self.graph = self.build_graph()

    def build_graph(self):
        graph = StateGraph(State)
        # Add node
        graph.add_node("llm", self.llm_invoke)
        graph.add_node("bind-tool", self.agent_bind_tool)
        graph.add_node("tools", ToolNode([extract_transaction_information]))

        # Add edge
        # graph.add_edge(START, "agent")
        # graph.add_edge("agent", END)

        graph.add_edge(START, "bind-tool")
        graph.add_conditional_edges(
            "bind-tool",
            self.router,
            {
                "has_tool": "tools",
                "exit": END
            }
        )
        # graph.add_edge("tools", "agent-tool")
        graph.add_edge("tools", "llm")
        graph.add_edge("llm", END)
        
        return graph.compile()

    def invoke_graph(self, messages: list):
        result = self.graph.invoke(
            {"messages": messages,
             "user_input": messages[-1]
             })
        return result
    
    def stream(self, messages: list):
        """Yield text chunks from the final agent response."""
        for event in self.graph.stream_events(
            {"messages": messages}, version="v3"
        ):
            # if (event["event"] == "on_chat_model_stream") \
            #     and (event["metadata"].get("langgraph_node") == "agent"):
            # chunk = event["data"]["chunk"]
            # if chunk.content:
            #     yield chunk.content
            yield event

    async def astream(self, messages: list):
        """Yield text chunks from the final agent response."""
        async for event in self.graph.astream_events(
            {"messages": messages}, version="v2"
        ):
            if (event["event"] == "on_chat_model_stream") \
                and (event["metadata"].get("langgraph_node") == "agent"):
                chunk = event["data"]["chunk"]
                if chunk.content:
                    yield chunk.content
    
    # ============================== Build nodes ==============================
    # Node: llm
    def llm_invoke(self, state: State):
        return {"messages": [self.llm.invoke(state["messages"])]}
    
    # Node: bind-tool
    def agent_bind_tool(self, state: State):
        llm_with_tools = self.llm.bind_tools([extract_transaction_information]) # TODO: add tool_retrieve from state, current is example
        return {"messages": [llm_with_tools.invoke(state["messages"])]} 
    
    # Node: router
    def router(self, state: State):
        # TODO: Add embedding method to retrieve tool
        if "tool" in state["user_input"]:
            return "tools"
        return "exit"
    

    # Visualization
    def visualize_graph(self):
        return GraphVisualization().visualize_png(self.graph)