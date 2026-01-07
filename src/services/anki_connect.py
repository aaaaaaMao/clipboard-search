from dataclasses import dataclass

import requests

from src import logging

@dataclass
class AnkiJPWord:
    note_id: int
    kanji: str
    furigana: str
    pitch: str
    pos: str
    def_cn: str
    extra: str
    audio: str
    tags: list[str]

class AnkiConnectClient:
    def __init__(self, url="http://localhost:8765"):
        super().__init__()

        self._url = url

    def invoke(self, action: str, params: dict = {}) -> str:

        payload = {
            "action": action,
            "version": 6,
            "params": params
        }

        r = requests.post(self._url, json=payload)
        return r.json()

    def query_notes(self, query: str) -> list[dict]:
        result_data = self.invoke("notesInfo", {
            "query": query
        })

        if result_data['error'] is not None:
            logging.error(f"AnkiConnectClient query_notes error: {result_data['error']}")
            return []

        return result_data['result']

    def search_jp_words(self, word: str) -> list[AnkiJPWord]:
        query = f'deck:NEW-JLPT and (vocabkanji:"{word}" or vocabfurigana:"{word}" or vocabplus:"{word}")'
        notes = self.query_notes(query)

        return [
            AnkiJPWord(
                note_id=item['noteId'], 
                kanji=item['fields']['VocabKanji']['value'], 
                furigana=item['fields']['VocabFurigana']['value'], 
                pitch=item['fields']['VocabPitch']['value'], 
                pos=item['fields']['VocabPoS']['value'],    
                def_cn=item['fields']['VocabDefCN']['value'],
                extra=item['fields']['VocabPlus']['value'],
                audio=item['fields']['VocabAudio']['value'],
                tags=item['tags']
            ) for item in notes
        ]
    
    def add_tags(self, note_ids: list[int], tags: list[str]) -> None:
        result_data = self.invoke("addTags", {
            "notes": note_ids,
            "tags": ' '.join(tags)
        })

        return result_data['result'] is None
    
    def remove_tags(self, note_ids: list[int], tags: list[str]) -> None:
        result_data = self.invoke("removeTags", {
            "notes": note_ids,
            "tags": ' '.join(tags)
        })

        return result_data['result'] is None