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
from speckle.connectors.ui.bindings import SelectionInfo
from speckle.connectors.ui.models import ModelCard, SenderModelCard
from speckle.connectors.ui.widgets.background import BackgroundWidget
from speckle.connectors.ui.widgets.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_WHITE,
    ZERO_MARGIN_PADDING,
)


class SelectionFilterWidget(QWidget):

    add_model_card_signal = pyqtSignal(ModelCard)
    background: BackgroundWidget = None
    _message_card: QWidget
    _model_card: SenderModelCard = None
    _selection_info: SelectionInfo
    _selection_info_label: QLabel
    _shadow_effect = None

    def __init__(
        self,
        parent=None,
        model_card: SenderModelCard = None,
        label_text: str = "3/3 Select objects",
        selection_info: SelectionInfo = None,
    ):
        super(SelectionFilterWidget, self).__init__(parent)
        self.parentWidget = parent
        self._selection_info = selection_info

        # update model card selection filter
        selection_filter = QgisSelectionFilter(selection_info.selected_object_ids)
        model_card.send_filter = selection_filter
        self._model_card = model_card

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self._add_background()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        self._create_fill_message_card(label_text)

        content = QWidget()
        content.layout = QVBoxLayout(self)
        content.layout.setContentsMargins(0, 0, 0, 0)
        content.layout.setAlignment(Qt.AlignCenter)
        content.layout.addWidget(self._message_card)

        self.layout.addWidget(content)

    def _create_widget_label(self, label_text: str, props: str = ""):

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

    def _create_text_widget(self, label_text: str, props: str = ""):

        label = QLabel(label_text)

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {"
            + f"{ZERO_MARGIN_PADDING}padding-left:5px;padding-right:5px;padding-bottom:5px;"
            + f"text-align:left;{props}"
            + "}"
        )
        return label

    def _add_background(self):
        self.background = BackgroundWidget(parent=self, transparent=False)
        self.background.show()

    def _add_drop_shadow(self, item=None):
        if not item:
            item = self
        # create drop shadow effect
        self._shadow_effect = QGraphicsDropShadowEffect()
        self._shadow_effect.setOffset(2, 2)
        self._shadow_effect.setBlurRadius(8)
        self._shadow_effect.setColor(QColor.fromRgb(100, 100, 100, 150))

        item.setGraphicsEffect(self._shadow_effect)

    def _create_fill_message_card(self, label_text: str):

        self._message_card = QWidget()
        self._message_card.setAttribute(Qt.WA_StyledBackground, True)
        self._message_card.setStyleSheet(
            "QWidget {" + "border-radius: 10px;" + f"{BACKGR_COLOR_WHITE}" + "}"
        )
        boxLayout = QVBoxLayout(self._message_card)

        label_main = self._create_widget_label(label_text)
        boxLayout.addWidget(label_main)

        # add text
        label = self._create_text_widget("Selection:")
        boxLayout.addWidget(label)

        # TODO: replace later with responsive item (to SelectionFilter)
        self._selection_info_label: QLabel = self._create_text_widget(
            (
                "No layers selected, go ahead and select some!"
                if not self._selection_info
                else self._selection_info.summary
            ),
            "color: blue;",
        )

        boxLayout.addWidget(self._selection_info_label)

        # add publish / load buttons
        button_publish = self._create_publish_button()
        boxLayout.addWidget(button_publish)

        self._add_drop_shadow(self._message_card)

    def _create_publish_button(self) -> QPushButton:

        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(
            lambda: self.add_model_card_signal.emit(self._model_card)
        )
        button_publish.setStyleSheet(
            "QPushButton {"
            + f"color:white;border-radius: 7px;margin:5px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR}"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        return button_publish

    def change_selection_info(self, selection_info: SelectionInfo):
        # function accessed from the parent dockwidget
        # change text on the widget
        self._selection_info_label.setText(selection_info.summary)

        # change selection info that will be passed to ModelCard
        selection_filter = QgisSelectionFilter(selection_info.selected_object_ids)
        self._model_card.send_filter = selection_filter

    def resizeEvent(self, event=None):
        QWidget.resizeEvent(self, event)
        try:
            self.background.resize(
                self.parentWidget.frameSize().width(),
                self.parentWidget.frameSize().height(),
            )

            self._message_card.setGeometry(
                int(1.5 * WIDGET_SIDE_BUFFER),
                int(
                    (
                        self.parentWidget.frameSize().height()
                        - self._message_card.height()
                    )
                    / 2
                ),
                self.parentWidget.frameSize().width() - 3 * WIDGET_SIDE_BUFFER,
                self._message_card.height(),
            )
        except RuntimeError as e:
            # e.g. Widget was deleted
            pass
