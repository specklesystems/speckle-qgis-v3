from typing import Any, List
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
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

    add_projects_search_signal = pyqtSignal()

    remove_model_signal = pyqtSignal(ModelCard)
    send_model_signal = pyqtSignal(ModelCard)

    child_cards: List[ModelCardWidget]

    def __init__(
        self,
        *,
        parent=None,
        cards_list: List[ModelCard] = None,
    ):
        super(ModelCardsWidget, self).__init__(parent=parent)
        self.parentWidget: Any = parent
        self.ui_model_card_utils = UiModelCardsUtils()

        self.child_cards: List[ModelCardWidget] = []

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self.add_background()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        self.create_search_button()  # will be added later to the child widget

        ##########################
        cards_selection_widget = self.create_cards_selection_widget(cards_list)

        content = QWidget()
        content.layout = QVBoxLayout(self)
        content.layout.setContentsMargins(0, LABEL_HEIGHT, 0, 0)
        content.layout.setAlignment(Qt.AlignCenter)
        content.layout.addWidget(cards_selection_widget)
        content.setStyleSheet("QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}")
        ##########################

        # add both overlapping elements to widget
        self.layout.addWidget(content)

    def create_search_button(self) -> QPushButton:

        button_publish = QPushButton("Publish")
        button_publish.clicked.connect(lambda: self.add_projects_search_signal.emit())
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
        scroll_container.layout().addWidget(self.global_publish_btn)

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
            "QLabel {font-size: 14px;color:rgba(130,130,130,1);"
            + f"{ZERO_MARGIN_PADDING}padding-left:{int(WIDGET_SIDE_BUFFER/6)}; padding-top:{int(WIDGET_SIDE_BUFFER/4)}; text-align:left;"
            + "}"
        )
        return label

    def create_scroll_area(self, cards_content_list: List[ModelCard]):

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setStyleSheet(
            "QScrollArea {"
            + f"{ZERO_MARGIN_PADDING}margin-bottom:{LABEL_HEIGHT};"  # space fot Publish btn
            + "}"
        )
        self.scroll_area.setAlignment(Qt.AlignHCenter)

        # create a widget inside scroll area
        cards_list_widget = self.create_area_with_cards(cards_content_list)
        self.scroll_area.setWidget(cards_list_widget)

        return self.scroll_area

    def create_area_with_cards(self, cards_content_list: List[ModelCard]) -> QWidget:

        cards_list_widget = QWidget()
        cards_list_widget.setStyleSheet("QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}")
        _ = QVBoxLayout(cards_list_widget)

        all_widgets = []

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
                    all_widgets.append(label)

                project_card = ModelCardWidget(self, content)
                all_widgets.append(project_card)

        for project_card in all_widgets:
            cards_list_widget.layout().addWidget(project_card)

            if isinstance(project_card, ModelCardWidget):
                self.child_cards.append(project_card)
                project_card.send_model_signal.connect(self.emit_from_child_card)

        self.cards_list_widget = cards_list_widget

        return self.cards_list_widget

    def modify_area_with_cards(self, widgets_list: List[Any]) -> QWidget:

        cards_list_widget = QWidget()
        cards_list_widget.setStyleSheet("QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}")
        _ = QVBoxLayout(cards_list_widget)

        # in case the input argument was missing or None, don't create any cards
        self.child_cards.clear()
        if isinstance(widgets_list, list):
            for widget in widgets_list:
                cards_list_widget.layout().addWidget(widget)

                if isinstance(widget, ModelCardWidget):
                    self.child_cards.append(widget)
                    widget.send_model_signal.connect(self.emit_from_child_card)

        self.cards_list_widget = cards_list_widget
        return self.cards_list_widget

    def emit_from_child_card(self, model_card: ModelCard):
        # declared as a separate function, because it's used several times
        self.send_model_signal.emit(model_card)

    def add_new_card(self, new_card: ModelCard):

        all_widgets = []
        new_card_widget = None
        for i in range(self.cards_list_widget.layout().count()):
            widget = self.cards_list_widget.layout().itemAt(i).widget()
            if isinstance(widget, ModelCardWidget):

                # check if it's the same project, to group together
                if (
                    widget.card_content.server_url == new_card.server_url
                    and widget.card_content.project_id == new_card.project_id
                ):
                    # if the same model, only add new
                    if widget.card_content.model_id == new_card.model_id:
                        if new_card_widget is None:
                            new_card_widget = ModelCardWidget(self, new_card)
                            all_widgets.append(new_card_widget)
                    else:  # add the old one and the new one
                        all_widgets.append(widget)
                        if new_card_widget is None:
                            new_card_widget = ModelCardWidget(self, new_card)
                            all_widgets.append(new_card_widget)
                else:
                    all_widgets.append(widget)

            else:  # labels
                all_widgets.append(widget)

        if new_card_widget is None:
            project: Project = self.ui_model_card_utils.get_project_by_id_from_client(
                new_card
            )
            label = self.create_widget_label(project.name)
            all_widgets.append(label)
            new_card_widget = ModelCardWidget(self, new_card)
            all_widgets.append(new_card_widget)

        assigned_cards_list_widget = self.modify_area_with_cards(all_widgets)
        self.scroll_area.setWidget(assigned_cards_list_widget)

        # adjust size of new widget:
        self.resizeEvent()

    def remove_card(self, new_card: ModelCard):

        all_widgets = []
        existing_content = []
        all_projects = []

        for i in range(self.cards_list_widget.layout().count()):
            widget = self.cards_list_widget.layout().itemAt(i).widget()
            if isinstance(widget, ModelCardWidget):
                # check if it's the card that needs to be removed
                if (
                    widget.card_content.server_url == new_card.server_url
                    and widget.card_content.project_id == new_card.project_id
                    and widget.card_content.model_id == new_card.model_id
                ):
                    # if the same model, don't add it
                    pass
                else:
                    existing_content.append(widget.card_content)
                    all_widgets.append(widget)
                    all_projects.append(widget.card_content.model_id)

            else:  # labels
                # check if previous project group has at least 1 project
                if len(all_projects) > 0:
                    # only add label if there are projects in the group
                    if len(all_projects[-1]) > 0:
                        all_widgets.append(widget)
                else:  # cannot verify, no project groups yey
                    all_widgets.append(widget)

                all_projects.append([])

        # delete label if the last project group is empty
        if len(all_projects) > 0 and len(all_projects[-1]) == 0:
            all_widgets.pop()

        # if no cards left, remove widget completely
        if len(existing_content) == 0:
            self.remove_model_signal.emit(new_card)
            self.parentWidget.remove_widget_model_cards()
            return

        assigned_cards_list_widget = self.modify_area_with_cards(all_widgets)
        self.scroll_area.setWidget(assigned_cards_list_widget)

        self.remove_model_signal.emit(new_card)

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
                self.parentWidget.frameSize().width() - int(0.5 * WIDGET_SIDE_BUFFER),
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
        return

    def destroy(self):
        return
