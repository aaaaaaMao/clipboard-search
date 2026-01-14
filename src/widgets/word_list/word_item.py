from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QTextEdit,
    QSizePolicy,
    QLabel,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QPixmap

from src import anki_client, config_manager
from .search_service import SearchResult


class WordListItem(QWidget):

    anki_tag = 'clipboard-search'

    def __init__(self, item: SearchResult):
        super().__init__()

        self._item = item

        layout = QVBoxLayout(self)

        operations_layout = QHBoxLayout()

        if item.source == 'anki':
            self.check = QCheckBox()
            self.check.stateChanged.connect(
                lambda state: self.on_box_checked(state, item)
            )

            if self.anki_tag in item.raw_data.get('tags', []):
                self.check.setChecked(True)
            operations_layout.addWidget(self.check)

            image = QPixmap(config_manager.get_image_file_path('volume.png'))
            image = image.scaled(15, 15, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            self.audio = QLabel()
            self.audio.setPixmap(image)
            self.audio.mousePressEvent = lambda _: self.on_play_audio()
            operations_layout.addWidget(self.audio)

            operations_layout.addStretch(1)

        layout.addLayout(operations_layout)

        self.html_content = QTextEdit()
        self.html_content.setHtml(item.html_content)

        self.html_content.setReadOnly(True)

        self.html_content.setReadOnly(True)
        self.html_content.setFrameShape(QTextEdit.NoFrame)
        self.html_content.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.html_content.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.html_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # 根据内容调整高度
        self.html_content.document().setTextWidth(self.html_content.viewport().width())
        doc_height = self.html_content.document().size().height()
        total_height = int(int(doc_height) * 1.25)
        self.html_content.setFixedHeight(min(total_height, 300))

        layout.addWidget(self.html_content)
        layout.setSizeConstraint(
            QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint
        )

    def on_box_checked(self, state, item: SearchResult):
        if item.source != 'anki':
            return
        
        if state == Qt.Checked:
            succeed = anki_client.add_tags([item.id], [self.anki_tag])
            self.check.setChecked(succeed)
        else:
            succeed = anki_client.remove_tags([item.id], [self.anki_tag])
            self.check.setChecked(not succeed)

    def on_play_audio(self):
        if self._item.source != 'anki':
            return

        audio_file_path = anki_client.get_audio_file_path(self._item.raw_data['audio'])
        if not audio_file_path:
            return

        player = QMediaPlayer()
        player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_file_path)))
        player.play()