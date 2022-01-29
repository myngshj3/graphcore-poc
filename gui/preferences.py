

from PyQt5.QtWidgets import QDialog
from gui.Ui_PreferencesDialog import Ui_PreferencesDialog
from graphcore.settings import GraphCoreSettings


class PreferencesDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        self._settings = None
        self.ui.buttonBox.clicked.connect(self.ok_clicked)
        self.ui.buttonBox.rejected.connect(self.cancel_clicked)

    @property
    def ui(self) -> Ui_PreferencesDialog:
        return self._ui

    @property
    def settings(self):
        return self._settings

    def set_settings(self, settings: GraphCoreSettings):
        self._settings = settings
        self.ui.chartLineWidth.setValue(self.settings.setting('preferences')['visualizer']['chart-line-width'])
        self.ui.bgcolorEditor.ui.lineEdit.setText(self.settings.setting('preferences')['visualizer']['chart-background'])

    def ok_clicked(self):
        # visualizer settings
        self.settings.setting('preferences')['visualizer']['chart-line-width'] = self.ui.chartLineWidth.value()
        self.settings.setting('preferences')['visualizer']['chart-background'] = self.ui.bgcolorEditor.ui.lineEdit.text()


    def cancel_clicked(self):
        pass
