from PyQt5.QtWidgets import (
    QListWidget
)

from src.services.fugashi_tagger import tag
from src.utils.utils import transform_kana, kana, invert_kana, invalid_tokens


class TokenList(QListWidget):

    def __init__(self, height=75):
        super().__init__()
        self.setMaximumHeight(height)

    def tokenizer(self, text: str):
        self.clear()
        dup = set()

        transformed = transform_kana(text)

        tokens = []
        for t in transformed:
            for item in tag(t):
                word_orth_base = item['orthBase']
                if self.is_invalid_token(word_orth_base):
                    continue
                if word_orth_base and (word_orth_base not in dup):
                    dup.add(word_orth_base)
                    self.addItem(word_orth_base)
                    tokens.append(word_orth_base)

            if t not in dup:
                self.addItem(t)
        return tokens

    def is_invalid_token(self, word):
        return word in invalid_tokens or word in kana or word in invert_kana