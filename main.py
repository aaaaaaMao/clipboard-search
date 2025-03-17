import sys
from PyQt5 import QtWidgets

from src.main_window import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    mainWin = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
