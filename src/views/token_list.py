from PyQt5.QtWidgets import (
    QListWidget
)

from src.services.fugashi_tagger import tag
from src.utils.utils import kana, invert_kana


class TokenList(QListWidget):

    def __init__(self, height=75):
        super().__init__()
        self.setMaximumHeight(height)

    def tokenizer(self, text: str):
        self.clear()
        dup = set()

        katagan = [x if x not in kana else kana[x] for x in text]
        hiragana = [x if x not in invert_kana else invert_kana[x]
                    for x in text]

        tokens = []
        for t in [text, ''.join(katagan), ''.join(hiragana)]:
            for item in tag(t):
                word_orth_base = item['orthBase']
                if word_orth_base and (word_orth_base not in dup):
                    dup.add(word_orth_base)
                    self.addItem(word_orth_base)
                    tokens.append(word_orth_base)
        if text not in dup:
            self.addItem(text)
        return tokens
