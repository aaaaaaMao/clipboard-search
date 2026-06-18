from typing import List, Dict
import re
from bs4 import BeautifulSoup, NavigableString


def trim(content: str, remove_new_line=False) -> str:
    if remove_new_line:
        return re.sub(r'(\r\n|\n)+', '', content).strip()
    else:
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
        data.append('--- ---')
        data.append('\n'.join(item['meanings']))
        if len(item['subheadwords']) > 0:
            data.append('--- subheadwords ---')
            data.append('\n'.join(item['subheadwords']))

        result.append('\n'.join(data))
    return '\n\n'.join(result)


kana = {
    'あ': 'ア', 'い': 'イ', 'う': 'ウ', 'え': 'エ', 'お': 'オ',
    'か': 'カ', 'き': 'キ', 'く': 'ク', 'け': 'ケ', 'こ': 'コ',
    'さ': 'サ', 'し': 'シ', 'す': 'ス', 'せ': 'セ', 'そ': 'ソ',
    'た': 'タ', 'ち': 'チ', 'つ': 'ツ', 'て': 'テ', 'と': 'ト',
    'な': 'ナ', 'に': 'ニ', 'ぬ': 'ヌ', 'ね': 'ネ', 'の': 'ノ',
    'は': 'ハ', 'ひ': 'ヒ', 'ふ': 'フ', 'へ': 'ヘ', 'ほ': 'ホ',
    'ま': 'マ', 'み': 'ミ', 'む': 'ム', 'め': 'メ', 'も': 'モ',
    'や': 'ヤ', 'ゆ': 'ユ', 'よ': 'ヨ',
    'ら': 'ラ', 'り': 'リ', 'る': 'ル', 'れ': 'レ', 'ろ': 'ロ',
    'わ': 'ワ', 'を': 'ヲ',
    'ん': 'ン',

    'が': 'ガ', 'ぎ': 'ギ', 'ぐ': 'グ', 'げ': 'ゲ', 'ご': 'ゴ',
    'ざ': 'ザ', 'じ': 'ジ', 'ず': 'ズ', 'ぜ': 'ゼ', 'ぞ': 'ゾ',
    'だ': 'ダ', 'ぢ': 'ヂ', 'づ': 'ヅ', 'で': 'デ', 'ど': 'ド',
    'ば': 'バ', 'び': 'ビ', 'ぶ': 'ブ', 'べ': 'ベ', 'ぼ': 'ボ',
    'ぱ': 'パ', 'ぴ': 'ピ', 'ぷ': 'プ', 'ぺ': 'ペ', 'ぽ': 'ポ',

    'ゃ': 'ャ', 'ゅ': 'ュ', 'ょ': 'ョ',

    'っ': 'ッ',
}

invert_kana = {value: key for key, value in kana.items()}


def transform_kana(text: str) -> List[str]:
    result = [text]
    katagan = []
    hiragana = []
    for c in text:
        if c not in kana and c not in invert_kana:
            return result
        if c in kana:
            katagan.append(kana[c])
        if c in invert_kana:
            hiragana.append(invert_kana[c])
    if katagan:
        result.append(''.join(katagan))
    if hiragana:
        result.append(''.join(hiragana))

    return result

def _has_purple_style(style: str) -> bool:
    """Check if a style string contains purple color (named or hex)."""
    normalized = re.sub(r'\s*:\s*', ':', style).lower().strip()
    return 'color:purple' in normalized or 'color:#800080' in normalized


def _is_pitch_char(ch: str) -> bool:
    """Check if a character is a pitch notation (circled number including ⓪)."""
    if len(ch) != 1:
        return False
    cp = ord(ch)
    return cp == 0x24EA or (0x2460 <= cp <= 0x2473)


def _extract_pitch_from_spans(parent) -> str:
    """Try to find pitch (circled number) in purple spans, fallback to any circled number."""
    # First: purple span that looks like pitch (single pitch character)
    for span in parent.find_all('span'):
        text = span.get_text().strip()
        style = span.get('style', '')
        if _has_purple_style(style) and _is_pitch_char(text):
            return text
    # Second: any span that looks like a pitch character
    for span in parent.find_all('span'):
        text = span.get_text().strip()
        if _is_pitch_char(text):
            return text
    # Third: any purple span (less reliable)
    for span in parent.find_all('span'):
        text = span.get_text().strip()
        style = span.get('style', '')
        if _has_purple_style(style) and text:
            return text
    return ''


def _extract_pos_from_element(parent) -> str:
    """Try to find PoS (contains ·) in purple spans, fallback to text-based."""
    # First: purple span with · in text (strongest signal for PoS)
    for span in parent.find_all('span'):
        text = span.get_text().strip()
        style = span.get('style', '')
        if _has_purple_style(style) and '·' in text:
            return text
    # Second: any span with · (PoS marker)
    for span in parent.find_all('span'):
        text = span.get_text().strip()
        if '·' in text:
            return text
    # Third: any purple span
    for span in parent.find_all('span'):
        text = span.get_text().strip()
        style = span.get('style', '')
        if _has_purple_style(style) and text:
            return text
    return ''


