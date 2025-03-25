from PyQt5.QtCore import pyqtSignal

from src.services.jp_word import list_words
from src.services.dictionary import search as search_word_from_dict
from src.services.hujiang import HuJiang
from src.utils import utils

from src import config_manager


class SearchWord:

    def __init__(self, search_succeed_signal: pyqtSignal):
        self.search_succeed_signal = search_succeed_signal

        self.hujiang = HuJiang(config_manager.config, self.search_succeed_signal)

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
            style_sheet = config_manager.get_dictionary_style_sheet(w['source'])
            if style_sheet:
                # w['data'].content = utils.extract_meanings(content)
                w['data'].content = f'<style>{style_sheet}</style>{content}'

            if not content in existed:
                words.append(w)

        if source == 'hujiang':
            self.hujiang.search(word)
        else:
            for item in words:
                item['word'] = word
            self.search_succeed_signal.emit(words)
