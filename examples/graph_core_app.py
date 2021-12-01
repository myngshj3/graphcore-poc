
from GUI.mainwindow import GraphCoreMainWindow
from GraphCore.shell_gui_facade import GraphCoreShellGuiFacade
import sys
# from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


def main():
    app = QApplication(sys.argv)
    main_window = GraphCoreMainWindow()
    shell = GraphCoreShellGuiFacade(main_window)
    shell.setup_property_sheet()

    def print_func(text):
        shell.ui().messages.append(text)

    shell.set_print_func(print_func)
    main_window.set_shell(shell)
    main_window.setCommandEnabilities()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
