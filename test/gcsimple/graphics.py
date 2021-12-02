
import sys
import re
import networkx as nx
from queue import Queue
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qt import *
from PyQt5.QtGui import *
from graphicsscene import GCScene
from gcparser import CommandParser



class GCGraph(nx.DiGraph):

    def __init__(self):
        super().__init__()

    def next_node_id(self) -> int:
        if len(self.nodes) == 0:
            return 0
        m = max(self.nodes)
        for n in range(m):
            if n not in self.nodes:
                return n
        return m+1

    def name_to_node_id(self, l: str) -> int:
        for n in self.nodes:
            if self.nodes[n]['name'] == l:
                return n
        return -1

    def node_to_edges(self, n: int):
        E = []
        for e in self.edges:
            if e[0] == n or e[1] == n:
                E.append(e)
        return E


class CommandReaderThread(QThread):

    def __init__(self, queue: Queue):
        super().__init__()
        self._queue = queue

    @property
    def queue(self) -> Queue:
        return self._queue

    def run(self):
        # reader loop
        while True:
            instr = input("$self> ")
            if re.match(r"^\s*$", instr):
                continue
            self._queue.put(instr)
            if re.match(r"\s*quit\s*$", instr):
                break


class CommandProcessorThread(QThread):

    Signal: pyqtSignal = pyqtSignal(str)
    queue: Queue = Queue()
    # animator: AnimationThread = AnimationThread(queue)

    def run(self):
        while True:
            item = self.queue.get()
            # print("queue got", item, self.queue)
            self.Signal.emit(item)


class GCPane(QGraphicsView):

    GCPANE_CONFIG = 'gcpane.conf'

    # shape holder
    @property
    def G(self) -> GCGraph:
        return self._G

    @property
    def scene(self) -> GCScene:
        return self._scene

    @property
    def command_parser(self):
        return self._command_parser

    def set_command_parser(self, parser):
        self._command_parser = parser

    # initializes
    def __init__(self):
        super().__init__()
        self._G = GCGraph()
        self._command_runner = CommandProcessorThread()
        self._scene = GCScene(self.G, self._command_runner.queue)
        self.setScene(self._scene)
        self._command_runner.Signal.connect(self.do_command)
        self._reader_runner = CommandReaderThread(self._command_runner.queue)
        self._command_parser = None

    # command loop
    def do_command(self, item):
        if re.match(r"^\s*$", item):
            pass
        elif re.match(r"^\s*(quit|exit)\s*$", item):  # matches `quit'
            self.close()
        elif self._command_parser is not None:
            self._command_parser(item, self.G, self.scene, self._command_runner.queue)

    def startCommandReader(self):
        self._reader_runner.start()
        self._command_runner.start()


def main():
    app = QApplication(sys.argv)
    parser = CommandParser()
    pane = GCPane()
    pane.set_command_parser(parser)
    pane.setGeometry(100, 100, 800, 600)
    # test shapes
    g = QGraphicsItemGroup()
    r = QGraphicsRectItem()
    r.setRect(0, 0, 200, 200)
    r.setBrush(QColor('green'))
    g.addToGroup(r)
    t = QGraphicsTextItem('hello')
    rect = t.sceneBoundingRect()
    t.setPos(50, 100)
    g.addToGroup(t)
    pane.scene.addItem(g)
    pane.show()
    pane.startCommandReader()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
