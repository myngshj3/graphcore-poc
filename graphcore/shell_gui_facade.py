from PyQt5.QtWidgets import *
from PyQt5.QtSql import *
from GraphCore.editor import Ui_MainWindow
from GraphCore.shell import GraphCoreShell
from GUI.mainwindow import GraphCoreMainWindow
from GraphCore.settings import GraphCoreSettings
from GraphCore.error import GraphCoreError
from GraphCore.ellipse_item import GraphEllipseItem
from GraphCore.line_item import GraphLineItem
from GraphCore.model import GraphCoreModel
from GraphCore.item_event_handler import GraphItemEventHandler
import networkx as nx


class GraphCoreShellGuiFacade(GraphCoreShell):
    def __init__(self, main_window: GraphCoreMainWindow):
        super().__init__()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(main_window)
        self._mainWindow = main_window
        self._scene = QGraphicsScene()
        self._ui.graphicsView.setScene(self._scene)
        self._db = None
        self._element_storage = {}
        self._node_radius = 10

    def main_window(self) -> GraphCoreMainWindow:
        return self._mainWindow

    def ui(self):
        return self._ui

    def is_opened(self):
        if self._db is None:
            return False
        if self._db.isOpen():
            return True
        return False

    def is_dirty(self):
        model = self.current_model()
        if model is None:
            return False
        elif model.dirty():
            return True
        return False

    def scene(self):
        return self._scene

    def draw_graph(self, view: QGraphicsView):
        self.print("draw_graph")
        model: GraphCoreModel = self.current_model()
        graph: nx.DiGraph = model.graph()
        for n in graph.nodes:
            attrs = graph.nodes[n]
            point = GraphEllipseItem(graph=graph, graph_element=n, element_storage=self._element_storage,
                                     print_func=self.print_func())
            handler = GraphItemEventHandler(owner=point, shell=self, print_func=self.print_func())
            point.set_event_handler(handler)
            point.setFlag(QGraphicsItem.ItemIsSelectable, True)
            point.setRect(attrs['x'] - self._node_radius, attrs['y'] - self._node_radius, self._node_radius * 2, self._node_radius * 2)
            self._scene.addItem(point)
            self._element_storage[str(n)] = point

        for e in graph.edges:
            u = graph.nodes[e[0]]
            v = graph.nodes[e[1]]
            line = GraphLineItem(graph=graph, graph_element=e, element_storage=self._element_storage,
                                 print_func=self.print_func())
            handler = GraphItemEventHandler(owner=line, shell=self, print_func=self.print_func())
            line.set_event_handler(handler)
            line.setLine(u['x'], u['y'], v['x'], v['y'])
            line.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self._scene.addItem(line)
            self._element_storage[str(e)] = line

    def load_graph(self):
        self.print("load_graph")
        if self.is_opened():
            db: QSqlDatabase = self._db
            graph: nx.DiGraph = self.current_model().graph()
            graph.clear()
            # read nodes
            sql = "select node_id, node_type, complexity, label, x, y from Nodes"
            query: QSqlQuery = db.exec(sql)
            while query.next():
                node_id = query.value(0)
                node_type = query.value(1)
                complexity = query.value(2)
                label = query.value(3)
                x = query.value(4)
                y = query.value(5)
                graph.add_node(node_id)
                n = graph.nodes[node_id]
                n['type'] = node_type
                n['complexity'] = complexity
                n['label'] = label
                n['x'] = x
                n['y'] = y
            query.clear()
            # read edges
            sql = "select src_node_id, dst_node_id, edge_type, distance, label from Edges"
            query = db.exec(sql)
            while query.next():
                src_node_id = query.value(0)
                dst_node_id = query.value(1)
                edge_type = query.value(2)
                distance = query.value(3)
                label = query.value(4)
                graph.add_edge(src_node_id, dst_node_id)
                e = graph.edges[src_node_id, dst_node_id]
                e['type'] = edge_type
                e['distance'] = distance
                e['label'] = label
            query.clear()

    def dispose(self):
        for key in self._element_storage.keys():
            item = self._element_storage[key]
            self._scene.removeItem(item)
        self._element_storage.clear()

    def node_add(self, p, node_type):
        graph = self.current_model().graph()
        new_node_id = 1
        for n in graph.nodes:
            if new_node_id <= n:
                new_node_id = n + 1
        graph.add_node(new_node_id)
        n = graph.nodes[new_node_id]
        p = self.ui().graphicsView.mapToScene(p)
        n['x'] = p.x()
        n['y'] = p.y()
        n['type'] = node_type
        n['complexity'] = 0
        n['label'] = "{} {}".format(node_type, new_node_id)
        point = GraphEllipseItem(graph=graph, graph_element=new_node_id, element_storage=self._element_storage,
                                 print_func=self.print_func())
        handler = GraphItemEventHandler(owner=point, shell=self, print_func=self.print_func())
        point.set_event_handler(handler)
        point.setFlag(QGraphicsItem.ItemIsSelectable, True)
        point.setRect(n['x'] - self._node_radius, n['y'] - self._node_radius, self._node_radius * 2,
                      self._node_radius * 2)
        self._scene.addItem(point)
        self._element_storage[str(new_node_id)] = point

    def node_remove(self, node):
        graph = self.current_model().graph()
        # collect associated edges
        edges = []
        for e in graph.edges:
            if e[0] == node or e[1] == node:
                edges.append(e)
        # delete all associated edges
        for e in edges:
            item = self._element_storage[str(e)]
            self._scene.removeItem(item)
            self._element_storage.pop(str(e))
            graph.remove_edge(e[0], e[1])
        # delete this node
        item = self._element_storage[str(node)]
        self._scene.removeItem(item)
        self._element_storage.pop(str(node))
        graph.remove_node(node)

    def node_position_changed(self, node):
        self.current_model().set_dirty(True)
        item: GraphEllipseItem = self._element_storage[str(node)]
        n = self.current_model().graph().nodes[node]
        item.setPos(n['x'], n['y'])

    def node_changed(self, node):
        self.current_model().set_dirty(True)
        self._mainWindow.setCommandEnabilities()

    def edge_changed(self, edge):
        self.current_model().set_dirty(True)
        item: GraphLineItem = self._element_storage[str(edge)]
        e = self.current_model().graph().edges[edge[0], edge[1]]
        self._mainWindow.setCommandEnabilities()

    def command_open(self):
        self.print("command_open")
        try:
            if not self.is_opened():
                if self.current_model() is None:
                    model = self.new_model()
                    self.set_current_model(model)
                settings = GraphCoreSettings()
                server = settings.setting('server')
                database = settings.setting('database')
                username = settings.setting('username')
                password = settings.setting('password')
                conn_str = f'DRIVER={{SQL Server}};' \
                           f'SERVER={server};' \
                           f'DATABASE={database};' \
                           f'USERNAME={username};' \
                           f'PASSWORD={password}'

                db: QSqlDatabase = QSqlDatabase.addDatabase("QODBC")
                db.setDatabaseName(conn_str)
                if not db.open():
                    raise GraphCoreError("Database Open Error")

                self._db: QSqlDatabase = db
                # create new model
                self.new_model()
                # load and draw graph
                self.load_graph()
                self.draw_graph(self.ui().graphicsView)
        except Exception as ex:
            self.print(ex)

    def open_enabled(self):
        return not self.is_opened()

    def command_close(self):
        self.print("command_close")
        try:
            if self.is_opened():
                db: QSqlDatabase = self._db
                db.close()
                self.remove_model(self.current_model())
                self.dispose()
        except Exception as ex:
            self.print(ex)

    def close_enabled(self):
        return self.is_opened()

    def command_save(self):
        self.print("command_save")
        try:
            model = self.current_model()
            if self.is_opened() and model is not None and model.dirty():
                db: QSqlDatabase = self._db
                sql = "begin transaction"
                db.exec(sql)
                sql = "delete from Edges"
                db.exec(sql)
                sql = "delete from Nodes"
                db.exec(sql)
                sql = "SET IDENTITY_INSERT[Nodes] ON"
                db.exec(sql)
                sql = "DBCC CHECKIDENT (Nodes ,RESEED ,0)"
                db.exec(sql)
                # insert nodes
                sql = "insert into Nodes (node_id, node_type, complexity, label, x, y) values (?, ?, ?, ?, ?, ?)"
                query = QSqlQuery()
                query.prepare(sql)
                for node in model.graph().nodes:
                    n = model.graph().nodes[node]
                    query.addBindValue(node)
                    query.addBindValue(n['type'])
                    query.addBindValue(n['complexity'])
                    query.addBindValue(n['label'])
                    query.addBindValue(n['x'])
                    query.addBindValue(n['y'])
                    query.exec_()
                # insert edges
                sql = "insert into Edges (src_node_id, dst_node_id, edge_type, distance, label) values (?, ?, ?, ?, ?)"
                query = QSqlQuery()
                query.prepare(sql)
                for edge in model.graph().edges:
                    e = model.graph().edges[edge[0], edge[1]]
                    query.addBindValue(edge[0])
                    query.addBindValue(edge[1])
                    query.addBindValue(e['type'])
                    query.addBindValue(e['distance'])
                    query.addBindValue(e['label'])
                    query.exec_()
                sql = "commit"
                db.exec(sql)
                db.commit()
                model.set_dirty(False)
        except Exception as ex:
            self.print(ex)
            self._db.exec("rollback")
            self._db.rollback()

    def save_enabled(self):
        if self.is_opened() and self.is_dirty():
            return True
        return False

    def command_save_as(self):
        self.print("command_save_as")

    def save_as_enabled(self):
        return False

    def import_enabled(self):
        return False

    def export_enabled(self):
        return False

    def command_quit(self):
        self.print("command_quit")

    def setup_property_sheet(self):
        propertySheet: QTableWidget = self.ui().propertyWidget
        propertySheet.setColumnCount(3)
        propertySheet.setRowCount(0)
        propertySheet.setHorizontalHeaderLabels(('Name', 'Value', 'type'))
        propertySheet.hideColumn(2)

    def quit_enabled(self):
        return False

