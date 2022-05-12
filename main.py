import sys
from PyQt5 import QtWidgets, QtNetwork
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit
)
from PyQt5.QtCore import QSize, Qt, QUrl
import keyboard

from utils import handle_hujiang_html


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(400, 240))
        self.setWindowTitle("Clipboard search")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.text_editor = QPlainTextEdit(self)
        self.text_editor.insertPlainText('Waiting copy')
        self.text_editor.move(10, 10)
        self.text_editor.resize(380, 220)
        # self.text_editor.setFocusPolicy(Qt.NoFocus)

        self.copy_text = ''

        QApplication.clipboard().dataChanged.connect(self.read_clipboard)

    def read_clipboard(self):
        self.copy_text = QApplication.clipboard().text()

        if self.text_editor.toPlainText() != self.copy_text:

            if self.isMinimized():
                keyboard.wait('alt')
                self.setWindowFlags(Qt.WindowStaysOnTopHint)
                self.showNormal()
            else:
                keyboard.wait('q')
                self.search_from_hujiang(self.copy_text)

    def search_from_hujiang(self, word):
        HEADERS = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "zh-CN,zh;q=0.9",
            "if-none-match": "\"69e1-2qJE+HGIwbzci5d+JKQcu+1SlwM\"",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "cookie": "HJ_UID=5df5cfc1-0b21-950e-0a2a-aeba7e3a2fa7; TRACKSITEMAP=3; _UZT_USER_SET_106_0_DEFAULT=2|6ed2e0a3900e22cb93d3dd68d679fad2; acw_tc=76b20f4416523625975416461eb48557179c94e5390cf486f1691647ffca1c; HJ_CST=0; _REF=https%3A%2F%2Fdict.hjenglish.com%2Fjp%2Fjc%2F%25E8%258B%25A5%25E3%2581%2584; HJ_SID=6tx4c3-05d6-4f5c-90c7-14ae640da641; HJ_SSID_3=6tx4c3-8ec4-4f65-8f72-2ae478068418; HJ_CSST_3=1; _SREG_3=dict.hjenglish.com%7C%7Cxiaodi_site%7Cdomain; _REG=dict.hjenglish.com%7C%7Cxiaodi_site%7Cdomain; _SREF_3=https%3A%2F%2Fdict.hjenglish.com%2Fjp%2Fjc%2F%E8%8B%A5%E3%81%84",
            "Referer": "https://dict.hjenglish.com/jp/jc/%E3%81%84",
            "Referrer-Policy": "no-referrer-when-downgrade"
        }

        url = 'https://dict.hjenglish.com/jp/jc/' + word
        req = QtNetwork.QNetworkRequest(QUrl(url))
        for k in HEADERS:
            req.setRawHeader(bytes(k, 'utf-8'), bytes(HEADERS[k], 'utf-8'))

        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.write_clipboard)
        self.nam.get(req)

    def write_clipboard(self, resp):
        err = resp.error()
        self.text_editor.setPlainText('')
        if err == QtNetwork.QNetworkReply.NoError:
            bytes_string = resp.readAll()
            text = handle_hujiang_html(str(bytes_string, 'utf-8'))
            self.text_editor.insertPlainText(text)

            cb = QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(text + '\n', mode=cb.Clipboard)
        else:
            print(resp.errorString())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
