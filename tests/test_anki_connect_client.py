import pytest

from src.services.anki_connect import AnkiConnectClient


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