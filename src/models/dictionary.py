from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer

Base = declarative_base()


class DictionaryEntry(Base):
    __tablename__ = 'main'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    keyword = Column(Text, index=True)
    link = Column(Text)
    content = Column(Text)
