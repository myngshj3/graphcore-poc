# -*- coding: utf-8 -*-

import traceback
import re
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLineEdit
from PyQt5.Qt import QKeyEvent
from graphcore.shell import GraphCoreContextHandler, GraphCoreAsyncContextHandler
from graphcore.reporter import GraphCoreReporter
from graphcore.shell import GraphCoreContextHandler, GraphCoreAsyncContextHandler
from gui.Ui_ConsoleWidget import Ui_ConsoleForm
from gui.Ui_ConsoleDialog import Ui_Dialog
from gui.geomserializable import GeometrySerializableDialog
from gui.widgetutil import GraphCoreContextHandlerInterface  # , GraphCoreReporterUser
from graphcore.script_worker import GCScriptWorker
from networkml.network import ExtensibleWrappedAccessor


class ContextHandlableDialog(GeometrySerializableDialog, GraphCoreContextHandlerInterface):
    def __init__(self,
                 serialize_position=None, serialize_size=None,
                 handler: GraphCoreContextHandler = None, async_handler: GraphCoreAsyncContextHandler = None):
        super().__init__()
        self._handler = handler
        self._async_handler = async_handler
        self.serialize_position = serialize_position
        self.serialize_size = serialize_size


# Console Dialog class
class ConsoleDialog(ContextHandlableDialog):
    def __init__(self, ui: Ui_ConsoleForm,
                 handler: GraphCoreContextHandler, async_handler: GraphCoreAsyncContextHandler,
                 serialize_position=None, serialize_size=None):
        super().__init__(serialize_position, serialize_size, handler, async_handler)
        self._ui = ui
        self.ui.setupUi(self)
        self._reporter = GraphCoreReporter(lambda x: self.ui.textBrowser.append(x))
        self.ui.textBrowser.reporter = self.reporter
        self.set_handler_pair(handler, async_handler)

    @property
    def reporter(self) -> GraphCoreReporter:
        return self._reporter

    @property
    def ui(self) -> Ui_ConsoleForm:
        return self._ui

    def set_handler_pair(self, handler: GraphCoreContextHandler, async_handler: GraphCoreAsyncContextHandler):
        super().set_handler_pair(handler, async_handler)
        self.ui.textBrowser.handler = handler
        self.ui.textBrowser.async_handler = async_handler


class Console(QDialog):

    def __init__(self, parent, handler):
        super().__init__(parent)
        self._script_handler = handler
        self._ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.lineEdit.set_return_func(self.enter_pressed)
        self.ui.lineEdit.set_cancel_func(self.ctrl_c_pressed)
        # self.ui.lineEdit.returnPressed.connect(self.enter_pressed)

    @property
    def ui(self) -> Ui_Dialog:
        return self._ui

    @property
    def handler(self) -> GCScriptWorker:
        return self._script_handler

    def set_handler(self, sh):
        self._script_handler = sh

    def print(self, *args):
        text = " ".join([str(_) for _ in args])
        self.ui.textBrowser.append(text)

    def ctrl_c_pressed(self):
        self.ui.textBrowser.append('^C')
        self.handler.toplevel.set_running(False)

    def enter_pressed(self):
        from gui.mainwindow import GraphCoreEditorMainWindow
        from graphcore.thread_signal import GraphCoreThreadSignal
        # execute script
        try:
            script = self.ui.lineEdit.text()
            self.ui.textBrowser.append(script)
            self.ui.lineEdit.clear()
            if re.match("^\s*$", script):
                return
            def print(*args):
                arg = " ".join([str(_) for _ in args])
                sig = GraphCoreThreadSignal("update console.textBrowser", arg,
                                            lambda x: self.ui.textBrowser.append(x), None)
                self.handler.main_thread_command.emit(sig)
            self.handler.toplevel.set_print_func(print)
            self.handler.toplevel.auto_flush = True
            def report_func(arg):
                sig = GraphCoreThreadSignal("update console.textBrowser", arg,
                                            lambda x: self.ui.textBrowser.append(x), None)
                self.handler.main_thread_command.emit(sig)
            self._script_handler.reporter.report_func = report_func
            m = ExtensibleWrappedAccessor(self.handler.toplevel, "print", self,
                                          lambda ao, c, eo, ca, ea: print(*ca))
            self.handler.toplevel.declare_method(m, globally=True)
            self.handler.run_script(script)
        except Exception as ex:
            self.print(ex)
            self.print(traceback.format_exc())
        finally:
            pass
