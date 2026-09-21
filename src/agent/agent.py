from typing import List
from typing_extensions import Literal
import os
from logging import getLogger

from langgraph.graph import StateGraph, END, START
# from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langchain_core.messages import ToolMessage, AIMessage

from src.llm import LLM
from src.agent.node import SequentialToolNode
from src.router import SemanticToolRouter
from src.knowledge_base import ToolKnowledgeBase
from src.agent.state import State
from src.settings import settings
from src.prompt import SYSTEM_PROMPT, REWRITE_PROMPT

# Tools
from src.tools import get_gg_sheet_tools
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
            log.info("[TRACING] - Using Langfuse tracing")
        
        self.tools = get_gg_sheet_tools()
        self.llm = LLM(settings.llm_provider).get_llm()

        if settings.update_kb and os.path.exists(settings.tool_kb):
            os.remove(settings.tool_kb)
            log.info("[ToolKnowledgeBase] - Removed to update tool knowledge base file")
        else:
            log.info("[ToolKnowledgeBase] - Tool knowledge base does not exist/Not update Tool knowledge base file, not remove")

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
        log.info("[AGENT] - Successfully build graph")

    def build_graph(self):
        graph = StateGraph(State)
        # Add nodes
        graph.add_node("rewrite", self.rewrite_node)
        graph.add_node("router", self.router_node)
        graph.add_node("llm-bind-tool", self.agent_bind_tool_node)
        # graph.add_node("tools", ToolNode(self.tools))
        graph.add_node("tools", SequentialToolNode(self.tools))
        graph.add_node("check-tool-error", self.check_tool_error_node)
        log.info("[NODE] - Finished adding nodes")

        # Add edges
        graph.add_edge(START, "rewrite")
        graph.add_edge("rewrite", "router")
        graph.add_edge("router", "llm-bind-tool")
        graph.add_edge("llm-bind-tool", "tools")
        graph.add_edge("tools", "check-tool-error")
        graph.add_edge("check-tool-error", END)
        log.info("[EDGE] - Finished adding edges")
        return graph.compile()

    def invoke_graph(self, query: str):
        log.info("[USER] - Prompt: %s", query)
        # messages = [{"role": "system", "content": SYSTEM_PROMPT.format(CURRENT_DATE=get_today_datetime())},
        #             {"role": "user", "content": query}]
        result = self.graph.invoke(
            {"messages": [],
             "user_input": query,
             "total_retry_tool": 0,
             "total_token_tool_call": 0,
             "total_token_llm": 0,
             "total_token": 0,
             "tool_call": []
             },
             config=self.callback)
        log.info("[AGENT] - Response: %s", result["messages"][-1].content)
        return result

    async def astream(self, query: str):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(CURRENT_DATE=get_today_datetime())},
            {"role": "user", "content": query}
        ]
        
        async for event in self.graph.astream_events(
            {
                "messages": messages,
                "user_input": messages[-1]["content"],
                "total_retry_tool": 0,
                "total_token_tool_call": 0,
                "total_token_llm": 0,
                "total_token": 0,
                "tool_call": []
            }, 
            version="v2"
        ):
            if event["event"] != "on_chat_model_stream":
                continue

            chunk = event["data"]["chunk"]

            if chunk.content:
                yield chunk.content
    
    # ============================== Build nodes ==============================
    # ------------------------------ Nodes ------------------------------
    def rewrite_node(self, state: State):
        rewrite_prompt = [
            {"role": "system", "content": REWRITE_PROMPT.format(CURRENT_DATE=get_today_datetime())},
            {"role": "user", "content": state["user_input"]}
        ]
        response = self.llm.invoke(rewrite_prompt)
        rewritten_query = response.content

        log.info("[NODE] - `rewrite` - Rewrite: %s", rewritten_query)

        return {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.format(CURRENT_DATE=get_today_datetime())},
                {"role": "user", "content": rewritten_query}
            ],
            "user_input": rewritten_query,
            "total_token_llm": response.usage_metadata["total_tokens"],
            "total_token": response.usage_metadata["total_tokens"]
        }

    def agent_bind_tool_node(self, state: State):
        llm_with_tools = self.llm.bind_tools(state["tool_call"])
        bind_tool_response = llm_with_tools.invoke(state["messages"])
        if not bind_tool_response.tool_calls:
            log.info("[NODE] - `llm-bind-tool` - No tool(s) available. Generate final response")
        log.info("[NODE] - `llm-bind-tool` - Response: %r", bind_tool_response)
        return {
            "messages": [bind_tool_response],
            "total_token_tool_call": bind_tool_response.usage_metadata["total_tokens"],
            "total_token": bind_tool_response.usage_metadata["total_tokens"]
        } 

    def router_node(self, state: State):
        tool_retrieve = self.router.retrieve(state["user_input"], settings.top_tool, settings.tool_threshold)
        log.info("[NODE] - `router` - Tool retrieve (%d tools): %r", len(tool_retrieve), [(tool["tool"].name, tool["score"]) for tool in tool_retrieve])
        # if tool_retrieve:
        log.info("[NODE] - `router` - Route to `llm-bind-tool`")
        return {"tool_call": [tool["tool"] for tool in tool_retrieve]}
        
        # log.info("[NODE router]: Route to `llm`")
        # return Command(goto="llm")

    def check_tool_error_node(self, state: State) -> Command[Literal["llm-bind-tool", "__end__"]]:
        messages = state["messages"]
        if isinstance(messages[-1], AIMessage) and not messages[-1].tool_calls:
            log.info("[NODE] - `check-tool-error` - No tool to execute.")
            return Command(
                    goto=END,
                    update={"total_retry_tool": 0}
                )
        tool_messages = []
        for message in reversed(messages):
            if not isinstance(message, ToolMessage):
                break

            tool_messages.append(message)
        tool_messages.reverse()
        retry_count = state.get("total_retry_tool", 0)
        max_retries = settings.max_tool_retry
       
        log.info("[NODE] - `check-tool-error` - Checking tool status (retry=%d/%d)", retry_count, max_retries)
        for i, tool_message in enumerate(tool_messages, start=1):
            log.info("[NODE] - `check-tool-error` - Tool #%d: %r", i, tool_message)

        failed_tools = [message for message in tool_messages if message.status == "error"]
        if failed_tools:
            for i, tool in enumerate(failed_tools, start=1):
                log.error("[NODE] - `check-tool-error` - Tool failed #%d: %r", i, tool.content)
            if retry_count < max_retries:
                new_retry_count = retry_count + 1
                log.info("[NODE] - `check-tool-error` - Routing to `llm-bind-tool` for retry (attempt %d/%d)", new_retry_count, max_retries)
                return Command(
                    goto="llm-bind-tool",
                    update={"total_retry_tool": new_retry_count}
                )
            else:
                log.info("[NODE] - `check-tool-error` - Max retries reached (%d/%d)", retry_count, max_retries)
                return Command(
                        goto=END,
                        update={"total_retry_tool": 0}
                    )
       
        log.info("[NODE] - `check-tool-error` - Tool succeeded")
        return Command(
                goto="llm-bind-tool",
                update={"total_retry_tool": 0}
            )

    # ------------------------------ Edges ------------------------------