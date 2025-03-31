import sys
import traceback

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSystemTrayIcon,
    QLineEdit,
)
from PyQt5.QtCore import QSize, Qt, QObject, QThread, pyqtSignal, QEvent, QPoint
from PyQt5.QtGui import QIcon, QCursor


from src import logging, config_manager
from src.views.floating_icon import FloatingIcon
from src.views.edit_window import EditWindow
from src.views.translation_window import TranslationWindow
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

        self.position = QPoint(10, 10)

        self.floating_icon = FloatingIcon()
        self.floating_icon.search_signal.connect(self.search)

        self.edit_window = EditWindow()
        self.translation_window = TranslationWindow()

        self.search_succeed_signal.connect(self.show_words)
        self.search_word = SearchWord(self.search_succeed_signal)

        self.init_ui()

        self.thread = QThread()
        self.worker = MouseMonitorWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.show_icon_window_sig.connect(self.show_floating_icon)
        self.worker.show_search_window_sig.connect(self.show_window)

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        self.copy_text = ''
        self.current_token = ''

        self.old_hook = sys.excepthook
        sys.excepthook = self.catch_exceptions

    def init_ui(self):

        self.main_icon = QIcon(config_manager.get_icon_path('icon'))

        minimun_size = config_manager.get('main_window')
        self.setMinimumSize(QSize(minimun_size['width'], minimun_size['height']))
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
        source_hbox.addStretch(1)

        translate_label = QLabel('翻译')
        translate_label.mousePressEvent = lambda _: self.on_translate()
        source_hbox.addWidget(translate_label)

        if config_manager.hujiang_enabled():
            hujiang_label = QLabel('hujiang')
            hujiang_label.mousePressEvent = \
                lambda _: self.search_word.search(
                    self.current_token, source='hujiang')
            source_hbox.addWidget(hujiang_label)

        new_label = QLabel('编辑')
        new_label.mousePressEvent = lambda _: self.show_edit_window()
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

    def search(self):
        self.current_token = ''
        if self.copy_text:
            if config_manager.in_debug():
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
            self.move(self.position.x() + 20, self.position.y() - 100)

            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            if self.floating_icon.isVisible():
                self.floating_icon.close()
            self.showNormal()

    def show_floating_icon(self, selectedText):
        if self.in_main_window:
            return
        
        self.position = QCursor().pos() + QPoint(20, -20)

        if self.isVisible():
            self.hide()
        
        self.copy_text = selectedText
        self.floating_icon.show(self.position)

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

    def on_translate(self):
        if not self.copy_text:
            return
        
        self.translation_window.move(self.position + QPoint(20, -100))
        self.translation_window.show(self.copy_text)
    