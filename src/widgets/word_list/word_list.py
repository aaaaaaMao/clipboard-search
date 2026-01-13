import json
import math

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidgetItem,
    QLabel,
    QCheckBox,
    QListWidget,
    QTextEdit,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

from src import logging
from src.services.jp_word import save_word, remove_word_by_id
from src.models.jp_word import JPWord
from src.services.hujiang import JPWordHj
from src.utils import utils

from .search_service import SearchService, SearchResult
from .word_item import WordListItem


class WordList(QListWidget):

    _search_succeed_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self._search_succeed_signal.connect(self.show_words)
        self._search_service = SearchService(self._search_succeed_signal)

        self.init_ui()

    def init_ui(self):
        self.addItem('Waiting ...')
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.setResizeMode(QListWidget.Adjust)

    def search_words(self, words, sources: list[str]=['anki', 'mdict']):
        self.clear()
        self.addItem('Searching ...')

        self._search_service.search_words(words, sources)

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
        item = QListWidgetItem(self)
        wordItem = WordListItem(word)

        size = wordItem.sizeHint()
        # size.setHeight(math.ceil(size.height()*1.25))
        item.setSizeHint(size)

        self.addItem(item)
        self.setItemWidget(item, wordItem)



