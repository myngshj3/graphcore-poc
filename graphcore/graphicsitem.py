# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import *
import typing
import sys
import networkx as nx
import math
import numpy as np
from graphcore.drawutil import *
from graphcore.shell import GraphCoreContext, GraphCoreContextHandler


# GraphCore Item Interafce class
class GraphCoreItemInterface(QGraphicsItem):
    def __init__(self, context=None, handler=None):
        super().__init__()
        self._context = context
        self._handler = handler
        self._label = None

    @property
    def context(self) -> GraphCoreContext:
        return self._context

    @context.setter
    def context(self, _context: GraphCoreContext):
        self._context = _context

    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @handler.setter
    def handler(self, _handler: GraphCoreContextHandler):
        self._handler = _handler

    @property
    def label(self) -> QGraphicsTextItem:
        return self._label

    @label.setter
    def label(self, _label: QGraphicsTextItem):
        self._label = _label


# GraphCore Node Item Interface class
class GraphCoreNodeItemInterface(GraphCoreItemInterface):
    def __init__(self, node=None, context=None, handler=None):
        super().__init__(context, handler)
        self._node = node
        self.context = context
        self.handler = handler
        self._label = QGraphicsTextItem(context.nodes[node]['label']['value'])
        self._label.setParentItem(self)

    @property
    def node(self):
        return self._node

    @property
    def show_label(self):
        return self.context.nodes[self.node]['show-label']['value']

    @show_label.setter
    def show_label(self, value: bool):
        self.context.nodes[self.node]['show-label']['value'] = value
        if value:
            self.label.show()
        else:
            self.label.hide()

    # def move_by(self, dx, dy):
    #     super().moveBy(dx, dy)


# GraphCore's circle shaped node graphics item class
class GraphCoreCircleNodeItem(QGraphicsEllipseItem, GraphCoreNodeItemInterface):
    def __init__(self, node, context: GraphCoreContext, handler: GraphCoreContextHandler):
        super().__init__(node, context, handler)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPen(QPen())
        self.draw()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...) -> None:
        super().paint(painter, option, widget)
        attrs = self.context.nodes[self.node]
        # draw image
        image_path = attrs['image-path']['value']
        if len(image_path) != 0:
            pixmap = gcore_get_pixmap(image_path)
            x = attrs['x']['value']
            y = attrs['y']['value']
            w = attrs['w']['value']
            h = attrs['h']['value']
            painter.drawPixmap(x-w/2, y-h/2, w, h, pixmap)
        # draw double line
        if self.handler.context.nodes[self.node]['shape']['value'] == "doublecircle":
            margin = 4
            rect = self.rect()
            x = rect.x() + margin
            y = rect.y() + margin
            w = rect.width() - margin * 2
            h = rect.height() - margin * 2
            painter.drawEllipse(QRectF(x, y, w, h))

    def draw(self):
        self.redraw()

    def redraw(self):
        n = self.context.nodes[self.node]
        if n['shape']['value'] not in ('circle', 'doublecircle'):
            item = gcore_create_node_item(self.node, self.context, self.handler)
            self.handler.extras['scene'].removeItem(self)
            self.handler.extras['scene'].addItem(item)
            self.handler.extras['element_to_item'][self.node] = item
            return
        label: QGraphicsTextItem = self.label
        label.setPlainText(n['label']['value'])
        if n['filled']['value']:
            brush = QBrush(QColor(n['fill-color']['value']))
            self.setBrush(brush)
        else:
            self.setBrush(QColor())
        x = n['x']['value']
        y = n['y']['value']
        w = n['w']['value']
        h = n['h']['value']
        # print("redraw rect ({}, {}, {}, {}) of {}".format(x, y, w, h, self))
        # print("  sceneRect ({}, {}, {}, {}) of {}".format(sceneRect.x() + sceneRect.width()/2, sceneRect.y() + sceneRect.height()/2, sceneRect.width(), sceneRect.height(), self))
        self.setRect(x - w/2, y - h/2, w, h)
        rect = label.sceneBoundingRect()
        label.setPos(x - rect.width()/2, y - rect.height()/2)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
         print("mouse pressed at {} of scene".format(event.pos()))
         if event.button() == 1:  # Left button
            self.handler.deselect_all()
            self.handler.select_node(self.node)
        # super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        dx, dy = event.scenePos().x() - event.lastScenePos().x(), event.scenePos().y() - event.lastScenePos().y()
        # dx, dy = event.pos().x() - event.lastPos().x(), event.pos().y() - event.lastPos().y()
        if dx != 0 or dy != 0:
            # print("mouseMoveEvent: dx={},dy={}".format(dx, dy))
            # self.moveBy(dx, dy)
            self.handler.move_node_by(self.node, dx, dy)


