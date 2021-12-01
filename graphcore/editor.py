from GUI.Ui_MainWindow import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
import sys
import os
import shutil
import sqlite3
import numpy as np


settings = {
    "default_directory": ".",
    "template_directory": "config/templates",
    "initialized_database": "initialized_database",
    "work_directory": ".tmp",
}


class GraphCoreError(Exception):
    def __init__(self, text="", exception: Exception=None):
        super(Exception, self).__init__()
        self.text = text
        self.exception = exception


class GraphCoreModel:
    def __init__(self, file_name=None, temporary=False):
        self.settings = settings
        self.temporary = temporary
        self.file_name = None
        self.dirty: bool = False
        self.db = None
        try:
            if file_name is None or len(file_name) == 0:
                db: QSqlDatabase = QSqlDatabase.addDatabase("QSQLITE")
                db.setDatabaseName(":memory:")
                self.db: QSqlDatabase = db
            else:
                self.open(file_name)
        except GraphCoreError as ex:
            raise ex
        except QSqlError as ex:
            raise GraphCoreError("Database Error", ex)
        except Exception as ex:
            raise GraphCoreError("System Error", ex)

    def init_db(self, connection: sqlite3):
        raise GraphCoreError("Not Implemented")

    def is_valid_db(self, connecction: sqlite3):
        # raise GraphCoreError("Not Implemented")
        return True

    def set_dirty(self, flag: bool):
        self.dirty = flag

    def is_dirty(self):
        return self.dirty

    def is_opened(self):
        if self.file_name is None:
            return False
        else:
            return True

    def open(self, file_name):
        try:
            if self.is_opened():
                raise GraphCoreError("Invalid Operation: file {} already opened".format(file_name))
            # db: QSqlDatabase = QSqlDatabase.addDatabase("QSQLITE")
            # db.setDatabaseName(file_name)
            SERVER = 'BOOGIE\\SQLEXPRESS'
            DATABASE = 'GeneralGraph'
            USERNAME = 'sa'
            PASSWORD = 'jupyter9'

            conn_str = f'DRIVER={{SQL Server}};' \
                       f'SERVER={SERVER};' \
                       f'DATABASE={DATABASE};' \
                       f'USERNAME={USERNAME};' \
                       f'PASSWORD={PASSWORD}'

            db: QSqlDatabase = QSqlDatabase.addDatabase("QODBC")
            db.setDatabaseName(conn_str)
            if not db.open():
                raise GraphCoreError("Database Open Error")
            # if not self.is_valid_db(connection):
            #     raise GraphCoreError("Argument Error: Invalid Content")
            self.db: QSqlDatabase = db
            self.file_name = file_name
        except GraphCoreError as ex:
            raise ex
        except Exception as ex:
            raise GraphCoreError("System Error", ex)

    def close(self):
        if not self.is_opened():
            raise GraphCoreError("Invalid Operation: not opened.")
        try:
            self.db.close()
            self.db = None
            self.file_name = None
            self.dirty = False
        except Exception as ex:
            raise GraphCoreError("System Error", ex)

    def save(self):
        if self.file_name is None:
            raise GraphCoreError("Invalid Operation: file not associated")
        try:
            self.db.commit()
            self.dirty = False
        except Exception as ex:
            raise GraphCoreError("System Error", ex)

    def save_as(self, new_file_name: str):
        raise GraphCoreError("Not Implemented")


