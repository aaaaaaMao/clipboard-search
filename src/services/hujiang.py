from dataclasses import dataclass
import re

from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtCore import QUrl, pyqtSignal
from bs4 import BeautifulSoup

from src import logging


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


class HuJiang():

    def __init__(self, config, search_succeed_signal: pyqtSignal):
        self.base_url = config['hujiang']['req_url']
        self.headers = config['hujiang']['req_headers']
        self.search_succeed_signal = search_succeed_signal

    def search(self, word):
        url = self.base_url + word
        req = QNetworkRequest(QUrl(url))
        for k in self.headers:
            req.setRawHeader(bytes(k, 'utf-8'),
                             bytes(self.headers[k], 'utf-8'))

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.handle_resp)
        self.nam.get(req)

    def handle_resp(self, resp):
        err = resp.error()

        if err == QNetworkReply.NoError:
            bytes_string = resp.readAll()
            result = self.parse(str(bytes_string, 'utf-8'))

            self.search_succeed_signal.emit(
                list(map(lambda x: {'source': 'hujiang', 'data': x}, result))
            )
        else:
            logging.error(resp.errorString())

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
