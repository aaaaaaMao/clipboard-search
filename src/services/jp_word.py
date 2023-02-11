import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_
from src.models import favorites_engine
from src.models.jp_word import JPWord

Session = sessionmaker(bind=favorites_engine)


def save_word(word, kana, source, content):
    with Session() as session:
        word = JPWord(
            word=word,
            kana=kana,
            source=source,
            content=content,
            created_time=datetime.datetime.now()
        )
        session.add(word)
        session.commit()


def list_words(word):
    with Session() as session:
        return session.query(JPWord).filter(
            or_(
                JPWord.word == word,
                JPWord.kana == word
            )
        ).all()


def get_by_word_and_kana(word, kana):
    with Session() as session:
        return session.query(JPWord).filter(
            and_(
                JPWord.word == word,
                JPWord.kana == kana
            )
        ).all()
