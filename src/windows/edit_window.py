from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QDialog,
    QPushButton,
    QFormLayout,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from src import anki_client


class EditWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('编辑')
        self.resize(300, 400)

        self.audio_sources = []
        self.selected_audio = None
        self.player = QMediaPlayer()

        self.main_layout = QFormLayout()

        self.input = {}
        self.fields = {
            "汉字": "VocabKanji",
            "假名": "VocabFurigana",
            "音调": "VocabPitch",
            "词性": "VocabPoS",
            "中文释义": "VocabDefCN",
            "补充信息": "VocabPlus",
            "例句汉字": "SentKanji1",
            "例句假名": "SentFurigana1",
            "例句释义": "SentDef1",
        }

        for field in self.fields:
            line_edit = QLineEdit()
            self.input[field] = line_edit

            self.main_layout.addRow(field, line_edit)

        self.audio_layout = QVBoxLayout()
        self.audio_label = QLabel('音频')
        self.audio_label.mousePressEvent = lambda _: self.on_audio_label_click()
        self.main_layout.addRow(self.audio_label, self.audio_layout)

        self.save_btn = QPushButton('保存')
        self.save_btn.clicked.connect(self.save_word)
        self.main_layout.addRow(self.save_btn)

        # self.main_layout.addStretch(1)
        self.setLayout(self.main_layout)

    def show_window(self, word=''):
        for field in self.fields:
            self.input[field].clear()

        self.input['汉字'].setText(word)        

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.show()

    def save_word(self):
        pass

    def on_audio_label_click(self):
        term = self.input['汉字'].text()
        reading = self.input['假名'].text() or term

        self.audio_sources = anki_client.list_audio_sources(term, reading)
        print(self.audio_sources)
        
        for source in self.audio_sources:
   
            audio_label = QLabel(source['name'])
            audio_label.mousePressEvent = lambda _, url=source['url']: self.on_play_audio(url)

            self.audio_layout.addWidget(audio_label)


    def on_play_audio(self, url):
        self.selected_audio = url
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.player.play()