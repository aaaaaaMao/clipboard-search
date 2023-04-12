from PyQt5.QtWidgets import (
    QListWidget
)

from src.services.fugashi_tagger import tag


class TokenList(QListWidget):

    def __init__(self, height=75):
        super().__init__()
        self.setMaximumHeight(height)

    def tokenizer(self, text: str):
        self.clear()
        tokens = set()
        for item in tag(text):
            word_orth_base = item['orthBase']
            if not word_orth_base in tokens:
                self.addItem(word_orth_base)
                tokens.add(word_orth_base)
        return list(tokens)
