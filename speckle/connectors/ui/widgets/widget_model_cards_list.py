from typing import List
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QStackedLayout,
    QLabel,
    QPushButton,
)

from speckle.connectors.ui.models import ModelCard
from speckle.connectors.ui.utils.model_cards_widget_utils import UiModelCardsUtils
from speckle.connectors.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
    LABEL_HEIGHT,
    BACKGR_COLOR_LIGHT_GREY,
    BACKGR_COLOR_LIGHT_GREY2,
)
from speckle.connectors.ui.widgets.background import BackgroundWidget
from speckle.connectors.ui.widgets.widget_model_card import ModelCardWidget
from specklepy.core.api.models.current import Project


class ModelCardsWidget(QWidget):

    ui_model_card_utils: UiModelCardsUtils = None
    background: BackgroundWidget = None
    cards_list_widget: QWidget = None  # needed here to resize child elements
    scroll_area: QtWidgets.QScrollArea = None
    global_publish_btn: QPushButton = None

    def __init__(
        self,
        *,
        parent=None,
        cards_list: List[ModelCard] = None,
    ):
        super(ModelCardsWidget, self).__init__(parent=parent)
        self.parentWidget: "SpeckleQGISv3Dialog" = parent
        self.ui_model_card_utils = UiModelCardsUtils()

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self.add_background()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        ##########################
        cards_selection_widget = self.create_cards_selection_widget(cards_list)

        content = QWidget()
        content.layout = QVBoxLayout(self)
        content.layout.setContentsMargins(
            0,
            LABEL_HEIGHT,
            0,
            0,
        )
        content.layout.setAlignment(Qt.AlignCenter)
        content.layout.addWidget(cards_selection_widget)
        ##########################

        # add both overlapping elements to widget
        self.layout.addWidget(content)

    def create_search_button(self) -> QPushButton:

        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(
            lambda: self.parentWidget.open_select_projects_widget()
        )
        button_publish.setStyleSheet(
            "QWidget {"
            + f"color:white;border-radius: 7px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR}"
            + "} QWidget:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )

        button_publish.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.global_publish_btn = button_publish

        return button_publish

    def add_background(self):
        self.background = BackgroundWidget(
            parent=self, transparent=False, background_color=BACKGR_COLOR_LIGHT_GREY2
        )
        self.background.show()

    def create_cards_selection_widget(
        self, cards_content_list: List[ModelCard]
    ) -> QWidget:

        # create a container
        scroll_container = self.create_container()

        # create scroll area with this widget
        scroll_area = self.create_scroll_area(cards_content_list)

        # add label and scroll area to the container
        scroll_container.layout().addWidget(scroll_area)

        return scroll_container

    def create_container(self):

        scroll_container = QWidget()
        scroll_container.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        scroll_container.setStyleSheet(
            "QWidget {"
            f"{ZERO_MARGIN_PADDING}{BACKGR_COLOR_LIGHT_GREY}"
            + "border-radius:0px;"  # border-color:rgba(220,220,220,1);border-width:1px;border-style:solid;"
            + "}"
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

    def create_scroll_area(self, cards_content_list: List[ModelCard]):

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setStyleSheet(
            "QScrollArea {"
            + f"{ZERO_MARGIN_PADDING}margin-bottom:{LABEL_HEIGHT};"
            + "}"
        )
        self.scroll_area.setAlignment(Qt.AlignHCenter)

        # create a widget inside scroll area
        cards_list_widget = self.create_area_with_cards(cards_content_list)
        self.scroll_area.setWidget(cards_list_widget)

        return self.scroll_area

    def create_area_with_cards(self, cards_content_list: List[ModelCard]) -> QWidget:

        self.cards_list_widget = QWidget()
        self.cards_list_widget.setStyleSheet(
            "QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}"
        )
        layout = QVBoxLayout(self.cards_list_widget)

        # in case the input argument was missing or None, don't create any cards
        if isinstance(cards_content_list, list):
            for i, content in enumerate(cards_content_list):
                project: Project = (
                    self.ui_model_card_utils.get_project_by_id_from_client(content)
                )

                # check if it's the same project, if so - skip label
                if (
                    i > 0
                    and content.server_url == cards_content_list[i - 1].server_url
                    and content.project_id == cards_content_list[i - 1].project_id
                ):
                    pass
                else:
                    label = self.create_widget_label(project.name)
                    self.cards_list_widget.layout().addWidget(label)

                project_card = ModelCardWidget(self, content)

                layout.addWidget(project_card)

        self.create_search_button()
        layout.addWidget(self.global_publish_btn)

        return self.cards_list_widget

    def add_new_card(self, new_card: ModelCard):

        self.cards_list_widget.setParent(None)

        existing_content = []
        cards_count = 0
        insert_index = -1
        for i in range(self.cards_list_widget.layout().count()):
            widget = self.cards_list_widget.layout().itemAt(i).widget()
            if isinstance(widget, ModelCardWidget):
                existing_content.append(widget.card_content)

                # check if it's the same project, to group together
                if (
                    widget.card_content.server_url == new_card.server_url
                    and widget.card_content.project_id == new_card.project_id
                ):
                    # if the same model, remove it
                    existing_content.pop()
                    cards_count -= 1
                    insert_index = cards_count

                cards_count += 1

        # add card to the end, or group with the same project cards
        if insert_index == -1:
            existing_content.append(new_card)
        else:
            existing_content.insert(insert_index + 1, new_card)

        assigned_cards_list_widget = self.create_area_with_cards(existing_content)
        self.scroll_area.setWidget(assigned_cards_list_widget)

        # adjust size of new widget:
        self.resizeEvent()

    def resizeEvent(self, event=None):
        QtWidgets.QWidget.resizeEvent(self, event)
        try:
            self.background.resize(
                self.parentWidget.frameSize().width(),
                self.parentWidget.frameSize().height(),
            )
            self.cards_list_widget.resize(
                self.parentWidget.frameSize().width() - 1 * WIDGET_SIDE_BUFFER,
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

    def destroy(self):
        return