class GraphCoreShell:
    def __init__(self):  # , settings):
        print("Hello GraphCore")
        self.settings = settings
        self.main_window = GraphCoreShellGui(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_window)
        self.models = []
        self.current = None
        self.main_window.graphCore_setCommandEnabilities()

    def print(self, text):
        self.main_window.print(text)

    def random_filename(self):
        tmp_dir = self.settings["work_directory"]
        max_rand = 9999999999
        i = 0
        while i < max_rand:
            filename = "{}".format(np.random.randint(0, max_rand))
            if not os.path.exists(tmp_dir + "/" + filename):
                return filename
            i += 1
        return None

    def initialize_temp_database(self):
        try:
            dir = self.settings["template_directory"]
            db = self.settings["initialized_database"]
            tmp_file = self.random_filename()
            if tmp_file is None:
                return None
            work_dir = self.settings["work_directory"]
            dst_path = work_dir + "/" + tmp_file
            src_path = dir + "/" + db
            shutil.copy(src_path, dst_path)
            return dst_path
        except Exception as ex:
            return None

    def show(self):
        self.main_window.show()

    def current_model(self) -> GraphCoreModel:
        return self.current

    def set_current_model(self, model: GraphCoreModel) -> bool:
        for i, m in enumerate(self.models):
            if m == model:
                self.current = m
                return True
        return False

    def current_index(self) -> int:
        if self.current_model() is None:
            return -1
        for i, m in enumerate(self.models):
            if m == self.current:
                return i
        return -1

    def set_current_index(self, index):
        if index < 0 or len(self.models) <= index:
            return False
        for i, m in enumerate(self.models):
            if i == index:
                self.current_model = self.models[index]
                return True
        return False

    def is_opened(self, file_name: str):
        self.print("is_opened({})".format(file_name))
        for m in self.models:
            if m.file_name is not None and m.file_name == file_name:
                return True
        return False

    def new(self) -> bool:
        self.print("new()")
        tmp_db = None
        try:
            tmp_db = self.initialize_temp_database()
            model = GraphCoreModel(tmp_db, temporary=True)
            self.models.append(model)
            self.set_current_model(model)
            return True
        except Exception as ex:
            self.print(ex)
            if tmp_db is not None:
                os.remove(tmp_db)
            return False

    def open(self, file_name) -> bool:
        self.print("open({})".format(file_name))
        try:
            if self.is_opened(file_name):
                self.print("GraphCore Error: file already opened")
                return False
            model = GraphCoreModel(file_name)
            self.models.append(model)
            self.set_current_model(model)
            return True
        except Exception as ex:
            self.print(ex)
            return False

    def open_enabled(self) -> bool:
        return True

    def close(self):
        self.print("close")
        try:
            model: GraphCoreModel = self.current_model()
            if model is None:
                self.print("GraphCore Error: current model not set")
                return False
            model.close()
            self.models.remove(model)
            if len(self.models) == 0:
                self.set_current_model(None)
            else:
                self.set_current_index(0)
            return True
        except Exception as ex:
            self.print(ex)
            return False

    def close_enabled(self) -> bool:
        model: GraphCoreModel = self.current_model()
        if model is None:
            return False
        else:
            return True

    def save(self, file_name):
        self.print("save({})".format(file_name))
        try:
            model = self.current_model()
            if model.file_name is None:
                raise GraphCoreError("Not Implemented")
            elif model.file_name == file_name:
                model.save()
            else:
                raise GraphCoreError("Operation Error: filename not matched")
            return True
        except Exception as ex:
            self.print("GraphCore Error: {}".format(ex))
            return False

    def save_enabled(self) -> bool:
        model: GraphCoreModel = self.current_model()
        if model is None:
            return False
        if model.is_dirty():
            return True
        else:
            return False

    def save_as(self, file_name):
        self.print("save_as({})".format(file_name))
        try:
            model: GraphCoreModel = self.current_model()
            raise GraphCoreError("Not Implemented")
        except Exception as ex:
            self.print("GraphCore Error: {}".format(ex))
            return False

    def save_as_enabled(self) -> bool:
        model: GraphCoreModel = self.current_model()
        if model is None:
            return False
        return True

    def quit(self):
        self.print("quit")
        quit_done: bool = False
        try:
            for (i, m) in enumerate(self.models):
                self.set_current_model(m)
                self.close()
                self.models.remove(m)
                if len(self.models) <= i:
                    self.set_current_index(i - 1)
            quit_done = True
        except Exception as ex:
            self.print("GraphCore Error: {}".format(ex))
            raise ex
        finally:
            return quit_done


