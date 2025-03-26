from PyQt5.QtCore import QThread, pyqtSignal

from src import config_manager
from openai import OpenAI

ai = config_manager.get('ai')[0]
client = OpenAI(api_key=ai['api_key'], base_url=ai['base_url'])

class TranslationWorker(QThread):

    translated_sig = pyqtSignal(str)

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def run(self):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一名日语翻译专业，你需要将我提供的内容翻译为中文，并分析句子结构，分析句子结构时，句子中出现的日语汉字需要标出假名注音。"},
                {"role": "user", "content": self.text},
            ],
            stream=False
        )

        self.translated_sig.emit(response.choices[0].message.content)