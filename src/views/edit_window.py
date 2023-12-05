from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDialog,
    QTextEdit,
    QPushButton
)
from PyQt5.QtCore import Qt
from src.services.jp_word import save_word


class EditWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('编辑')
        self.resize(300, 400)

        vbox = QVBoxLayout()

        hbox1 = QHBoxLayout()
        word_label = QLabel()
        word_label.setText('word')
        self.word_input = QLineEdit()

        hbox1.addWidget(word_label)
        hbox1.addWidget(self.word_input)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        kana_label = QLabel()
        kana_label.setText('kana')
        self.kana_input = QLineEdit()

        hbox2.addWidget(kana_label)
        hbox2.addWidget(self.kana_input)
        vbox.addLayout(hbox2)

        self.content_input = QTextEdit()
        vbox.addWidget(self.content_input)

        self.save_btn = QPushButton('保存')
        self.save_btn.clicked.connect(self.save_word)
        vbox.addWidget(self.save_btn)

        vbox.addStretch(1)
        self.setLayout(vbox)

    def show_window(self, word=''):
        self.word_input.setText(word)
        self.kana_input.clear()
        self.content_input.clear()
        self.show()

    def save_word(self):
        word = self.word_input.text()
        kana = self.kana_input.text()
        content = self.content_input.toPlainText()

        if word and content:
            save_word(word, kana, '自建', content)
            self.close()
