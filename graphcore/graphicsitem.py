# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import *
from PyQt5 import QtCore, QtGui
import typing
import sys
import networkx as nx
import math
import numpy as np
from graphcore.drawutil import *
from graphcore.shell import GraphCoreContext, GraphCoreContextHandler


class GCItemGroup(QGraphicsItemGroup):

    def __init__(self, context, handler):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self._context = context
        self._handler = handler
        self._selected = False
        self._left_top_bound = QGraphicsRectItem()
        self._left_center_bound = QGraphicsRectItem()
        self._left_bottom_bound = QGraphicsRectItem()
        self._center_top_bound = QGraphicsRectItem()
        self._center_bottom_bound = QGraphicsRectItem()
        self._right_top_bound = QGraphicsRectItem()
        self._right_center_bound = QGraphicsRectItem()
        self._right_bottom_bound = QGraphicsRectItem()
        self._left_top_bound.setVisible(False)
        self._left_center_bound.setVisible(False)
        self._left_bottom_bound.setVisible(False)
        self._center_top_bound.setVisible(False)
        self._center_bottom_bound.setVisible(False)
        self._right_top_bound.setVisible(False)
        self._right_center_bound.setVisible(False)
        self._right_bottom_bound.setVisible(False)

    def boundingRect(self) -> QtCore.QRectF:
        return self.childrenBoundingRect()

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        boundingRect = self.boundingRect()
        painter.setPen(QtCore.Qt.PenStyle.DashLine)
        painter.drawRect(boundingRect)
        if self.is_selected:
            w, h = 4, 4
            rect = QRectF(boundingRect.x(), boundingRect.y(), w, h)
            painter.drawRect(rect)
            rect = QRectF(boundingRect.x(), boundingRect.y()+boundingRect.height()-h, w, h)
            painter.drawRect(rect)
            rect = QRectF(boundingRect.x()+boundingRect.width()-w, boundingRect.y(), w, h)
            painter.drawRect(rect)
            rect = QRectF(boundingRect.x() + boundingRect.width() - w, boundingRect.y()+boundingRect.height()-h, w, h)
            painter.drawRect(rect)

    @property
    def is_selected(self):
        return self._selected

    def select(self):
        self._selected = True
        self.show_bound_points(True)

    def deselect(self):
        self._selected = False
        self.show_bound_points(False)

    def show_bound_points(self, flag=True):
        self._left_top_bound.setVisible(flag)
        self._left_center_bound.setVisible(flag)
        self._left_bottom_bound.setVisible(flag)
        self._center_top_bound.setVisible(flag)
        self._center_bottom_bound.setVisible(flag)
        self._right_top_bound.setVisible(flag)
        self._right_center_bound.setVisible(flag)
        self._right_bottom_bound.setVisible(flag)

    def paint_bound_points(self, boundingRect):
        w, h = 4, 4
        x, y = boundingRect.x(), boundingRect.y()
        self._left_top_bound.setRect(x, y, w, h)
        x = boundingRect.x() + boundingRect.width()/2 - w/2
        self._center_top_bound.setRect(x, y, w, h)
        x = boundingRect.x() + boundingRect.width() - w
        self._right_top_bound.setRect(x, y, w, h)
        x, y = boundingRect.x(), boundingRect.y() + boundingRect.height()/2 - h/2
        self._left_center_bound.setRect(x, y, w, h)
        x = boundingRect.x() + boundingRect.width() - w
        self._right_center_bound.setRect(x, y, w, h)
        x, y = boundingRect.x(), boundingRect.y() + boundingRect.height() - h
        self._left_bottom_bound.setRect(x, y, w, h)
        x = boundingRect.x() + boundingRect.width() / 2 - w / 2
        self._center_bottom_bound.setRect(x, y, w, h)
        x = boundingRect.x() + boundingRect.width() - w
        self._right_bottom_bound.setRect(x, y, w, h)

    def move_bound_points_by(self, dx, dy):
        x, y = self._left_top_bound.x() + dx, self._left_top_bound.y() + dy
        self._left_top_bound.setX(x)
        self._left_top_bound.setY(y)
        x, y = self._center_top_bound.x() + dx, self._center_top_bound.y() + dy
        self._center_top_bound.setX(x)
        self._center_top_bound.setY(y)
        x, y = self._right_top_bound.x() + dx, self._right_top_bound.y() + dy
        self._right_top_bound.setX(x)
        self._right_top_bound.setY(y)
        x, y = self._left_center_bound.x() + dx, self._left_center_bound.y() + dy
        self._left_center_bound.setX(x)
        self._left_center_bound.setY(y)
        x, y = self._right_center_bound.x() + dx, self._right_center_bound.y() + dy
        self._right_center_bound.setX(x)
        self._right_center_bound.setY(y)
        x, y = self._left_bottom_bound.x() + dx, self._left_bottom_bound.y() + dy
        self._left_bottom_bound.setX(x)
        self._left_bottom_bound.setY(y)
        x, y = self._center_bottom_bound.x() + dx, self._center_bottom_bound.y() + dy
        self._center_bottom_bound.setX(x)
        self._center_bottom_bound.setY(y)
        x, y = self._right_bottom_bound.x() + dx, self._right_bottom_bound.y() + dy
        self._right_bottom_bound.setX(x)
        self._right_bottom_bound.setY(y)

    def draw(self):
        self.redraw()

    def redraw(self):
        self.paint_bound_points(self.boundingRect())

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # print("mouseMoveEvent pos:{}, scenePos:{}".format(event.pos(), event.scenePos()))
        super().mouseMoveEvent(event)
        dx, dy = event.scenePos().x() - event.lastScenePos().x(), event.scenePos().y() - event.lastScenePos().y()
        dx, dy = event.pos().x() - event.lastPos().x(), event.pos().y() - event.lastPos().y()
        if dx != 0 or dy != 0:
            for c in self.childItems():
                pass # c.moveBy(dx, dy)
            # for g in self._handler.element_to_item.keys():
            #     if self == self._handler.element_to_item[g]:
            #         self._handler.move_group_by(g, dx, dy)
            #         break
                    # for e in self._handler.collect_edges(n):
                    #     i: GraphCoreEdgeItemInterface = items[e]
                    #     if i.parentItem() != self and e not in edges:
                    #         edges.append(e)
                    #self._handler.change_node_attr(n, 'x', x, 'y', y)
            # for e in edges:
            #     self._handler.update_edge(e[0], e[1])

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        #print("mousePressEvent pos:{}, scenePos:{}".format(event.pos(), event.scenePos()))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        #print("mouseReleseEvent pos:{}, scenePos:{}".format(event.pos(), event.scenePos()))
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseDoubleClickEvent(event)


