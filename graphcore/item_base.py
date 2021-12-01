
from PyQt5.QtWidgets import *


class GraphItemBase:
    # def __init__(self):  # , graph=None, graph_element=None, element_storage=None, event_handler=None, print_func=None):
    #     # self._graph = graph
    #     # self._graph_element = graph_element
    #     # self._element_storage = element_storage
    #     # self._print = print_func
    #     # self._event_handler = None
    #     # self.set_event_handler(event_handler)

    def graph_element(self):
        return self._graph_element

    def set_graph_element(self, n):
        self._graph_element = n

    def graph(self):
        return self._graph

    def set_graph(self, g):
        self._graph = g

    def element_storage(self):
        return self._element_storage

    def set_element_storage(self, s):
        self._element_storage = s

    def set_print_func(self, func):
        self._print = func

    def set_event_handler(self, handler):
        self._event_handler = handler
        if handler is not None:
            handler.set_owner(self)

    def print(self, text):
        if self.print is not None:
            self.print(str(text))

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        element = self.element_storage()[str(self.graph_element())]
        self._event_handler.move_node(element, event)