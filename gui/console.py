# -*- coding: utf-8 -*-

import traceback
from graphcore.reporter import GraphCoreReporter
from graphcore.shell import GraphCoreContextHandler, GraphCoreAsyncContextHandler
from gui.Ui_ConsoleWidget import Ui_ConsoleForm
from gui.geomserializable import GeometrySerializableDialog
from gui.widgetutil import GraphCoreContextHandlerInterface  # , GraphCoreReporterUser


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
