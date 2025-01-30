import webbrowser
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)

from speckle.ui.models import ModelCard
from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_SEMI_TRANSPARENT,
    BACKGR_COLOR_SUCCESS_SEND,
    ZERO_MARGIN_PADDING,
    BACKGR_COLOR_TRANSPARENT,
    SPECKLE_COLOR,
)
from speckle.ui.widgets.utils.utils import create_text_for_widget, open_in_web


class ModelCardNotificationWidget(QWidget):
    dismiss_btn: QPushButton
    card_content: ModelCard

    def __init__(
        self,
        card_content: ModelCard,
        parent=None,
    ):
        super(ModelCardNotificationWidget, self).__init__(parent)
        self.card_content = card_content

        # create a container that will be added to the main Stacked layout
        # make it semi-transparent
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "QWidget {"
            + f"border-radius: 0px;color:white;{ZERO_MARGIN_PADDING}"
            + f"text-align: left;{BACKGR_COLOR_SEMI_TRANSPARENT}"
            + "}"
        )
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignBottom)
        self.layout.setContentsMargins(0, 0, 0, 0)

        line = self.create_notification_line()

        # Add line widget to the container
        self.layout.addWidget(line)

    def create_notification_line(self):

        # create a line widget
        line = QWidget()
        line.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        line.setStyleSheet(
            "QWidget {"
            + f"border-radius: 0px;color:white;{ZERO_MARGIN_PADDING}"
            + f"text-align: left;{BACKGR_COLOR_SUCCESS_SEND}"
            + "}"
        )
        layout_line = QHBoxLayout(line)
        layout_line.setAlignment(Qt.AlignLeft)
        layout_line.setContentsMargins(10, 5, 10, 5)

        # add main text
        main_text = self.create_main_text("Version created!")
        layout_line.addWidget(main_text)

        # Add a spacer item to push the next button to the right
        spacer = self.create_horizontal_spacer()
        layout_line.addItem(spacer)

        # Add dismiss buttom
        dismiss_btn = self.create_dismiss_btn()
        layout_line.addWidget(dismiss_btn)
        self.dismiss_btn = dismiss_btn

        # Add view in Web buttom
        view_web = self.create_web_view_btn()
        layout_line.addWidget(view_web)

        return line

    def create_main_text(self, text: str):
        return create_text_for_widget(text, color=SPECKLE_COLOR)

    def create_horizontal_spacer(self):
        return QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

    def create_web_view_btn(self):

        view_web = QPushButton("View")
        view_web.clicked.connect(lambda: open_in_web(self.card_content))
        view_web.setStyleSheet(
            "QPushButton {"
            + f"color:white; border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"{BACKGR_COLOR} height:15px; text-align: center; padding: 0px 10px;"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        view_web.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        return view_web

    def create_dismiss_btn(self):

        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.setStyleSheet(
            "QPushButton {"
            + f"color:{SPECKLE_COLOR}; {ZERO_MARGIN_PADDING}"
            + f"{BACKGR_COLOR_TRANSPARENT} height:15px;text-align: center; "
            + " }"
        )
        dismiss_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        return dismiss_btn
