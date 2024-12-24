from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QGraphicsDropShadowEffect,
)

from speckle.connectors.ui.models import ModelCard, SenderModelCard
from speckle.connectors.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    ZERO_MARGIN_PADDING,
    BACKGR_COLOR_WHITE,
    BACKGR_COLOR_TRANSPARENT,
    BACKGR_COLOR_LIGHT_GREY2,
    BACKGR_COLOR_GREY,
)
from specklepy.core.api.models.current import Model


class ModelCardWidget(QWidget):
    card_content: ModelCard = None
    send_data = pyqtSignal(object)
    shadow_effect = None

    def __init__(self, parent=None, card_content: ModelCard = None):
        super(ModelCardWidget, self).__init__(None)
        self.parent = parent
        self.card_content = card_content

        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.setStyleSheet(
            "QWidget {"
            + f"border-radius:5px;{ZERO_MARGIN_PADDING} margin-bottom:3px; min-height:40px;"
            + f"{BACKGR_COLOR_WHITE}"
            + "}"
        )

        self.add_drop_shadow()

        # create areas in the card
        top_section = self.create_card_header(card_content)

        # add to layout
        layout.addWidget(top_section)

    def add_drop_shadow(self, item=None):
        if not item:
            item = self
        # create drop shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setOffset(2, 2)
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setColor(QColor.fromRgb(100, 100, 100, 150))

        item.setGraphicsEffect(self.shadow_effect)

    def create_card_header(self, card_content: ModelCard):
        top_line = QWidget()
        layout_top_line = QHBoxLayout(top_line)
        layout_top_line.setAlignment(Qt.AlignLeft)
        top_line.setStyleSheet(
            "QWidget {"
            + f"color:white;border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"height: 20px;text-align: left;{BACKGR_COLOR_TRANSPARENT}"
            + "}"
        )

        if isinstance(card_content, SenderModelCard):
            layout_top_line.addWidget(self.add_send_btn())

        model: Model = self.parent.ui_model_card_utils.get_model_by_id_from_client(
            self.card_content
        )
        layout_top_line.addWidget(self.add_main_text(model.name))

        return top_line

    def add_send_btn(self):

        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(lambda: None)
        button_publish.setStyleSheet(
            "QPushButton {"
            + f"color:white;border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"max-height:20px;max-width: 50px;text-align: center;{BACKGR_COLOR}"
            + "} QPushButton:hover { "
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
            + "}"
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
