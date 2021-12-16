# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np
from graphcore.shell import GraphCoreContextHandler
from graphcore.gcsolver import GCSolver
from gui.Ui_SolverController import Ui_SolverControllerForm
from PyQt5.QtWidgets import QDialog, QMenu
from PyQt5.QtCore import QPoint


class SolverControllerDialog(QDialog):
    def __init__(self, parent, ui: Ui_SolverControllerForm):
        super().__init__(parent)
        self._ui = ui
        ui.setupUi(self)
        self._G = None
        self._post_data = None
        self._cancel = False

    @property
    def post_data(self):
        return self._post_data

    @property
    def G(self) -> nx.DiGraph:
        return self._G

    @G.setter
    def G(self, value: nx.DiGraph):
        self._G = value

    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @property
    def ui(self) -> Ui_SolverControllerForm:
        return self._ui

    def start_clicked(self):
        try:
            self._cancel = False
            value_property = self.ui.valuePropertyNameComboBox.currentText()
            max_value_property = self.ui.maxValuePropertyComboBox.currentText()
            velocity_property = self.ui.velocityPropertyComboBox.currentText()
            max_velocity_property = self.ui.maxVelocityPropertyComboBox.currentText()
            current_max_velocity_property = self.ui.currentMaxVelocityPropertyComboBox.currentText()
            self.ui.startButton.setEnabled(False)
            self.ui.stopButton.setEnabled(True)
            self.ui.closeButton.setEnabled(False)
            dt = self.ui.doubleSpinBox.value()
            steps = self.ui.spinBox.value()
            solver: GCSolver = GCSolver(self.G, dt)
            G = solver.clone_graph(self.G)
            G_array = [G]
            for i in range(steps):
                if self._cancel:
                    break
                percentage = 100.0 * i / steps
                self.ui.progressBar.setValue(percentage)
                if 0 == i:
                    print(f'[{i}]')
                    for n in G.nodes:
                        print(f'  n={n}, value={G.nodes[n][value_property]}, maxValue={G.nodes[n][max_value_property]}')
                    for e in G.edges:
                        print(f'  e={e}, velocity={G.edges[e[0], e[1]][velocity_property]}, currentMaxVelocity={G.edges[e[0], e[1]][current_max_velocity_property]}, maxVelocity={G.edges[e[0], e[1]][max_velocity_property]}')
                G = solver.calc_one_step(value_property, max_value_property, velocity_property, max_velocity_property,
                                         current_max_velocity_property)
                data = nx.node_link_data(G)
                if 0 < i and divmod(i, 100)[1] == 0:
                    print(f'[{i}]')
                    for n in G.nodes:
                        print(f'  n={n}, value={G.nodes[n][value_property]}, maxValue={G.nodes[n][max_value_property]}')
                    for e in G.edges:
                        print(f'  e={e}, velocity={G.edges[e[0], e[1]][velocity_property]}, maxVelocity={G.edges[e[0], e[1]][max_velocity_property]}')
                G_array.append(data)
                self._G = G
            if not self._cancel:
                self.ui.progressBar.setValue(100)
                self._post_data = tuple(G_array)
        except Exception as ex:
            print(ex)
        finally:
            self._cancel = True
            self.ui.startButton.setEnabled(True)
            self.ui.stopButton.setEnabled(False)
            self.ui.closeButton.setEnabled(True)

    def stop_clicked(self):
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.closeButton.setEnabled(True)
        # FIXME  self.solver.stop()

    def close_clicked(self):
        self.hide()

    def parallel_clicked(self):
        self.ui.priorSerial.setChecked(False)

    def serial_clicked(self):
        self.ui.priorParallel.setChecked(False)

    #def context_menu_popup(self, pos: QPoint):
    #    menu = QMenu(self.ui.coordinateWidget)
    #    menu.addAction("AAA")
    #    menu.addAction("BBB")
    #    menu.addAction("CCC")
    #    menu.popup(self.ui.coordinateWidget.mapToGlobal(pos))
    #    # FIXME