# GraphCore Item Interafce class
class GraphCoreItemInterface(QGraphicsItem):
    def __init__(self, context=None, handler=None):
        super().__init__()
        self._context = context
        self._handler = handler
        self._label = None
        self._selected = False

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

    @property
    def is_selected(self):
        return self._selected

    def select(self):
        self._selected = True

    def deselect(self):
        self._selected = False

# GraphCore Node Item Interface class
class GraphCoreNodeItemInterface(GraphCoreItemInterface):
    def __init__(self, node=None, context=None, handler=None):
        super().__init__(context, handler)
        self._node = node
        self.context = context
        self.handler = handler
        self._label = QGraphicsTextItem(context.nodes[node]['label'])
        self._label.setParentItem(self)
        self._left_top_bound = QGraphicsRectItem()
        self._left_center_bound = QGraphicsRectItem()
        self._left_bottom_bound = QGraphicsRectItem()
        self._center_top_bound = QGraphicsRectItem()
        self._center_bottom_bound = QGraphicsRectItem()
        self._right_top_bound = QGraphicsRectItem()
        self._right_center_bound = QGraphicsRectItem()
        self._right_bottom_bound = QGraphicsRectItem()
        self._left_top_bound.setVisible(False)
        self._left_top_bound.setParentItem(self)
        self._left_top_bound.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self._left_center_bound.setVisible(False)
        self._left_center_bound.setParentItem(self)
        self._left_center_bound.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self._left_bottom_bound.setVisible(False)
        self._left_bottom_bound.setParentItem(self)
        self._center_top_bound.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self._center_top_bound.setVisible(False)
        self._center_top_bound.setParentItem(self)
        self._center_bottom_bound.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self._center_bottom_bound.setVisible(False)
        self._center_bottom_bound.setParentItem(self)
        self._right_top_bound.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self._right_top_bound.setVisible(False)
        self._right_top_bound.setParentItem(self)
        self._right_center_bound.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self._right_center_bound.setVisible(False)
        self._right_center_bound.setParentItem(self)
        self._right_bottom_bound.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self._right_bottom_bound.setVisible(False)
        self._right_bottom_bound.setParentItem(self)

    @property
    def node(self):
        return self._node

    @property
    def show_label(self):
        return self.context.nodes[self.node]['show-label']

    @show_label.setter
    def show_label(self, value: bool):
        self.context.nodes[self.node]['show-label'] = value
        if value:
            self.label.show()
        else:
            self.label.hide()

    def show_bound_points(self, flag=True):
        self._left_top_bound.setVisible(flag)
        self._left_center_bound.setVisible(flag)
        self._left_bottom_bound.setVisible(flag)
        self._center_top_bound.setVisible(flag)
        self._center_bottom_bound.setVisible(flag)
        self._right_top_bound.setVisible(flag)
        self._right_center_bound.setVisible(flag)
        self._right_bottom_bound.setVisible(flag)

    def paint_bound_points(self):
        w, h = 4, 4
        x, y = self.boundingRect().x() - w/2, self.boundingRect().y() - h/2
        self._left_top_bound.setRect(x, y, w, h)
        x = self.boundingRect().x() + self.boundingRect().width()/2 - w/2
        self._center_top_bound.setRect(x, y, w, h)
        x = self.boundingRect().x() + self.boundingRect().width() - w/2
        self._right_top_bound.setRect(x, y, w, h)
        x, y = self.boundingRect().x() - w/2, self.boundingRect().y() + self.boundingRect().height()/2 - h/2
        self._left_center_bound.setRect(x, y, w, h)
        x = self.boundingRect().x() + self.boundingRect().width() - w / 2
        self._right_center_bound.setRect(x, y, w, h)
        x, y = self.boundingRect().x() - w / 2, self.boundingRect().y() + self.boundingRect().height() - h / 2
        self._left_bottom_bound.setRect(x, y, w, h)
        x = self.boundingRect().x() + self.boundingRect().width() / 2 - w / 2
        self._center_bottom_bound.setRect(x, y, w, h)
        x = self.boundingRect().x() + self.boundingRect().width() - w / 2
        self._right_bottom_bound.setRect(x, y, w, h)

    def select(self):
        self.show_bound_points(True)
        super().select()

    def deselect(self):
        self.show_bound_points(False)
        super().deselect()


