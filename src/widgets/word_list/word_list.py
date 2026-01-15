from PyQt5.QtWidgets import (
    QListWidgetItem,
    QLabel,
    QListWidget,
)
from PyQt5.QtCore import pyqtSignal

from .search_service import SearchService
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



