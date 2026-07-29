from typing import Annotated, List
from typing_extensions import TypedDict
from operator import add

from langgraph.graph.message import add_messages


class State(TypedDict):
    user_input: str
    messages: Annotated[List, add_messages]
    tool_call: List
    tool_used: List
    output: str
    total_retry_tool: int

    # Token - AIMessage(usage_metadata={'input_tokens': int, 'output_tokens': int, 'total_tokens': int})
    total_token_tool_call: Annotated[int, add]
    total_token_llm: Annotated[int, add]
    total_token: Annotated[int, add]