import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import config_manager


favorites_engine = create_engine(
    'sqlite:///data/favorites.db?check_same_thread=False')


def load_dictionaries(filepath='./data/dictionary'):
    if not os.path.exists(filepath):
        os.mkdir(filepath)

    db_dir = f'{filepath}/db'
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)

    # for file in os.listdir(db_dir):
    #     (filename, ext) = os.path.splitext(file)
    result = []
    for item in config_manager.config['dictionaries']:
        filename = item['name']
        if item['search'] and os.path.exists(f'{db_dir}/{filename}.db'):
            item = {
                'name': filename,
                'engine': create_engine(f'sqlite:///{db_dir}/{filename}.db?check_same_thread=False')
            }
            item['Session'] = sessionmaker(bind=item['engine'])
            result.append(item)
        else:
            pass
    return result


dictionary_engines = load_dictionaries()
