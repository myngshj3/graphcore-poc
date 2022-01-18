# -*- coding: utf-8 -*-

import networkx as nx
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QTableWidget, QWidget, QGraphicsWidget, QGraphicsGridLayout
from PyQt5.QtWidgets import QStyle
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QItemSelection
from PyQt5.QtWidgets import QGraphicsItem
import pyqtgraph as pg
from pyqtgraph import PlotItem, PlotWidget, AxisItem
import numpy as np
from gui.Ui_Visualizer import Ui_visualizerDialog
import typing


class CustomAxesItem(QGraphicsItem):

    def __init__(self, parent=None, size=40, show_bottom=True, show_left=True):
        super().__init__(parent)
        self._size = size
        self._bottom = show_bottom
        self._left = show_left

    def boundingRect(self):
        view_rect = self.scene().views()[0].rect()
        tl = self.scene().views()[0].mapToScene(view_rect.x(), view_rect.y())
        br = self.scene().views()[0].mapToScene(view_rect.x() + view_rect.width(), view_rect.y() + view_rect.height())
        return QtCore.QRectF(tl.x(), tl.y(), br.x() - tl.x(), br.y() - tl.y())

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: typing.Optional[QWidget] = ...) -> None:
        painter.setBrush(QtGui.QColor("gray"))
        painter.setPen(QtGui.QColor("white"))
        painter.pen().setWidth(1)
        view_rect = self.scene().views()[0].rect()
        # bottom
        rect = QtCore.QRect(0, view_rect.height() - self._size, view_rect.width(), self._size)
        #painter.fillRect(rect, QtGui.QColor("black"))
        tl = self.scene().views()[0].mapToScene(rect.x(), rect.y())
        br = self.scene().views()[0].mapToScene(rect.x() + rect.width(), rect.y() + rect.height())
        print("bottom pane", tl.x(), tl.y(), br.x()-tl.x(), br.y()-tl.y())
        painter.drawLine(tl.x(), (tl.y() + br.y())/2, br.x(), (tl.y() +br.y())/2)
        # left
        rect = QtCore.QRect(0, 0, self._size, view_rect.height())
        #painter.fillRect(rect, QtGui.QColor("black"))
        tl = self.scene().views()[0].mapToScene(rect.x(), rect.y())
        br = self.scene().views()[0].mapToScene(rect.x() + rect.width(), rect.y() + rect.height())
        print("bottom pane", tl.x(), tl.y(), br.x()-tl.x(), br.y()-tl.y())
        painter.drawLine((tl.x() + br.x())/2, tl.y(),
                         (tl.x() + br.x())/2, br.y())

