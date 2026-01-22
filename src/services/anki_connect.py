from dataclasses import dataclass
import os
import re

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
        query = f'(deck:NEW-JLPT or deck:额外) and (vocabkanji:"{word}" or vocabfurigana:"{word}" or vocabplus:"{word}")'
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
    
    def get_audio_file_path(self, filename: str) -> str:
        result_data = self.invoke("getMediaDirPath")

        if result_data['error'] is not None:
            logging.error(f"AnkiConnectClient get_audio_file_path error: {result_data['error']}")
            return ""

        return os.path.join(result_data['result'], re.sub(r'^\[sound:(.+)\]$', r'\1', filename))
    
    # list audio sources from "Local Audio Server for Yomichan" Anki add-on
    def list_audio_sources(self,term: str, reading: str):
        r = requests.get(f"http://localhost:5050/?term={term}&reading={reading}")
        if r.status_code != 200:
            logging.error(f"AnkiConnectClient list_audio_sources error: status code {r.status_code}")
            return []
        
        sources = r.json()["audioSources"]
        for source in sources:
            source["url"] = re.sub(r'\\', '/', source["url"])

        return sources

    def add_note(self, deck_name: str, model_name: str, fields: dict, tags: list[str]=[], audio=None) -> bool:
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags,
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck",
                "duplicateScopeOptions": {
                    "deckName": deck_name,
                    "checkChildren": False,
                    "checkAllModels": False
                }
            },
            "audio": [audio] if audio else []
        }

        result_data = self.invoke("addNote", {
            "note": note
        })

        if result_data['error'] is not None:
            logging.error(f"AnkiConnectClient add_note error: {result_data['error']}")
            return False

        return result_data['result']