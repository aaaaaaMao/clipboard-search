import re
from dataclasses import dataclass

from bs4 import BeautifulSoup


def parse_hujiang_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    panes = soup.find_all(class_='word-details-pane-header')

    result = []
    for pane in panes:
        word = pane.find(class_='word-info').h2.get_text()
        pronounces = pane.find(class_='pronounces').find_all('span')[
            0].get_text()
        simple = pane.find(class_='simple')

        word_type = ''
        translation = []

        if simple.h2:
            word_type = simple.h2.get_text()

            for li in simple.ul.find_all('li'):
                translation.append(li.get_text())
            if len(translation) == 1:
                # tran_ = translation[0].replace('；', '；\n')
                translation = [re.sub(r'\d+\.\s*', '', translation[0])]

        pronounces = re.sub(r'\[|\]', '', pronounces)
        result.append(JPWord(word, pronounces, word_type, translation))

    return result


@dataclass
class JPWord:
    word: str
    pronounces: str
    word_type: str
    translation: str

    def __str__(self) -> str:
        return '\n'.join([
            self.word + f'({self.pronounces})',
            self.word_type,
            '---',
            '\n'.join(self.translation)
        ])
