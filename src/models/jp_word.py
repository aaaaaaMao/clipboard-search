from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, DateTime, UniqueConstraint

from src.models import favorites_engine

Base = declarative_base()


class JPWord(Base):
    __tablename__ = 'jp_words'
    __table_args__ = (
        UniqueConstraint('word', 'kana', 'source',
                         name='Idx_word_kana_source'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    word = Column(Text, index=True)
    kana = Column(Text, index=True)
    source = Column(Text)
    source_id = Column(Integer)
    content = Column(Text)
    created_time = Column(DateTime)


JPWord.__table__.create(favorites_engine, checkfirst=True)