class GCCustomNodeItem(GraphCoreNodeItemInterface):

    def __init__(self, node, context: GraphCoreContext, handler: GraphCoreContextHandler):
        super().__init__(node, context, handler)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def boundingRect(self) -> QtCore.QRectF:
        x = self.handler.context.nodes[self.node]['x']
        y = self.handler.context.nodes[self.node]['y']
        w = self.handler.context.nodes[self.node]['w']
        h = self.handler.context.nodes[self.node]['h']
        return QRectF(x-w/2, y-h/2, w, h)

    def redraw(self):
        self.update(self.boundingRect())

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        n = self.handler.context.nodes[self.node]
        x = n['x']
        y = n['y']
        w = n['w']
        h = n['h']
        shape = n['shape']
        text_align = n['text-align']
        font_height = n['font-height']
        show_label = n['show-label']
        line_width = n['line-width']
        fill_color = n['fill-color']
        filled = n['filled']
        image_path = n['image-path']

        # fill
        if filled:
            if shape in ('box', 'doublebox'):
                painter.fillRect(QRectF(x - w / 2, y - h / 2, w, h), QColor(fill_color))
            elif shape in ('circle', 'doublecircle'):
                painter.setBrush(QColor(fill_color))
                painter.drawEllipse(x - w / 2, y - h / 2, w, h)
            else: # not supported, then force to box
                painter.fillRect(QRectF(x - w / 2, y - h / 2, w, h), QColor(fill_color))

        # image
        if len(image_path) != 0:
            extension = image_path.split(".")[1]
            if extension in ('png', 'bmp', 'jpeg', 'jpg'):
                pixmap = QPixmap(image_path)
                painter.drawPixmap(QRectF(x-w/2, y-h/2, w, h), pixmap, QRectF(0, 0, pixmap.width(), pixmap.height()))
            elif extension == 'svg':
                svg = QSvgRenderer(image_path)
                svg.render(painter, QRectF(x-w/2, y-h/2, w, h))

        # draw outline
        painter.pen().setWidth(line_width)
        painter.setBrush(Qt.NoBrush)
        if shape in ('box', 'doublebox'):
            painter.drawRect(x-w/2, y-h/2, w, h)
            if shape == 'doublebox':
                painter.drawRect(x-w/2-5, y-h/2-5, w-10, h-10)
        elif shape in ('circle', 'doublecircle'):
            painter.drawEllipse(x-w/2, y-h/2, w, h)
            if shape == 'doublecircle':
                painter.drawEllipse(x-w/2-5, y-h/2-5, w-10, h-10)
        else: # not supported, then force to box
            self.handler.reporter("Unsupported shape '{}'. Forced to box.".format(shape))
            painter.drawRect(x - w / 2, y - h / 2, w, h)

        # label
        if show_label:
            self.label.show()
        else:
            self.label.hide()
        rect = self.label.sceneBoundingRect()
        if text_align == 'top-left':
            self.label.setPos(x - w/2, y - h/2 - rect.height())
        elif text_align == 'center-left':
            self.label.setPos(x - w/2, y - rect.height()/2)
        elif text_align == 'bottom-left':
            self.label.setPos(x - w/2, y + h/2)
        elif text_align == 'top-center':
            self.label.setPos(x - rect.width()/2, y - h/2 - rect.height())
        elif text_align == 'center-center':
            self.label.setPos(x - rect.width()/2, y - rect.height()/2)
        elif text_align == 'bottom-center':
            self.label.setPos(x - rect.width() / 2, y + h/2)
        elif text_align == 'top-right':
            self.label.setPos(x + w/2 - rect.width(), y - h/2 - rect.height())
        elif text_align == 'center-right':
            self.label.setPos(x + w/2 - rect.width(), y - rect.height()/2)
        elif text_align == 'bottom-right':
            self.label.setPos(x + w/2 - rect.width(), y + h/2)
        else:
            self.label.setPos(x - rect.width() / 2, y - rect.height() / 2)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        dx, dy = event.scenePos().x() - event.lastScenePos().x(), event.scenePos().y() - event.lastScenePos().y()
        if dx != 0 or dy != 0:
            # self.handler.context.nodes[self.node]['x'] += dx
            # self.handler.context.nodes[self.node]['y'] += dy
            # self.handler.context.dirty = True
            self.handler.move_node_by(self.node, dx, dy)


