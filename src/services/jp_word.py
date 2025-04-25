import datetime
import json

from src.models.jp_word import JPWord

def save_word(word, kana, source, content, source_id=None):
    word = JPWord(
        word=word,
        kana=kana,
        source=source,
        content=content,
        created_time=datetime.datetime.now()
    )
    word.save()

def remove_word_by_id(id):
    record = JPWord.get(id==id)
    record.delete_instance()

def list_words(word: str):
    result = JPWord.select().where(
        (JPWord.word == word) | (JPWord.kana == word)
    )

    return list(map(lambda x: {'source': 'favorites', 'data': x}, result))

def get_by_word_and_kana(word, kana):
    return JPWord.select().where(
        JPWord.word == word,
        JPWord.kana == kana
    )

def dump_to_json(file='./data/favorites.json'):
    result = []
    for item in JPWord.select():
        result.append({
            'word': item.word,
            'kana': item.kana,
            'source': item.source,
            'content': item.content,
            'created_time': item.created_time.isoformat(),
        })
    with open(file, 'w', encoding='utf8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)