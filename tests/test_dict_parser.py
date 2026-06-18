import pytest
import os

from src.utils.utils import parse_mdict_html


FULL = {
    "VocabFurigana": 'てんせい',
    "VocabKanji": '転生',
    "VocabPitch": '⓪',
    "VocabPoS": '名·自サ',
    "VocabDefCN": '（佛）轉世',
    "SentKanji1": 'こんど生まれる時は男に転生したい',
    "SentDef1": '希望來生轉世成為男人。',
}

EMPTY = {k: '' for k in FULL}


def read_mock(name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), 'mock', name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def test_parse_mdict_html_basic():
    assert parse_mdict_html(read_mock('dict_entry_1.html')) == FULL


def test_parse_mdict_html_with_style_prefix():
    html = '<style>body { margin: 0; }</style>' + read_mock('dict_entry_1.html')
    assert parse_mdict_html(html) == FULL


def test_parse_mdict_html_empty():
    assert parse_mdict_html('<div></div>') == EMPTY


def test_parse_mdict_html_pje4_format():
    assert parse_mdict_html(read_mock('dict_entry_2.html')) == FULL


def test_parse_mdict_html_style_no_space():
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
    assert parse_mdict_html(html) == FULL


def test_parse_mdict_html_middle_period_replacement():
    html = '''
<div style="margin-left:0.2em">
  <span style="color:green;font-weight:bold">てんせい</span>
  <span style="color:purple">⓪</span>
  <span>【転生】</span>
</div>
<div style="margin-left:1em">
  <span style="color:purple">名·自サ</span>（佛）轉世。也作「転生」。
</div>
'''
    result = parse_mdict_html(html)
    assert result["VocabDefCN"] == '（佛）轉世；也作「転生」'
