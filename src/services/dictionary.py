
from src.models import dictionary_engines
from src.models.dictionary import DictionaryEntry


def search(word):
    result = []
    for dictionary in dictionary_engines:
        with dictionary['Session']() as session:
            data = session.query(DictionaryEntry).filter_by(keyword=word).all()
            if len(data) != 0:
                for item in data:
                    if item.link != "" and item.content == "":
                        link_data = session.query(DictionaryEntry).filter_by(
                            keyword=item.link).all()
                        result.extend(link_data)
                    else:
                        result.append(item)
    return result
