import asyncio
from dataclasses import dataclass

from PyQt5.QtCore import pyqtSignal
from mdict_query_r.query import Querier, Dictionary

from src.services.jp_word import list_words
from src.services.hujiang import HuJiang
from src.utils import utils

from src import config_manager

@dataclass
class SearchResultData:
    id: int = None
    keyword: str = None
    content: str = None

class SearchWord:

    def __init__(self, search_succeed_signal: pyqtSignal):
        self.search_succeed_signal = search_succeed_signal
        self._mdict_querier: Querier = None

        if config_manager.hujiang_enabled():
            self.hujiang = HuJiang(config_manager.config, self.search_succeed_signal)

        asyncio.run(self.init_mdict_querier())

    async def init_mdict_querier(self):
        dictionaries = config_manager.list_dictionaries()
        if len(dictionaries) == 0:
            return
        
        dictionaries = [
            Dictionary(
                name=d['name'], 
                filepath=config_manager.get_dictionary_path(d['name'], ext='.mdx')
            )
            for d in dictionaries
        ]

        self._mdict_querier = Querier(dictionaries)

    def search(self, word: str, source=''):
        if not str:
            self.search_succeed_signal.emit([])

        existed = set()
        words = list_words(word)
        for w in words:
            if w['data'].source == '自建':
                w['data'].content = f'{w["data"].kana}\n---\n{w["data"].content}'
            existed.add(utils.trim(w['data'].content))

        for record in self._mdict_querier.query(word):
            content = utils.trim(record.entry.data)
            style_sheet = config_manager.get_dictionary_style_sheet(record.dictionary_name)
            if style_sheet:
                content = f'<style>{style_sheet}</style>{content}'

            if not content in existed:
                words.append({
                    'source': record.dictionary_name,
                    'data': SearchResultData(
                            id=record.entry.id,
                            keyword=record.entry.key_text,
                            content=record.entry.data
                        )
                })

        if source == 'hujiang' and self.hujiang:
            self.hujiang.search(word)
        else:
            for item in words:
                item['word'] = word
            self.search_succeed_signal.emit(words)