# GraphCore's circle shaped node graphics item class
class GraphCoreCircleNodeItem(QGraphicsEllipseItem, GraphCoreNodeItemInterface):
    def __init__(self, node, context: GraphCoreContext, handler: GraphCoreContextHandler):
        super().__init__(node, context, handler)
        # self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPen(QPen())
        self.draw()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...) -> None:
        # super().paint(painter, option, widget)
        attrs = self.context.nodes[self.node]

        painter.pen().setWidth(attrs['line-width'])
        if self.handler.context.nodes[self.node]['filled']:
            color = self.handler.context.nodes[self.node]['fill-color']
            painter.setBrush(QColor(color))
            painter.drawEllipse(self.rect())
        painter.brush().setStyle(Qt.NoBrush)
        painter.drawEllipse(self.rect())
        # draw double line
        if self.handler.context.nodes[self.node]['shape'] == "doublecircle":
            margin = 4
            rect = self.rect()
            x = rect.x() + margin
            y = rect.y() + margin
            w = rect.width() - margin * 2
            h = rect.height() - margin * 2
            painter.drawEllipse(QRectF(x, y, w, h))

        # draw image
        image_path = attrs['image-path']
        if len(image_path) != 0:
            x = attrs['x']
            y = attrs['y']
            w = attrs['w']
            h = attrs['h']
            extension = image_path.split(".")[1]
            if extension in ('png', 'bmp', 'jpeg', 'jpg'):
                pixmap = QPixmap(image_path)
                painter.drawPixmap(QRectF(x-w/2, y-h/2, w, h), pixmap, QRectF(0, 0, pixmap.width(), pixmap.height()))
            elif extension == 'svg':
                svg = QSvgRenderer(image_path)
                svg.render(painter, QRectF(x-w/2, y-h/2, w, h))


    def draw(self):
        self.redraw()

    def redraw(self):
        n = self.context.nodes[self.node]
        if n['shape'] not in ('circle', 'doublecircle'):
            item = gcore_create_node_item(self.node, self.context, self.handler)
            self.handler.extras['scene'].removeItem(self)
            self.handler.extras['scene'].addItem(item)
            self.handler.extras['element_to_item'][self.node] = item
            return
        label: QGraphicsTextItem = self.label
        label.setPlainText(n['label'])
        self.update(self.rect())
        # if n['filled']:
        #     brush = QBrush(QColor(n['fill-color']))
        #     self.setBrush(brush)
        # else:
        #     self.setBrush(QBrush())
        #     self.brush().setStyle(Qt.NoBrush)
        x = n['x']
        y = n['y']
        w = n['w']
        h = n['h']
        # print("redraw rect ({}, {}, {}, {}) of {}".format(x, y, w, h, self))
        # print("  sceneRect ({}, {}, {}, {}) of {}".format(sceneRect.x() + sceneRect.width()/2, sceneRect.y() + sceneRect.height()/2, sceneRect.width(), sceneRect.height(), self))
        self.setRect(x - w/2, y - h/2, w, h)
        rect = label.sceneBoundingRect()
        text_align = n['text-align']
        if text_align == 'top-left':
            label.setPos(x - w/2, y - h/2 - rect.height())
        elif text_align == 'center-left':
            label.setPos(x - w/2, y - rect.height()/2)
        elif text_align == 'bottom-left':
            label.setPos(x - w/2, y + h/2)
        elif text_align == 'top-center':
            label.setPos(x - rect.width()/2, y - h/2 - rect.height())
        elif text_align == 'center-center':
            label.setPos(x - rect.width()/2, y - rect.height()/2)
        elif text_align == 'bottom-center':
            label.setPos(x - rect.width() / 2, y + h/2)
        elif text_align == 'top-right':
            label.setPos(x + w/2 - rect.width(), y - h/2 - rect.height())
        elif text_align == 'center-right':
            label.setPos(x + w/2 - rect.width(), y - rect.height()/2)
        elif text_align == 'bottom-right':
            label.setPos(x + w/2 - rect.width(), y + h/2)
        else:
            label.setPos(x - rect.width() / 2, y - rect.height() / 2)
        self.paint_bound_points()
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
         # ("mouse pressed at {} of scene".format(event.pos()))
         # if event.button() == 1:  # Left button
         #    self.handler.deselect_all()
         #    self.handler.select_node(self.node)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        #print("mouseMoveEvent", type(self), event)
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
        # self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setPen(QPen())
        self.draw()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...) -> None:
        # super().paint(painter, option, widget)
        attrs = self.context.nodes[self.node]

        painter.pen().setWidth(attrs['line-width'])
        if self.handler.context.nodes[self.node]['filled']:
            color = self.handler.context.nodes[self.node]['fill-color']
            painter.fillRect(self.rect(), QColor(color))
        painter.drawRect(self.rect())
        if self.handler.context.nodes[self.node]['shape'] == "doublebox":
            margin = 4
            rect = self.rect()
            x = rect.x() + margin
            y = rect.y() + margin
            w = rect.width() - margin * 2
            h = rect.height() - margin * 2
            painter.drawRect(QRectF(x, y, w, h))

        # draw image
        image_path = attrs['image-path']
        if len(image_path) != 0:
            x = attrs['x']
            y = attrs['y']
            w = attrs['w']
            h = attrs['h']
            extension = image_path.split(".")[1]
            if extension in ('png', 'bmp', 'jpeg', 'jpg'):
                pixmap = QPixmap(image_path)
                painter.drawPixmap(QRectF(x-w/2, y-h/2, w, h), pixmap, QRectF(0, 0, pixmap.width(), pixmap.height()))
            elif extension == 'svg':
                svg = QSvgRenderer(image_path)
                svg.render(painter, QRectF(x-w/2, y-h/2, w, h))

    def draw(self):
        self.redraw()

    def redraw(self):
        n = self.context.nodes[self.node]
        if n['shape'] not in ('box', 'doublebox'):
            item = gcore_create_node_item(self.node, self.context, self.handler)
            self.handler.extras['scene'].removeItem(self)
            self.handler.extras['scene'].addItem(item)
            self.handler.extras['element_to_item'][self.node] = item
            return
        label: QGraphicsTextItem = self.label
        label.setPlainText(n['label'])
        self.update(self.rect())
        # if n['filled']:
        #     brush = QBrush(QColor(n['fill-color']))
        #     self.setBrush(brush)
        # else:
        #     self.setBrush(QBrush())
        #     self.brush().setStyle(Qt.NoBrush)
        x = n['x']
        y = n['y']
        w = n['w']
        h = n['h']
        self.setRect(x - w/2, y - h/2, w, h)
        self.setRect(x - w/2, y - h/2, w, h)
        rect = label.sceneBoundingRect()
        text_align = n['text-align']
        if text_align == 'top-left':
            label.setPos(x - w/2, y - h/2 - rect.height())
        elif text_align == 'center-left':
            label.setPos(x - w/2, y - rect.height()/2)
        elif text_align == 'bottom-left':
            label.setPos(x - w/2, y + h/2)
        elif text_align == 'top-center':
            label.setPos(x - rect.width()/2, y - h/2 - rect.height())
        elif text_align == 'center-center':
            label.setPos(x - rect.width()/2, y - rect.height()/2)
        elif text_align == 'bottom-center':
            label.setPos(x - rect.width() / 2, y + h/2)
        elif text_align == 'top-right':
            label.setPos(x + w/2 - rect.width(), y - h/2 - rect.height())
        elif text_align == 'center-right':
            label.setPos(x + w/2 - rect.width(), y - rect.height()/2)
        elif text_align == 'bottom-right':
            label.setPos(x + w/2 - rect.width(), y + h/2)
        else:
            label.setPos(x - rect.width() / 2, y - rect.height() / 2)
        self.paint_bound_points()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # print("mouse pressed at {} of scene".format(event.pos()))
        # if event.button() == 1:  # Left button
        #     self.handler.deselect_all()
        #     self.handler.select_node(self.node)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        #print("mouseMoveEvent", type(self), event)
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
        self.label = QGraphicsTextItem(context.edges[u, v]['label'])
        self.label.setParentItem(self)
        self._start_bound = QGraphicsRectItem(self)
        self._target_bound = QGraphicsRectItem(self)

    @property
    def u(self):
        return self._u

    @property
    def v(self):
        return self._v

    def show_bound_rects(self, flag=True):
        self._start_bound.setVisible(flag)
        self._target_bound.setVisible(flag)

    def paint_bound_rects(self):
        w,h = 4, 4
        u = self.context.nodes[self.u]
        if u['w'] < u['h']:
            r_u = u['h']/2
        else:
            r_u = u['w']/2
        v = self.context.nodes[self.v]
        if v['w'] < v['h']:
            r_v = v['h']/2
        else:
            r_v = v['w']/2
        x_u, y_u = u['x'], u['y']
        x_v, y_v = v['x'], v['y']
        vec = (x_v - x_u, y_v - y_u)
        len_vec = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
        vec = (vec[0] / len_vec, vec[1] / len_vec)
        x_s, y_s = vec[0] * r_u + x_u, vec[1] * r_u + y_u
        x_d, y_d = x_v - vec[0] * r_v, y_v - vec[1] * r_v
        x, y = x_s - w/2, y_s - h/2
        self._start_bound.setRect(x, y, w, h)
        x, y = x_d - w/2, y_d - h/2
        self._target_bound.setRect(x, y, w, h)

    def select(self):
        self.show_bound_rects(True)
        super().select()

    def deselect(self):
        self.show_bound_rects(False)
        super().deselect()


