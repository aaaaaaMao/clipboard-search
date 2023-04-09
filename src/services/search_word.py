from PyQt5.QtCore import pyqtSignal

from src.services.jp_word import list_words
from src.services.dictionary import search as search_word_from_dict
from src.services.hujiang import HuJiang


class SearchWord:

    def __init__(self, config, search_succeed_signal: pyqtSignal):
        self.search_succeed_signal = search_succeed_signal

        self.hujiang = HuJiang(config, self.search_succeed_signal)

    def search(self, word: str):
        if not str:
            self.search_succeed_signal.emit([])

        existed = set()
        words = list_words(word)
        for w in words:
            existed.add(trimContent(w['data'].content))
        for w in search_word_from_dict(word):
            content = trimContent(w['data'].content)
            if not content in existed:
                words.append(w)

        if not words or not len(words):
            self.hujiang.search(word)
        else:
            self.search_succeed_signal.emit(words)


def trimContent(content: str):
    return content.strip().replace('\r\n', '\n')
