import json

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QListWidgetItem,
    QLabel,
    QCheckBox,
    QListWidget
)
from PyQt5.QtCore import Qt

from src import logging
from src.services.jp_word import save_word, get_by_word_and_kana, remove_word_by_id
from src.models.jp_word import JPWord
from src.services.hujiang import JPWordHj


class WordList(QListWidget):

    def __init__(self):
        super().__init__()

    def init_ui(self):
        self.addItem('Waiting copy')
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item: QListWidgetItem):
        widget = self.itemWidget(item)
        lebel = widget.findChild(QLabel)
        # self.copy_to_clipboard(lebel.text())

    def show_words(self, words):
        self.clear()
        if len(words) > 0:
            for word in words:
                self.add_word(word)
        else:
            self.addItem('Not Found.')

    def add_word(self, word):
        item = QListWidgetItem()
        widget = QWidget()
        text = None

        layout = QHBoxLayout()

        if isinstance(word, JPWordHj):
            text = QLabel(str(word))
            check = QCheckBox()
            if get_by_word_and_kana(word.word, word.pronounces):
                check.setChecked(True)
            check.stateChanged.connect(
                lambda state: self.on_box_checked(state, word)
            )
            layout.addWidget(check)
        elif isinstance(word, JPWord):
            if word.source == 'hujiang':
                hj_word = json.loads(word.content)
                text = QLabel(str(JPWordHj(
                    hj_word['word'],
                    hj_word['pronounces'],
                    hj_word['word_type'],
                    hj_word['translation'],
                )))
            else:
                text = QLabel(word.content)
            check = QCheckBox()
            check.setChecked(True)
            check.stateChanged.connect(
                lambda state: self.on_box_checked(state, word)
            )
            layout.addWidget(check)
        else:
            text = QLabel(word.content)
        layout.addWidget(text)

        layout.setSizeConstraint(
            QtWidgets.QLayout.SizeConstraint.SetFixedSize
        )
        widget.setLayout(layout)
        size = widget.sizeHint()
        size.setHeight(size.height() + 50)
        item.setSizeHint(size)

        self.addItem(item)
        self.setItemWidget(item, widget)

    def on_box_checked(self, state, word):
        if state == Qt.Checked:
            save_word(word.word, word.pronounces, 'hujiang', json.dumps({
                'word': word.word,
                'pronounces': word.pronounces,
                'word_type': word.word_type,
                'translation': word.translation,
            }, ensure_ascii=False))
            logging.info(f'Check: {word.word}')
        else:
            if isinstance(word, JPWord):
                remove_word_by_id(word.id)
                logging.info(f'Cancel: {word.word}')
