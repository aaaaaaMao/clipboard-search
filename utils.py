import re
from bs4 import BeautifulSoup


def handle_hujiang_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    pane = soup.find(class_='word-details-pane-header')
    if not pane:
        return 'Not Found'
    word_info = pane.find(class_='word-info').h2.get_text()
    pronounces = pane.find(class_='pronounces').find_all('span')[0].get_text()
    simple = pane.find(class_='simple')

    type_ = ''
    translation = []

    if simple.h2:
        type_ = simple.h2.get_text()

        for li in simple.ul.find_all('li'):
            translation.append(li.get_text())
        if len(translation) == 1:
            tran_ = translation[0].replace('；', '；\n')
            translation = [re.sub(r'\d+\.\s*', '', tran_)]

    pronounces = re.sub(r'\[|\]', '', pronounces)
    return '\n'.join([
        word_info + f'({pronounces})',
        type_,
        '---',
        '\n'.join(translation)
    ])
