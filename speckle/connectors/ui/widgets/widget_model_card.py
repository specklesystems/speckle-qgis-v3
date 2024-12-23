from typing import List
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
)

from speckle.connectors.ui.models import ModelCard, SenderModelCard
from speckle.connectors.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    ZERO_MARGIN_PADDING,
    SPECKLE_COLOR,
    BACKGR_COLOR_TRANSPARENT,
    BACKGR_COLOR_LIGHT_GREY2,
    BACKGR_COLOR_GREY,
)


class ModelCardWidget(QWidget):
    card_content: ModelCard = None
    send_data = pyqtSignal(object)

    def __init__(self, card_content: ModelCard):
        super(ModelCardWidget, self).__init__(None)

        self.card_content = card_content

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

        # create areas in the card
        top_line = QWidget()
        layout_top_line = QHBoxLayout(top_line)

        if isinstance(card_content, SenderModelCard):
            layout_top_line.addWidget(self.add_send_btn())
        layout_top_line.addWidget(self.add_main_text(card_content.model_id))
        layout.addWidget(top_line)

    def add_send_btn(self):

        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(lambda: None)
        button_publish.setStyleSheet(
            "QWidget {"
            + f"color:white;border-radius: 10px;margin-top:0px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR}"
            + "} QWidget:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        return button_publish

    def add_main_text(self, content: str):

        # add label text (in a shape of QPushButton for easier styling)
        main_text = QPushButton(content)

        # reiterating callback, because QPushButton clicks are not propageted to the parent widget
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
        text_line.setStyleSheet(
            "QPushButton {color:grey;border-radius: 7px;"
            + f"{ZERO_MARGIN_PADDING} {BACKGR_COLOR_TRANSPARENT} min-height: 10px;text-align: left;"
            + " }"
        )
        return text_line
