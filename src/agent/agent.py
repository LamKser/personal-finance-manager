from typing import List
from typing_extensions import Literal
from logging import getLogger

from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langchain_core.messages import ToolMessage

from src.llm import LLM
from src.router import SemanticToolRouter
from src.knowledge_base import ToolKnowledgeBase
from src.agent.state import State
from src.settings import settings
from src.prompt import SYSTEM_PROMPT

# Tools
from src.tools.gg_sheet import get_tools
from src.tools.date_time import get_today_datetime


log = getLogger(__name__)


class LangGraphAgent:
    def __init__(self):
        # Langfuse tracing
        self.callback = None
        if settings.tracing:
            from langfuse import Langfuse, get_client
            from langfuse.langchain import CallbackHandler

            Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_base_url
            )
            self.langfuse = get_client()
            self.callback = {"callbacks": [CallbackHandler()]}
            log.info("[TRACING] Using Langfuse tracing")
        
        self.tools = get_tools()
        self.llm = LLM(settings.llm_provider, settings.llm_model, settings.llm_reasoning).get_llm()
        log.info("[LLM] Using Provider: '%s' - Model: '%s' - think_mode: '%s'", settings.llm_provider, settings.llm_model, settings.llm_reasoning)

        self.tool_kb = ToolKnowledgeBase(settings.embedding_provider,
                                         settings.embedding_model,
                                         settings.dimension
                                        ).create_json_kb(settings.tool_kb)

        if settings.router_type == "semantic":
            self.router = SemanticToolRouter(settings.embedding_provider,
                                         settings.embedding_model,
                                         settings.dimension,
                                         settings.tool_kb)

        self.graph = self.build_graph()
        log.info("[AGENT] Successfully build graph")

    def build_graph(self):
        graph = StateGraph(State)
        # Add nodes
        graph.add_node("router", self.router_node)
        graph.add_node("llm-bind-tool", self.agent_bind_tool)
        graph.add_node("tools", ToolNode(self.tools))
        graph.add_node("check-tool-error", self.check_tool_error_node)
        graph.add_node("llm", self.llm_invoke)
        log.info("[NODE] Finished adding nodes")

        # Add edges
        graph.add_edge(START, "router")
        # graph.add_edge(START, "llm-bind-tool")
        graph.add_edge("llm-bind-tool", "tools")
        graph.add_edge("tools", "check-tool-error")
        graph.add_edge("llm", END)
        log.info("[EDGE] Finished adding edges")
        return graph.compile()

    def invoke_graph(self, query: str):
        log.info("[USER] Prompt: %s", query)
        messages = [{"role": "system", "content": SYSTEM_PROMPT.format(CURRENT_DATE=get_today_datetime())},
                    {"role": "user", "content": query}]
        result = self.graph.invoke(
            {"messages": messages,
             "user_input": messages[-1]["content"],
             "total_retry_tool": 0,
             "total_token_tool_call": 0,
             "total_token_llm": 0,
             "total_token": 0,
             "tool_call": []
             },
             config=self.callback)
        log.info("[AGENT] Response: %r", result["messages"][-1].content)
        return result
    
    # def stream_(self, messages: List[str]):
    #     for output in self.graph.stream(
    #         {"messages": messages,
    #          "user_input": messages[-1]}):
    #         for key, value in output.items():
    #             print(key, "----", value)

    # async def astream(self, messages: List[str]):
    #     """Yield text chunks from the final agent response."""
    #     async for event in self.graph.astream_events(
    #         {"messages": messages}, version="v2"
    #     ):
    #         if (event["event"] == "on_chat_model_stream") \
    #             and (event["metadata"].get("langgraph_node") == "agent"):
    #             chunk = event["data"]["chunk"]
    #             if chunk.content:
    #                 yield chunk.content
    
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
        llm_with_tools = self.llm.bind_tools(state["tool_call"])
        bind_tool_response = llm_with_tools.invoke(state["messages"])
        log.info("[NODE llm-bind-tool]: %r", bind_tool_response)
        if not bind_tool_response.tool_calls:
            log.info("[NODE llm-bind-tool]: No tool(s) available - Route to `llm`")
        
        return {
            "messages": [bind_tool_response],
            "total_token_tool_call": bind_tool_response.usage_metadata["total_tokens"],
            "total_token": bind_tool_response.usage_metadata["total_tokens"]
        } 

    def router_node(self, state: State) -> Command[Literal["llm-bind-tool", "llm"]]:
        tool_retrieve = self.router.retrieve(state["user_input"], settings.top_tool, settings.tool_threshold)
        log.info("[NODE router]: Tool retrieve (%d tools): %r", len(tool_retrieve), [(tool["tool"].name, tool["score"]) for tool in tool_retrieve])
        if tool_retrieve:
            log.info("[NODE router]: Route to `llm-bind-tool`")
            return Command(goto="llm-bind-tool", update={"tool_call": [tool["tool"] for tool in tool_retrieve]})
        
        log.info("[NODE router]: Route to `llm`")
        return Command(goto="llm")

    def check_tool_error_node(self, state: State) -> Command[Literal["llm-bind-tool", "llm"]]:
        last_message = state["messages"][-1]
        retry_count = state.get("total_retry_tool", 0)
        max_retries = settings.max_tool_retry
       
        log.info("[NODE check-tool-error] Checking tool status (retry=%d/%d)", retry_count, max_retries)
        if isinstance(last_message, ToolMessage):
            log.info("[NODE tools] - %r", last_message)

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
