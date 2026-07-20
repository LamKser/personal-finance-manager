from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langchain_core.messages import ToolMessage

from src.llm import OllamaModel
from src.agent.state import State
from src.agent.tools.google_sheet import extract_transaction_information
from src.utils.visualization .graph_visualize import GraphVisualization
from src.logger import get_logger

log = get_logger()

class LangGraphAgent:
    def __init__(self, config):
        self.config = config
        self.tools = list(extract_transaction_information) # TODO: implement tools
        self.llm = OllamaModel(config['model']['name'], config['model']['reasoning']).get_llm()
        
        self.graph = self.build_graph()
        log.info("Successfully build graph")

    def build_graph(self):
        graph = StateGraph(State)
        # Add node
        graph.add_node("router", self.router)
        graph.add_node("llm-bind-tool", self.agent_bind_tool)
        graph.add_node("tools", ToolNode([extract_transaction_information]))
        graph.add_node("llm", self.llm_invoke)
        log.info("Finished adding nodes")

        # Add edge
        graph.add_edge(START, "router")
        graph.add_conditional_edges(
            "router",
            self.need_tool,
            {
                "need_tool": "llm-bind-tool",
                "exit": "llm"
            }
        )
        graph.add_edge("llm-bind-tool", "tools")
        graph.add_conditional_edges(
            "tools",
            self.check_tool_error,
            {
                "retry": "llm-bind-tool",
                "continue": "llm"
            }
        )
        graph.add_edge("llm", END)
        log.info("Finished adding edges")
        return graph.compile()

    def invoke_graph(self, messages: list):
        result = self.graph.invoke(
            {"messages": messages,
             "user_input": messages[-1]
             })
        return result
    
    def stream_(self, messages: list):
        for output in self.graph.stream(
            {"messages": messages,
             "user_input": messages[-1]}):
            for key, value in output.items():
                print(key, "----", value)

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
    # ------------------------------ Node ------------------------------
    def llm_invoke(self, state: State):
        response = self.llm.invoke(state["messages"])
        state["output"] = response
        log.info(f"[LLM]: {response}")

        return {"messages": [response]}

    def agent_bind_tool(self, state: State):
        # state["tool_call"] = 
        llm_with_tools = self.llm.bind_tools([extract_transaction_information]) # TODO: add tool_retrieve from state, current is example
        # state["tool_used"] = 
        bind_tool_response = llm_with_tools.invoke(state["messages"])
        log.info(f"[Bind-tool]: {bind_tool_response}")

        return {"messages": [bind_tool_response]} 

    def router(self, state: State):
        # TODO: Add embedding method to retrieve tool
        if "tool" in state["user_input"]:
            log.info("[Router]: Route to Tool calling")
            return Command(goto="llm-bind-tool")
        log.info("[Router]: Route to LLM")
        return Command(goto="llm")
    
    # ------------------------------ Edge conditions ------------------------------
    def need_tool(self, state: State):
        # TODO: Add embedding method to retrieve tool
        if "tool" in state["user_input"]:
            return "need_tool"
        return "exit"
    
    def check_tool_error(self, state: State):
        """Check if tool execution failed and decide whether to retry."""
        last_message = state["messages"][-1]
        
        retry_count = state.get("total_retry_tool", 0)
        max_retries = self.config["model"]["max-tool-retry"]  # Maximum number of retries
        
        # Check if it's a ToolMessage with an error
        if isinstance(last_message, ToolMessage) and last_message.status == "error":
            if retry_count < max_retries:
                # Increment retry count and retry
                state["total_retry_tool"] = retry_count + 1
                return "retry"
            else:
                # Max retries reached, continue to LLM with error context
                return "continue"
        
        # Success - reset retry count and continue
        state["tool_retry_count"] = 0
        return "continue"

    # ------------------------------ Visualization ------------------------------
    def visualize_graph(self):
        return GraphVisualization().visualize_png(self.graph)