from PyQt5.QtCore import QThread, pyqtSignal
import keyboard
import time
import threading
from pynput import mouse

from src import config, logging


class MouseMonitorWorker(QThread):

    show_search_window_sig = pyqtSignal()
    show_icon_window_sig = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._debug = config['mouse_monitor']['debug']

        self._press_time = 0
        self._press_double_state = False
        self._move = (0, 0)

        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )

    def run(self):
        self.listener.start()
        self.listener.join()
        keyboard.add_hotkey('alt', lambda: self.show_search_window_sig.emit())
        keyboard.wait()

    def on_move(self, x, y):
        if self._press_time == 0:
            self._move = (x, y)

    def on_click(self, x, y, button, pressed):
        if str(button) == 'Button.left':
            if pressed:
                self.on_pressed(x, y)
            else:
                self.on_released(x, y)

    def on_pressed(self, x, y):
        if self._press_double_state:
            # double click
            if self.is_timeout(time.time(), 0.4):
                self.log('double1 click timeout and reset')
                self.reset()
                self._press_time = time.time()
        else:
            # single click
            self._press_time = time.time()

    def on_released(self, x, y):
        if self._press_double_state:
          # double click
            if not self.is_timeout(time.time(), 0.6):
                self.log(f'double click')
                self.show_icon_window()
                self._press_double_state = False
            else:
                self.log('double2 click timeout and reset')
                self.reset()
        else:
            if not self.is_timeout(time.time()):
                self.log('maybe double click')
                self._press_double_state = True
                threading.Timer(0.5, self.timeout_handler).start()
            elif self.is_timeout(time.time(), 0.6):
                if self._move != (0, 0):
                    self.log(f'selected')
                    self.show_icon_window()
                    self.reset()
            else:
                self.log('reset state')
                self.reset()

    def reset(self):
        self._press_time = 0
        self._press_double_state = False
        self._move = (0, 0)

    def timeout_handler(self):
        self.reset()
        self.log('timeout to reset state')

    def is_timeout(self, now, delta=0.2):
        return now - self._press_time > delta

    def show_icon_window(self):
        self.show_icon_window_sig.emit()

    def log(self, message):
        if not self._debug:
            return
        logging.info(message)
