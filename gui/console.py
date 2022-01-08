# -*- coding: utf-8 -*-

import traceback
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.Qt import QKeyEvent
from graphcore.shell import GraphCoreContextHandler, GraphCoreAsyncContextHandler
from graphcore.reporter import GraphCoreReporter
from graphcore.shell import GraphCoreContextHandler, GraphCoreAsyncContextHandler
from gui.Ui_ConsoleWidget import Ui_ConsoleForm
from gui.Ui_ConsoleDialog import Ui_Dialog
from gui.geomserializable import GeometrySerializableDialog
from gui.widgetutil import GraphCoreContextHandlerInterface  # , GraphCoreReporterUser
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

    def __init__(self, parent, handler, async_handler):
        super().__init__(parent)
        self._handler = handler
        self._async_handler = async_handler
        self._ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.lineEdit.returnPressed.connect(self.enter_pressed)

    @property
    def ui(self) -> Ui_Dialog:
        return self._ui

    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @property
    def async_handler(self) -> GraphCoreAsyncContextHandler:
        return self._async_handler

    def print(self, *args):
        text = " ".join([str(_) for _ in args])
        self.ui.textBrowser.append(text)

    def set_handler_pair(self, handler, async_handler):
        self._handler = handler
        self._async_handler = async_handler

    def enter_pressed(self):
        script = self.ui.lineEdit.text()
        self.ui.textBrowser.append(script)
        self.ui.lineEdit.clear()
        # execute script
        try:
            interpret = self.handler.toplevel.get_method(self.handler.toplevel, "interpret")
            self.handler.toplevel.set_print_func(lambda x: self.ui.textBrowser.append(str(x)))
            self.handler.toplevel.auto_flush = True
            m = ExtensibleWrappedAccessor(self.handler.toplevel, "print", self,
                                          lambda ao, c, eo, ca, ea: self.print(*ca))
            self.handler.toplevel.declare_method(m, globally=True)
            interpret(self.handler.toplevel, [script, "--safe=False"])
        except Exception as ex:
            self.print(ex)
            self.print(traceback.format_exc())
        finally:
            pass