# GraphCore's rectangle shaped node graphics item class
class GraphCoreRectNodeItem(QGraphicsRectItem, GraphCoreNodeItemInterface):
    def __init__(self, node, context: GraphCoreContext, handler: GraphCoreContextHandler):
        super().__init__(node, context, handler)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setPen(QPen())
        self.draw()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...) -> None:
        super().paint(painter, option, widget)
        attrs = self.context.nodes[self.node]
        # draw image
        image_path = attrs['image-path']['value']
        if len(image_path) != 0:
            pixmap = gcore_get_pixmap(image_path)
            x = attrs['x']['value']
            y = attrs['y']['value']
            w = attrs['w']['value']
            h = attrs['h']['value']
            painter.drawPixmap(x-w/2, y-h/2, w, h, pixmap)
        if self.handler.context.nodes[self.node]['shape']['value'] == "doublebox":
            margin = 4
            rect = self.rect()
            x = rect.x() + margin
            y = rect.y() + margin
            w = rect.width() - margin * 2
            h = rect.height() - margin * 2
            painter.drawRect(QRectF(x, y, w, h))

    def draw(self):
        self.redraw()

    def redraw(self):
        n = self.context.nodes[self.node]
        if n['shape']['value'] not in ('box', 'doublebox'):
            item = gcore_create_node_item(self.node, self.context, self.handler)
            self.handler.extras['scene'].removeItem(self)
            self.handler.extras['scene'].addItem(item)
            self.handler.extras['element_to_item'][self.node] = item
            return
        label: QGraphicsTextItem = self.label
        label.setPlainText(n['label']['value'])
        if n['filled']['value']:
            brush = QBrush(QColor(n['fill-color']['value']))
            self.setBrush(brush)
        else:
            self.setBrush(QColor())
        x = n['x']['value']
        y = n['y']['value']
        w = n['w']['value']
        h = n['h']['value']
        self.setRect(x - w/2, y - h/2, w, h)
        rect = label.sceneBoundingRect()
        # label.setPos(x + w/2 - rect.width()/2, y + h/2 - rect.height()/2)
        label.setPos(x - rect.width()/2, y - rect.height()/2)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # print("mouse pressed at {} of scene".format(event.pos()))
        if event.button() == 1:  # Left button
            self.handler.deselect_all()
            self.handler.select_node(self.node)
        # super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        dx, dy = event.scenePos().x() - event.lastScenePos().x(), event.scenePos().y() - event.lastScenePos().y()
        # dx, dy = event.pos().x() - event.lastPos().x(), event.pos().y() - event.lastPos().y()
        if dx != 0 or dy != 0:
            # print("mouseMoveEvent: dx={},dy={}".format(dx, dy))
            # self.moveBy(dx, dy)
            self.handler.move_node_by(self.node, dx, dy)


# GraphCore Edge Item interface
class GraphCoreEdgeItemInterface(GraphCoreItemInterface):
    def __init__(self, u, v, context: GraphCoreContext, handler: GraphCoreContextHandler):
        super().__init__(context, handler)
        self._u = u
        self._v = v
        self.context = context
        self.handler = handler
        self.label = QGraphicsTextItem(context.edges[u, v]['label']['value'])
        self.label.setParentItem(self)

    @property
    def u(self):
        return self._u

    @property
    def v(self):
        return self._v


