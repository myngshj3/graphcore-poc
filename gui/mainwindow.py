
import networkx as nx
import traceback
import re
import json
from graphcore.shell import GraphCoreThreadSignal
from graphcore.shell import GraphCoreShell, GraphCoreContext, GraphCoreContextHandler, GraphCoreAsyncContextHandler
from gui.Ui_MainWindow import Ui_MainWindow
from graphcore.graphicsitem import GraphCoreCircleNodeItem, GraphCoreRectNodeItem, GraphCoreEdgeItem, \
    GraphCoreNodeItemInterface, GraphCoreItemInterface, GCCustomNodeItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from graphcore.graphicsitem import GCItemGroup
from graphcore.propertyeditor import TextEditor, IntEditor, FloatEditor, BoolEditor, ComboBoxEditor
from graphcore.propertyeditor import SpinBoxEditor, FloatSpinBoxEditor, LongTextEditor, EquationEditor
# from GraphCore.graphcoreeditor import TextEditor, IntEditor, FloatEditor, ComboBoxEditor, CheckBoxEditor,\
#     CheckBoxEditorEx, TextEditorEx
from graphcore.constraint import GCConstraintParser
from networkml.error import NetworkParserError, NetworkModelCheckError
from networkml.network import NetworkClass, NetworkInstance
from networkml.specnetwork import SpecValidator
from gui.console import ConsoleDialog
from gui.scripteditor import ScriptEditorDialog
from gui.coordfinderwidget import CoordFinderWidget
from gui.solvercontroller import SolverControllerDialog
from gui.visualizer import GCVisualizerDialog
from gui.postscreen import PostScreenDialog
from graphcore.settings import GraphCoreSettings
from graphcore.graphicsscene import GraphCoreScene
from graphcore.graphicsview import GraphCoreView
from graphcore.reporter import GraphCoreReporter
from graphcore.script import GraphCoreScript
from graphcore.script_worker import GCScriptWorker, GraphCoreThreadSignal
import os
from graphcore.solver import GraphCoreGenericSolver
from gui.geomserializable import GeometrySerializer


