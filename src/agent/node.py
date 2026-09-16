from typing import Any, TypedDict, Dict, List

from langchain_core.messages import ToolMessage
from langchain_core.runnables import Runnable
from pydantic import ValidationError

from src.agent.state import State


INVALID_TOOL_NAME_ERROR_TEMPLATE = (
    "Error: {requested_tool} is not a valid tool, try one of [{available_tools}]."
)

# TOOL_CALL_ERROR_TEMPLATE = (
#     "Error: {error}\n Please fix your mistakes."
# )

TOOL_EXECUTION_ERROR_TEMPLATE = (
    "Error executing tool '{tool_name}' with kwargs {tool_kwargs} with error:\n"
    " {error}\n"
    " Please fix the error and try again."
)

TOOL_INVOCATION_ERROR_TEMPLATE = (
    "Error invoking tool '{tool_name}' with kwargs {tool_kwargs} with error:\n"
    " {error}\n"
    " Please fix the error and try again."
)


class ToolCall(TypedDict):
    name: str
    args: Dict[str, Any]
    id: str


class SequentialToolNode(Runnable):
    def __init__(self, tools: List[ToolMessage]) -> None:
        self.tools = {tool.name: tool for tool in tools}

    def invoke(
        self,
        state: State,
        config: Any = None,
        **kwargs: Any,
    ) -> Dict[str, List[ToolMessage]]:

        last_message = state["messages"][-1]

        tool_calls: List[ToolCall] = getattr(last_message, "tool_calls", [])

        tool_messages: List[ToolMessage] = []

        # Sequential execution
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            tool = self.tools.get(tool_name)

            if tool is None:
                available_tools = ", ".join(self.tools.keys())

                content = INVALID_TOOL_NAME_ERROR_TEMPLATE.format(
                    requested_tool=tool_name,
                    available_tools=available_tools,
                )

                tool_messages.append(
                    ToolMessage(
                        content=content,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="error",
                    )
                )
                continue

            try:
                result = tool.invoke(tool_args)

                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="success",
                    )
                )
            except ValidationError as e:
                content = TOOL_INVOCATION_ERROR_TEMPLATE.format(
                    tool_name=tool_name,
                    tool_kwargs=tool_args,
                    error=e,
                )
            
                tool_messages.append(
                    ToolMessage(
                        content=content,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="error",
                    )
                )

            except Exception as e:
                content = TOOL_EXECUTION_ERROR_TEMPLATE.format(
                    tool_name=tool_name,
                    tool_kwargs=tool_args,
                    error=e,
                )

                tool_messages.append(
                    ToolMessage(
                        content=content,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="error",
                    )
                )

        return {
            "messages": tool_messages,
        }

    async def ainvoke(
        self,
        state: State,
        config: Any = None,
        **kwargs: Any,
    ) -> Dict[str, List[ToolMessage]]:

        last_message = state["messages"][-1]

        tool_calls: List[ToolCall] = getattr(
            last_message,
            "tool_calls",
            [],
        )

        tool_messages: List[ToolMessage] = []

        # Sequential execution
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            tool = self.tools.get(tool_name)

            if tool is None:
                available_tools = ", ".join(self.tools.keys())

                content = INVALID_TOOL_NAME_ERROR_TEMPLATE.format(
                    requested_tool=tool_name,
                    available_tools=available_tools,
                )

                tool_messages.append(
                    ToolMessage(
                        content=content,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="error",
                    )
                )
                continue

            try:
                # Await before moving to the next tool
                result = await tool.ainvoke(tool_args)

                tool_messages.append(
                    ToolMessage(
                        content=str(result),
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="success",
                    )
                )
            except ValidationError as e:
                content = TOOL_INVOCATION_ERROR_TEMPLATE.format(
                    tool_name=tool_name,
                    tool_kwargs=tool_args,
                    error=e,
                )
            
                tool_messages.append(
                    ToolMessage(
                        content=content,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="error",
                    )
                )

            except Exception as e:
                content = TOOL_EXECUTION_ERROR_TEMPLATE.format(
                    tool_name=tool_name,
                    tool_kwargs=tool_args,
                    error=e,
                )

                tool_messages.append(
                    ToolMessage(
                        content=content,
                        name=tool_name,
                        tool_call_id=tool_call_id,
                        status="error",
                    )
                )

        return {
            "messages": tool_messages,
        }