# GraphCore's edge item
class GraphCoreEdgeItem(QGraphicsPolygonItem, GraphCoreEdgeItemInterface):
    def __init__(self, u, v, context: GraphCoreContext, handler: GraphCoreContextHandler):
        super().__init__(u, v, context=context, handler=handler)
        # super().__init__()
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setPen(QPen())
        self.draw()

    @property
    def u(self):
        return self._u

    @property
    def v(self):
        return self._v

    def calc_polygon(self, x_u, y_u, r_u, x_v, y_v, r_v, head_len, head_angle):
        polygon = QPolygonF()
        try:
            vec = (x_v - x_u, y_v - y_u)
            len_vec = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
            vec = (vec[0]/len_vec, vec[1]/len_vec)
            x_s, y_s = vec[0] * r_u + x_u, vec[1] * r_u + y_u
            x_d, y_d = x_v - vec[0]*r_v, y_v - vec[1]*r_v
            polygon.fill(QPointF(x_s, y_s))
            polygon.append(QPointF(x_s, y_s))
            polygon.append(QPointF(x_d, y_d))
            vec2 = gcore_rot_vec(vec[0], vec[1], math.pi - head_angle)
            polygon.append(QPointF(x_d + vec2[0] * head_len, y_d + vec2[1] * head_len))
            vec3 = gcore_rot_vec(vec[0], vec[1], -math.pi + head_angle)
            polygon.append(QPointF(x_d + vec3[0] * head_len, y_d + vec3[1] * head_len))
            polygon.append(QPointF(x_d, y_d))
        except ZeroDivisionError as ex:
            print(ex)
        finally:
            return polygon

    def create_polygon(self):
        u = self.context.nodes[self.u]
        if u['w']['value'] < u['h']['value']:
            r_u = u['h']['value']/2
        else:
            r_u = u['w']['value']/2
        v = self.context.nodes[self.v]
        if v['w']['value'] < v['h']['value']:
            r_v = v['h']['value']/2
        else:
            r_v = v['w']['value']/2
        e = self.context.edges[self.u, self.v]
        polygon = self.calc_polygon(u['x']['value'], u['y']['value'], r_u, v['x']['value'], v['y']['value'],
                                    r_v, e['arrow-length']['value'], e['arrow-angle']['value'])
        return polygon

    def draw(self):
        self.redraw()

    def redraw(self):
        e = self.context.edges[self.u, self.v]
        if e['filled']['value']:
            brush = QBrush(QColor(e['fill-color']['value']))
            self.setBrush(brush)
        else:
            self.setBrush(QColor())
        self.setPolygon(self.create_polygon())
        u = self.context.nodes[self.u]
        v = self.context.nodes[self.v]
        self._label.setPlainText(e['label']['value'])
        self._label.setPos((u['x']['value']+v['x']['value'])/2, (u['y']['value']+v['y']['value'])/2)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print("mouse of {} pressed at {}".format(self, event.pos()))
        if event.button() == 1:  # Left button
            self.handler.deselect_all()
            self.handler.select_edge(self.u, self.v)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if event.button() == 1:  # Left button
            self.handler.deselect_all()
            self.handler.select_edge(self.u, self.v)


def gcore_create_node_item(n, context: GraphCoreContext, handler: GraphCoreContextHandler):
    attr = context.nodes[n]
    if attr['shape']['value'] in ('circle', 'doublecircle'):
        item = GraphCoreCircleNodeItem(n, context, handler)
    elif attr['shape']['value'] in ('box', 'doublebox'):
        item = GraphCoreRectNodeItem(n, context, handler)
    else:
        handler.reporter.report("GraphCore Error!!! Unsupported shape:{}".format(attr['shape']['value']))
        return None
    return item
