from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
import itertools
import asyncio

from PyQt5.QtCore import pyqtSignal
from mdict_query_r.query import Querier, Dictionary
from src.services.hujiang import HuJiangClient

from src import config_manager, anki_client


@dataclass
class SearchResult:
    id: int = None
    source: str = None
    keyword: str = None
    html_content: str = None
    raw_data: dict = None

class SearchService():

    def __init__(self, signal: pyqtSignal = None):
        self._signal = signal
        self._executor = ThreadPoolExecutor(max_workers=3)

        self._mdict_querier: Querier = None

        self._hujiang_client = HuJiangClient(config=config_manager.config)

        self._search_method = {
            'anki': self._search_from_anki,
            'mdict': self._search_from_mdict,
            'hujiang': self._search_from_hujiang,
        }

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

    def search_words(self, words: list[str], sources: list[str] = ['anki', 'mdict']):
        futures = []

        methods = [self._search_method[s] for s in sources if s in self._search_method]
        if len(methods) == 0:
            self._signal.emit([])
            return

        for word in words:
            for f in methods:
                futures.append(
                    self._executor.submit(f, word)
                )


        # 在后台线程中等待所有任务完成
        def wait_for_completion():
            try:
                results = [future.result() for future in futures]
                self._signal.emit(list(itertools.chain.from_iterable(results)))
            except Exception as e:
                print(f'Search error: {e}')
        
        # 在单独的线程中等待
        self._executor.submit(wait_for_completion)

    def _search_from_anki(self, word: str):
        words: list[SearchResult] = []

        for record in anki_client.search_jp_words(word):
            html_content = '<br />'.join([
                f'{record.kanji} ({record.furigana}) {record.pitch}',
                f'【{record.pos}】{record.def_cn}',
                f'<{record.extra}>'
            ])
            words.append(SearchResult(
                source='anki',
                id=record.note_id,
                keyword=record.kanji,
                html_content=html_content,
                raw_data=asdict(record),
            ))

        return words
    
    def _search_from_mdict(self, word: str) -> list[SearchResult]:
        words: list[SearchResult]  = []

        for record in self._mdict_querier.query(word):
            html_content = record.entry.data
            style_sheet = config_manager.get_dictionary_style_sheet(record.dictionary_name)
            if style_sheet:
                html_content = f'<style>{style_sheet}</style>{html_content}'

            words.append(SearchResult(
                source='mdict',
                id=record.entry.id,
                keyword=record.entry.key_text,
                html_content=html_content,
            ))

        return words

    def _search_from_hujiang(self, word: str):
        words: list[SearchResult]  = []

        for record in self._hujiang_client.search(word):
            html_content = '<br />'.join([
                f'{record.word} ({record.pronounces})',
                f'{record.word_type}',
                '<br />'.join(record.translation)
            ])

            words.append(SearchResult(
                source='hujiang',
                keyword=record.word,
                html_content=html_content,
                raw_data=asdict(record),
            ))

        return words