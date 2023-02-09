from PyQt5.QtWidgets import QSystemTrayIcon, QAction, QMenu
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QCoreApplication


class TrayIcon(QSystemTrayIcon):

    def __init__(self, icon: QPixmap):
        super().__init__()
        self.setIcon(icon)
        self.init_ui()

    def init_ui(self):

        self.menu = QMenu()
        self.quit_action = QAction('Quit')
        self.dump_action = QAction('Dump')

        self.quit_action.triggered.connect(self.quit_app)

        self.menu.addAction(self.quit_action)
        self.menu.addAction(self.dump_action)

        self.setContextMenu(self.menu)

    def quit_app(self):
        QCoreApplication.quit()
