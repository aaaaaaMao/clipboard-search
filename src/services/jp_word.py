import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_
from src.models import favorites_engine
from src.models.jp_word import JPWord

Session = sessionmaker(bind=favorites_engine)


def save_word(word, kana, source, content, source_id=None):
    with Session() as session:
        word = JPWord(
            word=word,
            kana=kana,
            source=source,
            source_id=source_id,
            content=content,
            created_time=datetime.datetime.now()
        )
        session.add(word)
        session.commit()


def remove_word_by_id(id):
    with Session() as session:
        record = session.query(JPWord).filter_by(id=id).first()
        session.delete(record)
        session.commit()


def list_words(word: str):
    with Session() as session:
        result = session.query(JPWord).filter(
            or_(
                JPWord.word == word,
                JPWord.kana == word
            )
        ).all()

        return list(map(lambda x: {'source': 'favorites', 'data': x}, result))


def get_by_word_and_kana(word, kana):
    with Session() as session:
        return session.query(JPWord).filter(
            and_(
                JPWord.word == word,
                JPWord.kana == kana
            )
        ).all()


def dump_to_json(file='./data/favorites.json'):
    import json

    with Session() as session:
        result = []
        for item in session.query(JPWord).filter().all():
            result.append({
                'word': item.word,
                'kana': item.kana,
                'source': item.source,
                'content': item.content,
                'created_time': item.created_time.isoformat(),
            })
        with open(file, 'w', encoding='utf8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
