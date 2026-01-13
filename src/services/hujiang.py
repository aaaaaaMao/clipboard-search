from dataclasses import dataclass
import re

from bs4 import BeautifulSoup
import requests


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


class HuJiangClient():

    def __init__(self, config):
        self.base_url = config['hujiang']['req_url']
        self.headers = config['hujiang']['req_headers']

    def search(self, word) -> list[JPWordHj]:
        url = self.base_url + word

        r = requests.get(url, headers=self.headers)

        return self.parse(r.text)

    def parse(self, text):
        soup = BeautifulSoup(text, 'html.parser')
        panes = soup.find_all(class_='word-details-pane-header')

        result = []
        for pane in panes:
            word = pane.find(class_='word-info').h2.get_text()

            pronounces_div = pane.find(class_='pronounces')
            pronounces = pronounces_div.find_all('span')[0].get_text()
            if pronounces:
                pronounces = re.sub(r'\[|\]', '', pronounces)

            simple_div = pane.find(class_='simple')

            word_type = ''
            translations = []

            word_type_h2 = simple_div.find_all('h2')
            translations_ul = simple_div.find_all('ul')

            if word_type_h2 and len(word_type_h2):
                for i in range(len(word_type_h2)):
                    word_type = ''
                    translations = []

                    word_type = word_type_h2[i].get_text()

                    for li in translations_ul[i].find_all('li'):
                        translations.append(li.get_text())
                    translations = remove_seq(translations)
                    # if len(translations) == 1:
                    #     translations = [
                    #         re.sub(r'\d+\.\s*', '', translations[0])]

                    result.append(
                        JPWordHj(word, pronounces, word_type, translations))
            else:
                if translations_ul and len(translations_ul):
                    for ul in translations_ul:
                        for li in ul.find_all('li'):
                            translations.append(li.get_text())
                    translations = remove_seq(translations)

                result.append(
                    JPWordHj(word, pronounces, word_type, translations))

        return result


def remove_seq(translations):
    if len(translations) == 1:
        return [re.sub(r'\d+\.\s*', '', translations[0])]
    return translations
