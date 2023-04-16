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
