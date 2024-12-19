from PyQt5 import QtCore
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel

from specklepy_qt_ui.qt_ui.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    BACKGR_COLOR_SEMI_TRANSPARENT,
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_GREY,
    BACKGR_COLOR_TRANSPARENT,
    BACKGR_COLOR_HIGHLIGHT,
    NEW_GREY,
    NEW_GREY_HIGHLIGHT,
    BACKGR_ERROR_COLOR,
    BACKGR_ERROR_COLOR_LIGHT,
)


class NoModelCardsWidget(QWidget):
    context_stack = None
    message_card: QPushButton
    send_data = pyqtSignal(object)

    def __init__(self, parent=None):
        super(NoModelCardsWidget, self).__init__(parent)
        self.parentWidget = parent

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 60, 10, 20)
        self.layout.setAlignment(Qt.AlignVCenter)

        # align with the parent widget size
        self.setGeometry(
            0,
            0,
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self.message_card = QWidget()
        self.message_card.setStyleSheet(
            "QWidget {"
            + f"border-radius: 10px;padding: 20px;margin:{WIDGET_SIDE_BUFFER};height: 100px;{BACKGR_COLOR_GREY}"
            + "}"
        )
        self.fill_message_card()
        self.layout.addWidget(self.message_card)

    def fill_message_card(self):
        boxLayout = QVBoxLayout(self.message_card)

        # add text
        label = QLabel(
            "There are no Speckle models being published or loaded in this file yet."
        )
        label.setStyleSheet(
            "QLabel {margin-bottom:10px;padding: 5px;height: 20px;text-align: left;}"
        )
        boxLayout.addWidget(label)

        # add publish / load buttons
        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(
            lambda: self.parentWidget.open_select_projects_widget()
        )
        button_publish.setStyleSheet(
            "QWidget {"
            + f"color:white;border-radius: 7px;margin-top:0px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR}"
            + "} QWidget:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        boxLayout.addWidget(button_publish)
