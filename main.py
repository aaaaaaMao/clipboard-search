import sys
import traceback

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSystemTrayIcon,
    QLineEdit,
)
from PyQt5.QtCore import QSize, Qt, QObject, QThread, pyqtSignal, QEvent, QTimer
from PyQt5.QtGui import QIcon, QCursor, QPixmap


from src import logging, config
from src.views.float_icon_window import FloatIconWindow
from src.views.edit_window import EditWindow
from src.views.tray_icon import TrayIcon
from src.views.word_list import WordList
from src.views.token_list import TokenList

from src.services.mouse_monitor_worker import MouseMonitorWorker
from src.services.search_word import SearchWord


class MainWindow(QMainWindow):

    search_succeed_signal = pyqtSignal(list)

    def __init__(self):
        QMainWindow.__init__(self)

        self.in_main_window = False
        self.installEventFilter(self)

        self.pos_x = 10
        self.pos_y = 10

        float_icon = QPixmap('./images/battery.png')
        self.icon_window = FloatIconWindow(float_icon)
        self.icon_window.search_signal.connect(self.search)
        self.icon_window_timer = QTimer()
        self.icon_window_timer.timeout.connect(
            self.on_show_icon_window_timeout
        )

        self.edit_window = EditWindow()

        self.search_succeed_signal.connect(self.show_words)
        self.search_word = SearchWord(config, self.search_succeed_signal)

        self.init_ui()

        self.thread = QThread()
        self.worker = MouseMonitorWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.show_icon_window_sig.connect(self.show_icon_window)
        self.worker.show_search_window_sig.connect(self.show_window)

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.copy_text = ''
        self.current_token = ''

        self.old_hook = sys.excepthook
        sys.excepthook = self.catch_exceptions

    def init_ui(self):

        self.main_icon = QIcon('./images/battery.png')

        minimun_size = config['main_window']['minimun_size']
        self.setMinimumSize(QSize(minimun_size[0], minimun_size[1]))
        self.setWindowTitle("Clipboard search")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(self.main_icon)

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        search_label = QLabel()
        search_label.setText('search: ')
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(
            lambda: self.search(self.search_input.text())
        )

        hbox.addWidget(search_label)
        hbox.addWidget(self.search_input)
        vbox.addLayout(hbox)

        source_hbox = QHBoxLayout()
        hujiang_label = QLabel()
        hujiang_label.setText('hujiang')
        hujiang_label.mousePressEvent = \
            lambda _: self.search_word.search(
                self.current_token, source='hujiang')
        new_label = QLabel()
        new_label.setText('编辑')
        new_label.mousePressEvent = lambda _: self.show_edit_window()

        source_hbox.addStretch(1)
        source_hbox.addWidget(hujiang_label)
        source_hbox.addWidget(new_label)
        vbox.addLayout(source_hbox)

        self.token_list = TokenList()
        self.token_list.itemDoubleClicked.connect(
            lambda item: self.select_token(item.text())
        )
        vbox.addWidget(self.token_list)

        self.word_list = WordList()
        vbox.addWidget(self.word_list)

        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setCentralWidget(main_widget)

        self.tray_icon = TrayIcon(self.main_icon)
        self.tray_icon.show()

    def search(self, text):
        self.copy_text = text
        self.current_token = ''
        if self.copy_text:
            logging.info(f'Search: {self.copy_text}')
            self.show_window()
            self.search_input.clear()
            self.token_list.clear()

            tokens = self.token_list.tokenizer(self.copy_text)
            if tokens:
                self.search_word.search(tokens[0])
                self.current_token = tokens[0]
            else:
                self.show_words([])

    def show_words(self, words):
        self.word_list.show_words(words)

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
        self.icon_window_timer.start(1200)

    def select_token(self, token: str):
        self.current_token = token
        self.search_word.search(token)

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
        self.copy_text = ''
        self.icon_window.hide()

    def catch_exceptions(self, err_type, err_value, err_traceback):
        traceback_format = traceback.format_exception(
            err_type,
            err_value,
            err_traceback
        )
        logging.error("".join(traceback_format))
        self.old_hook(err_type, err_value, err_traceback)

    def show_edit_window(self):
        self.edit_window.show_window(self.current_token)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    mainWin = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
