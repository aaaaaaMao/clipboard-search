from PyQt5.QtCore import QThread, pyqtSignal
import keyboard
import time
import threading
from pynput import mouse
from pynput.keyboard import Key, Controller
import win32clipboard as wc
import win32con

from src import config, logging


class MouseMonitorWorker(QThread):
    search = pyqtSignal(str)
    show_window = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._debug = config['mouse_monitor']['debug']

        self._press_time = 0
        self._press_double_state = False
        self._move = (0, 0)
        self._content = None

        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )

    def run(self):
        self.listener.start()
        self.listener.join()
        keyboard.add_hotkey('alt', lambda: self.show_window.emit())
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
                content = self.read_clipboard()
                self.log(f'double click: {content}')
                self.on_selected(content)
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
                    content = self.read_clipboard()
                    self.log(f'selected: {content}')
                    self.on_selected(content)
                    self.reset()
            else:
                self.log('reset state')
                self.reset()

    def read_clipboard(self):

        def trigger_copy():
            key = Controller()
            with key.pressed(Key.ctrl):
                key.press('c')
                key.release('c')
            time.sleep(0.1)

        trigger_copy()

        content = ''
        try:
            wc.OpenClipboard()
            content = wc.GetClipboardData(win32con.CF_UNICODETEXT)
            wc.CloseClipboard()
        except Exception as e:
            self.log('Clipboard Content error' + str(e))

        self._content = content
        return content

    def reset(self):
        self._press_time = 0
        self._press_double_state = False
        self._move = (0, 0)
        self._content = None

    def timeout_handler(self):
        self.reset()
        self.log('timeout to reset state')

    def is_timeout(self, now, delta=0.2):
        return now - self._press_time > delta

    def on_selected(self, content):
        self.log(f'select:\n{content}')
        if content:
            self.search.emit(content)

    def log(self, message):
        if not self._debug:
            return
        logging.info(message)
