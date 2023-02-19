from PyQt5.QtCore import pyqtSignal

from src.services.jp_word import list_words
from src.services.dictionary import search as search_word_from_dict
from src.services.hujiang import HuJiang


class SearchWord:

    def __init__(self, config, search_succeed_signal: pyqtSignal):
        self.search_succeed_signal = search_succeed_signal

        self.hujiang = HuJiang(config, self.search_succeed_signal)

    def search(self, word: str):
        words = list_words(word)
        words.extend(search_word_from_dict(word))

        if not words or not len(words):
            self.hujiang.search(word)
        else:
            self.search_succeed_signal.emit(words)