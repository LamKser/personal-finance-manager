from PIL import Image


class GraphVisualization:

    def __init__(self):
        pass
    
    def visualize_mermaid(self, graph):
        return graph.get_graph().draw_mermaid()
    
    def visualize_png(self, graph, save=None):
        if save:
            Image(graph.get_graph().draw_mermaid_png()).save(save)
            return 
        return graph.get_graph().draw_mermaid_png()
