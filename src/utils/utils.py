import re
from bs4 import BeautifulSoup


def trim(content: str):
    return content.strip().replace('\r\n', '\n')


def extract_kana(content: str):
    soup = BeautifulSoup(content, 'html.parser')
    div = soup.find_all('div')
    if len(div) == 0:
        return ''
    span = div[0].find_all('span')
    if len(span) == 0:
        return ''
    return trim(span[0].get_text())


def extract_meanings(content: str):
    soup = BeautifulSoup(content, 'html.parser')
    excf_div_list = soup.find_all('div', class_='excf')
    result = []
    for excf_div in excf_div_list:
        item = {
            'kana': '',
            'kanji': '',
            'meanings': [],
            'subheadwords': []
        }
        word_text = excf_div.h3.extract().get_text()
        pattern = re.compile('([^【]*)(【(.*)】)?')
        match = pattern.search(word_text)
        if match:
            if match.group(1):
                item['kana'] = match.group(1)
            if match.group(3):
                item['kanji'] = match.group(3)

        meaning_p_list = excf_div.find_all('p', 'meaning')
        for meaning_p in meaning_p_list:
            text = trim(meaning_p.get_text())
            if re.search('^\d+', text) and trim(re.sub('^\d+', '', text)) == '':
                continue
            else:
                item['meanings'].append(text.replace('；', '\n'))
        subheadword_p_list = excf_div.find_all('p', 'subheadword')
        for subheadword_p in subheadword_p_list:
            item['subheadwords'].append(trim(subheadword_p.get_text()))

        data = []
        if item['kanji'] != '':
            data.append(f'{item["kana"]}【{item["kanji"]}】')
        else:
            data.append(item["kana"])
        data.append('---')
        data.append('\n'.join(item['meanings']))
        if len(item['subheadwords']) > 0:
            data.append('--- subheadwords ---')
            data.append('\n'.join(item['subheadwords']))

        result.append('\n'.join(data))
    return '\n\n'.join(result)
