import sqlite3
import time
import json
import os

dictionaries = []
dict_dir = './dict'
dict_temp_files_dir = './dict/temp'

if os.path.exists(dict_dir):
    if not os.path.exists(dict_temp_files_dir):
        os.mkdir(dict_temp_files_dir)
    for file in os.listdir(dict_dir):
        (filename, ext) = os.path.splitext(file)
        if ext == '.mdx' and not os.path.exists(f'{dict_dir}/{filename}.db'):
            pass
    for file in os.listdir(dict_temp_files_dir):
        dictionaries.append({
            'db_name': file,
            'conn': sqlite3.connect(f'{dict_temp_files_dir}/{file}')
        })

conn = sqlite3.connect('favorites.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS words
           (word TEXT,
            kana TEXT,
            source TEXT,
            content TEXT,
            created_time INTEGER);''')


def dump_to_json(file='./favorites.json'):
    sql = 'SELECT * FROM words'
    cur.execute(sql)

    result = []
    for item in cur.fetchall():
        result.append({
            'word': item[0],
            'kana': item[1],
            'source': item[2],
            'content': json.loads(item[3]),
            'created_time': item[4],
        })
    with open(file, 'w', encoding='utf8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def search_word_from_dict(word):
    sql = f'SELECT * FROM main WHERE keyword="{word}"'
    result = []
    for dictionary in dictionaries:
        cur = dictionary['conn'].cursor()
        cur.execute(sql)

        for item in cur.fetchall():
            result.append({
                'keyword': item[0],
                'link': item[1],
                'content': item[2]
            })
    return result
