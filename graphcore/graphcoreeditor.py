# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *


# Text Editor Widget which provides input checking and type conversion
class TextEditor(QLineEdit):
    def __init__(self, main_window, elem, property_name, value, check_valid=None, type_converter=None):
        super().__init__(str(value))
        self._main_window = main_window
        self._elem = elem
        self._property_name = property_name
        self._value = value
        self._check_valid = check_valid
        self._type_converter = type_converter
        self.editingFinished.connect(self.focus_out)

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value
        self.setText(str(value))

    def focus_out(self):
        if self._check_valid is not None and not self._check_valid(self.text()):
            print("value error: {}".format(self.text()))
            self.setText(str(self.value))
            return
        if self._type_converter is not None:
            self._value = self._type_converter(self.text())
        else:
            self._value = self.text()
        if type(self._elem) == str:
            self._main_window.command_change_node_attr(self._elem, self._property_name, self._value)
        else:
            self._main_window.command_change_edge_attr(self._elem, self._property_name, self._value)


# Integer Value Editor Widget
class IntEditor(TextEditor):
    def __init__(self, main_window, elem, property_name, value, check_valid=None, type_converter=None):
        super().__init__(main_window, elem, property_name, value, self.basic_validator, self.convert_type)

    def basic_validator(self, text):
        try:
            v = int(text)
            return True
        except Exception:
            return False

    def convert_type(self, text):
        return int(text)


# Float Value Editor Widget
class FloatEditor(TextEditor):
    def __init__(self, main_window, elem, property_name, value, check_valid=None, type_converter=None):
        super().__init__(main_window, elem, property_name, value, self.basic_validator, self.convert_type)

    def basic_validator(self, text):
        try:
            v = float(text)
            return True
        except Exception:
            return False

    def convert_type(self, text):
        return float(text)


# ComboBox Widget
class ComboBoxEditor(QComboBox):
    def __init__(self, main_window, elem, property_name, value, entries=None):
        super().__init__()
        self._main_window = main_window
        self._elem = elem
        self._property_name = property_name
        self._value = value
        self._entries = entries
        self._callback_enabled = False
        self.currentIndexChanged.connect(self.index_changed)

    def callback_enabled(self):
        return self._callback_enabled

    def set_callback_enabled(self, flag):
        self._callback_enabled = flag

    def set_entries(self, entries):
        self._entries = entries
        self.construct_menu()

    def construct_menu(self):
        menu_items = []
        for entry in self._entries:
            menu_items.append(entry[1])
        self.clear()
        self.addItems(menu_items)

    def set_value(self, value):
        for i, r in enumerate(self._entries):
            if r[0] == value:
                self.setCurrentIndex(i)
                self._value = value
                return True
        return False

    def value(self):
        if self.currentIndex() < 0:
            return None
        return self._entries[self.currentIndex()][0]

    def index_changed(self, index):
        # print("combobox index changed {}".format(index))
        if self.callback_enabled():
            self._value = self._entries[index][0]
            if type(self._elem) == str:
                self._main_window.command_change_node_attr(self._elem, self._property_name, self._value)
            else:
                self._main_window.command_change_edge_attr(self._elem, self._property_name, self._value)


# CheckBox Widget
class CheckBoxEditor(QCheckBox):
    def __init__(self, main_window, elem, property_name, value):
        super().__init__()
        self.setChecked(value)
        self._main_window = main_window
        self._elem = elem
        self._property_name = property_name
        self._value = value
        self.stateChanged.connect(self.check_changed)

    def value(self):
        return self.isChecked()

    def set_value(self, value):
        self.setChecked(value)

    def check_changed(self, value):
        self._value = self.isChecked()
        if type(self._elem) == str:
            self._main_window.command_change_node_attr(self._elem, self._property_name, self._value)
        else:
            self._main_window.command_change_edge_attr(self._elem, self._property_name, self._value)


# Extended CheckBox Editor
class CheckBoxEditorEx(QCheckBox):
    def __init__(self, value):
        super().__init__()
        self.setChecked(value)
        self._value = value
        self._reflector = None
        self.stateChanged.connect(self.check_changed)

    def value(self):
        return self.isChecked()

    def set_value(self, value):
        self.setChecked(value)

    def set_reflector(self, reflector):
        self._reflector = reflector

    def check_changed(self, value):
        self._value = self.isChecked()
        if self._reflector is not None:
            self._reflector(self._value)


# Text Editor Widget which provides input checking and type conversion
class TextEditorEx(QLineEdit):
    def __init__(self, value, check_valid=None, type_converter=None):
        super().__init__(str(value))
        self._value = value
        self._check_valid = check_valid
        self._type_converter = type_converter
        self._reflector = None
        self.editingFinished.connect(self.focus_out)

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value
        self.setText(str(value))

    def set_reflector(self, reflector):
        self._reflector = reflector

    def focus_out(self):
        if self._check_valid is not None and not self._check_valid(self.text()):
            print("value error: {}".format(self.text()))
            self.setText(str(self.value()))
            return
        if self._type_converter is not None:
            self._value = self._type_converter(self.text())
        else:
            self.set_value(self.text())
        if self._reflector is not None:
            self._reflector(self.value())