def _find_heading_element(soup) -> dict:
    """Find the heading element and extract furigana/kanji/pitch."""
    result = {}
    # Try known heading tags
    heading = soup.find('h3') or soup.find('div')
    if not heading:
        return result

    # Furigana: prefer direct text node before first span (e.g. <h3>てんせい<span>⓪</span>【転生】</h3>)
    if heading.contents:
        first = heading.contents[0]
        if isinstance(first, NavigableString):
            text = first.strip()
            if text:
                result['furigana'] = text
    if not result.get('furigana'):
        spans = heading.find_all('span')
        if spans:
            result['furigana'] = spans[0].get_text().strip()

    result['pitch'] = _extract_pitch_from_spans(heading)

    full_text = heading.get_text()
    match = re.search(r'【(.+?)】', full_text)
    if match:
        result['kanji'] = match.group(1).strip()
    else:
        # If no 【】, check last span for CJK text
        spans = heading.find_all('span')
        if len(spans) > 1:
            last_text = spans[-1].get_text().strip()
            if re.search(r'[\u4e00-\u9fff]', last_text):
                result['kanji'] = last_text

    return result


def _find_meaning_element(soup) -> dict:
    """Find the meaning/definition element and extract PoS and definition."""
    result = {}
    # Try known meaning selectors
    meaning = (
        soup.find('p', class_='meaning') or
        soup.find('div', class_='meaning') or
        soup.find_all('div')[1] if len(soup.find_all('div')) > 1 else None
    )
    if not meaning:
        return result

    result['pos'] = _extract_pos_from_element(meaning)

    full_text = meaning.get_text()
    if result['pos']:
        pos_idx = full_text.find(result['pos'])
        if pos_idx >= 0:
            result['def_cn'] = full_text[pos_idx + len(result['pos']):].strip()
    else:
        result['def_cn'] = re.sub(r'^\d+\s*', '', full_text).strip()

    return result


def _find_sentence_element(soup) -> dict:
    """Find the example sentence element and extract JP and CN parts."""
    result = {}
    # Try known sentence selectors
    ex_elem = (
        soup.find('div', class_='sec ex') or
        soup.find('div', class_='example') or
        soup.find('p', class_='example')
    )
    if not ex_elem:
        return result

    # Check for dedicated sub-elements first (PJE4 format)
    jpexam = ex_elem.find('jpexam')
    cnexam = ex_elem.find('cnexam') or ex_elem.find('enexam')
    if jpexam:
        result['sent_jp'] = jpexam.get_text().strip()
    if cnexam:
        result['sent_cn'] = cnexam.get_text().strip()
    if result.get('sent_jp') and result.get('sent_cn'):
        return result

    # Fallback: slash-separated format
    text = ex_elem.get_text().strip()
    text = re.sub(r'^▸\s*', '', text)
    text = re.sub(r'^▷\s*', '', text)
    if '/' in text:
        parts = text.split('/', 1)
        result['sent_jp'] = parts[0].strip()
        result['sent_cn'] = parts[1].strip()

    return result


def parse_mdict_html(content: str) -> Dict[str, str]:
    soup = BeautifulSoup(content, 'html.parser')

    result = {
        "VocabFurigana": "",
        "VocabKanji": "",
        "VocabPitch": "",
        "VocabPoS": "",
        "VocabDefCN": "",
        "SentKanji1": "",
        "SentDef1": "",
    }

    heading = _find_heading_element(soup)
    result["VocabFurigana"] = heading.get('furigana', '')
    result["VocabKanji"] = heading.get('kanji', '')
    result["VocabPitch"] = heading.get('pitch', '')

    meaning = _find_meaning_element(soup)
    result["VocabPoS"] = meaning.get('pos', '')
    def_cn = meaning.get('def_cn', '').rstrip('。')
    result["VocabDefCN"] = def_cn.replace('。', '；')

    sentence = _find_sentence_element(soup)
    sent_jp = sentence.get('sent_jp', '')
    if result["VocabKanji"]:
        sent_jp = sent_jp.replace('～', result["VocabKanji"])
    result["SentKanji1"] = sent_jp
    result["SentDef1"] = sentence.get('sent_cn', '')

    return result


invalid_tokens = [
    ' ', '　', '、', '。', '、', '・', '「', '」', '（', '）',
    '【', '】', '〔', '〕', '［', '］', '《', '》', '〈', '〉',
    '\n', '\r', '\t', '!', '?', '…', 'ー', '゛', '゜', 'ヽ', 'ヾ',
    '『', '』',
]