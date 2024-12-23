from typing import List
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QStackedLayout, QLabel, QPushButton

from speckle.connectors.ui.widgets.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
    BACKGR_COLOR_WHITE,
    LABEL_HEIGHT,
    BACKGR_COLOR_LIGHT_GREY2,
)
from speckle.connectors.ui.widgets.background import BackgroundWidget
from speckle.connectors.ui.widgets.widget_card_from_list import CardInListWidget


class CardsListTemporaryWidget(QWidget):

    background: BackgroundWidget = None
    cards_list_widget: QWidget = None  # needed here to resize child elements
    load_more_btn: QPushButton = None
    scroll_area: QtWidgets.QScrollArea = None

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "Label",
        cards_content_list: List[List] = None,
    ):
        super(CardsListTemporaryWidget, self).__init__(parent)
        self.parentWidget: "SpeckleQGISv3Dialog" = parent

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self.add_background()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        project_selection_widget = self.create_project_selection_widget(
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
        content.layout.addWidget(project_selection_widget)

        self.layout.addWidget(content)

    def add_background(self):
        self.background = BackgroundWidget(parent=self, transparent=False)
        self.background.show()

    def create_project_selection_widget(
        self, label_text: str, cards_content_list: List[List]
    ) -> QWidget:

        # create a container
        scroll_container = self.create_container()

        # create scroll area with this widget
        label = self.create_widget_label(label_text)
        scroll_area = self.create_scroll_area(cards_content_list)

        # add label and scroll area to the container
        scroll_container.layout().addWidget(label)
        scroll_container.layout().addWidget(scroll_area)

        return scroll_container

    def create_container(self):

        scroll_container = QWidget()
        scroll_container.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        scroll_container.setStyleSheet(
            "QWidget {"
            f"{ZERO_MARGIN_PADDING}" + f"border-radius:5px; {BACKGR_COLOR_WHITE}" + "}"
        )
        scroll_container_layout = QVBoxLayout(scroll_container)
        scroll_container_layout.setAlignment(Qt.AlignHCenter)

        return scroll_container

    def create_widget_label(self, label_text: str):

        label = QLabel(label_text)

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {"
            + f"{ZERO_MARGIN_PADDING}padding-left:{int(WIDGET_SIDE_BUFFER/2)}; padding-top:{int(WIDGET_SIDE_BUFFER/4)}; margin-bottom:{int(WIDGET_SIDE_BUFFER/4)}; text-align:left;"
            + "}"
        )
        return label

    def create_scroll_area(self, cards_content_list: List[List]):

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setStyleSheet("QScrollArea {" + f"{ZERO_MARGIN_PADDING}" + "}")
        self.scroll_area.setAlignment(Qt.AlignHCenter)

        # create a widget inside scroll area
        cards_list_widget = self.create_area_with_cards(cards_content_list)
        self.scroll_area.setWidget(cards_list_widget)

        return self.scroll_area

    def load_more(self):
        """Overwride in the inheriting widgets."""
        return

    def create_load_more_btn(self):

        load_more_btn = QPushButton()
        load_more_btn.clicked.connect(lambda: self.load_more())
        self.load_more_btn = load_more_btn
        self.style_load_btn()

    def style_load_btn(self, active: bool = True, text="Load more"):

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

    def create_area_with_cards(self, cards_content_list: List[List]) -> QWidget:

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

        self.create_load_more_btn()
        self.cards_list_widget.layout().addWidget(self.load_more_btn)

        return self.cards_list_widget

    def add_more_cards(self, new_cards_content_list: list):

        self.cards_list_widget.setParent(None)

        existing_content = []
        for i in range(self.cards_list_widget.layout().count()):
            widget = self.cards_list_widget.layout().itemAt(i).widget()
            if not isinstance(widget, CardInListWidget):
                continue
            existing_content.append(widget.card_content)

        existing_content.extend(new_cards_content_list)
        assigned_cards_list_widget = self.create_area_with_cards(existing_content)

        self.scroll_area.setWidget(assigned_cards_list_widget)
        # scroll down
        vbar = self.scroll_area.verticalScrollBar()
        vbar.setValue(vbar.maximum())

        return
        # remove load button from layout
        self.load_more_btn.setParent(None)

        for content in new_cards_content_list:
            project_card = CardInListWidget(content)
            self.cards_list_widget.layout().addWidget(project_card)

        # return load button
        self.cards_list_widget.layout().addWidget(self.load_more_btn)

    def resizeEvent(self, event=None):
        QtWidgets.QWidget.resizeEvent(self, event)
        try:
            self.background.resize(
                self.parentWidget.frameSize().width(),
                self.parentWidget.frameSize().height(),
            )
            self.cards_list_widget.resize(
                self.parentWidget.frameSize().width() - 3 * WIDGET_SIDE_BUFFER,
                self.cards_list_widget.height(),
            )
        except RuntimeError as e:
            # e.g. Widget was deleted
            pass

    def installEventFilter(self):
        """Overwriting native behavior of passing click (and other) events
        to parent widgets. This is needed, so that only click on background
        itself would close the widget.
        """
        return

    def mouseReleaseEvent(self, event):
        # print("Mouse Release Event")
        return
        self.destroy()

    def destroy(self):
        return
        # remove all buttons
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        # delete reference from the parent widget
        for i in reversed(range(self.parentWidget.layout().count())):
            current_widget = self.parentWidget.layout().itemAt(i).widget()
            if current_widget is type(self):
                current_widget.setParent(None)
        self.parentWidget.widget_project_search = None
