from typing import List

from langchain_core.tools import StructuredTool

from src.tools.gg_sheet import get
from src.tools.gg_sheet import count
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


def get_gg_sheet_tools() -> List[StructuredTool]:
    all_get_tools = get_tools(get)
    all_count_tools = get_tools(count)
    all_create_tools = get_tools(create)
    # all_update_tools = get_tools(get)
    return all_get_tools + all_count_tools + all_create_tools
