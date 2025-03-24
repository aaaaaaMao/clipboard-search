from PyQt5.QtCore import QThread, pyqtSignal
import time

import keyboard
from pynput import mouse

from src import config_manager, logging
from src.services.clipboard import read_clipboard


class MouseMonitorWorker(QThread):

    show_search_window_sig = pyqtSignal()
    show_icon_window_sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._debug = config_manager.get('env') == "debug"

        self._click_time = 0
        self._double_clicked = False

        self.listener = mouse.Listener(
            on_click=self.on_click
        )

    def run(self):
        self.listener.start()
        self.listener.join()
        keyboard.add_hotkey('alt', lambda: self.show_search_window_sig.emit())
        keyboard.wait()

    def on_click(self, x, y, button, pressed):
        if str(button) == 'Button.left':
            if pressed:
                self.on_pressed(x, y)
            else:
                self.on_released(x, y)

    def on_pressed(self, x, y):
        if self._double_clicked:
            if self.is_timeout(time.time(), 0.4):
                self.log('double1 click timeout and reset')
                self.reset()

        self._click_time = time.time()

    def on_released(self, x, y):
        if self._double_clicked:
            if not self.is_timeout(time.time(), 0.6):
                self.log(f'double click')
                self.show_icon_window()
                self.reset()
            else:
                self.log('double2 click timeout and reset')
                self.reset()
        else:
            if not self.is_timeout(time.time(), 0.2):
                self.log('maybe double click')
                self._double_clicked = True

            elif not self.is_timeout(time.time(), 5):
                self.log(f'selected')
                self.show_icon_window()
                self.reset()
            else:
                self.log('reset state')
                self.reset()

    def reset(self):
        self._click_time = 0
        self._double_clicked = False

    def is_timeout(self, now, delta=0.2):
        diff = now - self._click_time
        return diff > delta

    def show_icon_window(self):
        content = read_clipboard()
        self.show_icon_window_sig.emit(content)

    def log(self, message):
        if not self._debug:
            return
        logging.info(message)
