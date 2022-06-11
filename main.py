import sys
import logging

from PyQt5 import QtWidgets, QtNetwork
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QLabel,
    QCheckBox,
)
from PyQt5.QtCore import QSize, Qt, QUrl, QObject, QThread, pyqtSignal
import keyboard

from utils import parse_hujiang_html


logging.basicConfig(
    format='%(levelname)s - %(asctime)s - %(message)s', 
    filename='app.log', 
    filemode='a',
    encoding='utf8',
    level=logging.INFO
)

class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.init_ui()

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.search.connect(self.search)
        self.worker.show_window.connect(self.show_window)

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.copy_text = ''

    def init_ui(self):
        self.setMinimumSize(QSize(400, 240))
        self.setWindowTitle("Clipboard search")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        vbox = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.addItem('Waiting copy')
        self.list_widget.itemDoubleClicked.connect(self.on_list_item_clicked)

        vbox.addWidget(self.list_widget)
        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setCentralWidget(main_widget)

        self.show()

    def search(self):
        self.copy_text = QApplication.clipboard().text()
        if self.copy_text:
            logging.info(f'Search: {self.copy_text}')
            self.show_window()
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
            "cookie": "HJ_UID=5df5cfc1-0b21-950e-0a2a-aeba7e3a2fa7; TRACKSITEMAP=3; _UZT_USER_SET_106_0_DEFAULT=2|6ed2e0a3900e22cb93d3dd68d679fad2; acw_tc=76b20f7616524644555637605e354ddb0a9fd34d9a07c51841838fd806ddd5; HJ_CST=0; _SREF_3=https://dict.hjenglish.com/; _REF=https://dict.hjenglish.com/; HJ_SID=ygaq09-0c63-48fb-afee-d54d00fed793; HJ_SSID_3=ygaq09-eebd-4102-b634-f5e66ff1fade; HJ_CSST_3=1; _SREG_3=dict.hjenglish.com||xiaodi_site|domain; _REG=dict.hjenglish.com||xiaodi_site|domain",
            "Referer": "https://dict.hjenglish.com/jp/jc/%E3%81%84",
            "Referrer-Policy": "no-referrer-when-downgrade"
        }

        url = 'https://dict.hjenglish.com/jp/jc/' + word
        req = QtNetwork.QNetworkRequest(QUrl(url))
        for k in HEADERS:
            req.setRawHeader(bytes(k, 'utf-8'), bytes(HEADERS[k], 'utf-8'))

        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.handle_resp)
        self.nam.get(req)

    def handle_resp(self, resp):
        err = resp.error()

        if err == QtNetwork.QNetworkReply.NoError:
            bytes_string = resp.readAll()
            result = parse_hujiang_html(str(bytes_string, 'utf-8'))

            self.list_widget.clear()
            if len(result) > 0:
                for word in result:
                    item = QListWidgetItem()
                    widget = QWidget()
                    text = QLabel(str(word))
                    check = QCheckBox()
                    check.stateChanged.connect(
                        lambda state: self.on_box_checked(state, word)
                    )
                    layout = QHBoxLayout()
                    layout.addWidget(check)
                    layout.addWidget(text)
                    
                    layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
                    widget.setLayout(layout)
                    item.setSizeHint(widget.sizeHint())

                    self.list_widget.addItem(item)
                    self.list_widget.setItemWidget(item, widget)

                self.copy_to_clipboard(str(result[0]))
            else:
                self.list_widget.addItem('Not Found.')
        else:
            logging.error(resp.errorString())

    def show_window(self):
        if self.isMinimized() and self.copy_text:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.showNormal()

    def copy_to_clipboard(self, text):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text + '\n', mode=cb.Clipboard)

    def on_list_item_clicked(self, item: QListWidgetItem):
        widget = self.list_widget.itemWidget(item)
        lebel = widget.findChild(QLabel)
        self.copy_to_clipboard(lebel.text())
        QMessageBox.information(self, 'Info', 'Copied!')

    def on_box_checked(self, state, word):
        if state == Qt.Checked:
            logging.info('Check: ' + str(word).replace('\n', ''))
        else:
            logging.info('Cancel: ')


class Worker(QObject):
    search = pyqtSignal()
    show_window = pyqtSignal()

    def run(self):
        keyboard.add_hotkey('ctrl+q', lambda: self.search.emit())
        keyboard.add_hotkey('alt', lambda: self.show_window.emit())
        keyboard.wait()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
