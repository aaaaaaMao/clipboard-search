from peewee import *

db = SqliteDatabase('data/favorites.db')

class JPWord(Model):
    id = AutoField(primary_key=True, index=True)
    word = TextField(index=True)
    kana = TextField(index=True)
    source = TextField()
    content = TextField()
    created_time = DateTimeField()

    class Meta:
        table_name = 'jp_words'
        database = db
        indexes = (
            (('word', 'kana', 'source'), True),
        )

db.connect()
db.create_tables([JPWord], safe=True)