class GCVisualizerDialog(QDialog):

    def __init__(self, parent, ui: Ui_visualizerDialog):
        super().__init__(parent)
        self._ui = ui
        self.ui.setupUi(self)
        self._Gs = None
        self.ui.nodes.selectionModel().selectionChanged.connect(self.selected_node_changed)
        self.ui.nodeProperties.itemDoubleClicked.connect(self.selected_node_property_double_clicked)
        self.ui.selectedNodeProperties.customContextMenuRequested.connect(self.nodesContextMenuEvent)
        self.ui.edges.selectionModel().selectionChanged.connect(self.selected_edge_changed)
        self.ui.edgeProperties.itemDoubleClicked.connect(self.selected_edge_property_double_clicked)
        self.ui.selectedEdgeProperties.customContextMenuRequested.connect(self.edgesContextMenuEvent)
        self.ui.animateButton.clicked.connect(self.plot)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.nodePlot.plotItem.getAxis('bottom').setLabel(text="time")
        self.ui.edgePlot.plotItem.getAxis('bottom').setLabel(text="time")
        # self._axes = CustomAxesItem()
        # scene = self.ui.nodePlot.scene()
        # scene.addItem(self._axes)
        self.setWindowState(Qt.WindowMaximized)


    def selected_node_changed(self, selected: QItemSelection, deselected: QItemSelection):
        G: nx.DiGraph = self._Gs[0]
        row = selected.indexes()[0].row()
        id = self.ui.nodes.item(row, 0).text()
        self.ui.nodeProperties.clear()
        for k in G.nodes[id].keys():
            text = "{}.{}".format(id, k)
            self.ui.nodeProperties.addItem(text)

    def selected_node_property_double_clicked(self):
        prop_row = self.ui.nodeProperties.selectedIndexes()[0].row()
        node_prop = self.ui.nodeProperties.item(prop_row).text()
        self.ui.selectedNodeProperties.addItem(node_prop)

    def selected_edge_changed(self, selected: QItemSelection, deselected: QItemSelection):
        G: nx.DiGraph = self._Gs[0]
        indices = selected.indexes()
        if len(indices) == 0:
            return
        row = selected.indexes()[0].row()
        id = self.ui.edges.item(row, 0).text()
        id = id[1:len(id) - 1]
        uv = id.split(",")
        self.ui.edgeProperties.clear()
        for k in G.edges[uv[0], uv[1]].keys():
            text = "({}).{}".format(id, k)
            self.ui.edgeProperties.addItem(text)

    def selected_edge_property_double_clicked(self):
        prop_row = self.ui.edgeProperties.selectedIndexes()[0].row()
        edge_prop = self.ui.edgeProperties.item(prop_row).text()
        self.ui.selectedEdgeProperties.addItem(edge_prop)


    @property
    def ui(self) -> Ui_visualizerDialog:
        return self._ui

    @property
    def nodePlot(self) -> pg.PlotWidget:
        return self.ui.nodePlot

    @property
    def nodePlotXAxis(self) -> pg.AxisItem:
        return self.ui.nodePlot.getAxis('bottom')

    @property
    def nodePlotYAxis(self) -> pg.AxisItem:
        return self.ui.nodePlot.getAxis('left')

    @property
    def edgePlot(self) -> pg.PlotWidget:
        return self.ui.edgePlot

    @property
    def edgePlotXAxis(self) -> pg.AxisItem:
        return self.ui.edgePlot.getAxis('bottom')

    @property
    def edgePlotYAxis(self) -> pg.AxisItem:
        return self.ui.edgePlot.getAxis('left')

    def setup(self, Gs):
        self._Gs = [nx.node_link_graph(_) for _ in Gs]
        G: nx.DiGraph = self._Gs[0]
        # reset nodes
        self.ui.nodes.clear()
        self.ui.nodes.resizeRowsToContents()
        self.ui.nodes.setColumnCount(4)
        self.ui.nodes.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
        self.ui.nodes.setHorizontalHeaderItem(1, QTableWidgetItem('label'))
        self.ui.nodes.setHorizontalHeaderItem(2, QTableWidgetItem('caption'))
        self.ui.nodes.setHorizontalHeaderItem(3, QTableWidgetItem('description'))
        self.ui.nodes.setRowCount(len(G.nodes))
        for i, v in enumerate(G.nodes):
            n = G.nodes[v]
            item = QTableWidgetItem(v)
            # item.setFlags(Qt.ItemIsEditable)
            self.ui.nodes.setItem(i, 0, item)
            item = QTableWidgetItem(n['label'])
            # item.setFlags(Qt.ItemIsEditable)
            self.ui.nodes.setItem(i, 1, item)
            item = QTableWidgetItem(n['caption'])
            # item.setFlags(Qt.ItemIsEditable)
            self.ui.nodes.setItem(i, 2, item)
            item = QTableWidgetItem(n['description'])
            # item.setFlags(Qt.ItemIsEditable)
            self.ui.nodes.setItem(i, 3, item)
        self.ui.nodes.resizeColumnsToContents()
        self.ui.nodeProperties.clear()
        self.ui.selectedNodeProperties.clear()
        self.ui.selectedNodeProperties.clear()

        self.ui.edges.clear()
        self.ui.edges.resizeRowsToContents()
        self.ui.edges.setColumnCount(4)
        self.ui.edges.setHorizontalHeaderItem(0, QTableWidgetItem('id'))
        self.ui.edges.setHorizontalHeaderItem(1, QTableWidgetItem('label'))
        self.ui.edges.setHorizontalHeaderItem(2, QTableWidgetItem('caption'))
        self.ui.edges.setHorizontalHeaderItem(3, QTableWidgetItem('description'))
        self.ui.edges.setRowCount(len(G.nodes))
        for i, e in enumerate(G.edges):
            n = G.edges[e[0], e[1]]
            item = QTableWidgetItem("({},{})".format(e[0], e[1]))
            # item.setFlags(Qt.ItemIsEditable)
            self.ui.edges.setItem(i, 0, item)
            item = QTableWidgetItem(n['label'])
            # item.setFlags(Qt.ItemIsEditable)
            self.ui.edges.setItem(i, 1, item)
            item = QTableWidgetItem(n['caption'])
            # item.setFlags(Qt.ItemIsEditable)
            self.ui.edges.setItem(i, 2, item)
            item = QTableWidgetItem(n['description'])
            # item.setFlags(Qt.ItemIsEditable)
            self.ui.edges.setItem(i, 3, item)
        self.ui.edges.resizeColumnsToContents()
        self.ui.edgeProperties.clear()
        self.ui.selectedEdgeProperties.clear()

        self.nodePlot.setTitle("Node attribute's time series charts.")
        self.edgePlot.setTitle("Edge attribute's time series charts.")

    def plot(self):
        self.plotNodes()
        self.plotEdges()
        # self.ui.nodePlot.plotItem.getAxis('bottom').setWidth(1263)
        # bottom: pg.AxisItem = self.ui.edgePlot.plotItem.getAxis('bottom')
        # print("bottomAxis boundingRect", bottom.boundingRect())
        # print("bottomAxis viewRect    ", bottom.viewRect())
        # print("bottomAxis viewPos     ", bottom.viewPos())
        # print("bottomAxis viewWidget  ", bottom.getViewWidget())
        # vb: pg.ViewBox = bottom.getViewBox()
        #
        # print("bottom     viewBox pos ", vb.pos())
        # print("bottom     viewBox size", vb.width(), vb.height())
        # print("leftAxis  ", self.ui.edgePlot.plotItem.getAxis('left').boundingRect())

    def plotNodes(self):
        x = [self.ui.dt.value()*i for i in range(self.ui.stepOffset.value(), self.ui.steps.value()+1)]
        plotItem: PlotItem = self.ui.nodePlot.plotItem
        plotItem.clear()
        plotItem.addLegend(offset=(-30, -5))
        ymin = 0
        ymax = 0
        for i in range(self.ui.selectedNodeProperties.count()):
            prop_id = self.ui.selectedNodeProperties.item(i).text()
            text = prop_id.split(".")
            id = text[0]
            prop = text[1]
            y = [self._Gs[i].nodes[id][prop] for i in range(len(x))]
            plotItem.plot(x, y, pen=self.decidePen(i), name=prop_id)
            m1 = min(y)
            m2 = max(y)
            ymin = min(ymin, m1)
            ymax = max(ymax, m2)
        plotItem.getViewBox().setXRange(x[0], x[len(x)-1])
        plotItem.getAxis('bottom').setRange(x[0], x[len(x)-1])
        plotItem.getAxis('left').setRange(ymin, ymax)

    def plotEdges(self):
        x = [self.ui.dt.value()*i for i in range(self.ui.stepOffset.value(), self.ui.steps.value()+1)]
        plotItem: PlotItem = self.edgePlot.plotItem
        plotItem.clear()
        legend = plotItem.addLegend(offset=(-30, -5))
        ymin = 0
        ymax = 0
        for i in range(self.ui.selectedEdgeProperties.count()):
            prop_id = self.ui.selectedEdgeProperties.item(i).text()
            text = prop_id.split(".")
            id = text[0]
            uv = id[1:len(id)-1].split(",")
            prop = text[1]
            y = [self._Gs[i].edges[uv[0], uv[1]][prop] for i in range(len(x))]
            plotItem.plot(x, y, pen=self.decidePen(i), name=prop_id)
            m1 = min(y)
            m2 = max(y)
            ymin = min(ymin, m1)
            ymax = max(ymax, m2)
        plotItem.getViewBox().setXRange(x[0], x[len(x)-1])
        plotItem.getAxis('bottom').setRange(x[0], x[len(x)-1])
        plotItem.getAxis('left').setRange(ymin, ymax)


    def decidePen(self, i: int):
        color = ((255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255), (0,255,255), (255,255,255))
        (r, ix) = divmod(i, len(color))
        c = [_ for _ in color[ix]]
        if r != 0:
            c[0] /= r
            c[1] /= r
            c[2] /= r
        return c

    def nodesContextMenuEvent(self, a0: QPoint) -> None:
        contextMenu = QMenu(self)
        removeAction = contextMenu.addAction("Remove")
        a0 = self.ui.selectedNodeProperties.mapToGlobal(a0)
        action = contextMenu.exec_(a0)
        if action == removeAction:
            self.ui.selectedNodeProperties.takeItem(self.ui.selectedNodeProperties.currentRow())

    def edgesContextMenuEvent(self, a0: QPoint) -> None:
        contextMenu = QMenu(self)
        removeAction = contextMenu.addAction("Remove")
        a0 = self.ui.selectedEdgeProperties.mapToGlobal(a0)
        action = contextMenu.exec_(a0)
        if action == removeAction:
            self.ui.selectedEdgeProperties.takeItem(self.ui.selectedEdgeProperties.currentRow())
