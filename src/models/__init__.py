import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

favorites_engine = create_engine(
    'sqlite:///data/favorites.db?check_same_thread=False')

dictionary_engines = []


def load_dictionaries(filepath='./data/dictionary'):
    if not os.path.exists(filepath):
        os.mkdir(filepath)

    db_dir = f'{filepath}/db'
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)

    for file in os.listdir(db_dir):
        (filename, ext) = os.path.splitext(file)
        if os.path.exists(f'{db_dir}/{filename}.db'):
            item = {
                'name': file,
                'engine': create_engine(f'sqlite:///{db_dir}/{filename}.db?check_same_thread=False')
            }
            item['Session'] = sessionmaker(bind=item['engine'])
            dictionary_engines.append(item)
        else:
            pass


load_dictionaries()
