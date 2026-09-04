import json
from pathlib import Path
from logging import getLogger


from src.embedding import EmbeddingModel
from src.tools.gg_sheet import get_tools


log = getLogger(__name__)


class ToolKnowledgeBase:
    def __init__(self, provider: str, model: str, dimension: int) -> None:
        self.model = EmbeddingModel(provider, model, dimension)
        log.info(f"[ToolKnowledgeBase] Using provider: '{provider.upper()}' - Model: '{model}' - dimension: '{dimension}")
        self.tools = {
            tool.name: tool.description
            for tool in get_tools()
        }

    def create_json_kb(self, json_path: str = "data/tool_kb.json") -> None:
        path = Path(json_path)

        if path.exists():
            log.info(f"[ToolKnowledgeBase] Path '{json_path}' exists")
            return

        path.parent.mkdir(parents=True, exist_ok=True)

        log.info(f"[ToolKnowledgeBase] Creating knowledge base for tool")
        with path.open("w", encoding="utf-8") as f:
            f.write("[\n")
            for i, (name, description) in enumerate(self.tools.items(), start=1):
                query_embed = self.model.get_embedding(description)

                record = {
                    "name": name,
                    "description": description,
                    "embed": query_embed
                    }
                
                f.write(
                    json.dumps(record, ensure_ascii=False) + ("\n" if i == len(self.tools) else ",\n")
                )
                log.info(f"[ToolKnowledgeBase] Creating for tool '{name}'")
                f.flush()
            f.write("]\n")
        log.info(f"[ToolKnowledgeBase] Created knowledge base for tool")
        return
    