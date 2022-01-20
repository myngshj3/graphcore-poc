

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from gui.Ui_LongTextEditorDialog import Ui_LongTextEditorDialog
from gui.Ui_LongTextEditorWidget import Ui_LongTextEditorWidget

class LongTextEditorWidget(QWidget):

    def __init__(self):
        super().__init__()
        self._ui = Ui_LongTextEditorWidget()
        self._ui.setupUi(self)

    @property
    def ui(self) -> Ui_LongTextEditorWidget:
        return self._ui


class TextEditor(QLineEdit):
    def __init__(self, value: str, name: str, value_convert=None, check_valid=None, apply=None):
        super().__init__()
        self._value = value
        self._name = name
        self._check_valid = check_valid
        self._value_convert = value_convert
        self._apply = apply
        self.setText(str(self.value))
        self.editingFinished.connect(self.focus_out)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    @property
    def name(self):
        return self._name

    @property
    def check_valid(self):
        return self._check_valid

    @check_valid.setter
    def check_valid(self, v):
        self._check_valid = v

    @property
    def value_convert(self):
        return self._value_convert

    @property
    def apply(self):
        return self._apply

    def focus_out(self):
        if self.check_valid is not None and not self.check_valid(self.text()):
            print("value error: {}".format(self.text()))
            self.setText(str(self.value))
            return
        if self.value_convert is not None:
            self.value = self.value_convert(self.text())
        else:
            self.value = self.text()
        if self.apply is not None:
            self.apply(self.name, self.value)




class LongTextEditor(LongTextEditorWidget):

    def __init__(self, value: str, name, value_converter=None, check_vaid=None, apply=None):
        super().__init__()
        self._initial_value = value
        self._name = name
        self._value_converter = value_converter
        self._validator = check_vaid
        self._applyer = apply
        self.ui.pushButton.clicked.connect(self.show_editor)
        self.ui.lineEdit.editingFinished.connect(self.focus_out)
        self.ui.lineEdit.setText(self._initial_value)

    def focus_out(self):
        if self._validator is not None and not self._validator(self.text()):
            print("value error: {}".format(self.ui.lineEdit.text()))
            self.setValue(self._initial_value)
            return
        if self._value_converter is not None:
            self.ui.lineEdit.setText(self._value_converter(self.ui.lineEdit.text()))
        if self._applyer is not None:
            self._applyer(self._name, self.ui.lineEdit.text())

    def show_editor(self):
        dialog: QDialog = QDialog()
        ui = Ui_LongTextEditorDialog()
        ui.setupUi(dialog)
        ui.buttonBox.clicked.connect(lambda: self.dialog_button_clicked(ui.plainTextEdit.toPlainText()))
        # ui.buttonBox.rejected.connect()
        ui.plainTextEdit.setPlainText(self.ui.lineEdit.text())
        dialog.exec_()

    def dialog_button_clicked(self, text):
        if self._value_converter is not None:
            text = self._value_converter(text)
        self.ui.lineEdit.setText(text)
        if self._applyer is not None:
            self._applyer(self._name, self.ui.lineEdit.text())


class SpinBoxEditor(QSpinBox):

    def __init__(self, value: int, name: str, value_converter=int, check_vaid=None, apply=None):
        super().__init__()
        self._initial_value = value
        self.setValue(self._initial_value)
        self._name = name
        self._value_converter = value_converter
        self._validator = check_vaid
        self._applyer = apply
        self.editingFinished.connect(self.focus_out)

    def focus_out(self):
        if self._validator is not None and not self._validator(self.text()):
            print("value error: {}".format(self.text()))
            self.setValue(self._initial_value)
            return
        if self._value_converter is not None:
            self.setValue(self._value_converter(self.value()))
        if self._applyer is not None:
            self._applyer(self._name, self.value())


class FloatSpinBoxEditor(QDoubleSpinBox):

    def __init__(self, value: float, name: str, value_converter=int, check_vaid=None, apply=None):
        super().__init__()
        self._initial_value = value
        self.setValue(self._initial_value)
        self._name = name
        self._value_converter = value_converter
        self._validator = check_vaid
        self._applyer = apply
        self.editingFinished.connect(self.focus_out)

    def focus_out(self):
        if self._validator is not None and not self._validator(self.text()):
            print("value error: {}".format(self.text()))
            self.setValue(self._initial_value)
            return
        if self._value_converter is not None:
            self.setValue(self._value_converter(self.value()))
        if self._applyer is not None:
            self._applyer(self._name, self.value())


class IntEditor(TextEditor):
    def __init__(self, value: int, name: str, value_convert=int, check_valid=None, apply=None):
        super().__init__(str(value), name, value_convert, check_valid, apply)
        self._value = value
        if check_valid is None:
            self.check_valid = lambda x: self.is_valid(x)

    def is_valid(self, text):
        try:
            i = int(text)
            return True
        except Exception:
            print("value error:{}".format(text))
            return False


class FloatEditor(TextEditor):
    def __init__(self, value: float, name: str, value_convert=float, check_valid=None, apply=None):
        super().__init__(str(value), name, value_convert, check_valid, apply)
        self._value = value
        if check_valid is None:
            self.check_valid = lambda x: self.is_valid(x)

    def is_valid(self, text):
        try:
            f = float(text)
            return True
        except Exception:
            print("value error:{}".format(text))
            return False


class BoolEditor(QCheckBox):
    def __init__(self, value: bool, name: str, apply=None):
        super().__init__()
        self._value = value
        self._name = name
        self._apply = apply
        self.setChecked(value)
        self.stateChanged.connect(self.check_changed)

    @property
    def value(self) -> bool:
        return self.isChecked()

    @value.setter
    def value(self, _value: bool):
        self.setChecked(_value)

    @property
    def name(self):
        return self._name

    @property
    def apply(self):
        return self._apply

    def check_changed(self, value):
        if self.apply is not None:
            self.apply(self.name, self.value)


# ComboBox Widget
class ComboBoxEditor(QComboBox):
    def __init__(self, value, name: str, entries: list, apply=None):
        super().__init__()
        self._name = name
        self._value = value
        self._entries = None
        self._apply = apply
        self._callback_enabled = False
        self.entries = entries
        self.currentIndexChanged.connect(self.index_changed)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        for i, r in enumerate(self._entries):
            if r[0] == value:
                self.setCurrentIndex(i)
                self._value = value

    @property
    def callback_enabled(self):
        return self._callback_enabled

    @callback_enabled.setter
    def callback_enabled(self, flag):
        self._callback_enabled = flag

    @property
    def entries(self):
        return self._entries

    @entries.setter
    def entries(self, entries):
        self._entries = entries
        self.construct_menu()

    @property
    def apply(self):
        return self._apply

    def construct_menu(self):
        menu_items = []
        index = 0
        for i, entry in enumerate(self._entries):
            if entry[0] == self.value:
                index = i
            menu_items.append(entry[1])
        self.clear()
        self.addItems(menu_items)
        self.setCurrentIndex(index)

    def index_changed(self, index):
        # print("combobox index changed {}".format(index))
        if self.callback_enabled:
            self.value = self._entries[index][0]
            if self.apply is not None:
                self.apply(self.name, self.value)

