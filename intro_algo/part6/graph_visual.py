import graphviz
from intro_algo.part6.graph import Graph


class GraphVisual:
    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def render(self):
        dot = graphviz.Digraph('graph')

        for u in self._graph.nodes:
            dot.node(u)
        
        for k, link in self._graph.links.items():
            dot.edge(link.src_id, link.dst_id)
        
        dot.render(directory='doctest-output').replace('\\', '/')