class GraphCoreShellGui(QMainWindow):
    def __init__(self, shell: GraphCoreShell):
        super(QMainWindow, self).__init__()
        self.shell = shell

    def print(self, text):
        self.shell.ui.messages.append(text)

    def graphCore_open(self):
        self.print("graphCore_open")
        dialog_title = "Open Model File"
        directory = "."
        file_masks = "sqlite/sqlite3 database file (*.db *.db3)"
        file_name = QFileDialog.getOpenFileName(self, dialog_title, directory, file_masks)
        if file_name[0] is not None and file_name[0] != "":
            self.shell.open(file_name[0])
        # read tables
        table_model: QSqlTableModel = QSqlTableModel(db=self.shell.current_model().db)
        table_model.setTable("Nodes")
        # table_model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        table_model.setEditStrategy(QSqlTableModel.OnRowChange)
        table_model.select()
        table_model.setHeaderData(0, Qt.Horizontal, "node_id")
        table_model.setHeaderData(1, Qt.Horizontal, "node_type")
        table_model.setHeaderData(3, Qt.Horizontal, "complexity")
        table_model.setHeaderData(4, Qt.Horizontal, "label")
        view: QTableView = self.shell.ui.nodeTableView
        view.setModel(table_model)
        # view.resizeColumnToContents()
        table_model: QSqlTableModel = QSqlTableModel(db=self.shell.current_model().db)
        table_model.setTable("Edges")
        # table_model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        table_model.setEditStrategy(QSqlTableModel.OnRowChange)
        table_model.select()
        table_model.setHeaderData(0, Qt.Horizontal, "src_node_id")
        table_model.setHeaderData(1, Qt.Horizontal, "dst_node_id")
        table_model.setHeaderData(2, Qt.Horizontal, "edge_type")
        table_model.setHeaderData(3, Qt.Horizontal, "complexity")
        table_model.setHeaderData(4, Qt.Horizontal, "label")
        view: QTableView = self.shell.ui.edgeTableView
        view.setModel(table_model)
        # view.resizeColumnToContents()

        self.graphCore_setCommandEnabilities()

    def graphCore_close(self):
        self.print("graphCore_close")
        self.shell.close()
        self.graphCore_setCommandEnabilities()

    def graphCore_save(self):
        self.print("graphCore_save")
        dialog_title = "Open Model File"
        directory = "."
        file_masks = "sqlite/sqlite3 database file (*.db *.db3)"
        file_name = QFileDialog.getSaveFileName(self, dialog_title, directory, file_masks)
        if file_name[0] is not None and file_name[0] != "":
            self.shell.save(file_name[0])
        self.graphCore_setCommandEnabilities()

    def graphCore_saveAs(self):
        self.print("graphCore_saveAs")
        dialog_title = "Open Model File"
        directory = "."
        file_masks = "sqlite/sqlite3 database file (*.db *.db3)"
        file_name = QFileDialog.getSaveFileName(self, dialog_title, directory, file_masks)
        if file_name[0] is not None and file_name[0] != "":
            self.shell.save_as(file_name[0])
        self.graphCore_setCommandEnabilities()

    def graphCore_quit(self):
        self.print("graphCore_quit")
        if self.shell.quit():  # quit
            self.shell.main_window.close()
        self.graphCore_setCommandEnabilities()

    def graphCore_setCommandEnabilities(self):
        self.shell.ui.actionOpen.setEnabled(self.shell.open_enabled())
        self.shell.ui.actionClose.setEnabled(self.shell.close_enabled())
        self.shell.ui.actionSave.setEnabled(self.shell.save_enabled())
        self.shell.ui.actionSaveAs.setEnabled(self.shell.save_as_enabled())
        # self.shell.ui.actionImport.setEnabled(self.shell.import_enabled())
        # self.shell.ui.actionExport.setEnabled(self.shell.export_enabled())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    shell = GraphCoreShell()
    shell.show()
    sys.exit(app.exec_())
