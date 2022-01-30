# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np
from graphcore.shell import GraphCoreContextHandler
from graphcore.gcsolver import GCSolver, GCGeneralSolver
from gui.Ui_SolverController import Ui_SolverControllerDialog
from PyQt5.QtWidgets import QDialog, QMenu
from graphcore.gcsolver import SolverController
from graphcore.reporter import GraphCoreReporter
import traceback


class SolverControllerDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self._ui = Ui_SolverControllerDialog()
        self.ui.setupUi(self)
        reporter = GraphCoreReporter(lambda x: self.ui.message.append(str(x)))
        self._solver = SolverController(reporter,
                                        lambda x: self.ui.progressBar.setValue(x))
        self.ui.startButton.clicked.connect(self.start_clicked)
        self.ui.stopButton.clicked.connect(self.stop_clicked)

    @property
    def post_data(self):
        return self.solver.post_data

    @property
    def G(self) -> nx.DiGraph:
        return self._G

    @G.setter
    def G(self, value: nx.DiGraph):
        self.solver.set_G(value)
        self._G = value

    @property
    def ui(self) -> Ui_SolverControllerDialog:
        return self._ui

    @property
    def solver(self) -> SolverController:
        return self._solver

    def start_clicked(self):
        try:
            self.ui.startButton.setEnabled(False)
            self.ui.stopButton.setEnabled(True)
            self.ui.buttonBox.setEnabled(False)
            self.ui.progressBar.setValue(100)
            dt = self.ui.doubleSpinBox.value()
            self.solver.set_dt(dt)
            steps = self.ui.spinBox.value()
            self.solver.set_steps(steps)
            self.solver.start()
        except Exception as ex:
            print('exception occured:', ex)
            print(traceback.format_exc())
        finally:
            self.ui.startButton.setEnabled(True)
            self.ui.stopButton.setEnabled(False)
            self.ui.buttonBox.setEnabled(True)

    def stop_clicked(self):
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.buttonBox.setEnabled(True)
        self.solver.cancel()

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
