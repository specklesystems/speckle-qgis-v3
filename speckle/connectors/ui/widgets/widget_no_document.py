from PyQt5 import QtCore
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel

from speckle.connectors.ui.widgets.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    BACKGR_COLOR_WHITE,
    BACKGR_COLOR_LIGHT_GREY2,
    LABEL_HEIGHT,
)


class NoDocumentWidget(QWidget):
    context_stack = None
    message_card: QWidget
    send_data = pyqtSignal(object)

    def __init__(self, parent=None):
        super(NoDocumentWidget, self).__init__(parent)
        self.parentWidget: "SpeckleQGISv3Dialog" = parent

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, {LABEL_HEIGHT}, 0, 0)
        self.layout.setAlignment(Qt.AlignVCenter)

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"{BACKGR_COLOR_LIGHT_GREY2}")

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self.message_card = QWidget()
        self.message_card.setStyleSheet(
            "QWidget {"
            + f"border-radius: 10px;padding: 20px;margin:{WIDGET_SIDE_BUFFER};height: 40px;{BACKGR_COLOR_WHITE}"
            + "}"
        )
        self.fill_message_card()
        self.layout.addWidget(self.message_card)

    def fill_message_card(self):
        boxLayout = QVBoxLayout(self.message_card)

        # add text
        label = QLabel("No active document")
        label.setStyleSheet(
            "QLabel {padding: 5px;padding-top: 20px;padding-bottom: 20px;height: 20px;text-align: left;}"
        )
        boxLayout.addWidget(label)
