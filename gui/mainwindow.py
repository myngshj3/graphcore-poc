
import networkx as nx
import traceback
import re
from graphcore.shell import GraphCoreThreadSignal
from graphcore.shell import GraphCoreShell, GraphCoreContext, GraphCoreContextHandler, GraphCoreAsyncContextHandler
from gui.Ui_MainWindow import Ui_MainWindow
from graphcore.graphicsitem import GraphCoreCircleNodeItem, GraphCoreRectNodeItem, GraphCoreEdgeItem, \
    GraphCoreNodeItemInterface
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from graphcore.propertyeditor import TextEditor, IntEditor, FloatEditor, BoolEditor, ComboBoxEditor
# from GraphCore.graphcoreeditor import TextEditor, IntEditor, FloatEditor, ComboBoxEditor, CheckBoxEditor,\
#     CheckBoxEditorEx, TextEditorEx
from graphcore.constraint import GCConstraintParser
from networkml.error import NetworkParserError
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
from graphcore.reporter import GraphCoreReporter
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
        self.install_shell_actions()

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
        self.handler.set_reflection(GraphCoreContextHandler.NodeSelected, lambda x: self.property_select_node(x))
        self.handler.set_reflection(GraphCoreContextHandler.EdgeSelected, lambda x: self.property_select_edge(x))
        self.handler.set_reflection(GraphCoreContextHandler.ConstraintAdded, lambda x: self.constraint_add_to_widget(x))
        self.handler.set_reflection(GraphCoreContextHandler.ConstraintRemoved, lambda x: self.constraint_delete(x))
        # FIXME
        self.handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionAdded, lambda x: print(x))
        self.handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionUpdated, lambda x: print(x))
        self.handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionRemoved, lambda x: print(x))

        self.async_handler.set_reflection(GraphCoreContextHandler.NodeAdded, lambda x: self.new_node_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.NodeUpdated, lambda x: self.redraw_node_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.NodeRemoved, lambda x: self.remove_node_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.EdgeAdded, lambda x: self.new_edge_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.EdgeUpdated, lambda x: self.redraw_edge_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.EdgeRemoved, lambda x: self.remove_edge_item(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.ViewUpdated, lambda x: self.change_view(x[0], x[1], x[2], x[3]))
        self.async_handler.set_reflection(GraphCoreContextHandler.AllDeselected, lambda x: self.property_deselect_all())
        self.async_handler.set_reflection(GraphCoreContextHandler.NodeSelected, lambda x: self.property_select_node(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.EdgeSelected, lambda u, v: self.property_select_edge((u, v)))
        self.async_handler.set_reflection(GraphCoreContextHandler.ConstraintAdded, lambda x: self.constraint_add_to_widget(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.ConstraintRemoved, lambda x: self.constraint_delete(x))
        # FIXME
        self.async_handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionAdded, lambda x: print(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionUpdated, lambda x: print(x))
        self.async_handler.set_reflection(GraphCoreContextHandler.UserDefinedFunctionRemoved, lambda x: print(x))

    def handler_new(self, handler, async_handler):
        handler.extras['element_to_item'] = {}
        handler.extras['edge_creating'] = False
        handler.extras['temp_coords'] = None
        scene = GraphCoreScene()
        scene.handler = handler
        scene.shell = self.shell
        scene.settings = self.settings
        handler.extras['scene'] = scene
        view = QGraphicsView(scene)
        view.setContextMenuPolicy(Qt.CustomContextMenu)
        view.customContextMenuRequested['QPoint'].connect(self.command_show_context_menu)
        # view.setBackgroundBrush(QBrush(QColor("pink")))
        self.ui.tabWidget.addTab(view, 'untitled')
        self.ui.tabWidget.setCurrentWidget(view)
        self.install_handler_actions()
        self.handler_changed(handler, async_handler)
        self.handler.loaded()
        index = self.ui.tabWidget.currentIndex()
        if self.handler.context.filename is None:
            self.ui.tabWidget.tabBar().setTabText(index, "untitled")
        else:
            name = os.path.basename(self.handler.context.filename)
            self.ui.tabWidget.tabBar().setTabText(index, name)

    def handler_changed(self, handler, async_handler):
        self.property_clear()
        self.constraints_clear()
        self._handler = handler
        self._async_handler = async_handler
        self.update_node_list()
        self.update_edge_list()

    def handler_purged(self):
        for e in self.element_to_item.keys():
            item = self.element_to_item[e]
            self.scene.removeItem(item)
        self.property_clear()
        self.constraints_clear()
        self.element_to_item.clear()
        self.ui.tabWidget.removeTab(self.ui.tabWidget.currentIndex())
        self._scene = None
        self._handler = None
        self._async_handler = None

    # create node item
    def new_node_item(self, n):
        attr = self.handler.context.nodes[n]
        if attr['shape']['value'] in ('circle', 'doublecircle'):
            item = GraphCoreCircleNodeItem(n, self.handler.context, self.handler)
        elif attr['shape']['value'] in ('box', 'doublebox'):
            item = GraphCoreRectNodeItem(n, self.handler.context, self.handler)
        else:
            self.print("Unsupported shape:{}. force to circle".format(attr['shape']['value']))
            item = GraphCoreCircleNodeItem(n, self.handler.context, self.handler)
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

    # change view
    def change_view(self, x, y, w, h):
        self.scene.setSceneRect(x, y, w, h)
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
    def print(self, text: object) -> None:
        # print(text)
        self.ui.messages.append(str(text))

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
        self.console.setModal(False)
        self.console.set_handler_pair(self.handler, self.async_handler)
        self.console.show()

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

    # Hidden Commands / Change Current command
    def command_change_current(self, index) -> None:
        try:
            view: QGraphicsView = self.ui.tabWidget.currentWidget()
            if isinstance(view, QGraphicsView):
                scene: GraphCoreScene = view.scene()
                # self.shell.handler.deselect_all()
                self.shell.set_current_handler(scene.handler)
        except Exception as ex:
            self.print(traceback.format_exc())

    # File / Open command
    def command_open(self) -> None:
        try:
            # self.handler.deselect_all()
            dialog_title = "Open Model File"
            directory = "."
            file_masks = "GraphCore graph file (*.yaml *.dot, *.gv)"
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
                    file_masks = "GraphCore graph file (*.yaml *.dot, *.gv)"
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
            self.setCommandEnabilities()

    # File / Save command
    def command_save(self) -> None:
        try:
            # save, if dirty
            if self.handler.context.dirty:
                filename = self.handler.context.filename
                if self.handler.context.filename is None:
                    dialog_title = "Save Model File"
                    directory = "."
                    file_masks = "GraphCore graph file (*.yaml *.dot, *.gv)"
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
            file_masks = "GraphCore graph file (*.yaml *.dot, *.gv)"
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
        self.print('command_save_as')

    def update_node_list(self):
        self.ui.nodeTableWidget.clear()
        self.ui.nodeTableWidget.setHorizontalHeaderItem(0, QTableWidgetItem('Id'))
        self.ui.nodeTableWidget.setHorizontalHeaderItem(1, QTableWidgetItem('Label'))
        self.ui.nodeTableWidget.setHorizontalHeaderItem(2, QTableWidgetItem('Caption'))
        self.ui.nodeTableWidget.setHorizontalHeaderItem(3, QTableWidgetItem('Description'))
        self.ui.nodeTableWidget.setRowCount(len(self.handler.context.G.nodes))
        for i, n in enumerate(self.handler.context.G.nodes):
            id = n
            label = self.handler.context.G.nodes[n]['label']['value']
            caption = self.handler.context.G.nodes[n]['caption']['value']
            description = self.handler.context.G.nodes[n]['description']['value']
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
            label = self.handler.context.G.edges[e[0], e[1]]['label']['value']
            caption = self.handler.context.G.edges[e[0], e[1]]['caption']['value']
            description = self.handler.context.G.edges[e[0], e[1]]['description']['value']
            self.ui.edgeTableWidget.setItem(i, 0, QTableWidgetItem(id))
            self.ui.edgeTableWidget.setItem(i, 1, QTableWidgetItem(label))
            self.ui.edgeTableWidget.setItem(i, 2, QTableWidgetItem(caption))
            self.ui.edgeTableWidget.setItem(i, 3, QTableWidgetItem(description))

    def command_new_node(self, x=None, y=None, node_type=None):
        try:
            # self.print('command_new_node')
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
                attr[k] = {}
                attr[k]['value'] = default_settings[k]['value']
                attr[k]['type'] = default_settings[k]['type']
                attr[k]['visible'] = default_settings[k]['visible']
                if 'list' in default_settings[k].keys():
                    attr[k]['list'] = default_settings[k]['list']
            attr['x']['value'] = x
            attr['y']['value'] = y
            if node_type is not None:
                attr['type']['value'] = node_type
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
                attrs[k] = {}
                attrs[k]['value'] = default_settings[k]['value']
                attrs[k]['type'] = default_settings[k]['type']
                attrs[k]['visible'] = default_settings[k]['visible']
                if 'list' in default_settings[k].keys():
                    attrs[k]['list'] = default_settings[k]['list']
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
    def command_quit(self) -> bool:
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
            for s in self.serializers:
                s()
            self.settings.save()
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
                    xmin = attr['x']['value']
                    xmax = attr['x']['value']
                elif ymin is None:
                    ymin = attr['y']['value']
                    ymax = attr['y']['value']
                else:
                    if attr['x']['value'] < xmin:
                        xmin = attr['x']['value']
                    if xmax < attr['x']['value']:
                        xmax = attr['x']['value']
                    if attr['y']['value'] < ymin:
                        ymin = attr['y']['value']
                    if ymax < attr['y']['value']:
                        ymax = attr['y']['value']
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
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # deselect all selected objects
    def command_deselect_all(self) -> None:
        try:
            self.handler.deselect_all()
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # selected node
    def command_select_node(self, n) -> None:
        try:
            self.print("command_select_node")
            self.handler.select_node(n)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

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
            self.print('command_remove_node({})'.format(n))
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

    # select edge
    def command_select_edge(self, e) -> None:
        try:
            self.print('command_select_edge')
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
                attrs['type']['value'] = edge_type
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
            self.print('command_remove_edge')
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
            has_error = False
            for cid in constraints.keys():
                equation = constraints[cid]['equation']
                # desc = constraints[cid]['description']
                enabled = constraints[cid]['enabled']
                if not enabled:
                    continue
                result, error = (), ()
                if len(error) != 0:
                    ui.errorWidget.setRowCount(ui.errorWidget.rowCount() + 1)
                    item = QTableWidgetItem("Constraint Error: {}: {}".format(cid, error))
                    ui.errorWidget.setItem(ui.errorWidget.rowCount() - 1, 0, item)
                    has_error = True
                else:
                    for r in result:
                        if not r.evaluate():
                            ui.errorWidget.setRowCount(ui.errorWidget.rowCount() + 1)
                            item = QTableWidgetItem("Constraint Violation: {}: {}".format(cid, equation))
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
            self.handler.change_node_attr(n, 'label', str(attr['complexity']['value']))

    # Labels/Node caption
    def command_set_node_caption_to_label(self):
        for n in self.handler.context.nodes:
            attr = self.handler.context.nodes[n]
            self.handler.change_node_attr(n, 'label', str(attr['caption']['value']))

    # Labels/Edge Id
    def command_set_edge_id_to_label(self):
        for e in self.handler.context.edges:
            self.handler.change_edge_attr(e[0], e[1], 'label', "e({},{})".format(e[0], e[1]))

    # Labels/Edge distance
    def command_set_edge_distance_to_label(self):
        for e in self.handler.context.edges:
            attr = self.handler.context.edges[e[0], e[1]]
            self.handler.change_edge_attr(e[0], e[1], 'label', str(attr['distance']['value']))

    # Labels/Edge caption
    def command_set_edge_caption_to_label(self):
        for e in self.handler.context.edges:
            attr = self.handler.context.edges[e[0], e[1]]
            self.handler.change_edge_attr(e[0], e[1], 'label', attr['caption']['value'])

    # Labels/Node Tooltips
    def command_change_node_tooltips(self):
        for n in self.handler.context.nodes:
            attr = self.handler.context.nodes[n]
            item = self.element_to_item[n]
            if item.toolTip() is None or item.toolTip() == "":
                item.setToolTip(attr['description']['value'])
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
                item.setToolTip(attr['description']['value'])
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
            # self.print("context menu at {}".format(p))
            view: QGraphicsView = self.ui.tabWidget.currentWidget()
            global_pos = view.mapToGlobal(p)
            item = view.itemAt(p)
            item = self.to_graph_element_item(item)
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
                    action.setData([p.x(), p.y()])
                    action.triggered.connect(new_node_call(p.x(), p.y(), t))
                menu.popup(global_pos)
        except Exception as ex:
            self.print(traceback.format_exc())
        finally:
            self.setCommandEnabilities()

    # begin edge
    def popup_menu_do_begin_edge(self, source, edge_type):
        self.print("popup_menu_do_begin_edge({})".format(source))
        s = self.handler.context.nodes[source]
        self.command_deselect_all()
        sx, sy, w = s['x']['value'], s['y']['value'], s['w']['value']
        # dx, dy = s['x'], s['y']
        arrow_line = QGraphicsPolygonItem()
        arrow_line.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.scene.addItem(arrow_line)
        self.set_temp_coords((source, sx, sy, 0, arrow_line, edge_type))
        self.set_edge_creating(True)

    def popup_menu_do_remove(self, item):
        self.print("popup_menu_do_remove({})".format(item))
        if isinstance(item, GraphCoreNodeItemInterface):
            self.command_remove_node(item.node)
        elif isinstance(item, GraphCoreEdgeItem):
            self.command_remove_edge((item.u, item.v))

    def check_if_edge_creation_mode(self):
        return self._edge_creating

    def set_command_enable(self):
        self.ui.actionNew.setEnabled(True)
        self.ui.actionOpen.setEnabled(True)
        self.ui.actionClose.setEnabled(self.ui.tabWidget.currentIndex() >= 0)
        enabled = False
        if self.handler is not None and self.handler.context.dirty:
            enabled = True
        self.ui.actionSave.setEnabled(enabled)
        self.ui.actionSaveAs.setEnabled(True)

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

    # select node
    def property_select_node(self, node):
        property_widget = self.ui.propertyWidget
        attrs = self.handler.context.nodes[node]
        _type = attrs['type']['value']
        node_properties = self.settings.setting('default-node-attrs')[_type].keys()
        property_widget.setRowCount(0)
        attr_count = 0
        for i, k in enumerate(node_properties):
            if not self.settings.setting('default-node-attrs')[_type][k]['visible']:
                continue
            # if not attrs[k]['visible']:
            #     continue
            attr_count += 1
            property_widget.setRowCount(attr_count)
            property_widget.setItem(attr_count - 1, 0, QTableWidgetItem(k))
            property_widget.setItem(attr_count - 1, 1, QTableWidgetItem(self.settings.setting('default-node-attrs')[_type][k]['caption']))
            editor = None
            t = attrs[k]['type']
            if "list" in attrs[k].keys():
                value_list = attrs[k]['list']
                entries = []
                for idx, n in enumerate(value_list):
                    entries.append((n, n))  # FIXME
                editor = ComboBoxEditor(attrs[k]['value'], k, entries,
                                        apply=lambda x, y: self.handler.change_node_attr(node, x, y))
                editor.callback_enabled = True
            elif t == "str":
                editor = TextEditor(attrs[k]['value'], k, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
            elif t == "int":
                editor = IntEditor(attrs[k]['value'], k, int, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
            elif t == "float":
                editor = FloatEditor(attrs[k]['value'], k, float, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
            elif t == "bool":
                editor = BoolEditor(attrs[k]['value'], k, apply=lambda x, y: self.handler.change_node_attr(node, x, y))
            else:
                self.print("unsupported type:{}".format(t))
            property_widget.setCellWidget(attr_count - 1, 2, editor)

    # select edge
    def property_select_edge(self, edge):
        property_widget = self.ui.propertyWidget
        attrs = self.handler.context.edges[edge[0], edge[1]]
        _type = attrs['type']['value']
        edge_properties = self.settings.setting('default-edge-attrs')[_type].keys()
        property_widget.setRowCount(0)
        attr_count = 0
        for i, k in enumerate(edge_properties):
            if not self.settings.setting('default-edge-attrs')[_type][k]['visible']:
                continue
            # if not attrs[k]['visible']:
            #     continue
            attr_count += 1
            property_widget.setRowCount(attr_count)
            property_widget.setItem(attr_count - 1, 0, QTableWidgetItem(k))
            property_widget.setItem(attr_count - 1, 1, QTableWidgetItem(self.settings.setting('default-edge-attrs')[_type][k]['caption']))
            editor = None
            t = attrs[k]['type']
            if "list" in attrs[k].keys():
                value_list = attrs[k]['list']
                entries = []
                for idx, n in enumerate(value_list):
                    entries.append((n, n))  # FIXME
                editor = ComboBoxEditor(attrs[k]['value'], k, entries,
                                        apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
                editor.callback_enabled = True
            elif t == "str":
                editor = TextEditor(attrs[k]['value'], k,
                                    apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
            elif t == "int":
                editor = IntEditor(attrs[k]['value'], k, int,
                                   apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
            elif t == "float":
                editor = FloatEditor(attrs[k]['value'], k, float,
                                     apply=lambda x, y: self.handler.change_edge_attr(edge[0], edge[1], x, y))
            elif t == "bool":
                editor = BoolEditor(attrs[k]['value'], k,
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
        for n in G.nodes:
            for k in G.nodes[n].keys():
                G.nodes[n][k] = G.nodes[n][k]['value']
        for e in G.edges:
            for k in G.edges[e[0], e[1]].keys():
                G.edges[e[0], e[1]][k] = G.edges[e[0], e[1]][k]['value']
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

    # Add constraint
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
            G = nx.DiGraph()
            for n in self.handler.context.G.nodes:
                G.add_node(n)
                for k in self.handler.context.G.nodes[n].keys():
                    G.nodes[n][k] = self.handler.context.G.nodes[n][k]['value']
            for e in self.handler.context.G.edges:
                G.add_edge(e[0], e[1])
                for k in self.handler.context.G.edges[e[0], e[1]].keys():
                    G.edges[e[0], e[1]][k] = self.handler.context.G.edges[e[0], e[1]][k]['value']
            self.solver_controller.G = G
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
