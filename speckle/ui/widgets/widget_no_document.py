from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel

from speckle.ui.widgets.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    BACKGR_COLOR_WHITE,
    BACKGR_COLOR_LIGHT_GREY2,
)


class NoDocumentWidget(QWidget):

    _message_card: QWidget

    def __init__(self, parent=None):
        super(NoDocumentWidget, self).__init__(parent)
        self.parent: "SpeckleQGISv3Dialog" = parent

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignVCenter)

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"{BACKGR_COLOR_LIGHT_GREY2}")

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self._message_card = QWidget()
        self._message_card.setStyleSheet(
            "QWidget {"
            + f"border-radius: 10px;padding: 20px;margin:{int(0.5 * WIDGET_SIDE_BUFFER)};height: 40px;{BACKGR_COLOR_WHITE}"
            + "}"
        )
        self.fill_message_card()
        self.layout.addWidget(self._message_card)

    def fill_message_card(self):
        boxLayout = QVBoxLayout(self._message_card)

        # add text
        label = QLabel("No active document")
        label.setStyleSheet(
            "QLabel {padding: 5px;padding-top: 20px;padding-bottom: 20px;height: 20px;text-align: left;}"
        )
        boxLayout.addWidget(label)
