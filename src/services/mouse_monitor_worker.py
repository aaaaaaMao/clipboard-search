from PyQt5.QtCore import QObject, pyqtSignal
import keyboard

from src.utils.mouse_monitor import MouseMonitor


class MouseMonitorWorker(QObject):
    search = pyqtSignal()
    show_window = pyqtSignal()

    def run(self):
        # keyboard.add_hotkey('ctrl+q', lambda: self.search.emit())
        mouse_monitor = MouseMonitor(signal=self.search)
        keyboard.add_hotkey('alt', lambda: self.show_window.emit())
        keyboard.wait()
