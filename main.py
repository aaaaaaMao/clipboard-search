import sys
import logging
import json

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
    QMenu,
    QAction,
    QSystemTrayIcon,
)
from PyQt5.QtCore import QSize, Qt, QUrl, QObject, QThread, pyqtSignal, QCoreApplication, QEvent, QTimer
from PyQt5.QtGui import QIcon, QCursor, QPixmap
import keyboard

from utils import parse_hujiang_html
from mouse_monitor import MouseMonitor
from db import save_word, is_favorite


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


class IconWindow(QWidget):

    search_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        self.setGeometry(100, 100, 100, 100)

        pix = QPixmap('./images/battery.png').scaled(
            45,
            45,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label = QLabel(self)
        label.setPixmap(pix)
        self.resize(pix.width(), pix.height())
        self.setMask(pix.mask())

        self.setWindowFlags(Qt.ToolTip)

        # 设置背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.search_signal.emit()


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.pos_x = 10
        self.pos_y = 10

        self.icon_window = IconWindow()
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

        self.quit_action.triggered.connect(self.quit_app)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.copy_text = ''

        self.in_main_window = False

        self.installEventFilter(self)
        self.icon_window_timer = QTimer()
        self.icon_window_timer.timeout.connect(
            self.on_show_icon_window_timeout)

    def init_ui(self):

        self.main_icon = QIcon('./images/battery.png')

        self.setMinimumSize(QSize(400, 240))
        self.setWindowTitle("Clipboard search")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(self.main_icon)

        vbox = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.addItem('Waiting copy')
        self.list_widget.itemDoubleClicked.connect(self.on_list_item_clicked)

        vbox.addWidget(self.list_widget)
        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setCentralWidget(main_widget)

        self.quit_action = QAction('Quit')
        # self.quit_action.setIcon(QIcon.fromTheme('application-exit'))

        self.tray_icon_memu = QMenu()
        self.tray_icon_memu.addAction(self.quit_action)
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.main_icon)
        self.tray_icon.setContextMenu(self.tray_icon_memu)
        self.tray_icon.show()

        # self.show()
        # self.icon_window.show()

    def search(self):
        self.copy_text = QApplication.clipboard().text()
        if self.copy_text:
            logging.info(f'Search: {self.copy_text}')
            self.show_window()
            self.search_from_hujiang(self.copy_text)

    def search_from_hujiang(self, word):
        HEADERS = config['hujiang']['req_headers']

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
                    if is_favorite(word.word):
                        check.setChecked(True)
                    check.stateChanged.connect(
                        lambda state: self.on_box_checked(state, word)
                    )
                    layout = QHBoxLayout()
                    layout.addWidget(check)
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

                self.copy_to_clipboard(str(result[0]))
            else:
                self.list_widget.addItem('Not Found.')
        else:
            logging.error(resp.errorString())

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
            save_word(word.word, 'hujiang', json.dumps({
                'word': word.word,
                'pronounces': word.pronounces,
                'word_type': word.word_type,
                'word_type': word.translation,
            }))
        else:
            logging.info('Cancel: ')

    def quit_app(self):
        QCoreApplication.quit()

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


class Worker(QObject):
    search = pyqtSignal()
    show_window = pyqtSignal()

    def run(self):
        # keyboard.add_hotkey('ctrl+q', lambda: self.search.emit())
        mouse_monitor = MouseMonitor(signal=self.search)
        keyboard.add_hotkey('alt', lambda: self.show_window.emit())
        keyboard.wait()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    mainWin = MainWindow()
    # mainWin.show()
    sys.exit(app.exec_())
