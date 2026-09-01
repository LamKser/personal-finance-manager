from typing import List
from typing_extensions import Literal
from logging import getLogger

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langchain_core.messages import ToolMessage

from src.llm import LLM
from src.router import LLMRouter, BasicRouter
from src.agent.state import State
from src.utils.visualization .graph_visualize import GraphVisualization
from src.settings import settings
from src.prompt import SYSTEM_PROMPT

# Tools
from src.agent.tools.gg_sheet import get_tools
from src.agent.tools.date_time import get_today_datetime


log = getLogger(__name__)


class LangGraphAgent:
    def __init__(self):
        self.tools = get_tools()
        self.llm = LLM(settings.llm_provider, settings.llm_model, settings.llm_reasoning).get_llm()
        log.info(f"[LLM] Using Provider: '{settings.llm_provider.upper()}' - Model: '{settings.llm_model}' - think_mode: '{settings.llm_reasoning}'")
        
        if settings.router_type == "llm":
            self.router = LLMRouter(settings.router_provider,
                                    settings.router_model,
                                    settings.router_reasoning)
            log.info(f"[ROUTER] Using Router: '{settings.router_type}' - Provider: '{settings.router_provider.upper()}' - Model: '{settings.router_model}' - think_mode: '{settings.router_reasoning}'")

        elif settings.router_type == "basic":
            self.router = BasicRouter()
            log.info(f"[ROUTER] Using Router: '{settings.router_type}'")


        self.graph = self.build_graph()
        log.info("Successfully build graph")

    def build_graph(self):
        graph = StateGraph(State)
        # Add nodes
        graph.add_node("router", self.router_node)
        graph.add_node("llm-bind-tool", self.agent_bind_tool)
        graph.add_node("tools", ToolNode(self.tools))
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
        log.info("Prompt: %s", messages)
        messages = [{"role": "system", "content": SYSTEM_PROMPT.format(CURRENT_DATE=get_today_datetime())}] + messages
        result = self.graph.invoke(
            {"messages": messages,
             "user_input": messages[-1],
             "total_retry_tool": 0,
             "total_token_tool_call": 0,
             "total_token_llm": 0,
             "total_token": 0
             })
        log.info("Final output: %s", result["messages"][-1].content)
        return result
    
    def stream_(self, messages: List[str]):
        for output in self.graph.stream(
            {"messages": messages,
             "user_input": messages[-1]}):
            for key, value in output.items():
                print(key, "----", value)

    async def astream(self, messages: List[str]):
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

        return {
            "messages": [response],
            "total_token_llm": response.usage_metadata["total_tokens"],
            "total_token": response.usage_metadata["total_tokens"]
        }

    def agent_bind_tool(self, state: State):
        llm_with_tools = self.llm.bind_tools(self.tools) # TODO: add tool_retrieve from state, current is example
        bind_tool_response = llm_with_tools.invoke(state["messages"])
        log.info("[NODE llm-bind-tool]: %r", bind_tool_response)

        return {
            "messages": [bind_tool_response],
            "total_token_tool_call": bind_tool_response.usage_metadata["total_tokens"],
            "total_token": bind_tool_response.usage_metadata["total_tokens"]
        } 

    def router_node(self, state: State) -> Command[Literal["llm-bind-tool", "llm"]]:
        use_tool = self.router.route(state["user_input"])
        if use_tool:
            log.info("[NODE router_node]: Route to `llm-bind-tool`")
            return Command(goto="llm-bind-tool")
        
        log.info("[NODE router_node]: Route to `llm`")
        return Command(goto="llm")

    def check_tool_error_node(self, state: State) -> Command[Literal["llm-bind-tool", "llm"]]:
        last_message = state["messages"][-1]
        retry_count = state.get("total_retry_tool", 0)
        max_retries = settings.max_tool_retry
       
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
        return Command(goto="llm")

    # ------------------------------ Edges ------------------------------
