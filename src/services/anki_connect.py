import requests


class AnkiConnectClient:
    def __init__(self, url="http://localhost:8765"):
        super().__init__()

        self._url = url

    def invoke(self, action: str, params: dict = {}) -> str:

        payload = {
            "action": action,
            "version": 6,
            "params": params
        }

        r = requests.post(self._url, json=payload)
        return r.json()