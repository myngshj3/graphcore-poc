from PyQt5 import QtWidgets
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import numpy as np
import math


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        x = np.linspace(-10, 10, 100)
        y = np.zeros(100, np.float)
        for i, a in enumerate(x):
            y[i] = 1/math.sqrt(2*math.pi*5*5)*math.exp(-a**2/(2*5*5))

        # plot data: x, y values
        self.graphWidget.plot(x, y)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()