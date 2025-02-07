from typing import List
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QStackedLayout, QLabel, QPushButton

from speckle.ui.widgets.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
    BACKGR_COLOR_WHITE,
    LABEL_HEIGHT,
    BACKGR_COLOR_LIGHT_GREY2,
)
from speckle.ui.widgets.background_widget import BackgroundWidget
from speckle.ui.widgets.widget_card_from_list import CardInListWidget


class CardsListTemporaryWidget(QWidget):

    background: BackgroundWidget = None
    cards_list_widget: QWidget = None  # needed here to resize child elements
    load_more_btn: QPushButton = None
    scroll_area: QtWidgets.QScrollArea = None

    scroll_container: QWidget = None  # overall container, added after the label

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "Label",
        cards_content_list: List[List],
    ):
        super(CardsListTemporaryWidget, self).__init__(parent)
        self.parent: "SpeckleQGISv3Dialog" = parent

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self._add_background()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        self.scroll_container = self._create_cards_selection_widget(
            label_text, cards_content_list
        )

        content = QWidget()
        content.layout = QVBoxLayout(self)
        content.layout.setContentsMargins(
            WIDGET_SIDE_BUFFER,
            WIDGET_SIDE_BUFFER + LABEL_HEIGHT,
            WIDGET_SIDE_BUFFER,
            WIDGET_SIDE_BUFFER,
        )
        content.layout.setAlignment(Qt.AlignCenter)
        content.layout.addWidget(self.scroll_container)

        self.layout.addWidget(content)

    def _add_background(self):
        self.background = BackgroundWidget(parent=self, transparent=False)
        self.background.show()

    def _create_cards_selection_widget(
        self, label_text: str, cards_content_list: List[List]
    ) -> QWidget:

        # create a container
        scroll_container = self._create_container()

        # create scroll area with this widget
        label = self._create_widget_label(label_text)
        scroll_area = self._create_scroll_area(cards_content_list)

        # add label and scroll area to the container
        scroll_container.layout().addWidget(label)
        scroll_container.layout().addWidget(scroll_area)

        return scroll_container

    def _create_container(self):

        scroll_container = QWidget()
        scroll_container.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        scroll_container.setStyleSheet(
            "QWidget {"
            f"{ZERO_MARGIN_PADDING}" + f"border-radius:5px; {BACKGR_COLOR_WHITE}" + "}"
        )
        scroll_container_layout = QVBoxLayout(scroll_container)
        scroll_container_layout.setAlignment(Qt.AlignHCenter)

        return scroll_container

    def _create_widget_label(self, label_text: str):

        label = QLabel(label_text)

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {"
            + f"{ZERO_MARGIN_PADDING}padding-left:{int(WIDGET_SIDE_BUFFER/2)}; padding-top:{int(WIDGET_SIDE_BUFFER/4)}; margin-bottom:{int(WIDGET_SIDE_BUFFER/4)}; text-align:left;"
            + "}"
        )
        return label

    def _create_scroll_area(self, cards_content_list: List[List] = None):

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setStyleSheet("QScrollArea {" + f"{ZERO_MARGIN_PADDING}" + "}")
        self.scroll_area.setAlignment(Qt.AlignHCenter)

        # create a widget inside scroll area
        cards_list_widget = self._create_area_with_cards(cards_content_list)
        self.scroll_area.setWidget(cards_list_widget)

        return self.scroll_area

    def _load_more(self):
        """Overwride in the inheriting widgets."""
        return

    def _create_load_more_btn(self):

        load_more_btn = QPushButton()
        load_more_btn.clicked.connect(lambda: self._load_more())
        self.load_more_btn = load_more_btn
        self._style_load_btn()

    def _style_load_btn(self, active: bool = True, text="Load more"):

        if active:
            self.load_more_btn.setStyleSheet(
                "QWidget {"
                + f"color:black;border-width:1px;border-color:rgba(100,100,100,1);border-radius: 5px;margin-top:0px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR_WHITE}"
                + "} QWidget:hover { "
                + f"{BACKGR_COLOR_LIGHT_GREY2};"
                + " }"
            )
            self.load_more_btn.setText(text)
            self.load_more_btn.setEnabled(True)
        else:
            self.load_more_btn.setStyleSheet(
                "QWidget {"
                + f"color:grey;border-width:1px;border-color:rgba(100,100,100,1);border-radius: 5px;margin-top:0px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR_WHITE}"
                + "} QWidget:hover { "
                + f"{BACKGR_COLOR_LIGHT_GREY2};"
                + " }"
            )
            self.load_more_btn.setText(text)
            self.load_more_btn.setEnabled(False)

    def _create_area_with_cards(self, cards_content_list: List[List]) -> QWidget:

        self.cards_list_widget = QWidget()
        self.cards_list_widget.setStyleSheet(
            "QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}"
        )
        _ = QVBoxLayout(self.cards_list_widget)

        # in case the input argument was missing or None, don't create any cards
        if isinstance(cards_content_list, list):
            for content in cards_content_list:
                project_card = CardInListWidget(content)
                self.cards_list_widget.layout().addWidget(project_card)

        self._create_load_more_btn()
        self.cards_list_widget.layout().addWidget(self.load_more_btn)

        return self.cards_list_widget

    def _add_more_cards(
        self, new_cards_content_list: list, keep_scroll_on_top=False, batch_size=1
    ):

        self.cards_list_widget.setParent(None)

        existing_content = []
        for i in range(self.cards_list_widget.layout().count()):
            widget = self.cards_list_widget.layout().itemAt(i).widget()
            if isinstance(widget, CardInListWidget):
                existing_content.append(widget.card_content)

        existing_content.extend(new_cards_content_list)
        assigned_cards_list_widget = self._create_area_with_cards(existing_content)

        self.scroll_area.setWidget(assigned_cards_list_widget)

        # scroll down
        if not keep_scroll_on_top:
            vbar = self.scroll_area.verticalScrollBar()
            vbar.setValue(vbar.maximum())

        # style LoadMore buttom
        if len(new_cards_content_list) < batch_size:
            self._style_load_btn(active=False, text="No more items found")
            return

    def _remove_all_cards(self):
        all_count = self.cards_list_widget.layout().count()
        for i in range(all_count):
            # remove items by reversed index
            widget = self.cards_list_widget.layout().itemAt(all_count - i - 1).widget()
            widget.setParent(None)

    def resizeEvent(self, event=None):
        QtWidgets.QWidget.resizeEvent(self, event)
        try:
            self.background.resize(
                self.parent.frameSize().width(),
                self.parent.frameSize().height(),
            )
            self.cards_list_widget.resize(
                self.parent.frameSize().width() - 3 * WIDGET_SIDE_BUFFER,
                self.cards_list_widget.height(),
            )
        except RuntimeError as e:
            # e.g. Widget was deleted
            pass

    def installEventFilter(self):
        """Overwriting native behavior of passing click (and other) events
        to parent widgets. This is needed, so that only click on background
        itself (and not widgets on top of it) would close the widget.
        """
        return

    def mouseReleaseEvent(self, event):
        return
