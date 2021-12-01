

from PyQt5.QtWidgets import *
import networkx as nx


class GraphItemEventHandler:

    # _instance = None
    #
    # def get_instance():
    #     if GraphItemEventHandler._instance is None:
    #         GraphItemEventHandler._instance = GraphItemEventHandler()
    #     return GraphItemEventHandler._instance

    def __init__(self, owner, shell=None, print_func=None):
        self._owner = owner
        self._shell = shell
        self._print_func = print_func

    def owner(self):
        return self._owner

    def set_owner(self, owner):
        self._owner = owner

    def print(self, text):
        if self._print_func is not None:
            self._print_func(str(text))

    def move_node(self, item, event: 'QGraphicsSceneMouseEvent') -> None:
        # self.print("item {} move to ({},{})".format(item.graph_element(), event.pos().x(), event.pos().y()))
        dx = event.pos().x() - event.lastPos().x()
        dy = event.pos().y() - event.lastPos().y()
        item.moveBy(dx, dy)
        src_node = self.owner().graph_element()
        u = self.owner().graph().nodes[src_node]
        u['x'] += dx
        u['y'] += dy
        self._shell.node_changed(item)
        adjs = self.owner().graph().successors(src_node)
        for edge in self.owner().graph().edges:
            if edge[0] == src_node:
                dst_node = edge[1]
                e = str(edge)
                if e in self.owner().element_storage().keys():
                    v = self.owner().graph().nodes[dst_node]
                    line = self.owner().element_storage()[e]
                    line.setLine(u['x'], u['y'], v['x'], v['y'])
        # for dst_node in adjs:
        #     e = (src_node, dst_node)
        #     e = str(e)
        #     if e in self.owner().element_storage().keys():
        #         v = self.owner().graph().nodes[dst_node]
        #         line = self.owner().element_storage()[e]
        #         self.print("forward edge {}".format(e))
        #         line.setLine(u['x'], u['y'], v['x'], v['y'])
        dst_node = src_node
        v = u
        for edge in self.owner().graph().edges:
            if edge[1] == dst_node:
                src_node = edge[0]
                e = str(edge)
                if e in self.owner().element_storage().keys():
                    u = self.owner().graph().nodes[src_node]
                    line = self.owner().element_storage()[e]
                    line.setLine(u['x'], u['y'], v['x'], v['y'])
        # adjs = nx.algorithms.dag.descendants(self.owner().graph(), dst_node)
        # for src_node in adjs:
        #     e = (src_node, dst_node)
        #     e = str(e)
        #     if e in self.owner().element_storage().keys():
        #         u = self.owner().graph().nodes[src_node]
        #         line = self.owner().element_storage()[e]
        #         line.setLine(u['x'], u['y'], v['x'], v['y'])

    def move_edge(self, item, event: 'QGraphicsSceneMouseEvent') -> None:
        # self.print("item {} move to ({},{})".format(item, event.pos().x(), event.pos().y()))
        # do nothing
        pass
