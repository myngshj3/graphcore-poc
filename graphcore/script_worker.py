
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from graphcore.thread_signal import GraphCoreThreadSignal
from graphcore.script import GraphCoreScript
from gui.Ui_MainWindow import Ui_MainWindow

# Script worker class
class ScriptWorker(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(int)
    main_window_command = pyqtSignal(GraphCoreThreadSignal)

    def __init__(self, script_handler, script):
        super().__init__(None)
        self.script_handler = script_handler
        self.script = script

    def run(self):
        self.script_handler.execute_script(self.script)
        self.finished.emit()


class GCScriptWorker(GraphCoreScript):

    finished = pyqtSignal()
    main_thread_command = pyqtSignal(GraphCoreThreadSignal)

    def __init__(self, main_window, thread):
        super().__init__(None, main_window.reporter)
        self._main_window = main_window
        self._script_thread = thread
        self._script = None

    @property
    def main_window(self):
        return self._main_window

    @property
    def script_thread(self) -> QThread:
        return self._script_thread

    def run_script(self, script):
        self._script = script
        self.script_thread.start()

    def enable_run(self):
        self._toplevel.set_running(True)

    def disable_run(self):
        self._toplevel.set_running(False)

    def interrupt(self):
        self._toplevel.set_running(False)

    def run(self):
        self.execute_script(self._script)
        self.finished.emit()


_worker = None

def get_script_worker():
    global _worker
    return _worker

def set_script_worker(worker):
    global _worker
    _worker = worker
