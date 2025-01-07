from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QStackedLayout,
    QPushButton,
    QLabel,
    QGraphicsDropShadowEffect,
)

from speckle.connectors.host_apps.qgis.connectors.filters import QgisSelectionFilter
from speckle.connectors.ui.models import ModelCard, SenderModelCard
from speckle.connectors.ui.widgets.background import BackgroundWidget
from speckle.connectors.ui.widgets.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_WHITE,
    LABEL_HEIGHT,
    ZERO_MARGIN_PADDING,
)


class SelectionFilterWidget(QWidget):
    background: BackgroundWidget = None
    message_card: QWidget
    add_model_card_signal = pyqtSignal(ModelCard)
    shadow_effect = None
    model_card: SenderModelCard = None

    def __init__(
        self,
        parent=None,
        model_card=None,
        label_text: str = "3/3 Select objects",
    ):
        super(SelectionFilterWidget, self).__init__(parent)
        self.parentWidget: "SpeckleQGISv3Dialog" = parent
        self.model_card = model_card

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self.add_background()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        self.create_fill_message_card(label_text)

        content = QWidget()
        content.layout = QVBoxLayout(self)
        content.layout.setContentsMargins(0, 0, 0, 0)
        content.layout.setAlignment(Qt.AlignCenter)
        content.layout.addWidget(self.message_card)

        self.layout.addWidget(content)

    def create_widget_label(self, label_text: str, props: str = ""):

        label = QLabel(label_text)

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {"
            + f"{ZERO_MARGIN_PADDING}padding-left:{int(WIDGET_SIDE_BUFFER/2)};"
            + f"padding-top:{int(WIDGET_SIDE_BUFFER/4)}; margin-bottom:{int(WIDGET_SIDE_BUFFER/4)};"
            + f"text-align:left;{props}"
            + "}"
        )
        return label

    def create_text_widget(self, label_text: str, props: str = ""):

        label = QLabel(label_text)

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {"
            + f"{ZERO_MARGIN_PADDING}padding-left:5px;padding-right:5px;padding-bottom:5px;"
            + f"text-align:left;{props}"
            + "}"
        )
        return label

    def add_background(self):
        self.background = BackgroundWidget(parent=self, transparent=False)
        self.background.show()

    def add_drop_shadow(self, item=None):
        if not item:
            item = self
        # create drop shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setOffset(2, 2)
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setColor(QColor.fromRgb(100, 100, 100, 150))

        item.setGraphicsEffect(self.shadow_effect)

    def create_fill_message_card(self, label_text: str):

        self.message_card = QWidget()
        self.message_card.setAttribute(Qt.WA_StyledBackground, True)
        self.message_card.setStyleSheet(
            "QWidget {" + "border-radius: 10px;" + f"{BACKGR_COLOR_WHITE}" + "}"
        )
        boxLayout = QVBoxLayout(self.message_card)

        label_main = self.create_widget_label(label_text)
        boxLayout.addWidget(label_main)

        # add text
        label = self.create_text_widget("Selection:")
        boxLayout.addWidget(label)

        # TODO: replace later with responsive item (to SelectionFilter)
        label2 = self.create_text_widget(
            "No layers selected, go ahead and select some!", "color: blue;"
        )

        boxLayout.addWidget(label2)

        # add publish / load buttons
        button_publish = self.create_publish_button()
        boxLayout.addWidget(button_publish)

        self.add_drop_shadow(self.message_card)

    def create_publish_button(self) -> QPushButton:

        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(
            lambda: self.add_model_card_signal.emit(self.model_card)
        )
        button_publish.setStyleSheet(
            "QPushButton {"
            + f"color:white;border-radius: 7px;margin:5px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR}"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        return button_publish

    def resizeEvent(self, event=None):
        QWidget.resizeEvent(self, event)
        try:
            self.background.resize(
                self.parentWidget.frameSize().width(),
                self.parentWidget.frameSize().height(),
            )

            self.message_card.setGeometry(
                int(1.5 * WIDGET_SIDE_BUFFER),
                int(
                    (
                        self.parentWidget.frameSize().height()
                        - self.message_card.height()
                    )
                    / 2
                ),
                self.parentWidget.frameSize().width() - 3 * WIDGET_SIDE_BUFFER,
                self.message_card.height(),
            )
        except RuntimeError as e:
            # e.g. Widget was deleted
            pass
