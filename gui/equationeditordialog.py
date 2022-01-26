
from PyQt5 import QtWidgets
from gui.Ui_EquationEditorDialog import Ui_EquationEditorDialog
from numpy import pi, sin, cos, tan, exp, log, log2, log10


_tmp = pi+sin(0)+cos(0)+tan(0)+exp(0)+log(1)+log2(1)+log10(1)

class EquationEditorDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_EquationEditorDialog()
        self.ui.setupUi(self)
        self.ui.showChartButton.clicked.connect(self.show_clicked)

    @property
    def ui(self) -> Ui_EquationEditorDialog:
        return self._ui

    def show_clicked(self):
        equation = self.ui.equation.text()
        start = self.ui.start.value()
        end = self.ui.end.value()
        dt = self.ui.dt.value()
        num = int((end - start) / dt)
        times = []
        values = []
        integral = 0
        for i in range(num):
            t = start + dt*i
            eq = equation.replace("{t}", str(t))
            v = eval(eq)
            times.append(t)
            values.append(v)
            integral += v * dt
        self.ui.chart.plotItem.clear()
        self.ui.chart.plotItem.plot(times, values)
        self.ui.integral.setText(str(integral))