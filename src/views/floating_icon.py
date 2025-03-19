from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QTimer
from PyQt5.QtGui import QPixmap


class FloatingIcon(QWidget):

    search_signal = pyqtSignal()

    def __init__(self, icon: QPixmap):
        super().__init__()

        self.icon = icon
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(
            self.on_show_timeout
        )

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
            self.search_signal.emit()

    def show(self, position: QPoint):
        self.move(position)
        self.timer.start(1200)
        
        super().show()

    def on_show_timeout(self):
        self.timer.stop()
        self.hide()
