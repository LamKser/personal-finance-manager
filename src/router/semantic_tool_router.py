import json
from logging import getLogger

log = getLogger(__name__)

import numpy as np

from src.embedding import EmbeddingModel
from src.tools.gg_sheet import get_tools


class SemanticToolRouter:
    def __init__(self, provider: str, model: str, dimension: int, kb_path: str):
        self.model = EmbeddingModel(provider, model, dimension)
        log.info("[SemanticToolRouter] Using Provider: '%d' - Model: '%s' - dimension: %d", provider, model, self.model.dimension)
        self.map_all_tools = dict()
        for tool in get_tools():
            self.map_all_tools[tool.name] = tool

        if "json" in kb_path:
            with open(kb_path, "r", encoding="utf-8") as f:
                self.kb = json.load(f)

    def retrieve(self, query, top_k: int = 5, threshold: float = 0.0):
        query_embed = self.model.get_embedding(query)
        top_scores = [-1.0] * top_k
        top_tools = [None] * top_k

        for tool in self.kb:
            name = tool["name"]
            embed = tool["embed"]

            # Cosine
            dot_product = np.dot(query_embed, embed)
            norm_query = np.linalg.norm(query_embed)
            norm_embed = np.linalg.norm(embed)
            score = dot_product / (norm_query * norm_embed)
            if score < threshold:
                continue
            
            min_index = np.argmin(top_scores)

            if score > top_scores[min_index]:
                top_scores[min_index] = score
                top_tools[min_index] = self.map_all_tools[name]

        return [
            {"tool": tool, "score": score.item()}
            for tool, score in zip(top_tools, top_scores)
            if tool is not None
        ]
