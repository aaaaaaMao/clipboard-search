import re
from dataclasses import dataclass

from bs4 import BeautifulSoup


def parse_hujiang_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    panes = soup.find_all(class_='word-details-pane-header')

    result = []
    for pane in panes:
        word = pane.find(class_='word-info').h2.get_text()
        pronounces_div = pane.find(class_='pronounces')
        pronounces = pronounces_div.find_all('span')[0].get_text()
        simple_div = pane.find(class_='simple')

        word_type = ''
        translation = []

        word_type_h2 = simple_div.find_all('h2')
        translation_ul = simple_div.find_all('ul')

        if word_type_h2 and len(word_type_h2):
            for i in range(len(word_type_h2)):
                word_type = ''
                translation = []

                word_type = word_type_h2[i].get_text()

                for li in translation_ul[i].find_all('li'):
                    translation.append(li.get_text())
                if len(translation) == 1:
                    # tran_ = translation[0].replace('；', '；\n')
                    translation = [re.sub(r'\d+\.\s*', '', translation[0])]

                pronounces = re.sub(r'\[|\]', '', pronounces)
                result.append(
                    JPWordHj(word, pronounces, word_type, translation))
        else:
            pronounces = re.sub(r'\[|\]', '', pronounces)
            result.append(JPWordHj(word, pronounces, word_type, translation))

    return result


@dataclass
class JPWordHj:
    word: str
    pronounces: str
    word_type: str
    translation: str

    def __str__(self) -> str:
        word = self.word
        if self.pronounces != word:
            word += f'({self.pronounces})'
        return '\n'.join([
            word,
            self.word_type,
            '---',
            '\n'.join(self.translation)
        ])
