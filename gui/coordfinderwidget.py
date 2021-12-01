# -*- coding: utf-8 -*-


import traceback
import re
from gui.CoordinationFinderWidget import Ui_CoordFinderForm
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from graphcore.layout import layout_combinations
from graphcore.shell import GraphCoreAsyncContextHandler


class LayoutProcessSignal:
    def __init__(self, sig, data):
        self._sig = sig
        self._data = data

    def signal(self):
        return self._sig

    def data(self):
        return self._data


class LayoutFinder(QThread):

    Signal: pyqtSignal = pyqtSignal(LayoutProcessSignal)
    LayoutFound: int = 1
    Finished: int = 2

    def __init__(self, nodes):
        super().__init__()
        self._nodes = nodes
        self._cancel = False
        self._finished_notified = None

    def canceler(self):
        return self._cancel

    def cancel(self):
        self._cancel = True

    def validate(self, grid):
        sig = LayoutProcessSignal(self.LayoutFound, grid)
        self.Signal.emit(sig)

    def run(self):
        layout_combinations(self._nodes, validator=self.validate, canceler=self.canceler)
        sig = LayoutProcessSignal(self.Finished, None)
        self.Signal.emit(sig)
        # if self._finished_notified is not None:
        #     self._finished_notified(None)


# Animating Process Signale class
class AnimationProcessSignal:
    def __init__(self, sig, data):
        self._sig = sig
        self._data = data

    def signal(self):
        return self._sig

    def data(self):
        return self._data


# Animating thread
class Animator(QThread):

    Signal: pyqtSignal = pyqtSignal(AnimationProcessSignal)
    Updated: int = 1
    Created: int = 0
    Running: int = 1
    Suspending: int = 2
    Suspended: int = 3
    Stopping: int = 4
    Finished: int = 5
    Canceling: int = 6
    Canceled: int = 7

    def __init__(self, interval=300, animation_pixmaps=(None), paused_pixmap=None,
                 canceled_pixmap=None, finished_pixmap=None):
        super().__init__()
        self._interval = interval
        self._animation_pixmaps = animation_pixmaps
        self._paused_pixmap = paused_pixmap
        self._finished_pixmap = finished_pixmap
        self._canceled_pixmap = canceled_pixmap
        self._scene_index = 0
        self._state = self.Created
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def pause(self):
        self._state = Animator.Suspending

    def resume(self):
        self._state = Animator.Running

    def stop(self):
        self._state = Animator.Stopping

    def run(self):
        self._state = self.Running
        while self._state in (Animator.Running, Animator.Suspending) and not self._cancel:
            # self.sleep(self._interval)
            self.usleep(self._interval)
            if self._state == self.Running:
                self._scene_index += 1
                self._scene_index %= len(self._animation_pixmaps)
                self.Signal.emit(AnimationProcessSignal(self.Updated, self._animation_pixmaps[self._scene_index]))
            elif self._state == self.Suspending:
                self.Signal.emit(AnimationProcessSignal(self.Suspending, self._paused_pixmap))
                self._state = self.Suspended
                break
        if self._cancel:
            self._cancel = False
            self._state = Animator.Canceled
            self.Signal.emit(AnimationProcessSignal(self.Canceled, self._canceled_pixmap))
        else:
            self._state = self.Finished
            self.Signal.emit(AnimationProcessSignal(self.Finished, self._finished_pixmap))


