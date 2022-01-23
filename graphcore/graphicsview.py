# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.Qt import QMouseEvent
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import numpy as np
import math
from graphcore.drawutil import gcore_arrow_polygon


class GraphCoreView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._main_window = None
        self._shell = None
        self._navigation_node = None
        self._press_pos = None
        self._double_clicked = False
        self._zoom = 1

    def set_main_window(self, main_window):
        self._main_window = main_window

    def set_shell(self, shell):
        self._shell = shell

    def set_navigation_node(self, node):
        self._navigation_node = node

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        #from graphcore.graphicsscene import GraphCoreScene
        #from graphcore.graphicsitem import GCGridItem
        super().resizeEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        if event.modifiers() & Qt.ControlModifier:
            self._zoom += event.angleDelta().y()/2880
            self.scale(self._zoom, self._zoom)
        else:
            super().wheelEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        pass  # do nothing
        # from graphcore.graphicsitem import GCItemGroup, GraphCoreNodeItemInterface, GraphCoreEdgeItemInterface
        # #self._main_window.print("mouseDoubleClickEvent({})".format(event.pos()))
        # self._double_clicked = True
        # self.setDragMode(QGraphicsView.NoDrag)
        # self._main_window.handler.deselect_all()
        # w, h = 4, 4
        # x, y = event.pos().x() - w/2, event.pos().y() - h/2
        # nodes_or_edges_or_groups = self.select_elements(x, y, w, h)
        # if len(nodes_or_edges_or_groups) > 0:
        #     elem = nodes_or_edges_or_groups[0]
        #     if isinstance(elem, GraphCoreNodeItemInterface):
        #         for n in self._main_window.element_to_item.keys():
        #             if elem == self._main_window.element_to_item[n]:
        #                 self._main_window.command_select_node(n)
        #                 break
        #     elif isinstance(elem, GraphCoreEdgeItemInterface):
        #         for e in self._main_window.element_to_item.keys():
        #             if elem == self._main_window.element_to_item[e]:
        #                 self._main_window.command_select_edge(e)
        #                 break
        #     elif isinstance(elem, GCItemGroup):
        #         for g in self._main_window.element_to_item.keys():
        #             if elem == self._main_window.element_to_item[g]:
        #                 self._main_window.command_select_group(g)
        #                 break
        # super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        from graphcore.graphicsscene import GraphCoreScene
        # render mouse coordinate
        scenePos = self.mapToScene(event.pos())
        coord = "({:.2f}, {:.2f})".format(scenePos.x(), scenePos.y())
        # painter = QtGui.QPainter(self)
        # painter.begin(self)
        # painter.setFont(QtGui.QFont(u'メイリオ', 11))
        # painter.setPen(QtGui.QColor("black"))
        # painter.drawText(self.rect(), Qt.AlignTop | Qt.AlignHCenter, coord)
        # painter.fillRect(self.rect(), QtGui.QColor("blue"))
        scene = self.scene()
        text_item: QGraphicsSimpleTextItem = scene.text_item
        text_item.setText(coord)
        text_item.setPos(self.mapToScene(5, 5))
        text_item.setZValue(1)
        # scene.set_coord(scenePos.x(), scenePos.y())
        #self._main_window.print("mouseMoveEvent button={}, pos={}".format(event.button(), event.pos()))
        if self._main_window.handler.extras['edge_creating']:
            (source, sx, sy, r, item, edge_type) = self._main_window.handler.extras['temp_coords']
            pos = self.mapToScene(event.pos())
            poly = gcore_arrow_polygon(sx, sy, r, pos.x(), pos.y(), 0, 10, np.pi/6.0)
            item.setPolygon(poly)
        else:
            pass
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        from graphcore.graphicsitem import GraphCoreNodeItemInterface
        #self._main_window.print("mousePressEvent button={}, pos={}".format(event.button(), event.pos()))
        self._press_pos = event.pos()
        if event.button() == 1:  # Left
            self.setDragMode(QGraphicsView.RubberBandDrag)
            if self._main_window.handler.extras['edge_creating']: # if edge creating
                item = self.find_top_node(event.pos())
                if item is not None:
                    if not isinstance(item, GraphCoreNodeItemInterface):
                        self._main_window.print("bug! item is not node")
                        return
                    d = item
                    (s, sx, sy, r, arrow, edge_type) = self._main_window.handler.extras['temp_coords']
                    if s == d.node:
                        return
                    e = (s, d.node)
                    if e in self._main_window.handler.context.edges:
                        self._main_window.print("edge {} already exists".format(e))
                        return
                    attrs = {}
                    default_settings = self._main_window.settings.setting('default-edge-attrs')[edge_type]
                    for k in default_settings.keys():
                        if k not in attrs.keys():
                            attrs[k] = default_settings[k]['value']
                    self._main_window.handler.add_edge(e[0], e[1], attrs=attrs)
                    self.scene().removeItem(arrow)
                    self._main_window.handler.extras['temp_coords'] = None
                    self._main_window.handler.extras['edge_creating'] = False
            else:
                pass
                # w, h = 6, 6
                # x, y = event.pos().x() - w/2, event.pos().y()/h
                # nodes = self.select_nodes(x, y, w, h)
                # if len(nodes) > 0:
                #     elem = self._main_window.item_to_element(nodes[0])
                #     self._main_window.handler.select_node(elem)
                # else:
                #     self._main_window.handler.deselect_all()
        elif event.button() == 2:  # right
            if self._main_window.handler.extras['edge_creating']:
                (s, sx, sy, r, item, _) = self._main_window.handler.extras['temp_coords']
                self.scene().removeItem(item)
                self._main_window.handler.extras['temp_coords'] = None
                self._main_window.handler.extras['edge_creating'] = False
            pass
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        #self._main_window.print("mouseReleaseEvent button={}, pos={}".format(event.button(), event.pos()))
        from graphcore.graphicsitem import GraphCoreNodeItemInterface, GraphCoreEdgeItemInterface
        if event.button() == 1:  # left button
            if self.rubberBandRect() is None or (self.rubberBandRect().width() == 0 and self.rubberBandRect().height() == 0):
                w, h = 4, 4
                x, y = event.pos().x() - w/2, event.pos().y() - h/2
                nodes_or_edges_or_groups = self.select_elements(x, y, w, h, Qt.IntersectsItemShape)
                if len(nodes_or_edges_or_groups) == 0:
                    self._main_window.handler.deselect_all()
                elif event.modifiers() & Qt.ControlModifier:
                    self._main_window.handler.add_select_elements([nodes_or_edges_or_groups[0]])
                else:
                    self._main_window.handler.select_elements([nodes_or_edges_or_groups[0]])
                self.setDragMode(QGraphicsView.NoDrag)
                return
            self.setDragMode(QGraphicsView.NoDrag)
            if event.pos().x() == self._press_pos.x() and event.pos().y() == self._press_pos.y(): # clicked:
                w, h = 8, 8
                x = event.pos().x() - w/2
                y = event.pos().y() - h/2
                if event.modifiers() & Qt.ControlModifier:
                    nodes_or_edges_or_groups = self.select_elements(x, y, w, h, Qt.IntersectsItemShape)
                    self._main_window.handler.add_select_elements([nodes_or_edges_or_groups[0]])
                else:
                    nodes_or_edges_or_groups = self.select_elements(x, y, w, h, Qt.IntersectsItemShape)
                    self._main_window.handler.deselect_all()
                    self._main_window.handler.select_elements([nodes_or_edges_or_groups[0]])
            else:
                if event.pos().x() < self._press_pos.x():
                    x = event.pos().x()
                    w = self._press_pos.x() - event.pos().x()
                else:
                    x = self._press_pos.x()
                    w = event.pos().x() - self._press_pos.x()
                if w == 0:
                    w = 1
                if event.pos().y() < self._press_pos.y():
                    y = event.pos().y()
                    h = self._press_pos.y() - event.pos().y()
                else:
                    y = self._press_pos.y()
                    h = event.pos().y() - self._press_pos.y()
                if h == 0:
                    h = 1
                if w < 8 or h < 8: # width or height is too small
                    m = Qt.IntersectsItemShape
                else:
                    m = Qt.ContainsItemShape
                if event.modifiers() & Qt.ControlModifier:
                    nodes_or_edges_or_groups = self.select_elements(x, y, w, h, m)
                    self._main_window.handler.add_select_elements(nodes_or_edges_or_groups)
                else:
                    nodes_or_edges_or_groups = self.select_elements(x, y, w, h, m)
                    self._main_window.handler.deselect_all()
                    self._main_window.handler.select_elements(nodes_or_edges_or_groups)
        super().mouseReleaseEvent(event)

    def select_elements(self, x, y, w, h, m=Qt.IntersectsItemShape):
        self._main_window.print("select_elements {},{}+{}x{}".format(x,y,w,h))
        nodes = self.select_nodes(x, y, w, h, m)
        edges = self.select_edges(x, y, w, h, m)
        groups = self.select_groups(x, y, w, h, m)
        elems = []
        for i in groups:
            self._main_window.print(i)
            elems.append(self._main_window.item_to_element(i))
        for i in nodes:
            self._main_window.print(i)
            elems.append(self._main_window.item_to_element(i))
        for i in edges:
            self._main_window.print(i)
            elems.append(self._main_window.item_to_element(i))
        return tuple(elems)

    def select_nodes(self, x, y, w, h, m=Qt.IntersectsItemShape):
        from graphcore.graphicsitem import GCItemGroup
        items = self.items(x,y, w, h, m)
        nodes = []
        for i in items:
            c = self.to_node(i)
            if c is not None and c not in nodes and not isinstance(c.parentItem(), GCItemGroup):
                nodes.append(c)
        return tuple(nodes)

    def select_edges(self, x, y, w, h, m=Qt.IntersectsItemShape):
        from graphcore.graphicsitem import GCItemGroup
        items = self.items(x, y, w, h, m)
        edges = []
        for i in items:
            c = self.to_edge(i)
            if c is not None and c not in edges and not isinstance(c.parentItem(), GCItemGroup):
                edges.append(c)
        return tuple(edges)

    def select_groups(self, x, y, w, h, m=Qt.IntersectsItemShape):
        items = self.items(x, y, w, h, m)
        groups = []
        for i in items:
            c = self.to_group(i)
            if c is not None and c not in groups:
                groups.append(c)
        return tuple(groups)

    def to_node(self, i):
        from graphcore.graphicsitem import GraphCoreNodeItemInterface
        for k in self._main_window.element_to_item.keys():
            c = self._main_window.element_to_item[k]
            if isinstance(c, GraphCoreNodeItemInterface):
                if i == c or i in c.childItems():
                    return c
        return None

    def to_edge(self, i):
        from graphcore.graphicsitem import GraphCoreEdgeItemInterface
        for k in self._main_window.element_to_item.keys():
            c = self._main_window.element_to_item[k]
            if isinstance(c, GraphCoreEdgeItemInterface):
                if i == c or i in c.childItems():
                    return c
        return None

    def to_group(self, i):
        from graphcore.graphicsitem import GCItemGroup
        for k in self._main_window.element_to_item.keys():
            c = self._main_window.element_to_item[k]
            if isinstance(c, GCItemGroup):
                return c
        return None

    def find_top_node(self, pos): # click only
        nodes = self.find_nodes(pos)
        if len(nodes) == 0:
            return None
        return nodes[0]

    def find_nodes(self, pos): # click only
        from graphcore.graphicsitem import GraphCoreNodeItemInterface
        w, h = 4, 4
        x, y = pos.x() - w/2, pos.y() - h/2
        items = []
        for c in self.items(x, y, w, h, Qt.IntersectsItemShape):
            if isinstance(c, GraphCoreNodeItemInterface):
                items.append(c)
        return items
