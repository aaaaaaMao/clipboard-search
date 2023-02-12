from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, PrimaryKeyConstraint

Base = declarative_base()


class DictionaryEntry(Base):
    __tablename__ = 'main'

    __table_args__ = (
        PrimaryKeyConstraint('keyword', 'content', name='Idx_keyword_content'),
    )

    keyword = Column(Text, index=True)
    link = Column(Text)
    content = Column(Text)
