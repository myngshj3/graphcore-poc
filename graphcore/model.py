
import networkx as nx


class GraphCoreModel:
    def __init__(self):
        self._dirty: bool = False
        self._graph: nx.DiGraph = nx.DiGraph()

    def dirty(self):
        return self._dirty

    def set_dirty(self, flag: bool):
        self._dirty = flag

    def is_dirty(self):
        return self.dirty()

    def graph(self):
        return self._graph

