from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from speckle.connectors.ui.widgets.utils.global_resources import (
    BACKGR_COLOR_DARK_GREY_SEMI,
    BACKGR_COLOR_TRANSPARENT,
    LABEL_HEIGHT,
)


class BackgroundWidget(QWidget):
    context_stack = None
    message_card: QWidget

    def __init__(self, parent=None, transparent=False, background_color=None):
        super(BackgroundWidget, self).__init__(parent)
        self.parentWidget = parent

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        if not transparent:  # first widget
            self.setStyleSheet(
                f"margin-top:{LABEL_HEIGHT};{BACKGR_COLOR_DARK_GREY_SEMI}"
            )
        else:  # more overlaying widgets
            self.setStyleSheet(f"margin-top:{LABEL_HEIGHT};{BACKGR_COLOR_TRANSPARENT}")

        # if custom color, overwrite
        if isinstance(background_color, str):
            self.setStyleSheet(f"margin-top:{LABEL_HEIGHT};{background_color}")

    def mouseReleaseEvent(self, event):
        self.setGeometry(0, 0, 0, 0)
        self.parentWidget.parentWidget.remove_current_widget(self.parentWidget)

    def show(self):
        self.setGeometry(
            0,
            0,
            self.parentWidget.parentWidget.frameSize().width(),
            self.parentWidget.parentWidget.frameSize().height(),
        )  # top left corner x, y, width, height
