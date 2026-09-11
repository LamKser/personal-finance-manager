from PIL import Image


class GraphVisualization:

    @classmethod
    def visualize_mermaid(self, graph):
        return graph.get_graph().draw_mermaid()

    @classmethod
    def visualize_png(self, graph, save=None):
        if save:
            Image(graph.get_graph().draw_mermaid_png()).save(save)
            return 
        return graph.get_graph().draw_mermaid_png()
