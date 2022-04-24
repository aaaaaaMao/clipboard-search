import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow,
    QPlainTextEdit
)
from PyQt5.QtCore import QSize, Qt
import keyboard

class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(400, 240))
        self.setWindowTitle("Clipboard search")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.text_editor = QPlainTextEdit(self)
        self.text_editor.insertPlainText('Waiting copy')
        self.text_editor.move(10, 10)
        self.text_editor.resize(380,220)

        QApplication.clipboard().dataChanged.connect(self.read_clipboard)

    def read_clipboard(self):
        text = QApplication.clipboard().text()
        
        if self.text_editor.toPlainText() != text:
            self.text_editor.setPlainText('')
            self.text_editor.insertPlainText(text)

            if self.isMinimized():
                keyboard.wait('alt')

                self.setWindowFlags(Qt.WindowStaysOnTopHint)
                self.showNormal()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())