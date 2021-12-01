# -*- coding: utf-8 -*-

import numpy as np
from graphcore.shell import GraphCoreContextHandler
from graphcore.solver import GraphCoreGenericSolver
from gui.Ui_SolverController import Ui_SolverControllerForm
from PyQt5.QtWidgets import QDialog, QMenu
from PyQt5.QtCore import QPoint


class SolverControllerDialog(QDialog):
    def __init__(self, parent, ui: Ui_SolverControllerForm, handler: GraphCoreContextHandler, dt=1.0):
        super().__init__(parent)
        self._handler = handler
        self._ui = ui
        ui.setupUi(self)
        self._solver = GraphCoreGenericSolver(self.handler, dt=1.0)

    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @property
    def solver(self) -> GraphCoreGenericSolver:
        return self._solver

    @property
    def ui(self) -> Ui_SolverControllerForm:
        return self._ui

    def start_clicked(self):
        self.ui.startButton.setEnabled(False)
        self.ui.stopButton.setEnabled(True)
        self.ui.okButton.setEnabled(False)
        self.ui.cancelButton.setEnabled(False)
        # FIXME self.solver.start()

    def stop_clicked(self):
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.okButton.setEnabled(True)
        self.ui.cancelButton.setEnabled(True)
        # FIXME  self.solver.stop()

    def ok_clicked(self):
        self.hide()

    def cancel_clicked(self):
        self.hide()

    def parallel_clicked(self):
        self.ui.priorSerial.setChecked(False)

    def serial_clicked(self):
        self.ui.priorParallel.setChecked(False)

    def context_menu_popup(self, pos: QPoint):
        menu = QMenu(self.ui.coordinateWidget)
        menu.addAction("AAA")
        menu.addAction("BBB")
        menu.addAction("CCC")
        menu.popup(self.ui.coordinateWidget.mapToGlobal(pos))
        # FIXME
