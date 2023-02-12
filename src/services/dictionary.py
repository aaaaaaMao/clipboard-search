
from src.models import dictionary_engines
from src.models.dictionary import DictionaryEntry


def search(word):
    result = []
    for dictionary in dictionary_engines:
        with dictionary['Session']() as session:
            data = session.query(DictionaryEntry).filter_by(keyword=word).all()
            result.extend(data)
    return result
