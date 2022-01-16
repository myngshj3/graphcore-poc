# -*- coding: utf-8 -*-

import traceback
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit


class ConsoleLineEdit(QLineEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancel_func = None
        self._return_func = None
        self._history = []
        self._hist_pos = -1

    def set_cancel_func(self, f):
        self._cancel_func = f

    def set_return_func(self, f):
        self._return_func = f

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_C and a0.modifiers() & Qt.ControlModifier: # CTRL-C
            if self._cancel_func is not None:
                self._cancel_func()
        elif a0.key() == Qt.Key_Up:
            if self._hist_pos < len(self._history):
                self._hist_pos += 1
                text = self._history[self._hist_pos]
                self.setText(text)
        elif a0.key() == Qt.Key_Down:
            if self._hist_pos >= -1:
                self._hist_pos -= 1
                text = self._history[self._hist_pos]
                self.setText(text)
        elif a0.key() == Qt.Key_Return:
            text = self.text()
            self._history.insert(0, text)
            self._hist_pos = -1
            if self._return_func is not None:
                self._return_func()
        else:
            super().keyPressEvent(a0)
