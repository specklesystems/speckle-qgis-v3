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
    ZERO_MARGIN_PADDING,
    BACKGR_COLOR_WHITE,
    BACKGR_COLOR_TRANSPARENT,
    SPECKLE_COLOR,
    BACKGR_COLOR_LIGHT_GREY,
    BACKGR_COLOR_LIGHT_GREY2,
)
from speckle.ui.widgets.utils.utils import create_text_for_widget, open_in_web
from speckle.ui.widgets.widget_model_card_notification import (
    ModelCardNotificationWidget,
)
from specklepy.core.api.models.current import Model


class ModelCardWidget(QWidget):
    card_content: ModelCard = None
    send_model_btn: QPushButton = None
    send_model_signal = pyqtSignal(SenderModelCard)
    cancel_operation_signal = pyqtSignal(SenderModelCard)
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
        top_section = self._create_card_header()
        bottom_section = self._create_send_filter_line()

        content.layout.addWidget(top_section)
        content.layout.addWidget(bottom_section)
        self.main_content = content
        self.layout.addWidget(self.main_content)

        # placeholder for notification bar to create on demand later
        self.notification_line = None

    def add_drop_shadow(self, item=None):
        if not item:
            item = self
        # create drop shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setOffset(2, 2)
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setColor(QColor.fromRgb(100, 100, 100, 150))

        item.setGraphicsEffect(self.shadow_effect)

    def _create_send_filter_line(self):
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

        clickable_text = create_text_for_widget("Selection:  ", color=SPECKLE_COLOR)
        clickable_text.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        clickable_text.clicked.connect(
            lambda: self.add_selection_filter_signal.emit(self.card_content)
        )
        layout_line.addWidget(clickable_text)

        self.selection_filter_text = create_text_for_widget(
            self.summary_text, color="rgba(130,130,130,1)"
        )
        layout_line.addWidget(self.selection_filter_text)

        return line

    def _hide_notification_line(self):

        self.layout.setCurrentWidget(self.main_content)
        self.layout.removeWidget(self.notification_line)
        self.notification_line = None

    def show_notification_line(
        self, main_text: str, btn_dismiss: bool, btn_view_web: bool, btn_cancel: bool
    ):
        if self.notification_line:
            self._hide_notification_line()

        self.notification_line = ModelCardNotificationWidget(
            self.card_content, main_text, btn_dismiss, btn_view_web, btn_cancel, self
        )
        # connect buttons from the new notification widget
        if btn_dismiss:
            self.notification_line.dismiss_btn.clicked.connect(
                lambda: self._hide_notification_line()
            )
        if btn_cancel:
            self.notification_line.cancel_operation_signal.connect(
                lambda: self.cancel_operation_signal.emit(self.card_content)
            )
        self.layout.addWidget(self.notification_line)

        # put notification widget on top
        self.layout.setCurrentWidget(self.notification_line)
        self.notification_line.resize(
            self.frameSize().width(), self.frameSize().height()
        )

    def change_selection_text(self, selection_text: str):
        # function accessed from the parent dockwidget
        # change text on the widget
        self.selection_filter_text.setText(selection_text)

    def _create_card_header(self):
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

        if isinstance(self.card_content, SenderModelCard):
            layout_top_line.addWidget(self._add_send_btn())
            self.send_model_btn.clicked.connect(
                lambda: self.send_model_signal.emit(self.card_content)
            )

        model: Model = self.ui_model_card_utils.get_model_by_id_from_client(
            self.card_content
        )
        layout_top_line.addWidget(
            create_text_for_widget(
                model.name, other_props="font-size: 14px;font-weight: bold;"
            )
        )

        # Add a spacer item to push the next button to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout_top_line.addItem(spacer)

        # Add the new button on the right side
        layout_top_line.addWidget(self._add_open_web_button())
        layout_top_line.addWidget(self._add_close_button())

        return top_line

    def _add_open_web_button(self):
        open_web_btn = QPushButton(" ↗ ")
        open_web_btn.clicked.connect(lambda: open_in_web(self.card_content))
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

    def _add_close_button(self):
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

    def _add_send_btn(self):

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
