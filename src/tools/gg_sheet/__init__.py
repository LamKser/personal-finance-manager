from typing import List

from langchain_core.tools import StructuredTool

from src.tools.gg_sheet import get
# from src.tools.gg_sheet import update
from src.tools.gg_sheet import create


def get_tools(module: str) -> List[StructuredTool]:
    all_objs = dir(module)
    all_tools = list()

    for name in all_objs:
        obj = getattr(module, name)
        if isinstance(obj, StructuredTool):
            all_tools.append(obj)
    return all_tools


def get_all_tools() -> List[StructuredTool]:
    all_get_tools = get_tools(get)
    all_create_tools = get_tools(create)
    # all_update_tools = get_tools(get)
    return all_get_tools + all_create_tools
