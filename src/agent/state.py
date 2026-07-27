from typing import Annotated, Dict, List
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class State(TypedDict):
    user_input: str
    messages: Annotated[List, add_messages]
    tool_call: List
    tool_used: List
    output: str
    total_retry_tool: int
    # token: int