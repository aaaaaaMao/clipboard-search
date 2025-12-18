import pytest

from src.services.anki_connect import AnkiConnectClient, AnkiJPWord


@pytest.fixture
def client():
    """
    提供一个 AnkiConnectClient 实例作为 pytest fixture。
    """
    return AnkiConnectClient()

# --- 测试用例（连接 anki 进行测试） ---

def test_successful_response_deck_names(client):
    """
    测试获取所有牌组名称的成功响应。
    """
    result_data = client.invoke("deckNames")

    assert isinstance(result_data, dict)
    assert "Default" in result_data['result'] # 假定 "Default" 牌组总是存在

def test_jp_words(client):
    word = 'あっさり'
    result = client.search_jp_words(word)

    assert result == [
        AnkiJPWord(
            note_id=1706702429737,
            kanji='あっさり',
            furigana='あっさり',
            pitch='③',
            pos='副・自動3',
            def_cn='清淡；朴素；（性格）爽快；简单',
            extra='',
            audio='[sound:あっさり_アッサ＼リ_3_NHK-2016-local.mp3]',
            tags=['NEW-JLPT-v2::N1::N1核心', 'NEW-JLPT-v2::v25.07.27', 'NEW-JLPT-v2::オノマトペ', '日语词汇新思维']
        )
    ]