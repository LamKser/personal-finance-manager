from typing import Any, Dict
from datetime import datetime

from pydantic import BaseModel


class ToolResult(BaseModel):
    result: Any
    reference: Dict


class UserQuery(BaseModel):
    prompt: str


class Response(BaseModel):
    message: str
    timestamp: datetime