# GraphCore's edge item
class GraphCoreEdgeItem(QGraphicsPathItem, GraphCoreEdgeItemInterface):
    def __init__(self, u, v, context: GraphCoreContext, handler: GraphCoreContextHandler):
        super().__init__(u, v, context=context, handler=handler)
        # super().__init__()
        # self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setPen(QPen(QColor("black")))
        self._coords = None
        self.draw()

    @property
    def u(self):
        return self._u

    @property
    def v(self):
        return self._v

    def calc_path(self):
        path = QPainterPath()
        path_item = QGraphicsPathItem(path)

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
        if u['w'] < u['h']:
            r_u = u['h']/2
        else:
            r_u = u['w']/2
        v = self.context.nodes[self.v]
        if v['w'] < v['h']:
            r_v = v['h']/2
        else:
            r_v = v['w']/2
        e = self.context.edges[self.u, self.v]
        # polygon = self.calc_polygon(u['x'], u['y'], r_u, v['x'], v['y'],
        #                             r_v, e['arrow-length'], e['arrow-angle'])
        angle = 2*np.arcsin(e['arrow-width']/(2*e['arrow-length']))
        polygon = self.calc_polygon(u['x'], u['y'], r_u, v['x'], v['y'],
                                    r_v, e['arrow-length'], angle)
        return polygon

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        super().paint(painter, option, widget)

    def draw(self):
        self.redraw()

    def redraw(self):
        e = self.context.edges[self.u, self.v]
        # FIXME filled property is unavailable now
        # if e['filled']:
        #     brush = QBrush(QColor(e['fill-color']))
        #     self.setBrush(brush)
        # else:
        #     self.setBrush(QBrush(Qt.NoBrush))
        self.setBrush(QBrush(Qt.NoBrush))
        u = self.context.nodes[self.u]
        v = self.context.nodes[self.v]
        x_u, y_u, w_u, h_u = u['x'], u['y'], u['w'], u['h']
        x_v, y_v, w_v, h_v = v['x'], v['y'], v['w'], v['h']
        a = np.deg2rad(e['curve-angle'])
        hl = e['arrow-length']
        hw = e['arrow-width']
        shape_u, shape_v = u['shape'], v['shape']
        path = QPainterPath()
        if a == 0:
            if shape_u in ('box', 'doublebox') and shape_v in ('box', 'doublebox'):
                coords = straight_edge_rect_to_rect(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, hl, hw)
            elif shape_u in ('box', 'doublebox') and shape_v in ('circle', 'doublecircle'):
                coords = straight_edge_rect_to_ellipse(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, hl, hw)
            elif shape_u in ('circle', 'doublecircle') and shape_v in ('box', 'doublebox'):
                coords = straight_edge_ellipse_to_rect(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, hl, hw)
            elif shape_u in ('circle', 'doublecircle') and shape_v in ('circle', 'doublecircle'):
                coords = straight_edge_ellipse_to_ellipse(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, hl, hw)
            else:
                coords = straight_edge_ellipse_to_ellipse(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, hl, hw)
            path.moveTo(coords[0][0], coords[0][1])
            path.lineTo(coords[1][0], coords[1][1])
            path.moveTo(coords[2][0][0], coords[2][0][1])
            for c in coords[2][1:]:
                path.lineTo(c[0], c[1])
            path.lineTo(coords[2][0][0], coords[2][0][1])
        else:
            if shape_u in ('box', 'doublebox') and shape_v in ('box', 'doublebox'):
                coords = curved_edge_rect_to_rect(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, a, hl, hw)
            elif shape_u in ('box', 'doublebox') and shape_v in ('circle', 'doublecircle'):
                coords = curved_edge_rect_to_ellipse(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, a, hl, hw)
            elif shape_u in ('circle', 'doublecircle') and shape_v in ('box', 'doublebox'):
                coords = curved_edge_ellipse_to_rect(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, a, hl, hw)
            elif shape_u in ('circle', 'doublecircle') and shape_v in ('circle', 'doublecircle'):
                coords = curved_edge_ellipse_to_ellipse(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, a, hl, hw)
            else:
                coords = curved_edge_ellipse_to_ellipse(x_u, y_u, w_u, h_u, x_v, y_v, w_v, h_v, a, hl, hw)
            path.moveTo(coords[0][0], coords[0][1])
            path.cubicTo(coords[0][0], coords[0][1], coords[1][0], coords[1][1], coords[2][0], coords[2][1])
            path.moveTo(coords[3][0][0], coords[3][0][1])
            for c in coords[3][1:]:
                path.lineTo(c[0], c[1])
            path.lineTo(coords[3][0][0], coords[3][0][1])
        self._coords = coords
        self.setPath(path)
        self._label.setPlainText(e['label'])
        if a == 0:
            x, y = (x_u + x_v)/2, (y_u + y_v)/2
        else:
            A = coords[0]
            B = coords[1]
            C = coords[2]
            D = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2]
            E = [(B[0] + C[0]) / 2, (B[1] + C[1]) / 2]
            F = [(D[0] + E[0]) / 2, (D[1] + E[1]) / 2]
            x, y = F[0], F[1]
        boundingRect = self._label.boundingRect()
        self._label.setPos(x - boundingRect.width()/2, y) # y - boundingRect.height()/2)
        self.paint_bound_rects()
        self.update(self.boundingRect())
        # e = self.context.edges[self.u, self.v]
        # if e['filled']:
        #     brush = QBrush(QColor(e['fill-color']))
        #     self.setBrush(brush)
        # else:
        #     self.setBrush(QColor())
        # self.setPolygon(self.create_polygon())
        # u = self.context.nodes[self.u]
        # v = self.context.nodes[self.v]
        # self._label.setPlainText(e['label'])
        # x, y = (u['x']+v['x'])/2, (u['y']+v['y'])/2
        # boundingRect = self._label.boundingRect()
        # self._label.setPos(x - boundingRect.width()/2, y) # y - boundingRect.height()/2)
        # self.paint_bound_rects()


    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # print("mouse of {} pressed at {}".format(self, event.pos()))
        # if event.button() == 1:  # Left button
        #     self.handler.deselect_all()
        #     self.handler.select_edge(self.u, self.v)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # if event.button() == 1:  # Left button
        #     self.handler.deselect_all()
        #     self.handler.select_edge(self.u, self.v)
        super().mouseDoubleClickEvent(event)

