import pytest
import os

from src.utils.utils import parse_mdict_html


def read_mock(name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), 'mock', name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def test_parse_mdict_html_basic():
    html = read_mock('dict_entry_1.html')

    result = parse_mdict_html(html)

    assert result["VocabFurigana"] == 'てんせい'
    assert result["VocabKanji"] == '転生'
    assert result["VocabPitch"] == '⓪'
    assert result["VocabPoS"] == '名·自サ'
    assert result["VocabDefCN"] == '（佛）轉世'
    assert result["SentKanji1"] == 'こんど生まれる時は男に～したい'
    assert result["SentDef1"] == '希望來生轉世成為男人'


def test_parse_mdict_html_with_style_prefix():
    """HTML may have a <style> tag prepended (how SearchService stores mdict content)."""
    html = '<style>body { margin: 0; }</style>' + read_mock('dict_entry_1.html')

    result = parse_mdict_html(html)

    assert result["VocabFurigana"] == 'てんせい'
    assert result["VocabKanji"] == '転生'
    assert result["VocabPitch"] == '⓪'
    assert result["VocabPoS"] == '名·自サ'
    assert result["VocabDefCN"] == '（佛）轉世'
    assert result["SentKanji1"] == 'こんど生まれる時は男に～したい'
    assert result["SentDef1"] == '希望來生轉世成為男人'


def test_parse_mdict_html_empty():
    result = parse_mdict_html('<div></div>')

    assert result["VocabFurigana"] == ''
    assert result["VocabKanji"] == ''
    assert result["VocabPitch"] == ''
    assert result["VocabPoS"] == ''
    assert result["VocabDefCN"] == ''
    assert result["SentKanji1"] == ''
    assert result["SentDef1"] == ''


def test_parse_mdict_html_pje4_format():
    """PJE4 class-based format (h3, .meaning, .example with jpexam/cnexam)."""
    html = read_mock('dict_entry_2.html')

    result = parse_mdict_html(html)

    assert result["VocabFurigana"] == 'てんせい'
    assert result["VocabKanji"] == '転生'
    assert result["VocabPitch"] == '⓪'
    assert result["VocabPoS"] == '名·自サ'
    assert result["VocabDefCN"] == '（佛）轉世'
    assert result["SentKanji1"] == 'こんど生まれる時は男に～したい'
    assert result["SentDef1"] == '希望來生轉世成為男人'


def test_parse_mdict_html_style_no_space():
    """Style string without space after colon (color:purple)."""
    html = '''
<div style="margin-left:0.2em">
  <span style="color:purple;font-weight:bold">てんせい</span>
  <span style="color:purple">⓪</span>
  <span>【転生】</span>
</div>
<div style="margin-left:1em">
  <span style="color:purple">名·自サ</span>（佛）轉世。
</div>
<div class="sec ex" style="color:gray">
  ▸ こんど生まれる時は男に～したい / 希望來生轉世成為男人。
</div>
'''
    result = parse_mdict_html(html)

    assert result["VocabFurigana"] == 'てんせい'
    assert result["VocabKanji"] == '転生'
    assert result["VocabPitch"] == '⓪'
    assert result["VocabPoS"] == '名·自サ'
    assert result["VocabDefCN"] == '（佛）轉世'
    assert result["SentKanji1"] == 'こんど生まれる時は男に～したい'
    assert result["SentDef1"] == '希望來生轉世成為男人'
