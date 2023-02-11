import sys
import logging
import json
import traceback
import os

from PyQt5 import QtWidgets, QtNetwork
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QCheckBox,
    QSystemTrayIcon,
    QLineEdit
)
from PyQt5.QtCore import QSize, Qt, QUrl, QObject, QThread, pyqtSignal, QEvent, QTimer
from PyQt5.QtGui import QIcon, QCursor, QPixmap
import keyboard

from src.views.float_icon_window import FloatIconWindow
from src.views.tray_icon import TrayIcon
from utils.hujiang import parse_hujiang_html, JPWordHj
from utils.mouse_monitor import MouseMonitor
from db import search_word_from_dict
from src.services.jp_word import save_word, get_by_word_and_kana


logging.basicConfig(
    format='%(levelname)s - %(asctime)s - %(message)s',
    filename='app.log',
    filemode='a',
    encoding='utf8',
    level=logging.INFO
)

config = {}
with open('./config.json', 'r', encoding='utf8') as f:
    config = json.load(f)

data_dir = './data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.pos_x = 10
        self.pos_y = 10

        float_icon = QPixmap('./images/battery.png')
        self.icon_window = FloatIconWindow(float_icon)
        self.icon_window.search_signal.connect(self.search)
        self.init_ui()

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.search.connect(self.show_icon_window)
        self.worker.show_window.connect(self.show_window)

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.copy_text = ''

        self.in_main_window = False

        self.installEventFilter(self)
        self.icon_window_timer = QTimer()
        self.icon_window_timer.timeout.connect(
            self.on_show_icon_window_timeout
        )

        self.old_hook = sys.excepthook
        sys.excepthook = self.catch_exceptions

    def init_ui(self):

        self.main_icon = QIcon('./images/battery.png')

        self.setMinimumSize(QSize(400, 240))
        self.setWindowTitle("Clipboard search")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(self.main_icon)

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        search_label = QLabel()
        search_label.setText('search: ')
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(
            lambda: self.search_from_hujiang(self.search_input.text())
        )
        hbox.addWidget(search_label)
        hbox.addWidget(self.search_input)
        vbox.addLayout(hbox)

        self.list_widget = QListWidget()
        self.list_widget.addItem('Waiting copy')
        self.list_widget.itemDoubleClicked.connect(self.on_list_item_clicked)
        vbox.addWidget(self.list_widget)

        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setCentralWidget(main_widget)

        self.tray_icon = TrayIcon(self.main_icon)
        self.tray_icon.show()

    def search(self):
        self.copy_text = QApplication.clipboard().text()
        if self.copy_text:
            logging.info(f'Search: {self.copy_text}')
            self.show_window()
            self.search_input.clear()

            words = search_word_from_dict(self.copy_text)
            if not words or not len(words):
                self.search_from_hujiang(self.copy_text)
            else:
                self.show_word_list(words)

    def search_from_hujiang(self, word):
        HEADERS = config['hujiang']['req_headers']

        url = config['hujiang']['req_url'] + word
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

            self.show_word_list(result)
        else:
            logging.error(resp.errorString())

    def show_word_list(self, words):
        self.list_widget.clear()
        if len(words) > 0:
            for word in words:
                item = QListWidgetItem()
                widget = QWidget()
                text = None

                layout = QHBoxLayout()

                if isinstance(word, JPWordHj):
                    text = QLabel(str(word))
                    check = QCheckBox()
                    if get_by_word_and_kana(word.word, word.pronounces):
                        check.setChecked(True)
                    check.stateChanged.connect(
                        lambda state: self.on_box_checked(state, word)
                    )
                    layout.addWidget(check)
                else:
                    text = QLabel(word['content'])
                layout.addWidget(text)

                layout.setSizeConstraint(
                    QtWidgets.QLayout.SizeConstraint.SetFixedSize
                )
                widget.setLayout(layout)
                size = widget.sizeHint()
                size.setHeight(size.height() + 50)
                item.setSizeHint(size)

                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, widget)
        else:
            self.list_widget.addItem('Not Found.')

    def show_window(self):
        if (self.isMinimized() or not self.isVisible()) and self.copy_text:
            self.move(self.pos_x + 20, self.pos_y)

            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            if self.icon_window.isVisible():
                self.icon_window.close()
            self.showNormal()

    def show_icon_window(self):
        if self.in_main_window:
            return

        pos = QCursor().pos()
        self.pos_x = pos.x() + 20
        self.pos_y = pos.y() - 20

        self.icon_window.move(self.pos_x, self.pos_y)
        if self.isVisible():
            self.hide()
        self.icon_window.show()
        self.icon_window_timer.start(1500)

    def copy_to_clipboard(self, text):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text + '\n', mode=cb.Clipboard)

    def on_list_item_clicked(self, item: QListWidgetItem):
        widget = self.list_widget.itemWidget(item)
        lebel = widget.findChild(QLabel)
        self.copy_to_clipboard(lebel.text())
        # QMessageBox.information(self, 'Info', 'Copied!')

    def on_box_checked(self, state, word):
        if state == Qt.Checked:
            logging.info('Check: ' + str(word).replace('\n', ''))
            save_word(word.word, word.pronounces, 'hujiang', json.dumps({
                'word': word.word,
                'pronounces': word.pronounces,
                'word_type': word.word_type,
                'translation': word.translation,
            }, ensure_ascii=False))
        else:
            logging.info('Cancel: ')

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.showNormal()

    def eventFilter(self, source: 'QObject', event: 'QEvent') -> bool:
        if source == self:
            if event.type() == QEvent.WindowDeactivate:
                self.in_main_window = False
                self.hide()
            if event.type() == QEvent.WindowActivate:
                self.in_main_window = True
        return super().eventFilter(source, event)

    def on_show_icon_window_timeout(self):
        self.icon_window_timer.stop()
        self.icon_window.hide()

    def catch_exceptions(self, err_type, err_value, err_traceback):
        traceback_format = traceback.format_exception(
            err_type,
            err_value,
            err_traceback
        )
        logging.error("".join(traceback_format))
        self.old_hook(err_type, err_value, err_traceback)


class Worker(QObject):
    search = pyqtSignal()
    show_window = pyqtSignal()

    def run(self):
        # keyboard.add_hotkey('ctrl+q', lambda: self.search.emit())
        mouse_monitor = MouseMonitor(signal=self.search)
        keyboard.add_hotkey('alt', lambda: self.show_window.emit())
        keyboard.wait()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    mainWin = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
