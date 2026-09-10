from typing import Any, Dict

from pydantic import BaseModel


class ToolResult(BaseModel):
    result: Any
    reference: Dict
