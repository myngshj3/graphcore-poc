
import sys
import re
import networkx as nx
from queue import Queue
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5.QtGui import *



class GCScene(QGraphicsScene):

    def __init__(self, graph, queue: Queue):
        super().__init__()
        self._selected_item = None
        self._selected_node = None
        self._selected_node_name = None
        self._graph = graph
        self._queue = queue

    @property
    def selected_item(self) -> QGraphicsItem:
        return self._selected_item

    @property
    def selected_node(self) -> int:
        return self._selected_node

    @property
    def selected_node_name(self) -> str:
        return self._selected_node_name

    @property
    def graph(self) -> nx.DiGraph:
        return self._graph

    @property
    def queue(self) -> Queue:
        return self._queue

    # mousePressEvent
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # Left
            item = self.itemAt(event.scenePos(), QTransform())
            if item is not None:
                for n in self.graph.nodes:
                    g: QGraphicsItemGroup = self.graph.nodes[n]['item']
                    if item in g.childItems():
                        self._selected_node = n
                        self._selected_node_name = self.graph.nodes[n]['name']
                        # print("node name {} stored".format(self.selected_node_name))
                        break
        elif event.button() == Qt.RightButton:  # right
            pass
        super().mousePressEvent(event)
        pass

    # mouseMoveEvent
    def mouseMoveEvent(self, event):
        if self._selected_node_name is not None:
            last_scene_pos = event.lastScenePos()
            scene_pos = event.scenePos()
            dx = scene_pos.x() - last_scene_pos.x()
            dy = scene_pos.y() - last_scene_pos.y()
            command = "move-by {} {},{}".format(self.selected_node_name, dx, dy)
            self.queue.put(command)
            # print("queue put command:", command, self.queue)
        pass

    # mouseReleaseEvent
    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self._selected_item = None
        self._selected_node = None
        self._selected_node_name = None
        super().mouseMoveEvent(event)
        pass

