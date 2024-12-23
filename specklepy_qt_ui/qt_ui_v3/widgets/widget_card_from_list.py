from typing import List
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
)

from specklepy_qt_ui.qt_ui.utils.global_resources import (
    ZERO_MARGIN_PADDING,
    SPECKLE_COLOR,
    BACKGR_COLOR_TRANSPARENT,
    BACKGR_COLOR_LIGHT_GREY2,
    BACKGR_COLOR_GREY,
)


class CardInListWidget(QWidget):
    context_stack = None
    callback = None
    send_data = pyqtSignal(object)

    def __init__(self, card_content: List):
        super(CardInListWidget, self).__init__(None)

        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "QWidget {"
            + "border-radius:5px; margin-bottom:3px; min-height:50px;"
            + f"{ZERO_MARGIN_PADDING} {BACKGR_COLOR_LIGHT_GREY2}"
            + "} QWidget:hover { "
            + f"{BACKGR_COLOR_GREY}"
            + "}"
        )

        layout = QVBoxLayout(self)

        # add callback function
        self.callback = card_content[0]

        # add content
        layout.addWidget(self.add_main_text(card_content[1]))

        for content in card_content[2:]:
            layout.addWidget(self.add_text_line(content))

    def add_main_text(self, content: str):

        # add label text (in a shape of QPushButton for easier styling)
        main_text = QPushButton(content)

        # reiterating callback, because QPushButton clicks are not propageted to the parent widget
        main_text.clicked.connect(self.callback)
        main_text.setStyleSheet(
            "QPushButton {color:black;border-radius: 7px;"
            + f"{ZERO_MARGIN_PADDING} {BACKGR_COLOR_TRANSPARENT} min-height: 15px;text-align: left;"
            + "} QPushButton:hover { "
            + f"color:rgba{SPECKLE_COLOR};"
            + " }"
        )
        return main_text

    def add_text_line(self, content: str):

        # add text line (in a shape of QPushButton for easier styling)
        text_line = QPushButton(content)

        # reiterating callback, because QPushButton clicks are not propageted to the parent widget
        text_line.clicked.connect(self.callback)
        text_line.setStyleSheet(
            "QPushButton {color:grey;border-radius: 7px;"
            + f"{ZERO_MARGIN_PADDING} {BACKGR_COLOR_TRANSPARENT} min-height: 10px;text-align: left;"
            + " }"
        )
        return text_line

    def mouseReleaseEvent(self, event):
        if self.callback:
            self.callback()
