
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from gui.ui_postscreen import Ui_PostScreenDialog
import pyqtgraph as pg


class PostScreenDialog(QDialog):
    def __init__(self, parent, ui: Ui_PostScreenDialog):
        super().__init__(parent)
        self._ui = ui
        ui.setupUi(self)
        self._G = None
        self._post_data = None
        self._cancel = False
        #
        self.plot()

    @property
    def ui(self) -> Ui_PostScreenDialog:
        return self._ui

    @property
    def post_data(self):
        return self._post_data

    @post_data.setter
    def post_data(self, value):
        self._post_data = value

    def plot(self):
        p1 = self.ui.plotWidget.getPlotItem()
        p1.addItem(pg.PlotCurveItem(x=[0, 1, 2, 3, 4],
                                    y=[0, 1, 2, 3, 4],
                                    pen=pg.mkPen(color="r", style=Qt.SolidLine),
                                    antialias=True))
        p1.addItem(pg.ScatterPlotItem(x=[0,1,2,3,4],
                                      y=[4,3,2,1,0],
                                      symbol="x",
                                      pen=pg.mkPen(),
                                      brush=pg.mkBrush("b"),
                                      size=7.5,
                                      antialias=True))