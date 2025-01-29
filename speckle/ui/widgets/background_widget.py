from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR_DARK_GREY_SEMI,
    BACKGR_COLOR_TRANSPARENT,
    LABEL_HEIGHT,
)


class BackgroundWidget(QWidget):
    ignore_close_on_click = False
    remove_current_widget_signal = pyqtSignal(QWidget)

    def __init__(
        self,
        parent=None,
        transparent=False,
        background_color=None,
        ignore_close_on_click=False,
    ):
        super(BackgroundWidget, self).__init__(parent)
        self.parentWidget = parent
        self.ignore_close_on_click = ignore_close_on_click

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
        if self.ignore_close_on_click:
            # don't clise the widget on MouseClick outside the background
            return

        self.setGeometry(0, 0, 0, 0)
        self.remove_current_widget_signal.emit(self.parentWidget)

    def show(self):
        self.setGeometry(
            0,
            0,
            self.parentWidget.parentWidget.frameSize().width(),
            self.parentWidget.parentWidget.frameSize().height(),
        )  # top left corner x, y, width, height
