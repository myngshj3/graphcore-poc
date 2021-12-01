# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *


class GraphCoreView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._main_window = None
        self._shell = None
        self._navigation_node = None

    def set_main_window(self, main_window):
        self._main_window = main_window

    def set_shell(self, shell):
        self._shell = shell

    def set_navigation_node(self, node):
        self._navigation_node = node

    def mouseMoveEvent(self, event):
        # print("{} mouseMoveEvent at {}".format(self, event))
        # if self._navigation_node is not None:
        #     graph = self._shell.graph()
        #     nn = graph.nodes[self._navigation_node]
        #     # self._main_window.command_
        #     self._main_window.command_move_node_by(self._navigation_node, event.pos().x() - nn['x'], event.pos().y() - nn['y'])
        super().mouseMoveEvent(event)

