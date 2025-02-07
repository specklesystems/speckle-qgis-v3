from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QGraphicsDropShadowEffect,
)

from speckle.ui.widgets.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_LIGHT_GREY2,
    BACKGR_COLOR_WHITE,
    LABEL_HEIGHT,
)


class NoModelCardsWidget(QWidget):

    add_projects_search_signal = pyqtSignal()
    _message_card: QWidget
    _shadow_effect = None

    def __init__(self, parent=None):
        super(NoModelCardsWidget, self).__init__(parent)
        self.parent: "SpeckleQGISv3Dialog" = parent

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, LABEL_HEIGHT, 0, 0)
        self.layout.setAlignment(Qt.AlignVCenter)

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"margin-top:60px;{BACKGR_COLOR_LIGHT_GREY2}")

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self._message_card = QWidget()
        self._message_card.setStyleSheet(
            "QWidget {"
            + f"border-radius: 10px;padding: 20px;margin:{int(0.5 * WIDGET_SIDE_BUFFER)};height: 100px;{BACKGR_COLOR_WHITE}"
            + "}"
        )
        self._fill_message_card()
        self._add_drop_shadow(self._message_card)

        self.layout.addWidget(self._message_card)

    def _add_drop_shadow(self, item=None):
        if not item:
            item = self
        # create drop shadow effect
        self._shadow_effect = QGraphicsDropShadowEffect()
        self._shadow_effect.setOffset(2, 2)
        self._shadow_effect.setBlurRadius(8)
        self._shadow_effect.setColor(QColor.fromRgb(100, 100, 100, 150))

        item.setGraphicsEffect(self._shadow_effect)

    def _fill_message_card(self):
        boxLayout = QVBoxLayout(self._message_card)

        # add text
        label = QLabel(
            "There are no Speckle models being published or loaded in this file yet."
        )
        label.setStyleSheet(
            "QLabel {margin-bottom:10px;padding: 5px;height: 20px;text-align: left;}"
        )
        boxLayout.addWidget(label)

        # add publish / load buttons
        button_publish = self._create_search_button()
        boxLayout.addWidget(button_publish)

    def _create_search_button(self) -> QPushButton:

        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(lambda: self.add_projects_search_signal.emit())
        button_publish.setStyleSheet(
            "QWidget {"
            + f"color:white;border-radius: 7px;margin-top:0px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR}"
            + "} QWidget:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        return button_publish
