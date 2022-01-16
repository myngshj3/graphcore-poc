# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.Qt import *
from graphcore.drawutil import *
from graphcore.settings import GraphCoreSettings, gcore_settings
from graphcore.graphicsitem import GraphCoreNodeItemInterface
from graphcore.graphicsitem import GraphCoreEdgeItemInterface
from graphcore.shell import GraphCoreContextHandler, GraphCoreShell


# scene to manipulate graph
class GraphCoreScene(QGraphicsScene):
    # initializer
    def __init__(self, handler=None):
        super().__init__()
        self.lines = []
        self._handler = handler
        self._settings = None
        self.setup_scene_rect()
        # self.draw_grid()

    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @handler.setter
    def handler(self, handler: GraphCoreContextHandler):
        self._handler = handler

    @property
    def settings(self) -> GraphCoreSettings:
        return self._settings

    @settings.setter
    def settings(self, settings: GraphCoreSettings):
        self._settings = settings

    # setup scene rectangle
    def setup_scene_rect(self):
        sets = gcore_settings()
        rect = sets.setting('default-scene-attrs')
        self.setSceneRect(rect['x'], rect['y'], rect['w'], rect['h'])

    # mouseMoveEvent
    def mouseMoveEvent(self, event):
        # if self.handler.extras['edge_creating']:
        #     (source, sx, sy, r, item, edge_type) = self.handler.extras['temp_coords']
        #     poly = gcore_arrow_polygon(sx, sy, r, event.scenePos().x(), event.scenePos().y(), 0, 10, np.pi/6.0)
        #     item.setPolygon(poly)
        super().mouseMoveEvent(event)

    def to_node(self, i):
        pass

    def to_edge(self, c):
        pass

    # find edges at
    def find_edges(self, pos):
        w, h = 4, 4
        x, y = pos.x() - w/2, pos.y() - h/2
        items = []
        for c in self.items(x, y, w, h, Qt.ContainsItemBoundingRect):
            if isinstance(c, GraphCoreEdgeItemInterface):
                items.append(c)
        return items

    # find top edge at
    def find_top_edge(self, pos):
        edges = self.find_edges(pos)
        if len(edges) == 0:
            return None
        return edges[0]

    # find nodes at
    def find_nodes(self, pos):
        w, h = 4, 4
        x, y = pos.x() - w/2, pos.y() - h/2
        items = []
        for c in self.items(x, y, w, h, Qt.ContainsItemBoundingRect, Qt.DescendingOrder):
            if isinstance(c, GraphCoreNodeItemInterface):
                items.append(c)
        return items

    # find top node at
    def find_top_node(self, pos):
        nodes = self.find_nodes(pos)
        if len(nodes) == 0:
            return None
        return nodes[0]

    def sceneRectChanged(self, rect: QtCore.QRectF) -> None:
        self.views()[0].fitInView(self.sceneRect())
        super().sceneRectChanged(rect)
    # mousePressEvent
    # def mousePressEvent(self, event):
        # print("mousePressEvent button={}, pos={}".format(event.button(), event.pos()))
        # if event.button() == 1:  # Left
        #     if self.handler.extras['edge_creating']:
        #         # item = self.itemAt(event.scenePos().x(), event.scenePos().y(), QTransform())
        #         item = self.find_top_node(event.scenePos())
        #         if item is not None:
        #             if not isinstance(item, GraphCoreNodeItemInterface):
        #                 print("bug! item is not node")
        #                 return
        #             d = item
        #             (s, sx, sy, r, arrow, edge_type) = self.handler.extras['temp_coords']
        #             if s == d.node:
        #                 return
        #             e = (s, d.node)
        #             if e in self.handler.context.edges:
        #                 print("edge {} already exists".format(e))
        #                 return
        #             attrs = {}
        #             default_settings = self._settings.setting('default-edge-attrs')[edge_type]
        #             for k in default_settings.keys():
        #                 if k not in attrs.keys():
        #                     attrs[k] = {}
        #                     attrs[k]['value'] = default_settings[k]['value']
        #                     attrs[k]['type'] = default_settings[k]['type']
        #                     attrs[k]['visible'] = default_settings[k]['visible']
        #                     if 'list' in default_settings[k].keys():
        #                         attrs[k]['list'] = default_settings[k]['list']
        #             self.handler.add_edge(e[0], e[1], attrs=attrs)
        #             self.removeItem(arrow)
        #             self.handler.extras['temp_coords'] = None
        #             self.handler.extras['edge_creating'] = False
        #     elif self.find_top_node(event.scenePos()) is None:
        #         self.handler.deselect_all()
        #         return
        #     else:
        #         pass
        #     pass
        # elif event.button() == 2:  # right
        #     if self.handler.extras['edge_creating']:
        #         (s, sx, sy, r, item, _) = self.handler.extras['temp_coords']
        #         self.removeItem(item)
        #         self.handler.extras['temp_coords'] = None
        #         self.handler.extras['edge_creating'] = False
        #     pass
        # super().mousePressEvent(event)

    # def draw_grid(self):
    #     width = 10 * 50
    #     height = 10 * 50
    #     self.setSceneRect(0, 0, width, height)
    #     self.setItemIndexMethod(QGraphicsScene.NoIndex)
    #
    #     pen = QPen(QColor(255, 0, 100), 1, Qt.SolidLine)
    #
    #     for x in range(0, 10 + 1):
    #         xc = x * 50
    #         self.lines.append(self.addLine(xc, 0, xc, height, pen))
    #
    #     for y in range(0, 10 + 1):
    #         yc = y * 50
    #         self.lines.append(self.addLine(0, yc, width, yc, pen))