# Coordination Finder Widget class
class CoordFinderWidget(QWidget):

    def __init__(self, async_handler):
        super().__init__()
        self._handler = async_handler
        self._ui = None
        self._layout_finder = None
        self._grids = []
        pixmaps = []
        pixmaps.append(QPixmap('images/blueball.png'))
        pixmaps.append(QPixmap('images/greenball.png'))
        pixmaps.append(QPixmap('images/yellowball.png'))
        self._animation_pixmaps = pixmaps
        self._paused_pixmap = QPixmap("images/pause.png")
        self._canceled_pixmap = QPixmap('images/redball.png')
        self._finished_pixmap = QPixmap("images/start.png")
        self._start_pixmap = self._finished_pixmap
        self._animator = Animator(interval=300, animation_pixmaps=self._animation_pixmaps,
                                  canceled_pixmap=self._canceled_pixmap,
                                  finished_pixmap=self._finished_pixmap, paused_pixmap=self._paused_pixmap)
        self._animator.Signal.connect(self.animation_notified)
        # self._animator.start()

    @property
    def handler(self) -> GraphCoreAsyncContextHandler:
        return self._handler

    @property
    def ui(self) -> Ui_CoordFinderForm:
        return self._ui

    @ui.setter
    def ui(self, _ui: Ui_CoordFinderForm):
        self._ui = _ui
        self.ui.setupUi(self)
        self.ui.searchButton.setEnabled(True)
        self.ui.cancelButton.setEnabled(False)
        self.ui.applyButton.setEnabled(False)
        self.ui.closeButton.setEnabled(True)
        self.ui.coordinationWidget.setRowCount(0)
        self.ui.coordinationWidget.setColumnCount(1)
        self.ui.coordinationWidget.setHorizontalHeaderLabels(['grid'])
        self.ui.imageLabel.setPixmap(self._start_pixmap)
        self.ui.statusLabel.setText("Normal")

    @property
    def layout_finder(self) -> LayoutFinder:
        return self._layout_finder

    @layout_finder.setter
    def layout_finder(self, finder):
        self._layout_finder = finder

    # Handler for Signal from Animator
    def animation_notified(self, sig: AnimationProcessSignal):
        ui: Ui_CoordFinderForm = self.ui
        if sig.signal() == Animator.Updated:
            ui.imageLabel.setPixmap(sig.data())
            ui.statusLabel.setText("Running")
        elif sig.signal() == Animator.Canceled:
            ui.imageLabel.setPixmap(sig.data())
            ui.statusLabel.setText("Canceled")
        elif sig.signal() == Animator.Suspended:
            ui.imageLabel.setPixmap(sig.data())
            ui.statusLabel.setText("Suspended")
        elif sig.signal() == Animator.Finished:
            ui.imageLabel.setPixmap(sig.data())
            ui.statusLabel.setText("Finished")

    def reset(self):
        self._grids = []
        self.setup_ui()

    def add_grid(self, grid):
        label = ""
        for row in grid:
            label += "{} ".format(row)
        # print(label)
        table: QTableWidget = self.ui.coordinationWidget
        row_count = table.rowCount()
        item = QTableWidgetItem(label)
        table.setRowCount(row_count + 1)
        table.setItem(row_count, 0, item)

    def signal_notified(self, sig: LayoutProcessSignal):
        # Layout found
        if sig.signal() == LayoutFinder.LayoutFound:
            # print("Layout found: {}".format(sig.data()))
            grid = sig.data()
            self.add_grid(grid)

        # Layout finding process finished
        elif sig.signal() == LayoutFinder.Finished:
            print("Layout finder finished")
            self._animator.stop()
            ui: Ui_CoordFinderForm = self.ui
            ui.searchButton.setEnabled(True)
            ui.cancelButton.setEnabled(False)
            ui.applyButton.setEnabled(False)
            ui.closeButton.setEnabled(True)

    def do_search(self):
        try:
            self._animator.start()
            self.reset()
            ui: Ui_CoordFinderForm = self.ui
            ui.searchButton.setEnabled(False)
            ui.cancelButton.setEnabled(True)
            ui.applyButton.setEnabled(False)
            ui.closeButton.setEnabled(False)
            self.start_searching()
        except Exception as ex:
            print(ex)

    def do_cancel(self):
        try:
            self._animator.cancel()
            self.cancel_searching()
        except Exception as ex:
            print(ex)

    def do_apply(self):
        try:
            self.apply()
        except Exception as ex:
            print(ex)

    def do_close(self):
        try:
            self.close()
        except Exception as ex:
            print(ex)

    def start_searching(self):
        self.layout_finder = LayoutFinder(self.handler.context.nodes)
        self.layout_finder.Signal.connect(self.signal_notified)
        self.layout_finder.start()
        pass

    def cancel_searching(self):
        self.layout_finder.cancel()
        pass

    def apply(self):
        pass

    def close(self):
        self.hide()
