# -*- coding: utf-8 -*-

import traceback
import re
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from graphcore.shell import GraphCoreContextHandler, GraphCoreAsyncContextHandler
from graphcore.script import GraphCoreScript
from graphcore.reporter import GraphCoreReporter
from gui.widgetutil import GraphCoreContextHandlerInterface  # , GraphCoreReporterUser


# Console Widget class
class ConsoleWidget(QTextEdit, GraphCoreContextHandlerInterface):
    def __init__(self, parent=None, handler=None, async_handler=None):
        super().__init__(parent)
        self._handler = handler
        self._async_handler = async_handler
        self._prompt = "> "
        self.append(self._prompt)
        self._script_handler = None
        self._reporter = None
        self._command_history = []
        self._history_point = 0
        self._current_string = ""

    @property
    def reporter(self) -> GraphCoreReporter:
        return self._reporter

    @reporter.setter
    def reporter(self, reporter: GraphCoreReporter):
        self._reporter = reporter

    @property
    def script_handler(self) -> GraphCoreScript:
        if self._script_handler is None:
            self._script_handler = GraphCoreScript(self.async_handler, self.reporter)
        else:
            self._script_handler.handler = self.async_handler
            self._script_handler.reporter = self.reporter
        return self._script_handler

    def showEvent(self, event: QShowEvent):
        self.grabKeyboard()
        super().showEvent(event)

    def hideEvent(self, event: QHideEvent):
        self.releaseKeyboard()
        super().hideEvent(event)

    # keyPressEvent (overrides super-class's method)
    def keyPressEvent(self, a0: QKeyEvent) -> None:
        ignore = False
        try:
            if a0.key() == Qt.Key_Return:
                a0.accept()
                # self.append("\n")
                self.execute_command()
                self.append(self._prompt)
            elif a0.key() == Qt.Key_Backspace:
                if self._current_string != "":
                    self._current_string = self._current_string[0:len(self._current_string) - 1]
                    a0.accept()
                    super().keyPressEvent(a0)
                else:
                    a0.ignore()
                    ignore = True
            elif a0.key() == Qt.Key_Escape:
                a0.ignore()
            else:
                self._current_string += a0.text()
                a0.accept()
                super().keyPressEvent(a0)
        except Exception as ex:
            print(ex)
        finally:
            pass

    def execute_command(self):
        try:
            self.script_handler.execute_script(self._current_string)
        except Exception as ex:
            self.reporter.report(traceback.format_exc())
        finally:
            self.current_string = ""
        pass

    def append_history(self, command):
        self._command_history.append(command)

    def send_backspaces(self, cnt):
        # FIXME
        pass

    def put_string(self, text):
        # FIXME
        pass

    def clear_current_command(self):
        self.send_backspaces(len(self._current_string))
        self._current_string = ""

    def change_history(self, pos):
        if (0 <= pos) and (pos < len(self._command_history)):
            self._history_point = pos
            self.clear_current_command()
            self.set_current_command(self._command_history[pos])

    def next_history(self):
        pass

    def prev_history(self):
        if self._history_point == 0:
            # nothing to do
            return
        self._history_point -= 1
        h = self._command_history[self._history_point]

    def clear(self):
        self.text_area().clear()

    def add_text(self, text):
        self.text_area().append(text)

