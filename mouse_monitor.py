import time
import threading
from pynput import mouse
from pynput.keyboard import Key, Controller
import win32clipboard as wc
import win32con


class MouseMonitor:

    _press_time = 0
    _press_double_state = False
    _move = (0, 0)
    _debug = False
    _content = None

    def __init__(self, debug=False, signal=None):

        self._debug = debug
        self._signal = signal

        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click
        )

        self.listener.start()
        self.listener.join()

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
            if not self.check_not_time_out(
                    self._press_time,
                    time.time(),
                    0.4
            ):
                self.log('double1 click timeout and reset')
                self.reset()
                self._press_time = time.time()
        else:
            # single click
            self._press_time = time.time()

    def on_released(self, x, y):
        if self._press_double_state:
          # double click
            if self.check_not_time_out(
                    self._press_time,
                    time.time(),
                    0.8
            ):
                content = self.get_copy()
                self.log(f'double click: {content}')
                self.on_selected(content)
                self._press_double_state = False
            else:
                self.log('double2 click timeout and reset')
                self.reset()
        else:
            if self.check_not_time_out(
                    self._press_time,
                    time.time()
            ):
                self.log('maybe double click')
                self._press_double_state = True
                threading.Timer(0.5, self.timeout_handler).start()
            elif not self.check_not_time_out(
                    self._press_time,
                    time.time(),
                    1
            ):
                if self._move != (0, 0):
                    content = self.get_copy()
                    self.log(f'selected: {content}')
                    self.on_selected(content)
                    self.reset()
            else:
                self.log('reset state')
                self.reset()

    def get_copy(self):

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

    def check_not_time_out(self, old, new, delta=0.2):
        return new - old < delta

    def on_selected(self, content):
        self.log(f'select:\n{content}')
        if content and self._signal:
            self._signal.emit()

    def log(self, message):
        if not self._debug:
            return
        print(message)
