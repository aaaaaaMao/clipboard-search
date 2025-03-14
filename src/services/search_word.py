from PyQt5.QtCore import pyqtSignal

from src.services.jp_word import list_words
from src.services.dictionary import search as search_word_from_dict
from src.services.hujiang import HuJiang
from src.utils import utils
from src import word_list_style_sheet as style_sheet


class SearchWord:

    def __init__(self, config, search_succeed_signal: pyqtSignal):
        self.search_succeed_signal = search_succeed_signal

        self.hujiang = HuJiang(config, self.search_succeed_signal)

    def search(self, word: str, source=''):
        if not str:
            self.search_succeed_signal.emit([])

        existed = set()
        words = list_words(word)
        for w in words:
            if w['data'].source == '自建':
                w['data'].content = f'{w["data"].kana}\n---\n{w["data"].content}'
            existed.add(utils.trim(w['data'].content))
        for w in search_word_from_dict(word):
            content = utils.trim(w['data'].content)
            if w['source'] == 'プログレッシブ和英中辞典_v4':
                # w['data'].content = utils.extract_meanings(content)
                w['data'].content = f'<style>{style_sheet}</style>{content}'

            if not content in existed:
                words.append(w)

        if not words or not len(words) or source == 'hujiang':
            self.hujiang.search(word)
        else:
            for item in words:
                item['word'] = word
            self.search_succeed_signal.emit(words)
