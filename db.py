import sqlite3
import time

conn = sqlite3.connect('favorites.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS words
           (word TEXT,
            source TEXT,
            content TEXT,
            created_time INTEGER);''')


def save_word(word, source, content):
    cur.execute(
        'INSERT INTO words VALUES (?,?,?,?)',
        (word, source, content, int(round(time.time() * 1000)))
    )
    conn.commit()


def list_words(word):
    sql = f'SELECT * FROM words WHERE word={word}'
    cur.execute(sql)
    return cur.fetchall()


def is_favorite(word):
    try:
        sql = f'SELECT * FROM words WHERE word={word}'
        cur.execute(sql)
        return cur.fetchall()
    except Exception:
        return None
