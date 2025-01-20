from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QCursor
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QGraphicsDropShadowEffect,
    QSpacerItem,
    QSizePolicy,
    QStackedLayout,
)

from speckle.ui.models import ModelCard, SenderModelCard
from speckle.ui.utils.model_cards_widget_utils import UiModelCardsUtils
from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_SUCCESS_SEND,
    ZERO_MARGIN_PADDING,
    BACKGR_COLOR_WHITE,
    BACKGR_COLOR_TRANSPARENT,
    SPECKLE_COLOR,
    BACKGR_COLOR_LIGHT_GREY,
    BACKGR_COLOR_LIGHT_GREY2,
)
from specklepy.core.api.models.current import Model
import webbrowser


class ModelCardWidget(QWidget):
    card_content: ModelCard = None
    send_model_btn: QPushButton = None
    send_model_signal = pyqtSignal(SenderModelCard)
    remove_self_card_signal = pyqtSignal(ModelCard)
    shadow_effect = None
    close_btn: QPushButton = None
    open_web_btn: QPushButton = None
    ui_model_card_utils: UiModelCardsUtils = None

    summary_text: str = "No objects are selected"
    selection_filter_text: QPushButton
    notification_line: QWidget
    main_content: QWidget

    # for the use in parent widget - to keep track if signals are already connected and not connect to btns twice
    connected: bool = False

    add_selection_filter_signal = pyqtSignal(SenderModelCard)

    def __init__(
        self, parent=None, ui_model_card_utils=None, card_content: ModelCard = None
    ):
        super(ModelCardWidget, self).__init__(None)
        self.parent = parent
        self.ui_model_card_utils = ui_model_card_utils
        self.card_content = card_content

        self.layout = QStackedLayout(self)
        self.layout.setStackingMode(QStackedLayout.StackAll)

        self.add_drop_shadow()

        # add to layout
        content = QWidget()
        content.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        content.setStyleSheet(
            "QWidget {"
            + f"border-radius:5px;{ZERO_MARGIN_PADDING}"
            + "margin-bottom:3px;"
            + f"{BACKGR_COLOR_WHITE}"
            + "}"
        )
        content.layout = QVBoxLayout(content)
        content.layout.setAlignment(Qt.AlignTop)
        content.layout.setContentsMargins(
            0,
            10,
            0,
            0,
        )

        # create areas in the card
        top_section = self.create_card_header(card_content)
        bottom_section = self.create_send_filter_line(card_content)
        self.notification_line = self._create_notification_section()  # to use later

        content.layout.addWidget(top_section)
        content.layout.addWidget(bottom_section)
        self.main_content = content

        self.layout.addWidget(self.main_content)
        self.layout.addWidget(self.notification_line)

    def add_drop_shadow(self, item=None):
        if not item:
            item = self
        # create drop shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setOffset(2, 2)
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setColor(QColor.fromRgb(100, 100, 100, 150))

        item.setGraphicsEffect(self.shadow_effect)

    def create_send_filter_line(self, card_content: SenderModelCard):
        line = QWidget()
        layout_line = QHBoxLayout(line)
        layout_line.setAlignment(Qt.AlignLeft)
        layout_line.setContentsMargins(10, 0, 10, 15)
        line.setStyleSheet(
            "QWidget {"
            + f"color:white;border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"text-align: left;{BACKGR_COLOR_TRANSPARENT}"
            + "}"
        )

        clickable_text = self.add_text("Selection:  ", color=SPECKLE_COLOR)
        clickable_text.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        clickable_text.clicked.connect(
            lambda: self.add_selection_filter_signal.emit(card_content)
        )
        layout_line.addWidget(clickable_text)

        self.selection_filter_text = self.add_text(
            self.summary_text, color="rgba(130,130,130,1)"
        )
        layout_line.addWidget(self.selection_filter_text)

        return line

    def _create_notification_section(self):

        content_notification_widget = QWidget()
        content_notification_widget.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        content_notification_widget.setStyleSheet(
            "QWidget {"
            + f"border-radius: 0px;color:white;{ZERO_MARGIN_PADDING}"
            + f"text-align: left;{BACKGR_COLOR_TRANSPARENT}"
            + "}"
        )
        content_notification_widget.layout = QVBoxLayout(content_notification_widget)
        content_notification_widget.layout.setAlignment(Qt.AlignBottom)
        content_notification_widget.layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        ###############################
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
        layout_line.setContentsMargins(10, 0, 10, 0)

        clickable_text = self.add_text("Version created!", color=SPECKLE_COLOR)
        layout_line.addWidget(clickable_text)

        # Add a spacer item to push the next button to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout_line.addItem(spacer)

        # Dismiss buttom
        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.clicked.connect(lambda: self._hide_notification_line())
        dismiss_btn.setStyleSheet(
            "QPushButton {"
            + f"color:{SPECKLE_COLOR}; {ZERO_MARGIN_PADDING}"
            + f"{BACKGR_COLOR_TRANSPARENT} height:15px;text-align: center; "
            + " }"
        )
        dismiss_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        layout_line.addWidget(dismiss_btn)

        # View in Web buttom
        dismiss_btn = QPushButton("View")
        dismiss_btn.clicked.connect(lambda: self.open_in_web(self.card_content))
        dismiss_btn.setStyleSheet(
            "QPushButton {"
            + f"color:white; border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"{BACKGR_COLOR} height:15px; text-align: center; padding: 0px 10px;"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        dismiss_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        layout_line.addWidget(dismiss_btn)

        spacer_vertical = QSpacerItem(
            40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding
        )
        # content_notification_widget.layout.addItem(spacer_vertical)
        content_notification_widget.layout.addWidget(line)

        return content_notification_widget

    def _hide_notification_line(self):

        self.layout.setCurrentWidget(self.main_content)
        self.notification_line.layout.setAlignment(Qt.AlignVCenter)

    def show_notification_line(self):

        self.layout.setCurrentWidget(self.notification_line)
        self.notification_line.layout.setAlignment(Qt.AlignBottom)

    def change_selection_text(self, selection_text: str):
        # function accessed from the parent dockwidget
        # change text on the widget
        self.selection_filter_text.setText(selection_text)

    def create_card_header(self, card_content: ModelCard):
        top_line = QWidget()
        layout_top_line = QHBoxLayout(top_line)
        layout_top_line.setAlignment(Qt.AlignLeft)
        layout_top_line.setContentsMargins(10, 0, 10, 0)
        top_line.setStyleSheet(
            "QWidget {"
            + f"color:white;{ZERO_MARGIN_PADDING}"
            + f"text-align: left;{BACKGR_COLOR_TRANSPARENT}"
            + "}"
        )

        if isinstance(card_content, SenderModelCard):
            layout_top_line.addWidget(self.add_send_btn())
            self.send_model_btn.clicked.connect(
                lambda: self.send_model_signal.emit(card_content)
            )

        model: Model = self.ui_model_card_utils.get_model_by_id_from_client(
            self.card_content
        )
        layout_top_line.addWidget(
            self.add_text(model.name, other_props="font-size: 14px;font-weight: bold;")
        )

        # Add a spacer item to push the next button to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout_top_line.addItem(spacer)

        # Add the new button on the right side
        layout_top_line.addWidget(self.add_open_web_button())
        layout_top_line.addWidget(self.add_close_button())

        return top_line

    def open_in_web(self, model_card: ModelCard):
        url = f"{model_card.server_url}/projects/{model_card.project_id}/models/{model_card.model_id}"
        webbrowser.open(url, new=0, autoraise=True)

    def add_open_web_button(self):
        open_web_btn = QPushButton(" ↗ ")
        open_web_btn.clicked.connect(lambda: self.open_in_web(self.card_content))
        open_web_btn.setStyleSheet(
            "QPushButton {"
            + f"color:rgba(130,130,130,1); border-radius: 10px;{ZERO_MARGIN_PADDING}font-size: 24px;max-width:20px;"
            + f"{BACKGR_COLOR_LIGHT_GREY} height:20px;text-align: center; "
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT_GREY2};"
            + " }"
        )
        open_web_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.open_web_btn = open_web_btn
        return open_web_btn

    def add_close_button(self):
        close_btn = QPushButton(" x ")
        close_btn.clicked.connect(
            lambda: self.remove_self_card_signal.emit(self.card_content)
        )
        close_btn.setStyleSheet(
            "QPushButton {"
            + f"color:rgba(130,130,130,1); border-radius: 10px;{ZERO_MARGIN_PADDING}font-size: 18px;"
            + f"{BACKGR_COLOR_LIGHT_GREY} height:20px;text-align: center; "
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT_GREY2};"
            + " }"
        )
        close_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.close_btn = close_btn
        return close_btn

    def add_send_btn(self):

        button_publish = QPushButton("↑")
        button_publish.setStyleSheet(
            "QPushButton {"
            + f"color:white; border-radius: 10px;{ZERO_MARGIN_PADDING}font-size: 24px;font-weight: bold;"
            + f"{BACKGR_COLOR} height:20px;text-align: center; padding: 0px 10px;"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        button_publish.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.send_model_btn = button_publish

        return button_publish

    def add_text(self, content: str, color: str = "black", other_props=""):

        # add label text (in a shape of QPushButton for easier styling)
        text = QPushButton(content)

        # reiterating callback, because QPushButton clicks are not propageted to the parent widget
        text.setStyleSheet(
            "QPushButton {"
            + f"color:{color};border-radius: 7px;{ZERO_MARGIN_PADDING}"
            + f" {BACKGR_COLOR_TRANSPARENT} height: 20px;text-align: left;{other_props}"
            + "}"
        )
        return text