# GraphCore's editor application main window class
class GraphCoreEditorMainWindow(QMainWindow, GeometrySerializer):
    # initializer
    def __init__(self, ui: Ui_MainWindow, settings: GraphCoreSettings, shell: GraphCoreShell,
                 handler: GraphCoreContextHandler, async_handler: GraphCoreAsyncContextHandler):
        super().__init__(parent=None, serialize_position=None, serialize_size=None)
        self._settings = settings
        self._shell = shell
        self._handler = handler
        self._async_handler = async_handler
        self._ui = ui
        self.ui.setupUi(self)
        self.ui.tabWidget.clear()
        self._coord_finder = None
        self._console = None
        self._script_editor = None
        self._solver_controller = None
        self._visualizer = None
        self._post_screen = None
        self._scene = None
        self._serializers = []
        self._reporter = GraphCoreReporter(lambda x: self.ui.messages.append(str(x)))
        self._copy_buf = {"nodes": {}, "edges": {}, "groups": {}}
        self._script_worker = None
        self._script_thread = None
        self.install_shell_actions()

    @property
    def script_handler(self) -> GCScriptWorker:
        return self._script_worker

    @property
    def script_worker(self) -> GCScriptWorker:
        return self._script_worker

    @property
    def script_thread(self) -> QThread:
        return self._script_thread

    def construct_script_handler(self):
        # print("construct_script_handler")
        self._script_handler = GraphCoreScript(self.handler, self.reporter)
        self._script_thread = QThread()
        self._script_worker = GCScriptWorker(self, self.script_thread)
        self.script_worker.main_thread_command.connect(self.process_thread_request)
        self.script_worker.moveToThread(self.script_thread)
        self.script_thread.started.connect(self.script_worker.run)
        self.script_worker.finished.connect(self.script_thread.quit)
        #self.script_worker.finished.connect(self.script_worker.deleteLater)
        #self.script_thread.finished.connect(self.script_thread.deleteLater)
        # self._worker.progress.connect(self.reportProgress)
        #self._thread.start()

    def process_thread_request(self, sig: GraphCoreThreadSignal):
        func = sig.func
        args = sig.args
        data = sig.data
        func(data)

    @property
    def node_copy_buf(self):
        return self._copy_buf["nodes"]

    @property
    def edge_copy_buf(self):
        return self._copy_buf["edges"]

    @property
    def group_copy_buf(self):
        return self._copy_buf["groups"]

    def clear_copy_buf(self):
        self._copy_buf = {"nodes": {}, "edges": {}, "groups": {}}

    @property
    def is_copy_buf_empty(self):
        return len(self.node_copy_buf) == 0 and len(self.edge_copy_buf) == 0 and len(self.group_copy_buf) == 0

    @property
    def is_grouping_enabled(self):
        return len(self.handler.selected_nodes) + len(self.handler.selected_edges) > 1

    @property
    def is_ungrouping_enabled(self):
        return len(self.handler.selected_groups) > 0

    @property
    def selected_elements(self) -> tuple:
        return tuple(self.handler.selected_elements)

    @property
    def reporter(self) -> GraphCoreReporter:
        return self._reporter

    @property
    def settings(self) -> GraphCoreSettings:
        return self._settings

    @property
    def shell(self) -> GraphCoreShell:
        return self._shell

    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @property
    def async_handler(self) -> GraphCoreAsyncContextHandler:
        return self._async_handler

    @property
    def ui(self) -> Ui_MainWindow:
        return self._ui

    @property
    def coord_finder(self) -> CoordFinderWidget:
        return self._coord_finder

    @coord_finder.setter
    def coord_finder(self, finder):
        self._coord_finder = finder

    @property
    def console(self) -> ConsoleDialog:
        return self._console

    @console.setter
    def console(self, _console):
        self._console = _console

    @property
    def script_editor(self) -> ScriptEditorDialog:
        return self._script_editor

    @script_editor.setter
    def script_editor(self, editor):
        self._script_editor = editor

    @property
    def solver_controller(self) -> SolverControllerDialog:
        return self._solver_controller

    @solver_controller.setter
    def solver_controller(self, solver_controller: SolverControllerDialog):
        self._solver_controller = solver_controller

    @property
    def visualizer(self) -> GCVisualizerDialog:
        return self._visualizer

    @visualizer.setter
    def visualizer(self, value: GCVisualizerDialog):
        self._visualizer = value

    @property
    def post_screen(self) -> PostScreenDialog:
        return self._post_screen

    @post_screen.setter
    def post_screen(self, value: PostScreenDialog):
        self._post_screen = value

    @property
    def serializers(self) -> list:
        return self._serializers

    @property
    def scene(self) -> GraphCoreScene:
        return self.handler.extras['scene']
        # return self._scene

    # @scene.setter
    # def scene(self, _scene: GraphCoreScene):
    #     self._scene = _scene
    #     # self.ui.graphicsView.setScene(_scene)

    @property
    def element_to_item(self):
        return self.handler.extras['element_to_item']

    # def do_shell_action(self, sig: GraphCoreThreadSignal):
    #     if sig.signal == GraphCoreContextHandler.NodeUpdated:
    #         self.redraw_node_item(sig.data)
    #     elif sig.signal == GraphCoreContextHandler.EdgeUpdated:
    #         self.redraw_edge_item(sig.data)
    #
    # # command slot from thread
    # def install_drawing_slot(self):
    #     from graphcore.script_worker import get_script_worker
    #     get_script_worker().main_window_command.connect(self.do_shell_action)

    # command interface from shell
    def install_shell_actions(self):
        self.shell.set_reflection(GraphCoreShell.HandlerNew, lambda x: self.handler_new(x[0], x[1]))
        self.shell.set_reflection(GraphCoreShell.HandlerChanged, lambda x: self.handler_changed(x[0], x[1]))
        self.shell.set_reflection(GraphCoreShell.HandlerPurged, lambda x: self.handler_purged())

    # command interface from handler
    def install_handler_actions(self):
        self.handler.set_reflection(GraphCoreContextHandler.NodeAdded, lambda x: self.new_node_item(x))
        self.handler.set_reflection(GraphCoreContextHandler.NodeUpdated, lambda x: self.redraw_node_item(x))
        self.handler.set_reflection(GraphCoreContextHandler.NodeRemoved, lambda x: self.remove_node_item(x))
        self.handler.set_reflection(GraphCoreContextHandler.EdgeAdded, lambda x: self.new_edge_item(x))
        self.handler.set_reflection(GraphCoreContextHandler.EdgeUpdated, lambda x: self.redraw_edge_item(x))
        self.handler.set_reflection(GraphCoreContextHandler.EdgeRemoved, lambda x: self.remove_edge_item(x))
        self.handler.set_reflection(GraphCoreContextHandler.ViewUpdated, lambda x: self.change_view(x[0], x[1], x[2], x[3]))
        self.handler.set_reflection(GraphCoreContextHandler.AllDeselected, lambda x: self.property_deselect_all())
        self.handler.set_reflection(GraphCoreContextHandler.NodeSelected, lambda x: self.select_node(x))
        self.handler.set_reflection(GraphCoreContextHandler.EdgeSelected, lambda x: self.select_edge(x))
        self.handler.set_reflection(GraphCoreContextHandler.ElementsSelected, lambda x: self.select_elements(x))
        self.handler.set_reflection(GraphCoreContextHandler.ElementsAddSelect, lambda x: self.add_select_elements(x))
        self.handler.set_reflection(GraphCoreContextHandler.ConstraintAdded, lambda x: self.constraint_add_to_widget(x))
        self.handler.set_reflection(GraphCoreContextHandler.ConstraintRemoved, lambda x: self.constraint_delete(x))
        # FIXME
        self.handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionAdded, lambda x: print(x))
        self.handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionUpdated, lambda x: print(x))
        self.handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionRemoved, lambda x: print(x))
        self.handler.set_reflection(GraphCoreContextHandler.UserScriptAdded, lambda x: self.user_script_add_to_widget(x))
        self.handler.set_reflection(GraphCoreContextHandler.UserScriptDeleted, lambda x: self.user_script_delete(x))
        self.handler.set_reflection(GraphCoreContextHandler.GroupCreated, lambda x: self.group_create(x))
        self.handler.set_reflection(GraphCoreContextHandler.GroupPurged, lambda x: self.group_purge(x))
        self.handler.set_reflection(GraphCoreContextHandler.GroupRemoved, lambda x: self.group_remove(x))

        self.async_handler.set_reflection(GraphCoreContextHandler.NodeAdded, lambda x: self.new_node_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.NodeUpdated, lambda x: self.redraw_node_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.NodeRemoved, lambda x: self.remove_node_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.EdgeAdded, lambda x: self.new_edge_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.EdgeUpdated, lambda x: self.redraw_edge_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.EdgeRemoved, lambda x: self.remove_edge_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.ViewUpdated, lambda x: self.change_view(x[0], x[1], x[2], x[3]))
        self.async_handler.set_reflection(GraphCoreContextHandler.AllDeselected, lambda x: self.property_deselect_all())
        self.async_handler.set_reflection(GraphCoreContextHandler.NodeSelected, lambda x: self.select_node(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.EdgeSelected, lambda u, v: self.select_edge((u, v)))
        self.async_handler.set_reflection(GraphCoreContextHandler.ElementsSelected, lambda x: self.select_elements(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.ElementsAddSelect, lambda x: self.add_select_elements(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.ConstraintAdded, lambda x: self.constraint_add_to_widget(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.ConstraintRemoved, lambda x: self.constraint_delete(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.UserScriptAdded, lambda x: self.user_script_add_to_widget(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.UserScriptDeleted, lambda x: self.user_script_delete(x))
        # FIXME
        self.async_handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionAdded, lambda x: print(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionUpdated, lambda x: print(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionRemoved, lambda x: print(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.GroupCreated, lambda x: self.group_create(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.GroupPurged, lambda x: self.group_purge(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.GroupRemoved, lambda x: self.group_remove(x))

    def item_to_element(self, i):
        for k in self.handler.extras["element_to_item"].keys():
            if i == self.handler.extras["element_to_item"][k]:
                return k
        return None

    def handler_new(self, handler, async_handler):
        scene = GraphCoreScene()
        scene.handler = handler
        view = GraphCoreView()  # QGraphicsView(scene)
        view.setScene(scene)
        handler.extras['element_to_item'] = {}
        handler.extras['edge_creating'] = False
        handler.extras['temp_coords'] = None
        self.ui.tabWidget.addTab(view, 'untitled')
        self.ui.tabWidget.setCurrentWidget(view)
        view.setBackgroundBrush(QBrush(QPixmap("images/grid-square.png")))
        scene.setSceneRect(0, 0, view.width(), view.height())
        scene.shell = self.shell
        scene.settings = self.settings
        handler.extras['scene'] = scene
        view.set_main_window(self)
        view.set_shell(self.shell)
        view.setRubberBandSelectionMode(Qt.ContainsItemBoundingRect)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        view.setContextMenuPolicy(Qt.CustomContextMenu)
        view.customContextMenuRequested['QPoint'].connect(self.command_show_context_menu)
        self.handler_changed(handler, async_handler)
        self.install_handler_actions()
        self.handler.loaded()
        view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        index = self.ui.tabWidget.currentIndex()
        if self.handler.context.filename is None:
            self.ui.tabWidget.tabBar().setTabText(index, "untitled")
        else:
            name = os.path.basename(self.handler.context.filename)
            self.ui.tabWidget.tabBar().setTabText(index, name)

    def handler_changed(self, handler, async_handler):
        # self.print("handler_changed")
        self.property_clear()
        self.constraints_clear()
        self.user_scripts_clear()
        self._handler = handler
        self._async_handler = async_handler
        self.handler.set_script_handler(self.script_handler)
        self.update_node_list()
        self.update_edge_list()
        self.constraint_add_all_to_widget()
        self.user_scripts_add_all_to_widget()

    def handler_purged(self):
        for e in self.element_to_item.keys():
            item = self.element_to_item[e]
            self.scene.removeItem(item)
        self.property_clear()
        self.constraints_clear()
        self.user_scripts_clear()
        self.element_to_item.clear()
        self.ui.tabWidget.removeTab(self.ui.tabWidget.currentIndex())
        self._scene = None
        self._handler = None
        self._async_handler = None

    # create node item
    def new_node_item(self, n):
        attr = self.handler.context.nodes[n]
        if attr['shape'] in ('circle', 'doublecircle'):
            item = GraphCoreCircleNodeItem(n, self.handler.context, self.handler)
        elif attr['shape'] in ('box', 'doublebox'):
            item = GraphCoreRectNodeItem(n, self.handler.context, self.handler)
        else:
            self.print("Unsupported shape:{}. force to circle".format(attr['shape']))
            item = GraphCoreCircleNodeItem(n, self.handler.context, self.handler)
        #item = GCCustomNodeItem(n, self.handler.context, self.handler)
        self.scene.addItem(item)
        self.element_to_item[n] = item
        self.update_node_list()
        self.update_edge_list()
        self.set_modified(True)

    # redraw node item
    def redraw_node_item(self, n):
        self.element_to_item[n].redraw()
        edges = self.handler.collect_edges(n, node_is_source=True, node_is_target=True)
        for e in edges:
            item = self.element_to_item[e]
            item.redraw()
        self.update_node_list()
        self.set_modified(True)

    def update_node_item(self, n):
        self.redraw_node_item(n)

    # delete node item
    def remove_node_item(self, n):
        item = self.element_to_item[n]
        self.scene.removeItem(item)
        self.element_to_item.pop(n)
        self.update_node_list()
        self.update_edge_list()
        self.set_modified(True)

    # create node item
    def new_edge_item(self, e):
        attr = self.handler.context.edges[e[0], e[1]]
        item = GraphCoreEdgeItem(e[0], e[1], self.handler.context, self.handler)
        self.scene.addItem(item)
        self.element_to_item[e] = item
        self.update_edge_list()
        self.set_modified(True)

    # redraw edge item
    def redraw_edge_item(self, e):
        self.element_to_item[e].redraw()
        self.update_node_list()
        self.update_edge_list()
        self.set_modified(True)

    def update_edge_item(self, e):
        self.redraw_edge_item(e)

    # delete edge item
    def remove_edge_item(self, e):
        item = self.element_to_item[e]
        self.scene.removeItem(item)
        self.element_to_item.pop(e)
        self.update_edge_list()
        self.set_modified(True)

    def new_item_group(self, gid):
        SG = self.handler.context.G.graph["groups"][gid]
        g = GCItemGroup(self.handler.context, self.handler)
        for n in SG.nodes:
            node = self.element_to_item[n]
            node.setSelected(False)
            g.addToGroup(node)
        for e in SG.edges:
            edge = self.element_to_item[e]
            edge.setSelected(False)
            g.addToGroup(edge)
        self.scene.addItem(g)
        self.element_to_item[gid] = g
        self.set_modified(True)

    def remove_item_group(self, gid):
        self.print("remove_item_group: {}".format(gid))
        g: QGraphicsItemGroup = self.element_to_item[gid]
        self.element_to_item.pop(gid)
        for c in g.childItems():
            g.removeFromGroup(c)
            c.setSelected(False)
        self.scene.destroyItemGroup(g)

    # change view
    def change_view(self, x, y, w, h):
        self.scene.setSceneRect(x, y, w, h)
        view: QGraphicsView = self.ui.tabWidget.currentWidget()
        view.setSceneRect(x, y, w, h)
        self.ui.actionSave.setEnabled(True)

    # modified action
    def set_modified(self, flag: bool):
        self.ui.actionSave.setEnabled(flag)
        index = self.ui.tabWidget.currentIndex()
        text = self.ui.tabWidget.tabBar().tabText(index)
        if text[0:1] != "*":
            text = "*" + text
            self.ui.tabWidget.tabBar().setTabText(index, text)

    # View/Scene / Script Editor
    def command_script_editor(self):
        self.script_editor.setModal(True)
        self.script_editor.set_handler_pair(self.handler, self.async_handler)
        self.script_editor.exec_()

    # check if edge creating
    def edge_creating(self):
        return self.handler.extras['edge_creating']

    # set edge creating or not
    def set_edge_creating(self, flag):
        self.handler.extras['edge_creating'] = flag

    # get coords temporary saved
    def temp_coords(self):
        return self.handler.extras['temp_coords']

    # set coords for temporary saving
    def set_temp_coords(self, coords):
        self.handler.extras['temp_coords'] = coords

    # print message
    def print(self, *args) -> None:
        text = " ".join([str(_) for _ in args])
        self.ui.messages.append(text)

    # Label menu command
    # setup label menu
    def setup_label_menu(self):
        sets = self._settings.setting('default-node-attrs')
        self.setup_node_label_menu(sets.keys())
        sets = self._settings.setting('default-edge-attrs')
        self.setup_edge_label_menu(sets.keys())

    # setup node label menu
    def setup_node_label_menu(self, item_names):
        menu_label = self.ui.menuLabel
        for name in item_names:
            action = QAction("Node's " + name)
            menu_label.addAction(action)
            action.triggered.connect(lambda: self.command_set_node_label(name))

    # setup node label menu
    def setup_edge_label_menu(self, item_names):
        menu_label = self.ui.menuLabel
        for name in item_names:
            action = QAction("Edge's " + name)
            menu_label.addAction(action)
            action.triggered.connect(lambda: self.command_set_edge_label(name))

    # View/Scene / Console command
    def command_console(self):
        # if self._script_worker is None:
        #     self.construct_script_handler()
        self.console.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.console.setModal(False)
        # self.console.setModal(True)
        # self.script_handler.handler = self.handler
        # self.console.set_handler(self.script_handler)
        # self.console.exec_()
        self.console.show()
        self.console.raise_()

    # node label change command
    def command_set_node_label(self, attr_name):
        for node in self.handler.context.nodes:
            attr = self.handler.context.nodes[node]
            attr["label"] = attr[attr_name]
            item = self.element_to_item[node]
            item.redraw()
        self.handler.context.dirty = True

    # edge label change command
    def command_set_edge_label(self, attr_name):
        for edge in self.handler.context.edges:
            attr = self.handler.context.edges[edge[0], edge[1]]
            attr["label"] = attr[attr_name]
            item = self.element_to_item[edge]
            item.redraw()
        self.handler.context.dirty = True

    # File / New command
    def command_new_model(self) -> None:
        try:
            self.shell.new_handler()
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    # Hidden Commands / Change Current command
    def command_change_current(self, index) -> None:
        try:
            view: QGraphicsView = self.ui.tabWidget.currentWidget()
            if isinstance(view, QGraphicsView):
                scene: GraphCoreScene = view.scene()
                # self.shell.handler.deselect_all()
                self.shell.set_current_handler(scene.handler)
                self.script_handler.handler = self.handler
                self.console.set_handler(self.script_handler)
        except Exception as ex:
            self.print(traceback.format_exc())

    # File / Open command
    def command_open(self) -> None:
        try:
            # self.handler.deselect_all()
            dialog_title = "Open Model File"
            directory = "."
            file_masks = "GraphCore graph file (*.gcm *.gcmx *.yaml)"
            filename = QFileDialog.getOpenFileName(self, dialog_title, directory, file_masks)
            if filename[0] is not None and filename[0] != "":
                if self.shell.opened(filename[0]):
                    self.shell.set_current_handler_by_name(filename[0])
                    return
                self.shell.open(filename[0])
                self.update_node_list()
                self.update_edge_list()

        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # File / Close command
    def command_close(self) -> bool:
        try:
            # save, if dirty
            if self.handler.context.dirty:
                filename = self.handler.context.filename
                if self.handler.context.filename is None:
                    dialog_title = "Save Model File"
                    directory = "."
                    file_masks = "GraphCore graph file (*.gcm *.gcmx *.yaml)"
                    filename = QFileDialog.getSaveFileName(self, dialog_title, directory, file_masks)
                    if filename[0] is not None and len(filename[0]) != 0:
                        filename = filename[0]
                    else:
                        return False
                self.handler.save(filename=filename)
            # deallocate all graph components
            self.ui.nodeTableWidget.clear()
            self.ui.edgeTableWidget.clear()
            self.shell.purge_handler(self.handler)
            return True
        except Exception as ex:
            self.print(traceback.format_exc())
            return False
        finally:
            self.set_command_enable()

    # File / Save command
    def command_save(self) -> None:
        try:
            # save, if dirty
            if self.handler.context.dirty:
                filename = self.handler.context.filename
                if self.handler.context.filename is None:
                    dialog_title = "Save Model File"
                    directory = "."
                    file_masks = "GraphCore graph file (*.gcm *.gcmx *.yaml)"
                    filename = QFileDialog.getSaveFileName(self, dialog_title, directory, file_masks)
                    if filename[0] is not None and len(filename[0]) != 0:
                        filename = filename[0]
                    else:
                        return
                self.handler.save(filename=filename)
                self.handler.context.dirty = False
                name = os.path.basename(filename)
                index = self.ui.tabWidget.currentIndex()
                self.ui.tabWidget.tabBar().setTabText(index, name)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # File / SaveAs command
    def command_saveAs(self) -> None:
        try:
            dialog_title = "Save Model File"
            directory = "."
            file_masks = "GraphCore graph file (*.gcm *.gcmx *.yaml)"
            filename = QFileDialog.getSaveFileName(self, dialog_title, directory, file_masks)
            if filename[0] is not None and len(filename[0]) != 0:
                filename = filename[0]
            else:
                return
            self.handler.save(filename=filename)
            name = os.path.basename(filename)
            index = self.ui.tabWidget.currentIndex()
            self.ui.tabWidget.tabBar().setTabText(index, name)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()
        # self.print('command_save_as')

    def update_node_list(self):
        self.ui.nodeTableWidget.clear()
        self.ui.nodeTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('Id'))
        self.ui.nodeTableWidget.setHorizontalHeaderItem(1, QTableWidgetItem('Label'))
        self.ui.nodeTableWidget.setHorizontalHeaderItem(2, QTableWidgetItem('Caption'))
        self.ui.nodeTableWidget.setHorizontalHeaderItem(3, QTableWidgetItem('Description'))
        self.ui.nodeTableWidget.setRowCount(len(self.handler.context.G.nodes))
        for i, n in enumerate(self.handler.context.G.nodes):
            id = n
            label = self.handler.context.G.nodes[n]['label']
            caption = self.handler.context.G.nodes[n]['caption']
            description = self.handler.context.G.nodes[n]['description']
            self.ui.nodeTableWidget.setItem(i, 0, QTableWidgetItem(id))
            self.ui.nodeTableWidget.setItem(i, 1, QTableWidgetItem(label))
            self.ui.nodeTableWidget.setItem(i, 2, QTableWidgetItem(caption))
            self.ui.nodeTableWidget.setItem(i, 3, QTableWidgetItem(description))

    def update_edge_list(self):
        self.ui.edgeTableWidget.clear()
        self.ui.edgeTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('Id'))
        self.ui.edgeTableWidget.setHorizontalHeaderItem(1, QTableWidgetItem('Label'))
        self.ui.edgeTableWidget.setHorizontalHeaderItem(2, QTableWidgetItem('Caption'))
        self.ui.edgeTableWidget.setHorizontalHeaderItem(3, QTableWidgetItem('Description'))
        self.ui.edgeTableWidget.setRowCount(len(self.handler.context.G.edges))
        for i, e in enumerate(self.handler.context.G.edges):
            id = "({0}, {1})".format(e[0], e[1])
            label = self.handler.context.G.edges[e[0], e[1]]['label']
            caption = self.handler.context.G.edges[e[0], e[1]]['caption']
            description = self.handler.context.G.edges[e[0], e[1]]['description']
            self.ui.edgeTableWidget.setItem(i, 0, QTableWidgetItem(id))
            self.ui.edgeTableWidget.setItem(i, 1, QTableWidgetItem(label))
            self.ui.edgeTableWidget.setItem(i, 2, QTableWidgetItem(caption))
            self.ui.edgeTableWidget.setItem(i, 3, QTableWidgetItem(description))

    def command_new_node(self, x=None, y=None, node_type=None):
        try:
            self.print(f'command_new_node({x}, {y}, {node_type})')
            if x is None or y is None:
                rect = self.scene.sceneRect()
                x = rect.x() + rect.width() / 2
                y = rect.y() + rect.height() / 2
            enabled_node_types = self._settings.setting("enabled-node-types")
            if node_type is None:
                node_type = enabled_node_types[0]
            attr = {}
            default_settings = self._settings.setting("default-node-attrs")[node_type]
            for k in default_settings.keys():
                attr[k] = default_settings[k]['value']
            attr['x'] = x
            attr['y'] = y
            if node_type is not None:
                attr['type'] = node_type
            self.handler.new_node(attr)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # create edge item
    def create_edge_item(self, e, edge_type=None):
        self.handler.add_edge(e[0], e[1])
        enabled_edge_types = self._settings.setting("enabled-edge-types")
        if edge_type is None:
            edge_type = enabled_edge_types[0]
        attrs = self.handler.context.edges[e[0], e[1]]
        default_settings = self._settings.setting('default-edge-attrs')[edge_type]
        for k in default_settings.keys():
            if k not in attrs.keys():
                attrs[k] = default_settings[k]['value']
        self.new_edge_item(e)

    # File / Import command
    def command_import(self) -> None:
        self.print('command_import')
        self.setCommandEnabilities()

    # File / Export command
    def command_export(self) -> None:
        self.print('command_export')
        self.setCommandEnabilities()

    # File / Quit command
    def command_quit(self):
        try:
            self.print('command_quit')
            while True:
                tab_index = self.ui.tabWidget.currentIndex()
                if tab_index is None or tab_index < 0:
                    break
                self.ui.tabWidget.removeTab(tab_index)
            # for ctx in self.shell.contexts:
            #     self.shell.current_context = ctx
            #     if not self.command_close():
            #         return False
            self.serialize()
            self.close()
        except Exception as ex:
            print("GraphCore bug!")
            self.print(traceback.format_exc())
        finally:
            pass

    # fit graph to scene
    def command_fit_to_scene(self):
        try:
            xmin = None
            ymin = None
            xmax = None
            ymax = None
            for n in self.handler.context.nodes:
                attr = self.handler.context.nodes[n]
                if xmin is None:
                    xmin = attr['x']
                    xmax = attr['x']
                elif ymin is None:
                    ymin = attr['y']
                    ymax = attr['y']
                else:
                    if attr['x'] < xmin:
                        xmin = attr['x']
                    if xmax < attr['x']:
                        xmax = attr['x']
                    if attr['y'] < ymin:
                        ymin = attr['y']
                    if ymax < attr['y']:
                        ymax = attr['y']
            if xmin is None:
                # do nothing
                return
            margin = 50
            xmin -= margin
            xmax += margin
            ymin -= margin
            ymax += margin
            attrs = self.handler.context.graph
            attrs['x'] = xmin
            attrs['y'] = ymin
            attrs['w'] = xmax - xmin
            attrs['h'] = ymax - ymin
            self.handler.change_view(xmin, ymin, xmax - xmin, ymax - ymin)
            view: QGraphicsView = self.ui.tabWidget.currentWidget()
            view.scale(1, 1)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    def select_elements(self, es):
        self.command_deselect_all()
        self.property_clear()
        for e in es:
            item = self.element_to_item[e]
            item.select()
        # self.set_selected_elements(es)
        self.set_command_enable()

    # deselect all selected objects
    def command_deselect_all(self) -> None:
        try:
            self.handler.deselect_all()
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    def add_select_elements(self, es):
        for e in es:
            item = self.element_to_item[e]
            item.select()
        self.property_clear()

    def add_select_node(self, n):
        item: GraphCoreItemInterface = self.element_to_item[n]
        item.select()
        self.property_clear()

    def select_node(self, n):
        self.command_deselect_all()
        item: GraphCoreItemInterface = self.element_to_item[n]
        item.select()
        self.property_select_node(n)
        self.ui.editorTabWidget.setCurrentIndex(0)

    def add_select_edge(self, e):
        item: GraphCoreItemInterface = self.element_to_item[e]
        item.select()
        self.property_clear()

    def select_edge(self, n):
        self.command_deselect_all()
        item: GraphCoreItemInterface = self.element_to_item[n]
        item.select()
        self.property_select_edge(n)
        self.ui.editorTabWidget.setCurrentIndex(0)

    # selected node
    def command_select_node(self, n) -> None:
        try:
            self.print("command_select_node")
            self.handler.select_node(n)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    # deselect selected node
    def command_deselect_node(self, n) -> None:
        try:
            self.handler.deselect_node(n)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # move node by (dx, dy)
    def command_move_node_by(self, n, dx, dy) -> None:
        try:
            edges = self.handler.collect_edges(n, node_is_source=True, node_is_target=True)
            self.handler.move_node_by(n, dx, dy)
            for e in edges:
                item = self.element_to_item[e]
                item.redraw()
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # remove node
    def command_remove_node(self, n) -> None:
        try:
            # self.print('command_remove_node({})'.format(n))
            edges = self.handler.collect_edges(n, node_is_source=True, node_is_target=True)
            for e in edges:
                self.handler.remove_edge(e[0], e[1])
            self.handler.remove_node(n)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # change node
    def command_change_node(self, n) -> None:
        try:
            self.print("command_change_node({})".format(n))
            self.handler.update_node(n)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # change node attr
    def command_change_node_attr(self, n, a, v):
        try:
            print("command_change_node_attr({}, {}, {}".format(n, a, v))
            self.handler.change_node_attr(n, a, v)
            self.handler.update_node(n)
            edges = self.handler.collect_edges(n, node_is_source=True, node_is_target=True)
            for e in edges:
                self.update_edge(e[0], e[1])
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    def command_select_group(self, g) -> None:
        try:
            self.print("command_select_group {}".format(g))
            self.handler.select_group(g)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    # select edge
    def command_select_edge(self, e) -> None:
        try:
            self.print('command_select_edge {}'.format(e))
            self.handler.select_edge(e[0], e[1])
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # deselect edge
    def command_deselect_edge(self, e) -> None:
        try:
            self.print('command_deselect_edge')
            self.handler.deselect_edge(e[0], e[1])
            pass
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # add new edge
    def command_add_edge(self, u, v, edge_type=None) -> None:
        try:
            self.print('command_add_edge')
            attrs = {}
            default_settings = self.settings.setting("default_edge_attrs")
            for k in default_settings.keys():
                attrs[k] = default_settings[k]
            if edge_type is not None:
                attrs['type'] = edge_type
            self.handler.add_edge(u, v, attrs)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # change edge
    def command_update_edge(self, e) -> None:
        try:
            self.print('command_change_edge_attr')
            self.handler.update_edge(e[0], e[1])
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # change edge
    def command_change_edge_attr(self, e, attr_name, value) -> None:
        try:
            self.print('command_change_edge_attr')
            self.handler.change_edge_attr(e[0], e[1], attr_name, value)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # remove edge
    def command_remove_edge(self, e) -> None:
        try:
            # self.print('command_remove_edge')
            self.handler.remove_edge(e[0], e[1])
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # Models menu section
    # Models / Layout Manager
    def command_layout_manager(self):
        self.coord_finder.show()

    # Models / Model Check
    def command_model_check(self):
        try:
            ui: Ui_MainWindow = self.ui
            constraints = self.handler.context.constraints
            meta = NetworkClass(None, "GCConstraintChecker")
            clazz_sig = "{}[{}]".format("NetworkML", 1)
            data = nx.node_link_data(self.handler.context.G)
            G = nx.node_link_graph(data)
            embedded = [("G", G)]
            args = ()
            meta.set_running(True)
            clazz = meta(meta, (clazz_sig, embedded, args))
            sig = "{}.{}".format(clazz.signature, clazz.next_instance_id)
            initializer_args = ()
            embedded = ()
            clazz.set_running(True)
            toplevel: NetworkInstance = clazz(clazz, (sig, embedded, initializer_args))
            toplevel.set_stack_enable(True)
            # validator/evaluator
            validator = SpecValidator(owner=toplevel)
            toplevel.set_validator(validator)
            toplevel.set_running(True)
            parser = GCConstraintParser(toplevel, reporter=self.shell.default_reporter)
            has_error = False
            ui.errorWidget.setRowCount(0)
            for cid in constraints.keys():
                eqn = constraints[cid]['equation']
                # desc = constraints[cid]['description']
                enabled = constraints[cid]['enabled']
                if not enabled:
                    continue
                r = parser.parse(eqn)
                rtn = r(toplevel)
                if not rtn:
                    ui.errorWidget.setRowCount(ui.errorWidget.rowCount() + 1)
                    item = QTableWidgetItem("Constraint Violation: {}: {}".format(cid, eqn))
                    ui.errorWidget.setItem(ui.errorWidget.rowCount() - 1, 0, item)
                    has_error = True
            return has_error
        except Exception as ex:
            self.print(traceback.format_exc())

    # Models / Add Constraint
    def command_add_constraint(self):
        self.handler.new_constraint()

    # Models / Delete Constraint
    def command_delete_constraint(self):
        # selected constraints.
        rows = []
        for i in self.ui.constraintWidget.selectedIndexes():
            if not i.row() in rows:
                rows.append(i.row())
        rows.sort(reverse=True)
        for r in rows:
            cid = self.ui.constraintWidget.item(r, 1).text()
            self.handler.remove_constraint(cid)

    def error_message_init(self):
        error_widget = self.ui.errorWidget
        error_widget.setColumnCount(1)
        error_widget.setHorizontalHeaderLabels(['Error Messages'])

    def print_error(self, err):
        error_widget = self.ui.errorWidget
        i = error_widget.rowCount()
        error_widget.setRowCount(i+1)
        item = QTableWidgetItem(err)
        error_widget.setItem(i, 0, item)

    # Labels menu
    # Labels/Node Id
    def command_set_node_id_to_label(self):
        for n in self.handler.context.nodes:
            self.handler.change_node_attr(n, 'label', "v{}".format(n))

    # Labels/Node complexity
    def command_set_node_complexity_to_label(self):
        for n in self.handler.context.nodes:
            attr = self.handler.context.nodes[n]
            self.handler.change_node_attr(n, 'label', str(attr['complexity']))

    # Labels/Node caption
    def command_set_node_caption_to_label(self):
        for n in self.handler.context.nodes:
            attr = self.handler.context.nodes[n]
            self.handler.change_node_attr(n, 'label', str(attr['caption']))

    # Labels/Edge Id
    def command_set_edge_id_to_label(self):
        for e in self.handler.context.edges:
            self.handler.change_edge_attr(e[0], e[1], 'label', "e({},{})".format(e[0], e[1]))

    # Labels/Edge distance
    def command_set_edge_distance_to_label(self):
        for e in self.handler.context.edges:
            attr = self.handler.context.edges[e[0], e[1]]
            self.handler.change_edge_attr(e[0], e[1], 'label', str(attr['distance']))

    # Labels/Edge caption
    def command_set_edge_caption_to_label(self):
        for e in self.handler.context.edges:
            attr = self.handler.context.edges[e[0], e[1]]
            self.handler.change_edge_attr(e[0], e[1], 'label', attr['caption'])

    # Labels/Node Tooltips
    def command_change_node_tooltips(self):
        for n in self.handler.context.nodes:
            attr = self.handler.context.nodes[n]
            item = self.element_to_item[n]
            if item.toolTip() is None or item.toolTip() == "":
                item.setToolTip(attr['description'])
            else:
                item.setToolTip("")
            item.redraw()
        pass

    # Labels/Edge Tooltips
    def command_change_edge_tooltips(self):
        for e in self.handler.context.edges:
            attr = self.handler.context.edges[e[0], e[1]]
            item: GraphCoreEdgeItem = self.graphElemToItem(e)
            if item.toolTip() is None or item.toolTip() == "":
                item.setToolTip(attr['description'])
            else:
                item.setToolTip("")
            item.redraw()
        pass

    def to_graph_element_item(self, item: QGraphicsItem):
        if isinstance(item, GraphCoreNodeItemInterface):
            return item
        elif isinstance(item, GraphCoreEdgeItem):
            return item
        else:
            scene: QGraphicsScene = self.scene
            for i in scene.items():
                if isinstance(i, GraphCoreNodeItemInterface) or isinstance(i, GraphCoreEdgeItem):
                    for c in i.childItems():
                        if c == item:
                            return i
        return None

    def command_show_context_menu(self, p):
        try:
            view: GraphCoreView = self.ui.tabWidget.currentWidget()
            global_pos = view.mapToGlobal(p)
            scene_pos = view.mapToScene(p)
            # scene_pos = view.mapToScene(int(p.x()), int(p.y()))
            # self.print("context menu at view pos:{}, scene pos:{}, global pos:{}".format(p, scene_pos, global_pos))
            items = view.select_elements(p.x(), p.y(), 4, 4, Qt.IntersectsItemShape)
            if len(items) == 0:
                item = None
            else:
                item = self.element_to_item[items[0]]
            #item = view.itemAt(p)
            #item = self.to_graph_element_item(item)
            if item is not None:
                menu = QMenu(view)
                self.command_deselect_all()
                # Property menu
                if isinstance(item, GraphCoreNodeItemInterface):
                    menu.addAction("Property").triggered.connect(lambda: self.command_select_node(item.node))
                elif isinstance(item, GraphCoreEdgeItem):
                    menu.addAction("Property").triggered.connect(lambda: self.command_select_edge((item.u, item.v)))
                # New Edge menu
                if isinstance(item, GraphCoreNodeItemInterface):
                    item.select()
                    enabled_edge_types = self.settings.setting('enabled-edge-types')
                    menu_node = menu.addMenu("New Edge")

                    def new_edge_call(i, t):
                        return lambda: self.popup_menu_do_begin_edge(i, t)

                    for t in enabled_edge_types:
                        action = menu_node.addAction(t)
                        action.triggered.connect(new_edge_call(item.node, t))
                menu.addAction("Remove").triggered.connect(lambda: self.popup_menu_do_remove(item))
                menu.popup(global_pos)
            else:
                menu = QMenu(view)
                enabled_node_types = self.settings.setting('enabled-node-types')
                menu_node = menu.addMenu("New Node")

                def new_node_call(x, y, t):
                    return lambda: self.command_new_node(x, y, t)

                for t in enabled_node_types:
                    action = menu_node.addAction(t)
                    action.setData([scene_pos.x(), scene_pos.y(), t])
                    action.triggered.connect(new_node_call(scene_pos.x(), scene_pos.y(), t))
                menu.popup(global_pos)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # begin edge
    def popup_menu_do_begin_edge(self, source, edge_type):
        # self.print("popup_menu_do_begin_edge({})".format(source))
        s = self.handler.context.nodes[source]
        self.command_deselect_all()
        sx, sy, w = s['x'], s['y'], s['w']
        # dx, dy = s['x'], s['y']
        arrow_line = QGraphicsPolygonItem()
        arrow_line.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.scene.addItem(arrow_line)
        self.set_temp_coords((source, sx, sy, 0, arrow_line, edge_type))
        self.set_edge_creating(True)

    def popup_menu_do_remove(self, item):
        # self.print("popup_menu_do_remove({})".format(item))
        if isinstance(item, GraphCoreNodeItemInterface):
            self.command_remove_node(item.node)
        elif isinstance(item, GraphCoreEdgeItem):
            self.command_remove_edge((item.u, item.v))

    def check_if_edge_creation_mode(self):
        return self._edge_creating

    def set_command_enable(self):
        # File menu
        self.ui.actionNew.setEnabled(True)
        self.ui.actionOpen.setEnabled(True)
        self.ui.actionClose.setEnabled(self.ui.tabWidget.currentIndex() >= 0)
        if self.handler is not None and self.handler.context.dirty:
            enabled = True
        else:
            enabled = False
        self.ui.actionSave.setEnabled(enabled)
        self.ui.actionSaveAs.setEnabled(True)
        # Edit menu
        if self.handler is not None and len(self.selected_elements) > 0:
            enabled = True
        else:
            enabled = False
        self.ui.actionCopy.setEnabled(enabled)
        self.ui.actionCut.setEnabled(enabled)
        if self.handler is not None and not self.is_copy_buf_empty:
            enabled = True
        else:
            enabled = False
        self.ui.actionPaste.setEnabled(enabled)
        if self.handler is not None and self.is_grouping_enabled:
            enabled = True
        else:
            enabled = False
        self.ui.actionGroup.setEnabled(enabled)
        if self.handler is not None and self.is_ungrouping_enabled:
            enabled = True
        else:
            enabled = False
        self.ui.actionUngroup.setEnabled(enabled)

    def setCommandEnabilities(self):
        self.set_command_enable()

    # Property sheet section
    # initializer
    def property_init(self):
        property_widget = self.ui.propertyWidget
        property_widget.setRowCount(0)
        property_widget.setColumnCount(3)
        property_widget.setHorizontalHeaderLabels(('property', 'property', 'value'))
        property_widget.setColumnHidden(0, True)

    def property_clear(self):
        self.ui.propertyWidget.setRowCount(0)

    # deselect_all
    def property_deselect_all(self):
        property_widget = self.ui.propertyWidget
        property_widget.setRowCount(0)
        for k in self.element_to_item.keys():
            item = self.element_to_item[k]
            item.deselect()
        self.set_command_enable()

    # select node
    def property_select_node(self, node):
        property_widget = self.ui.propertyWidget
        attrs = self.handler.context.nodes[node]
        default_node_attrs = self.settings.setting('default-node-attrs')
        _type = attrs['type']
        node_properties = self.settings.setting('default-node-attrs')[_type].keys()
        property_widget.setRowCount(0)
        attr_count = 0
        for i, k in enumerate(node_properties):
            if not default_node_attrs[_type][k]['visible']:
                continue
            # if not attrs[k]['visible']:
            #     continue
            attr_count += 1
            property_widget.setRowCount(attr_count)
            property_widget.setItem(attr_count - 1, 0, QTableWidgetItem(k))
            property_widget.setItem(attr_count - 1, 1, QTableWidgetItem(self.settings.setting('default-node-attrs')[_type][k]['caption']))
            editor = None
            t = default_node_attrs[_type][k]['type']
            if "list" in default_node_attrs[_type][k].keys():
                value_list = default_node_attrs[_type][k]['list']
                entries = []
                for idx, n in enumerate(value_list):
                    entries.append((n, n))  # FIXME
                editor = ComboBoxEditor(attrs[k], k, entries,
                                        apply=lambda x, y: self.handler.change_node_attr(node, x, y))
                editor.callback_enabled = True
            elif t == "str":
                editor = TextEditor(attrs[k], k, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
            elif t == "longtext":
                editor = LongTextEditor(attrs[k], k, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
            elif t == "int":
                #editor = IntEditor(attrs[k], k, int, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
                editor = SpinBoxEditor(attrs[k], k, int, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
            elif t == "float":
                #editor = FloatEditor(attrs[k], k, float, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
                editor = FloatSpinBoxEditor(attrs[k], k, float, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
                editor.setMinimum(default_node_attrs[_type][k]['min'])
                editor.setMaximum(default_node_attrs[_type][k]['max'])
                editor.setValue(attrs[k])
                #print(_type, k, attrs[k], t, default_node_attrs[_type][k]['min'], default_node_attrs[_type][k]['max'])
            elif t == "bool":
                editor = BoolEditor(attrs[k], k, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
            elif t == "equation":
                editor = EquationEditor(attrs[k], k, apply=lambda x,y:self.handler.change_node_attr(node,x,y))
            else:
                self.print("unsupported type:{}".format(t))
            property_widget.setCellWidget(attr_count - 1, 2, editor)

    # select edge
    def property_select_edge(self, edge):
        property_widget = self.ui.propertyWidget
        attrs = self.handler.context.edges[edge[0], edge[1]]
        default_edge_attrs = self.settings.setting('default-edge-attrs')
        _type = attrs['type']
        edge_properties = default_edge_attrs[_type].keys()
        property_widget.setRowCount(0)
        attr_count = 0
        for i, k in enumerate(edge_properties):
            if not default_edge_attrs[_type][k]['visible']:
                continue
            # if not attrs[k]['visible']:
            #     continue
            attr_count += 1
            property_widget.setRowCount(attr_count)
            property_widget.setItem(attr_count - 1, 0, QTableWidgetItem(k))
            property_widget.setItem(attr_count - 1, 1, QTableWidgetItem(self.settings.setting('default-edge-attrs')[_type][k]['caption']))
            editor = None
            t = default_edge_attrs[_type][k]['type']
            if "list" in default_edge_attrs[_type][k].keys():
                value_list = default_edge_attrs[_type][k]['list']
                entries = []
                for idx, n in enumerate(value_list):
                    entries.append((n, n))  # FIXME
                editor = ComboBoxEditor(attrs[k], k, entries,
                                        apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
                editor.callback_enabled = True
            elif t == "str":
                editor = TextEditor(attrs[k], k,
                                    apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
            elif t == "longtext":
                editor = LongTextEditor(attrs[k], k,
                                        apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
            elif t == "int":
                #editor = IntEditor(attrs[k], k, int,
                #                   apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
                editor = SpinBoxEditor(attrs[k], k, int,
                                       apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
            elif t == "float":
                #editor = FloatEditor(attrs[k], k, float,
                #                     apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
                editor = FloatSpinBoxEditor(attrs[k], k, float,
                                            apply = lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
                editor.setMinimum(default_edge_attrs[_type][k]['min'])
                editor.setMaximum(default_edge_attrs[_type][k]['max'])
                editor.setValue(attrs[k])
                #print(_type, k, attrs[k], t, default_edge_attrs[_type][k]['min'], default_edge_attrs[_type][k]['max'])
            elif t == "bool":
                editor = BoolEditor(attrs[k], k,
                                    apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
            elif t == "equation":
                editor = EquationEditor(attrs[k], k,
                                        apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
            else:
                self.print("unsupported type:{}".format(t))
            property_widget.setCellWidget(attr_count - 1, 2, editor)

    def system_constraints_init(self):
        header_labels = ('Enabled', 'Id', 'Constraint', 'Description')
        constraint_widget = self.ui.systemConstraintWidget
        constraint_widget.setColumnCount(4)
        constraint_widget.setHorizontalHeaderLabels(header_labels)
        constraint_widget.setColumnWidth(0, 20)
        constraint_widget.setColumnWidth(1, 20)
        constraints = self.settings.setting('system-constraints')
        constraint_widget.setRowCount(len(constraints.keys()))
        for i, k in enumerate(constraints.keys()):
            constraint = constraints[k]
            item = QTableWidgetItem(constraint['enabled'])
            if constraint['enabled']:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
            constraint_widget.setItem(i, 0, item)
            item = QTableWidgetItem(k)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
            constraint_widget.setItem(i, 1, item)
            item = QTableWidgetItem(constraint['equation'])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
            constraint_widget.setItem(i, 2, item)
            item = QTableWidgetItem(constraint['description'])
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
            constraint_widget.setItem(i, 3, item)

    def constraints_init(self):
        header_labels = ('Enabled', 'Id', 'Constraint', 'Description')
        constraint_widget = self.ui.constraintWidget
        constraint_widget.setRowCount(0)
        constraint_widget.setColumnCount(4)
        constraint_widget.setHorizontalHeaderLabels(header_labels)
        constraint_widget.setColumnWidth(0, 20)
        constraint_widget.setColumnWidth(1, 20)

    def constraints_clear(self):
        self.ui.constraintWidget.setRowCount(0)

    # Add all constraints to constraint_widget
    def constraint_add_all_to_widget(self):
        constraints = self.handler.context.constraints
        for c in constraints.keys():
            self.constraint_add_to_widget(c)

    # Check constraint syntax
    def constraint_check_equation(self, eq):
        meta = NetworkClass(None, "GCScriptClass")
        clazz_sig = "{}[{}]".format("NetworkML", 1)
        data = nx.node_link_data(self.handler.context.G)
        G = nx.node_link_graph(data)
        embedded = [("G", G)]
        args = ()
        meta.set_running(True)
        clazz = meta(meta, (clazz_sig, embedded, args))
        sig = "{}.{}".format(clazz.signature, clazz.next_instance_id)
        initializer_args = ()
        embedded = ()
        clazz.set_running(True)
        toplevel: NetworkInstance = clazz(clazz, (sig, embedded, initializer_args))
        toplevel.set_stack_enable(True)
        # validator/evaluator
        validator = SpecValidator(owner=toplevel)
        toplevel.set_validator(validator)
        parser = GCConstraintParser(toplevel, reporter=self.shell.default_reporter)
        # parser = GCConstraintParser(toplevel, reporter=self.reporter)
        try:
            parser.parse(eq)
            return True
        except NetworkParserError as ex:
            # self.reporter.report("Syntax error:")
            self.reporter.report(ex.detail())
            return False
        except Exception as ex:
            self.reporter.report(traceback.format_exc())
            return False

    # Add constraint to constraint_widget
    def constraint_add_to_widget(self, cid):
        constraints = self.handler.context.constraints
        constraint = constraints[cid]
        constraint_widget = self.ui.constraintWidget
        constraint_widget.setRowCount(constraint_widget.rowCount() + 1)

        # set enabled
        item = BoolEditor(constraint['enabled'], "enabled",
                          apply=lambda x, y: self.handler.change_constraint(cid, x, y))
        constraint_widget.setCellWidget(constraint_widget.rowCount() - 1, 0, item)
        item = QTableWidgetItem(cid)
        item.setFlags(Qt.ItemIsEditable)
        constraint_widget.setItem(constraint_widget.rowCount() - 1, 1, item)

        # set equation
        equation = constraint['equation']
        item = TextEditor(equation, 'equation', check_valid=lambda x: self.constraint_check_equation(x),
                          apply=lambda x, y: self.handler.change_constraint(cid, x, y))
        constraint_widget.setCellWidget(constraint_widget.rowCount() - 1, 2, item)

        # set description
        description = constraint['description']
        item = TextEditor(description, 'description',
                          apply=lambda x, y: self.handler.change_constraint(cid, x, y))
        constraint_widget.setCellWidget(constraint_widget.rowCount() - 1, 3, item)

        self.handler.context.dirty = True
        self.set_command_enable()

    # Add constraint
    def constraints_add_new(self):
        self.handler.new_constraint()

    # Delete constraint
    def constraint_delete(self, cid):
        for i in self.ui.constraintWidget.selectedIndexes():
            item = self.ui.constraintWidget.item(i.row(), 1)
            if item.text() == cid:
                self.ui.constraintWidget.removeRow(i.row())
                break

    # Solve/Simulation Menu / Solver Controller command
    def command_start_solver(self):
        try:
            self.solver_controller.setModal(True)
            self.solver_controller.G = self.handler.context.G

            # initialize value property combobox
            node_properties = self.settings.setting('default-node-attrs')['control-volume'].keys()
            combo_boxes = (
                self.solver_controller.ui.valuePropertyNameComboBox,
                self.solver_controller.ui.maxValuePropertyComboBox
            )
            for cb in combo_boxes:
                cb.clear()
                for k in node_properties:
                    cb.addItem(k)
            self.solver_controller.ui.valuePropertyNameComboBox.setCurrentText("value")
            self.solver_controller.ui.maxValuePropertyComboBox.setCurrentText("maxValue")

            # initialize edge property combobox
            edge_properties = self.settings.setting('default-edge-attrs')['dataflow'].keys()
            combo_boxes = (
                self.solver_controller.ui.velocityPropertyComboBox,
                self.solver_controller.ui.maxVelocityPropertyComboBox,
                self.solver_controller.ui.currentMaxVelocityPropertyComboBox,
                self.solver_controller.ui.distancePropertyComboBox
            )
            for cb in combo_boxes:
                cb.clear()
                for k in edge_properties:
                    cb.addItem(k)
            self.solver_controller.ui.velocityPropertyComboBox.setCurrentText("velocity")
            self.solver_controller.ui.maxVelocityPropertyComboBox.setCurrentText("maxVelocity")
            self.solver_controller.ui.currentMaxVelocityPropertyComboBox.setCurrentText("currentMaxVelocity")
            self.solver_controller.ui.distancePropertyComboBox.setCurrentText("distance")

            # open dialog
            self.solver_controller.exec_()

            # save post data within graph of current context.
            self.handler.context.G.graph['dt'] = self.solver_controller.ui.doubleSpinBox.value()
            self.handler.context.G.graph['steps'] = self.solver_controller.ui.spinBox.value()
            self.handler.context.G.graph['post-data'] = self.solver_controller.post_data

        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()


    # Solver/Simulation menu Visualizer command
    def command_visualizer(self):
        try:
            self.visualizer.setModal(True)
            self.visualizer.ui.steps.setValue(self.handler.context.G.graph['steps'])
            self.visualizer.ui.steps.setMaximum(self.handler.context.G.graph['steps'])
            self.visualizer.ui.steps.setMinimum(0)
            self.visualizer.ui.stepOffset.setValue(0)
            self.visualizer.ui.stepOffset.setMinimum(0)
            self.visualizer.ui.stepOffset.setMaximum(self.handler.context.G.graph['steps'])
            self.visualizer.ui.dt.setValue(self.handler.context.G.graph['dt'])
            self.visualizer.setup(self.handler.context.G.graph['post-data'])
            self.visualizer.exec_()
        except Exception as ex:
            self.print(ex)
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    # delete system script command
    def command_delete_system_script(self):
        try:
            self.print("command_system_system_script")
            ix = []
            for i in self.ui.systemScriptTable.selectedIndexes():
                if i.row() not in ix:
                    ix.append(i.row())
            scripts = self.settings.setting('system-scripts')
            for i in ix:
                item = self.ui.systemScriptTable.item(i, 1)
                scripts.pop(item.text())
                self.ui.systemScriptTable.removeRow(i)
        except Exception as ex:
            self.reporter.report(str(ex))
        finally:
            self.set_command_enable()

    # add system script command
    def command_add_system_script(self):
        try:
            self.print("command_add_system_script")
            scripts = self.settings.setting('system-scripts')
            ix = []
            sid = 0
            for i in range(1, len(scripts.keys())+1):
                if str(i) not in scripts.keys():
                    sid = i
                    break
            if sid == 0:
                sid = len(scripts.keys()) + 1
            sid = str(sid)
            scripts[sid] = {'id': sid, 'enabled': True, 'script': ''}
            self.system_script_add_to_widget(sid)
        except Exception as ex:
            self.reporter.report(str(ex))
        finally:
            self.set_command_enable()

    def system_script_add_to_widget(self, sid):
        scripts = self.settings.setting('system-scripts')
        script = scripts[sid]
        self.ui.systemScriptTable.setRowCount(self.ui.systemScriptTable.rowCount() + 1)

        # current row
        row = self.ui.systemScriptTable.rowCount() - 1
        # set enabled
        def set_enabled(i,k,v):
            scripts[i][k] = v
        item = BoolEditor(script['enabled'], "enabled", apply=lambda x, y: set_enabled(sid, x, y))
        self.ui.systemScriptTable.setCellWidget(row, 0, item)

        # set id
        item = QTableWidgetItem(sid)
        #item.setFlags(Qt.ItemIsEditable)
        self.ui.systemScriptTable.setItem(row, 1, item)

        # set script
        def set_script(i,k,v):
            scripts[i][k] = v
        item = LongTextEditor(script['script'], "script", apply=lambda x, y: set_script(sid, x, y))
        self.ui.systemScriptTable.setCellWidget(row, 2, item)

    # add user script command
    def command_add_user_script(self):
        try:
            self.print("command_add_user_script")
            ix = []
            for i in range(self.ui.userScriptTable.rowCount()):
                item = self.ui.userScriptTable.item(i, 1)
                ix.append(int(item.text()))
            if len(ix) == 0:
                sid = 1
            else:
                sid = max(ix) + 1
            for i in range(1, len(ix)+1):
                if i not in ix:
                    sid = i
                    break
            sid = str(sid)
            self.handler.context.scripts[sid] = {'id': sid, 'enabled': True, 'script': ''}
            self.user_script_add_to_widget(sid)
        except Exception as ex:
            self.reporter.report(str(ex))
        finally:
            self.set_command_enable()

    # delete user script command
    def command_delete_user_script(self):
        try:
            self.print("command_delete_user_script")
            ix = []
            for i in self.ui.userScriptTable.selectedIndexes():
                if i.row() not in ix:
                    ix.append(i.row())
            for i in ix:
                item = self.ui.userScriptTable.item(i, 1)
                self.handler.context.scripts.pop(item.text())
                self.ui.userScriptTable.removeRow(i)
        except Exception as ex:
            self.reporter.report(str(ex))
        finally:
            self.set_command_enable()

    def user_scripts_init(self):
        self.user_scripts_clear()
        self.ui.userScriptTable.setColumnWidth(0, 20)
        self.ui.userScriptTable.setColumnWidth(1, 20)

    def user_scripts_clear(self):
        self.ui.userScriptTable.setRowCount(0)

    # Add all constraints to constraint_widget
    def user_scripts_add_all_to_widget(self):
        scripts = self.handler.context.scripts
        for c in scripts.keys():
            self.user_script_add_to_widget(c)

    def user_script_delete(self, sid):
        self.handler.context.scripts.pop(sid)
        self.handler.context.dirty = True

    def user_script_add_to_widget(self, sid):
        scripts = self.handler.context.scripts
        script = scripts[sid]
        self.ui.userScriptTable.setRowCount(self.ui.userScriptTable.rowCount() + 1)

        # current row
        row = self.ui.userScriptTable.rowCount() - 1
        # set enabled
        item = BoolEditor(script['enabled'], "enabled",
                          apply=lambda x, y: self.handler.change_script(sid, x, y))
        self.ui.userScriptTable.setCellWidget(row, 0, item)

        # set id
        item = QTableWidgetItem(sid)
        # item.setFlags(Qt.ItemIsEditable)
        self.ui.userScriptTable.setItem(row, 1, item)

        # set script
        item = LongTextEditor(script['script'], "script",
                              apply=lambda x, y: self.handler.change_script(sid, x, y))
        self.ui.userScriptTable.setCellWidget(row, 2, item)
        # item = QTableWidgetItem(script['script'])
        # item.setFlags(Qt.ItemIsEditable)
        # self.ui.userScriptTable.setItem(self.ui.userScriptTable.rowCount() - 1, 2, item)

        # set button
        # item = QPushButton("Edit")
        # self.ui.userScriptTable.setCellWidget(self.ui.userScriptTable.rowCount() - 1, 3, item)
        # item.clicked.connect(lambda: self.command_edit_on_script_editor(sid))


    def command_edit_on_script_editor(self, sid):
        script = self.handler.context.scripts[sid]['script']
        self.script_editor.setModal(True)
        self.script_editor.set_handler_pair(self.handler, self.async_handler)
        self.script_editor.ui.scriptEdit.setPlainText(script)
        self.script_editor.exec_()
        if self.script_editor.ok:
            text = self.script_editor.ui.scriptEdit.toPlainText()
            self.handler.change_script(sid, 'script', text)
            for i in range(self.ui.userScriptTable.rowCount()):
                item = self.ui.userScriptTable.item(i, 1)
                if sid == item.text():
                    item = self.ui.userScriptTable.item(i, 2)
                    item.setText(text)
                    break
        self.set_command_enable()

    def system_scripts_init(self):
        header_labels = ('enabled', 'id', 'script')
        scripts_widget = self.ui.systemScriptTable
        scripts_widget.setColumnCount(3)
        scripts_widget.setHorizontalHeaderLabels(header_labels)
        scripts_widget.setColumnWidth(0, 20)
        scripts_widget.setColumnWidth(1, 20)
        scripts = self.settings.setting('system-scripts')
        scripts_widget.setRowCount(len(scripts.keys()))
        def set_enabled(i,k,v):
            self.settings.setting('system-scripts')[i][k] = v
        def set_script(i,k,v):
            self.settings.setting('system-scripts')[i][k] = v
        for i, k in enumerate(scripts.keys()):
            script = scripts[k]['script']
            enabled = scripts[k]['enabled']
            # item = QTableWidgetItem(enabled)
            # if enabled:
            #     item.setCheckState(Qt.CheckState.Checked)
            # else:
            #     item.setCheckState(Qt.CheckState.Unchecked)
            #item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
            item = BoolEditor(enabled, "enabled", apply=lambda x,y: set_enabled(k,x,y))
            scripts_widget.setCellWidget(i, 0, item)
            item = QTableWidgetItem(k)
            #item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
            scripts_widget.setItem(i, 1, item)
            item = LongTextEditor(script, "script", apply=lambda x,y: set_script(k,x,y))
            scripts_widget.setCellWidget(i, 2, item)

    def copy_impl(self):
        nodes = {}
        edges = {}
        groups = {}
        # copy nodes
        for n in self.handler.selected_nodes:
            nodes[n] = {}
            for k in self.handler.context.G.nodes[n].keys():
                nodes[n][k] = self.handler.context.G.nodes[n][k]
        # copy edges
        for e in self.handler.selected_edges:
            edges[e] = {}
            for k in self.handler.context.G.edges[e[0], e[1]].keys():
                edges[e][k] = self.handler.context.G.edges[e[0], e[1]][k]
        # copy groups
        for g in self.handler.selected_groups:
            groups[g] = {"nodes": [], "edges": []}
            for c in self.handler.context.graph["groups"][g]:
                if isinstance(c, str):  # node
                    nodes[c] = {}
                    for k in self.handler.context.nodes[c].keys():
                        nodes[c][k] = self.handler.context.nodes[c][k]
                    groups[g]["nodes"].append(c)
                else:  # edge
                    edges[c] = {}
                    for k in self.handler.context.edges[c[0], c[1]].keys():
                        edges[c][k] = self.handler.context.edges[c[0], c[1]][k]
                    groups[g]["edges"].append(c)
        self.clear_copy_buf()
        for k in nodes.keys():
            self.node_copy_buf[k] = nodes[k]
        for k in edges.keys():
            self.edge_copy_buf[k] = edges[k]
        for k in groups.keys():
            self.group_copy_buf[k] = groups[k]

    def paste_impl(self):
        node_map = {}
        for v in self.node_copy_buf:
            node_map[v] = v
        for e in self.edge_copy_buf.keys():
            node_map[e[0]] = e[0]
            node_map[e[1]] = e[1]
        for v in self.node_copy_buf.keys():
            n = self.handler.new_node(self.node_copy_buf[v])
            node_map[v] = n
        for e in self.edge_copy_buf.keys():
            u = node_map[e[0]]
            v = node_map[e[1]]
            self.handler.add_edge(u, v, self.edge_copy_buf[e])
        for g in self.group_copy_buf.keys():
            nodes = [node_map[_] for _ in self.group_copy_buf[g]["nodes"]]
            edges = [(node_map[_[0]], node_map[_[1]]) for _ in self.group_copy_buf[g]["edges"]]
            nodes.extend(edges)
            self.handler.add_group(nodes)

    def command_copy(self):
        try:
            self.print("command_copy")
            self.copy_impl()

        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    def command_cut(self):
        try:
            self.print("command_cut")
            self.copy_impl()
            for g in self.handler.selected_groups:
                self.handler.remove_group(g)
            for e in self.handler.selected_edges:
                self.handler.remove_edge(e[0], e[1])
            for n in self.handler.selected_nodes:
                self.handler.remove_node(n)

        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    def command_paste(self):
        try:
            self.print("command_paste")
            self.paste_impl()
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    def group_create(self, gid):
        self.new_item_group(gid)

    def group_purge(self, gid):
        self.remove_item_group(gid)

    def group_remove(self, gid):
        self.remove_item_group(gid)

    def command_group(self):
        try:
            self.print("command_group")
            self.handler.create_group()
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    def command_ungroup(self):
        try:
            self.print("command_ungroup")
            self.handler.purge_group()
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.set_command_enable()

    def construct_custom_menus(self):
        try:
            custom_menus = self.settings.setting('custom-menus')
            for k in custom_menus.keys():
                menu = custom_menus[k]
                name = menu['name']
                command = menu['command']
                action = QAction(self)
                #action.setObjectName(name)
                self.ui.menuCustom.addAction(action)
                action.setText(name)
                action.triggered.connect(lambda: self.do_custom_menu(command))
        except Exception as ex:
            self.print(ex)
        finally:
            self.set_command_enable()

    def do_custom_menu(self, menu_command):
        try:
            self.print("do_custom_menu", menu_command)
            from graphcore.thread_signal import GraphCoreThreadSignal
            from networkml.network import ExtensibleWrappedAccessor
            def print(*args):
                arg = " ".join([str(_) for _ in args])
                sig = GraphCoreThreadSignal("update main_window.message", arg,
                                            lambda x: self.print(x), None)
                self.script_handler.main_thread_command.emit(sig)
            self.handler.toplevel.set_print_func(print)
            self.handler.toplevel.auto_flush = True
            # def report_func(arg):
            #     sig = GraphCoreThreadSignal("update console.textBrowser", arg,
            #                                 lambda x: self.ui.textBrowser.append(x), None)
            #     self.script_handler.main_thread_command.emit(sig)
            self._script_handler.reporter.report_func = print
            m = ExtensibleWrappedAccessor(self.handler.toplevel, "print", self,
                                          lambda ao, c, eo, ca, ea: print(*ca))
            self.script_handler.toplevel.declare_method(m, globally=True)
            self.script_handler.run_script(menu_command)
        except Exception as ex:
            self.print(ex)
        finally:
            self.set_command_enable()

    def deserialize(self):
        with open("graphcore-ui.cfg", "r") as f:
            data = json.load(f)
        # main_window
        self.move(data['main-window']['x'], data['main-window']['y'])
        self.resize(data['main-window']['width'], data['main-window']['height'])
        if data['main-window']['maximized']:
            self.setWindowState(Qt.WindowState.WindowMaximized)
        self.ui.left_pane.resize(data['main-window-left-pane']['width'], data['main-window-left-pane']['height'])
        self.ui.left_top_pane.resize(data['main-window-left-top-pane']['width'], data['main-window-left-top-pane']['height'])
        self.ui.left_bottom_pane.resize(data['main-window-left-bottom-pane']['width'], data['main-window-left-bottom-pane']['height'])
        self.ui.right_pane.resize(data['main-window-right-pane']['width'], data['main-window-right-pane']['height'])
        self.ui.right_top_pane.resize(data['main-window-right-top-pane']['width'], data['main-window-right-top-pane']['height'])
        self.ui.right_bottom_pane.resize(data['main-window-right-bottom-pane']['width'], data['main-window-right-bottom-pane']['height'])
        # console
        self.console.move(data['console']['x'], data['console']['y'])
        self.console.resize(data['console']['width'], data['console']['height'])
        # solver_controller
        self.solver_controller.move(data['solver-controller']['x'], data['solver-controller']['y'])
        self.solver_controller.resize(data['solver-controller']['width'], data['solver-controller']['height'])
        # visualizer
        self.visualizer.move(data['visualizer']['x'], data['visualizer']['y'])
        self.visualizer.resize(data['visualizer']['width'], data['visualizer']['height'])

    def serialize(self):
        data = {}
        # main_window
        data['main-window'] = {
            "maximized": self.isMaximized(),
            "x": self.x(),
            "y": self.y(),
            "width": self.width(),
            "height": self.height()
        }
        data['main-window-left-pane'] = {
            "width": self.ui.left_pane.width(),
            "height": self.ui.left_pane.height()
        }
        data['main-window-left-top-pane'] = {
            "width": self.ui.left_top_pane.width(),
            "height": self.ui.left_top_pane.height()
        }
        data['main-window-left-bottom-pane'] = {
            "width": self.ui.left_bottom_pane.width(),
            "height": self.ui.left_bottom_pane.height()
        }
        data['main-window-right-pane'] = {
            "width": self.ui.right_pane.width(),
            "height": self.ui.right_pane.height()
        }
        data['main-window-right-top-pane'] = {
            "width": self.ui.right_top_pane.width(),
            "height": self.ui.right_top_pane.height()
        }
        data['main-window-right-bottom-pane'] = {
            "x": self.ui.right_bottom_pane.x(),
            "y": self.ui.right_bottom_pane.y(),
            "width": self.ui.right_bottom_pane.width(),
            "height": self.ui.right_bottom_pane.height()
        }
        # console
        data['console'] = {
            "x": self.console.x(),
            "y": self.console.y(),
            "width": self.console.width(),
            "height": self.console.height()
        }
        # solver_controller
        data['solver-controller'] = {
            "x": self.solver_controller.x(),
            "y": self.solver_controller.y(),
            "width": self.solver_controller.width(),
            "height": self.solver_controller.height()
        }
        # visualizer
        data['visualizer'] = {
            "x": self.visualizer.x(),
            "y": self.visualizer.y(),
            "width": self.visualizer.width(),
            "height": self.visualizer.height()
        }
        with open("graphcore-ui.cfg", "w") as f:
            json.dump(data, f, indent=4)
        self.settings.save()
