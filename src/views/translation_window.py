from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QTextEdit,
)
from PyQt5.QtCore import Qt

from src.services.translation import TranslationWorker


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

    def show(self, content=''):
        self.content.setText('翻译中...')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        super().show()

        self.thread = TranslationWorker(content)
        self.thread.translated_sig.connect(
                    lambda x: self.content.setText(x)
                )
        self.thread.start()


