# -*- coding: utf-8 -*-

import traceback
import re
import time
from gui.Ui_ScriptEditor import Ui_ScriptEdior
from graphcore.script_worker import ScriptWorker
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal
# import PyQt5.Qt as Qt
from graphcore.thread_signal import GraphCoreThreadSignal
from graphcore.shell import GraphCoreContextHandler, GraphCoreAsyncContextHandler
from graphcore.reporter import GraphCoreReporter
from graphcore.script import GraphCoreScript
from graphcore.settings import GraphCoreSettings
from gui.geomserializable import GeometrySerializableDialog
from gui.widgetutil import GraphCoreContextHandlerInterface
from networkml.network import NetworkClass, NetworkInstance
from networkml.lexer import NetworkParser, NetworkParserError


# Script Editor Dialog class
class ScriptEditorDialog(QDialog, GraphCoreContextHandlerInterface):
    def __init__(self, parent, ui: Ui_ScriptEdior,
                 handler: GraphCoreContextHandler, async_handler: GraphCoreAsyncContextHandler):
        super().__init__(parent)
        self._handler = handler
        self._async_handler = async_handler
        self._ui = ui
        self.ui.setupUi(self)
        self.set_handler_pair(handler, async_handler)
        self._reporter = GraphCoreReporter(lambda x: self.ui.messages.append(str(x)))
        self._script_handler = GraphCoreScript(self.async_handler, self.reporter)
        self._thread = None
        self._worker = None

    @property
    def script_handler(self) -> GraphCoreScript:
        return self._script_handler

    @property
    def reporter(self) -> GraphCoreReporter:
        return self._reporter

    @property
    def ui(self) -> Ui_ScriptEdior:
        return self._ui

    def test_script(self):
        from graphcore.script_worker import set_script_worker
        script = self.ui.scriptEdit.toPlainText()
        self.script_handler.handler = self.handler
        self.script_handler.reporter = self.reporter
        # execute script
        # self.script_handler.execute_script(script)
        self._thread = QThread()
        self._worker = ScriptWorker(self.script_handler, script)
        set_script_worker(self._worker)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        # self._worker.progress.connect(self.reportProgress)
        self._thread.start()

        self.ui.testScriptButton.setEnabled(False)
        self.ui.cancelButton.setEnabled(True)
        self._thread.finished.connect(lambda: self.ui.testScriptButton.setEnabled(True))
        self._thread.finished.connect(lambda: self.ui.cancelButton.setEnabled(False))

    def clear_message(self):
        self.ui.messages.clear()

    def cancel_script(self):
        self.script_handler.cancel_script()