# grid pane
class GCGridItem(QGraphicsItem):

    def __init__(self, parent=None, tick=20, x=0, y=0, width=800, height=600):
        super().__init__(parent=parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self._tick = tick

    def boundingRect(self) -> QtCore.QRectF:
        scene = self.scene()
        # return scene.sceneRect()
        view = scene.views()[0]
        left_top = view.mapToScene(0, 0)
        right_bottom = view.mapToScene(view.width(), view.height())
        return QRectF(left_top.x(), left_top.y(), right_bottom.x() - left_top.x(), right_bottom.y() - left_top.y())

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        pass
        # painter.setPen(QPen(QColor("#888")))
        # painter.pen().setStyle(Qt.PenStyle.DashDotDotLine)
        # rect = self.boundingRect()
        # # vertical grids
        # num = int(rect.width() / self._tick)
        # if divmod(rect.width(), self._tick) != 0:
        #     num += 1
        # for i in range(num):
        #     x = rect.x() + self._tick / 2 + self._tick * i
        #     painter.drawLine(QLineF(x, rect.y(), x, rect.y() + rect.height()))
        # # horizontal grids
        # num = int(rect.height() / self._tick)
        # if divmod(rect.height(), self._tick) != 0:
        #     num += 1
        # for i in range(num):
        #     y = rect.y() + self._tick / 2 + self._tick * i
        #     painter.drawLine(QLineF(rect.x(), y, rect.x() + rect.width(), y))

    def sceneEvent(self, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.Type.GraphicsSceneResize:
            #print("sceneEvent resize", self.scene().sceneRect())
            #self.setRect(self.scene().sceneRect())
            pass
        return  super().sceneEvent(event)


# horizontal/vertical axis
class GCAxisItem(QGraphicsItem):

    def __init__(self, parent=None, orientation='bottom', tick=20, size=30,
                 left_margin=20, top_margin=20, bottom_margin=40, right_margin=40):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self._orientation = orientation
        self._size = size
        self._tick = tick
        self._left_margin = left_margin
        self._top_margin = top_margin
        self._bottom_margin = bottom_margin
        self._right_margin = right_margin

    @property
    def orientation(self):
        return self._orientation

    def boundingRect(self) -> QtCore.QRectF:
        scene = self.scene()
        view = scene.views()[0]
        if self.orientation == 'bottom':
            view_rect = QRectF(0, view.height()-self._size, view.width(), self._size)
        elif self.orientation == 'top':
            view_rect = QRectF(0, 0, view.width(), self._size)
        elif self.orientation == 'left':
            view_rect = QRectF(0, 0, self._size, view.height())
        elif self.orientation == 'right':
            view_rect = QRectF(view.width()-self._size, 0, self._size, view.height())
        else:
            raise Exception("bug!")
        left_top = view.mapToScene(view_rect.x(), view_rect.y())
        right_bottom = view.mapToScene(view_rect.x()+view_rect.width(), view_rect.y()+view_rect.height())
        return QRectF(left_top.x(), left_top.y(), right_bottom.x()-left_top.x(), right_bottom.y()-left_top.y())

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        painter.setPen(QColor("#888"))
        rect = self.boundingRect()
        if self.orientation in ('bottom', 'top'):
            painter.drawLine(QPointF(rect.x() + self._left_margin, rect.y() + self._size / 2),
                             QPointF(rect.x() + rect.width() - self._right_margin, rect.y() + self._size / 2))
            line_width = rect.width() - self._left_margin - self._right_margin
            tick_count = int(line_width / self._tick)
            for i in range(tick_count):
                x = self._tick * i + rect.x() + self._left_margin
                painter.drawLine(QLineF(x, rect.y(), x, rect.y() + rect.height()))
        elif self.orientation in ('left', 'right'):
            painter.drawLine(QPointF(rect.x() + self._size / 2, rect.y() + self._top_margin),
                             QPointF(rect.x() + self._size / 2, rect.y() + rect.height() - self._bottom_margin))
            line_height = rect.height() - self._top_margin - self._bottom_margin
            tick_count = int(line_height / self._tick)
            for i in range(tick_count):
                y = self._tick * i + rect.y() + self._top_margin
                painter.drawLine(QLineF(rect.x(), y, rect.x() + rect.width(), y))

def gcore_create_node_item(n, context: GraphCoreContext, handler: GraphCoreContextHandler):
    attr = context.nodes[n]
    if attr['shape'] in ('circle', 'doublecircle'):
        item = GraphCoreCircleNodeItem(n, context, handler)
    elif attr['shape'] in ('box', 'doublebox'):
        item = GraphCoreRectNodeItem(n, context, handler)
    else:
        handler.reporter.report("GraphCore Error!!! Unsupported shape:{}".format(attr['shape']))
        return None
    return item
