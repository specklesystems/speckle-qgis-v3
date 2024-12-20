from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from specklepy_qt_ui.qt_ui.utils.global_resources import (
    BACKGR_COLOR_DARK_GREY_SEMI,
)


class BackgroundWidget(QWidget):
    context_stack = None
    message_card: QWidget
    send_data = pyqtSignal(object)

    def __init__(self, parent=None):
        super(BackgroundWidget, self).__init__(parent)
        self.parentWidget = parent

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"{BACKGR_COLOR_DARK_GREY_SEMI}")
        self.setGeometry(0, 0, 0, 0)

    def mouseReleaseEvent(self, event):
        self.setGeometry(0, 0, 0, 0)
        self.parentWidget.parentWidget.kill_process_widgets()

    def show(self):
        self.setGeometry(
            0,
            0,
            self.parentWidget.parentWidget.frameSize().width(),
            self.parentWidget.parentWidget.frameSize().height(),
        )  # top left corner x, y, width, height
