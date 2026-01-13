from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QTextEdit,
    QSizePolicy
)
from PyQt5.QtCore import Qt

from src import anki_client
from .search_service import SearchResult


class WordListItem(QWidget):

    anki_tag = 'clipboard-search'

    def __init__(self, item: SearchResult):
        super().__init__()

        layout = QVBoxLayout(self)

        if item.source == 'anki':
            self.check = QCheckBox()
            self.check.stateChanged.connect(
                lambda state: self.on_box_checked(state, item)
            )

            if self.anki_tag in item.raw_data.get('tags', []):
                self.check.setChecked(True)

            layout.addWidget(self.check)

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