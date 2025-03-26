from pynput.keyboard import Key, Controller
import win32clipboard as wc
import win32con
import time

from src.utils import utils
from src import logging


def read_clipboard():

    def trigger_copy():
        key = Controller()
        with key.pressed(Key.ctrl):
            key.press('c')
            key.release('c')

        time.sleep(0.1)

    def close_clipboard():
        try:
            wc.EmptyClipboard()
            wc.CloseClipboard()
        except Exception as e:
            logging.error(e)

    trigger_copy()

    content = ''
    try:
        wc.OpenClipboard()
        content = wc.GetClipboardData(win32con.CF_UNICODETEXT)
        close_clipboard()
    except Exception as e:
        logging.error(e)
        close_clipboard()



    return utils.trim(content)
