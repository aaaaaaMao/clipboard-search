from dataclasses import dataclass

import requests

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
    
    def search_jp_words(self, word: str) -> list[AnkiJPWord]:
        query = f'deck:NEW-JLPT and (vocabkanji:"{word}" or vocabfurigana:"{word}" or vocabplus:"{word}")'
        result_data =  self.invoke("notesInfo", {
            "query": query
        })

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
            ) for item in result_data['result']
        ]