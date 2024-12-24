from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QCursor
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
    SPECKLE_COLOR,
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

        # self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )
        self.setStyleSheet(
            "QWidget {"
            + f"border-radius:5px;{ZERO_MARGIN_PADDING}"
            + "margin-bottom:3px; max-height:80px;"
            + f"{BACKGR_COLOR_WHITE}"
            + "}"
        )

        self.add_drop_shadow()

        # create areas in the card
        top_section = self.create_card_header(card_content)
        bottom_section = self.create_send_filter_line(card_content)

        # add to layout
        layout.addWidget(top_section)
        layout.addWidget(bottom_section)

    def add_drop_shadow(self, item=None):
        if not item:
            item = self
        # create drop shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setOffset(2, 2)
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setColor(QColor.fromRgb(100, 100, 100, 150))

        item.setGraphicsEffect(self.shadow_effect)

    def create_send_filter_line(self, card_content: ModelCard):
        line = QWidget()
        layout_line = QHBoxLayout(line)
        layout_line.setAlignment(Qt.AlignLeft)
        layout_line.setContentsMargins(0, 0, 0, 0)
        line.setStyleSheet(
            "QWidget {"
            + f"color:white;border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"text-align: left;{BACKGR_COLOR_TRANSPARENT}"
            + "}"
        )

        clickable_text = self.add_text("Selection:  ", color=SPECKLE_COLOR)
        clickable_text.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        layout_line.addWidget(clickable_text)

        layout_line.addWidget(self.add_text("0 layers", color="rgba(130,130,130,1)"))

        return line

    def create_card_header(self, card_content: ModelCard):
        top_line = QWidget()
        layout_top_line = QHBoxLayout(top_line)
        layout_top_line.setAlignment(Qt.AlignLeft)
        layout_top_line.setContentsMargins(0, 0, 0, 0)
        top_line.setStyleSheet(
            "QWidget {"
            + f"color:white;border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"text-align: left;{BACKGR_COLOR_TRANSPARENT}"
            + "}"
        )

        if isinstance(card_content, SenderModelCard):
            layout_top_line.addWidget(self.add_send_btn())

        model: Model = self.parent.ui_model_card_utils.get_model_by_id_from_client(
            self.card_content
        )
        layout_top_line.addWidget(self.add_text(model.name))

        return top_line

    def add_send_btn(self):

        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(lambda: None)
        button_publish.setStyleSheet(
            "QPushButton {"
            + f"color:white; border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"{BACKGR_COLOR} height:20px;text-align: center; padding: 0px 10px;"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        button_publish.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        return button_publish

    def add_text(self, content: str, color: str = "black"):

        # add label text (in a shape of QPushButton for easier styling)
        text = QPushButton(content)

        # reiterating callback, because QPushButton clicks are not propageted to the parent widget
        text.setStyleSheet(
            "QPushButton {"
            + f"color:{color};border-radius: 7px;{ZERO_MARGIN_PADDING}"
            + f" {BACKGR_COLOR_TRANSPARENT} height: 20px;text-align: left;"
            + "}"
        )
        return text
