import sqlite3
import time
import json

conn = sqlite3.connect('favorites.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS words
           (word TEXT,
            kana TEXT,
            source TEXT,
            content TEXT,
            created_time INTEGER);''')


def save_word(word, kana, source, content):
    cur.execute(
        'INSERT INTO words VALUES (?,?,?,?,?)',
        (word, kana, source, content, int(round(time.time() * 1000)))
    )
    conn.commit()


def list_words(word):
    sql = f'SELECT * FROM words WHERE word="{word}" OR kana="{word}"'
    cur.execute(sql)
    return cur.fetchall()


def get_by_word_and_kana(word, kana):
    sql = f'SELECT * FROM words WHERE word="{word}" AND kana="{kana}"'
    cur.execute(sql)
    return cur.fetchall()


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
