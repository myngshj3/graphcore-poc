
from PyQt5.QtCore import QObject, pyqtSignal
from graphcore.thread_signal import GraphCoreThreadSignal


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


_worker = None

def get_script_worker():
    global _worker
    return _worker

def set_script_worker(worker):
    global _worker
    _worker = worker
