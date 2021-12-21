# -*- coding: utf-8 -*-

import networkx as nx
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QTableWidget
from gui.Ui_Visualizer import Ui_visualizerDialog


class GCVisualizerDialog(QDialog):

    def __init__(self, parent, ui: Ui_visualizerDialog):
        super().__init__(parent)
        self._ui = ui
        self.ui.setupUi(self)


    @property
    def ui(self) -> Ui_visualizerDialog:
        return self._ui


    def setup(self, G: nx.DiGraph, default_node_attrs, default_edge_attrs):
        self.ui.nodeTable.clear()
        # fill nodeTable header
        self.ui.nodeTable.setColumnCount(len(default_node_attrs))
        for i, k in enumerate(default_node_attrs['control-volume'].keys()):
            self.ui.nodeTable.setHorizontalHeaderItem(i, QTableWidgetItem(k))
        self.ui.nodeTable.setRowCount(12)

        self.ui.edgeTable.clear()
        # fill edgeTable header
        for i, k in enumerate(default_edge_attrs['dataflow'].keys()):
            self.ui.edgeTable.setHorizontalHeaderItem(i, QTableWidgetItem(k))
        self.ui.edgeTable.setRowCount(12)
        for n in G.nodes:
            pass
