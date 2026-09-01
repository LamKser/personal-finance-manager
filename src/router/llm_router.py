from pydantic import BaseModel, Field

from src.llm import LLM
from src.prompt import ROUTER_PROMPT

class UseTool(BaseModel):
    """LLM routing decision indicating whether tool(s) should be invoked."""
    use_tool: bool = Field(description="Whether tool(s) should be invoked to handle the user's request.")


class LLMRouter:
    def __init__(self, provider: str, model: str, reasoning: bool | str | None = None):
        self.model = LLM(provider, model, reasoning).get_llm().with_structured_output(UseTool)

    def route(self, query):
        llm_decision = self.model.invoke([
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user", "content": query}
        ])
        return llm_decision.use_tool
