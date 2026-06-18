import re
import hashlib

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QDialog,
    QPushButton,
    QFormLayout,
)
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from src import anki_client


class AudioFetchThread(QThread):
    result = pyqtSignal(list)

    def __init__(self, term, reading):
        super().__init__()
        self._term = term
        self._reading = reading

    def run(self):
        sources = anki_client.list_audio_sources(self._term, self._reading)
        self.result.emit(sources)


class EditWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('编辑')
        self.resize(300, 400)

        self.audio_sources = []
        self.selected_audio_source = None
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
        self._field_labels = {v: k for k, v in self.fields.items()}

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

        self.setLayout(self.main_layout)

    def show_window(self, word='', field_data: dict = None):
        self.save_btn.setDisabled(True)
        self.selected_audio_source = None
        self.audio_sources = []

        self.clear_audio_layout()

        for field in self.fields:
            self.input[field].clear()

        if field_data:
            for anki_field, value in field_data.items():
                label = self._field_labels.get(anki_field)
                if label:
                    self.input[label].setText(value)
        else:
            self.input['汉字'].setText(word)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.show()

        if self.input['汉字'].text() and self.input['中文释义'].text():
            self._start_audio_fetch(auto_play=True)

    def save_word(self):
        deck_name = "额外"
        model_name = "JLPT-NEW"

        fields = {}
        for field in self.fields:
            value = self.input[field].text().strip()
            if value:
                fields[self.fields[field]] = re.sub(r' ', '&nbsp', value) if ' ' in value else value

        tags = ["clipboard-search"]
        audio = None
        if self.selected_audio_source:
            audio = {
                "filename": self.selected_audio_source['name'], 
                "url": self.selected_audio_source['url'],
                "fields": ["VocabAudio"]
            }
            
            audio['filename'] = re.sub(r' ', '-', f'{fields["VocabKanji"]}_{fields["VocabFurigana"]}━{audio['filename']}.mp3')
            audio['skipHash'] = hashlib.md5(audio['filename'].encode('utf-8')).hexdigest()
        
        fields['NoteID'] = hashlib.md5(f'{deck_name}:{fields["VocabKanji"]}_{fields["VocabFurigana"]}'.encode('utf-8')).hexdigest()

        if 'VocabKanji' not in fields or 'VocabFurigana' not in fields:
            return

        anki_client.add_note(deck_name, model_name, fields, tags, audio)
        self.close()

    def clear_audio_layout(self):
        if self.audio_layout is not None:
            while self.audio_layout.count():
                item = self.audio_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def on_audio_label_click(self):
        self._start_audio_fetch(auto_play=False)

    def _start_audio_fetch(self, auto_play):
        term = self.input['汉字'].text()
        reading = self.input['假名'].text() or term

        self.clear_audio_layout()

        self._audio_thread = AudioFetchThread(term, reading)
        self._audio_thread.result.connect(lambda sources, ap=auto_play: self._on_audio_ready(sources, ap))
        self._audio_thread.finished.connect(self._audio_thread.deleteLater)
        self._audio_thread.start()

    def _on_audio_ready(self, sources, auto_play):
        self.audio_sources = sources
        self.save_btn.setDisabled(False)

        for source in sources:
            audio_label = QLabel(source['name'])
            audio_label.mousePressEvent = lambda _, s=source: self.on_play_audio(s)
            self.audio_layout.addWidget(audio_label)

        if auto_play and sources:
            self.on_play_audio(sources[0])


    def on_play_audio(self, source):
        self.selected_audio_source = source
        self.player.setMedia(QMediaContent(QUrl(source['url'])))
        self.player.play()