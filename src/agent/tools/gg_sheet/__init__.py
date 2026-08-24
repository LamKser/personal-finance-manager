from typing import List

from langchain_core.tools import StructuredTool

from src.agent.tools.gg_sheet import get
from src.agent.tools.gg_sheet import update
from src.agent.tools.gg_sheet import write



def get_tools() -> List[StructuredTool]:
    all_objs = dir(get)
    all_get_tools = list()

    for name in all_objs:
        obj = getattr(get, name)
        if isinstance(obj, StructuredTool):
            all_get_tools.append(obj)
    
    return all_get_tools