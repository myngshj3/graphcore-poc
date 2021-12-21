

from gui.gcplotwidget import GCplotWidget
from gui.ui_postproc import Ui_Form
import sys


def main(argv):
    app = QApplication(sys.argv)
    main_win = QMainWindow()
    ui = Ui_Form()
    ui.setupUi(main_win)
    main_win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)

