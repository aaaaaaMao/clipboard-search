import json
import math

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

from src import logging, word_list_style_sheet as style_sheet
from src.services.jp_word import save_word, remove_word_by_id
from src.models.jp_word import JPWord
from src.services.hujiang import JPWordHj
from src.utils import utils


class WordList(QListWidget):

    def __init__(self):
        super().__init__()

    def init_ui(self):
        self.addItem('Waiting copy')
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        if style_sheet:
            self.setStyleSheet(style_sheet)

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
        wordItem = WordListItem(word)

        size = wordItem.sizeHint()
        size.setHeight(math.ceil(size.height()*1.25))
        item.setSizeHint(size)

        self.addItem(item)
        self.setItemWidget(item, wordItem)


class WordListItem(QWidget):

    def __init__(self, word):
        super().__init__()

        layout = QHBoxLayout()
        text = ''

        if 'word' in word:
            self.word = word['word']
        self.source = word['source']
        data = word['data']

        if isinstance(data, JPWord):
            if data.source == 'hujiang':
                hj_word = json.loads(data.content)
                text = QLabel(str(JPWordHj(
                    hj_word['word'],
                    hj_word['pronounces'],
                    hj_word['word_type'],
                    hj_word['translation'],
                )))
            else:
                text = QLabel(data.content)
            check = QCheckBox()
            check.setChecked(True)
            check.stateChanged.connect(
                lambda state: self.on_box_checked(state, data)
            )
            layout.addWidget(check)
        else:

            if isinstance(data, JPWordHj):
                text = QLabel(str(data))
            else:
                text = QLabel(data.content)

            check = QCheckBox()
            check.stateChanged.connect(
                lambda state: self.on_box_checked(state, data)
            )
            layout.addWidget(check)

        layout.addWidget(text)
        layout.setSizeConstraint(
            QtWidgets.QLayout.SizeConstraint.SetFixedSize
        )
        self.setLayout(layout)

    def on_box_checked(self, state, data):
        if state == Qt.Checked:
            if self.source == 'hujiang':
                save_word(data.word, data.pronounces, self.source, json.dumps({
                    'word': data.word,
                    'pronounces': data.pronounces,
                    'word_type': data.word_type,
                    'translation': data.translation,
                }, ensure_ascii=False))
                logging.info(f'Check: {data.word}')
            else:
                kana = ''
                if self.source == '新時代日漢辭典':
                    kana = utils.extract_kana(data.content)
                save_word(self.word, kana, self.source,
                          data.content, data.id)
        else:
            if isinstance(data, JPWord):
                remove_word_by_id(data.id)
                logging.info(f'Cancel: {data.word}')
