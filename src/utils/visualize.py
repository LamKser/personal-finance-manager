class GraphVisualization:

    @classmethod
    def visualize_mermaid(self, graph):
        return graph.get_graph().draw_mermaid()

    @classmethod
    def visualize_mermaid_png(self, graph):
        return graph.get_graph().draw_mermaid_png()

    @classmethod
    def visualize_png(self, graph):
            return graph.get_graph().draw_png()