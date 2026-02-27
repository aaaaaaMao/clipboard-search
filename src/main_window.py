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
    QStackedWidget,
)
from PyQt5.QtCore import QSize, Qt, QObject, QThread, QEvent, QPoint
from PyQt5.QtGui import QIcon, QCursor


from src import logging, config_manager, ctx
from src.views.floating_icon import FloatingIcon
from src.windows.edit_window import EditWindow
from src.views.translation import Translation
from src.views.tray_icon import TrayIcon
from src.widgets.word_list.word_list import WordList
from src.views.token_list import TokenList

from src.services.mouse_monitor_worker import MouseMonitorWorker


class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.installEventFilter(self)

        self.position = QPoint(10, 10)

        self.floating_icon = FloatingIcon()
        self.floating_icon.search_signal.connect(self.search)

        self.edit_window = EditWindow()

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

        self.conetnt_switch_label = QLabel('翻译')
        self.conetnt_switch_label.mousePressEvent = lambda _: self.on_switch_content()
        source_hbox.addWidget(self.conetnt_switch_label)

        if config_manager.hujiang_enabled():
            hujiang_label = QLabel('hujiang')
            hujiang_label.mousePressEvent = lambda _: self.word_list.search_words([self.current_token], sources=['hujiang'])
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

        self.stack_widget = QStackedWidget()
        self.word_list = WordList()
        self.translation = Translation()
        self.stack_widget.addWidget(self.word_list)
        self.stack_widget.addWidget(self.translation)
        self.stack_widget.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.stack_widget)

        main_widget = QWidget()
        main_widget.setLayout(vbox)
        self.setCentralWidget(main_widget)

        self.tray_icon = TrayIcon(self.main_icon)
        self.tray_icon.show()

    def search(self, text = ''):
        self.current_token = ''
        _text = text or self.copy_text
        if _text:
            if config_manager.in_debug():
                logging.info(f'Search: {_text}')

            self.show_window()
            self.search_input.clear()
            self.token_list.clear()

            tokens = self.token_list.tokenizer(_text)
            if tokens:
                self.current_token = tokens[0]
                self.word_list.search_words(tokens[0:1])
            else:
                self.word_list.show_words([])

    def show_window(self):
        if (self.isMinimized() or not self.isVisible()) and self.copy_text:
            ctx.copy_clipboard_disabled = True

            self.position = self.position + QPoint(20, -100)
            self.move(self.position)

            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            if self.floating_icon.isVisible():
                self.floating_icon.close()

            self.conetnt_switch_label.setText('翻译')
            self.stack_widget.setCurrentIndex(0)
            self.showNormal()

    def show_floating_icon(self, selectedText):        
        self.position = QCursor().pos() + QPoint(20, -20)

        if self.isVisible():
            self.hide()
        
        self.copy_text = selectedText
        self.floating_icon.show(self.position)

    def select_token(self, token: str):
        self.word_list.search_words([token])
        self.current_token = token

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.showNormal()

    def eventFilter(self, source: 'QObject', event: 'QEvent') -> bool:
        if source == self:
            if event.type() == QEvent.WindowDeactivate:
                if not self.edit_window.isVisible():
                    ctx.copy_clipboard_disabled = False

                    self.hide()
            if event.type() == QEvent.WindowActivate:
                pass

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
        self.edit_window.move(self.position + QPoint(self.width(), 0))
        self.edit_window.show_window(self.current_token)

    def on_translate(self):
        if not self.copy_text:
            return
        
        self.stack_widget.setCurrentIndex(1)
        self.translation.translate(self.copy_text)

    def on_switch_content(self):
        if self.stack_widget.currentIndex() == 0:
            self.conetnt_switch_label.setText('词典')
            self.stack_widget.setCurrentIndex(1)
            self.on_translate()
        else:
            self.conetnt_switch_label.setText('翻译')
            self.stack_widget.setCurrentIndex(0)
    