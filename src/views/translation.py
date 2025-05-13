from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QTextEdit,
)

from src.services.translation import TranslationWorker


class Translation(QWidget):

    def __init__(self):
        super().__init__()
        self.last_text = ''

        vbox = QVBoxLayout()

        self.content = QTextEdit()
        vbox.addWidget(self.content)

        self.setLayout(vbox)

    def translate(self, text=''):
        if text == self.last_text:
            return
        
        self.content.setText('翻译中...')

        self.thread = TranslationWorker(text)
        self.thread.translated_sig.connect(
                    lambda x: self._set_content(text, x)
                )
        self.thread.start()

    def _set_content(self, text, result):
        self.last_text = text
        self.content.setText(result)