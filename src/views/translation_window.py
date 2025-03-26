from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QTextEdit,
)
from PyQt5.QtCore import Qt


class TranslationWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('翻译')
        self.resize(600, 400)

        vbox = QVBoxLayout()

        self.content = QTextEdit()
        vbox.addWidget(self.content)

        self.setLayout(vbox)

    def show_window(self, content=''):
        self.content.setText(content)
        self.show()

