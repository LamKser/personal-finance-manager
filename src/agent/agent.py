from typing_extensions import Literal
from logging import getLogger

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langchain_core.messages import ToolMessage, AIMessage

from src.llm import OllamaModel
from src.agent.state import State
from src.agent.tools import extract_transaction_information
from src.utils.visualization .graph_visualize import GraphVisualization

log = getLogger(__name__)


class LangGraphAgent:
    def __init__(self, config):
        self.config = config
        self.tools = list(extract_transaction_information) # TODO: implement tools
        self.llm = OllamaModel(config['model']['name'], config['model']['reasoning']).get_llm()
        
        self.graph = self.build_graph()
        log.info("Successfully build graph")

    def build_graph(self):
        graph = StateGraph(State)
        # Add nodes
        graph.add_node("router", self.router)
        graph.add_node("llm-bind-tool", self.agent_bind_tool)
        graph.add_node("tools", ToolNode([extract_transaction_information]))
        graph.add_node("check-tool-error", self.check_tool_error_node)
        graph.add_node("llm", self.llm_invoke)
        log.info("Finished adding nodes")

        # Add edges
        graph.add_edge(START, "router")
        graph.add_edge("llm-bind-tool", "tools")
        graph.add_edge("tools", "check-tool-error")
        graph.add_edge("llm", END)
        log.info("Finished adding edges")
        return graph.compile()

    def invoke_graph(self, messages: list):
        result = self.graph.invoke(
            {"messages": messages,
             "user_input": messages[-1],
             "total_retry_tool": 0
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
    # ------------------------------ Nodes ------------------------------
    def llm_invoke(self, state: State):
        response = self.llm.invoke(state["messages"])
        state["output"] = response
        log.info("[NODE llm]: %r", response)

        return {"messages": [response]}

    def agent_bind_tool(self, state: State):
        llm_with_tools = self.llm.bind_tools([extract_transaction_information]) # TODO: add tool_retrieve from state, current is example
        bind_tool_response = llm_with_tools.invoke(state["messages"])
        log.info("[NODE llm-bind-tool]: %r", bind_tool_response)

        return {"messages": [bind_tool_response]} 

    def router(self, state: State) -> Command[Literal["llm-bind-tool", "llm"]]:
        # TODO: Add embedding method to retrieve tool
        if "tool" in state["user_input"]:
            log.info("[NODE router]: Route to `llm-bind-tool`")
            return Command(goto="llm-bind-tool")
        
        log.info("[NODE router]: Route to `llm`")
        return Command(goto="llm")

    def check_tool_error_node(self, state: State) -> Command[Literal["llm-bind-tool", "llm"]]:
        last_message = state["messages"][-1]
        retry_count = state.get("total_retry_tool", 0)
        max_retries = self.config["model"]["max-tool-retry"]
       
        log.info("[NODE check-tool-error] Checking tool status (retry=%d/%d)", retry_count, max_retries)
        if isinstance(last_message, ToolMessage):
            log.info("[NODE tools] - %s", last_message)

        if isinstance(last_message, ToolMessage) and last_message.status == "error":
            log.error("[NODE check-tool-error] Tool failed: %r", last_message.content)
           
            if retry_count < max_retries:
                new_retry_count = retry_count + 1
                log.info("[NODE check-tool-error] Routing to `llm-bind-tool` for retry (attempt %d/%d)", new_retry_count, max_retries)
                return Command(
                    goto="llm-bind-tool",
                    update={"total_retry_tool": new_retry_count}
                )
            else:
                log.warning("[NODE check-tool-error] Max retries reached (%d/%d), routing to `llm`", retry_count, max_retries)
                return Command(goto="llm")
       
        log.info("[NODE check-tool-error] Tool succeeded, routing to `llm`")
        return Command(
            goto="llm",
            update={"total_retry_tool": 0}
        )


    # ------------------------------ Edges ------------------------------

    # ------------------------------ Visualization ------------------------------
    def visualize_graph(self):
        return GraphVisualization().visualize_png(self.graph)