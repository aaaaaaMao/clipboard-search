from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap

from src.services.clipboard import read_clipboard


class FloatingIcon(QWidget):

    search_signal = pyqtSignal(str)

    def __init__(self, icon: QPixmap):
        super().__init__()
        
        self.icon = icon
        self.init_ui()

    def init_ui(self):

        self.setGeometry(100, 100, 100, 100)

        pix = self.icon.scaled(
            45,
            45,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label = QLabel(self)
        label.setPixmap(pix)
        self.resize(pix.width(), pix.height())
        self.setMask(pix.mask())

        self.setWindowFlags(Qt.ToolTip)

        # 设置背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.hide()
            content = read_clipboard()
            self.search_signal.emit(content)
