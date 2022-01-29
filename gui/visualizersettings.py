
from PyQt5.QtWidgets import QWidget
from gui.Ui_VisualizerSettings import Ui_VisualizerSettingsForm


class VisualizerSettingsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_VisualizerSettingsForm()
        self.ui.setupUi(self)

    @property
    def ui(self) -> Ui_VisualizerSettingsForm:
        return self._ui
