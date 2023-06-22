from pynput.keyboard import Key, Controller
import win32clipboard as wc
import win32con
import time

from src.utils import utils


def read_clipboard():

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
        print(e)

    return utils.trim(content)
