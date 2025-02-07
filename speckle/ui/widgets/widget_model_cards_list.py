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

from speckle.ui.models import ModelCard, SenderModelCard
from speckle.ui.utils.model_cards_widget_utils import UiModelCardsUtils
from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
    LABEL_HEIGHT,
    BACKGR_COLOR_LIGHT_GREY,
    BACKGR_COLOR_LIGHT_GREY2,
)
from speckle.ui.widgets.background_widget import BackgroundWidget
from speckle.ui.widgets.widget_model_card import ModelCardWidget
from specklepy.core.api.models.current import Project


class ModelCardsWidget(QWidget):

    ui_model_card_utils: UiModelCardsUtils = None
    background: BackgroundWidget = None
    cards_list_widget: QWidget = None  # needed here to resize child elements
    scroll_area: QtWidgets.QScrollArea = None
    global_publish_btn: QPushButton = None

    add_projects_search_signal = pyqtSignal()
    remove_model_cards_widget_signal = pyqtSignal()

    remove_model_signal = pyqtSignal(ModelCard)
    send_model_signal = pyqtSignal(SenderModelCard)
    cancel_operation_signal = pyqtSignal(str)
    add_selection_filter_signal = pyqtSignal(SenderModelCard)

    child_cards: List[ModelCardWidget]

    def __init__(
        self,
        *,
        parent=None,
    ):
        super(ModelCardsWidget, self).__init__(parent=parent)
        self.parent: Any = parent
        self.ui_model_card_utils = UiModelCardsUtils()

        self.child_cards: List[ModelCardWidget] = []

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self._add_background()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        self._create_search_button()  # will be added later to the child widget

        ##########################
        self.scroll_container = self._create_cards_selection_widget()

        content = QWidget()
        content.layout = QVBoxLayout(self)
        content.layout.setContentsMargins(0, LABEL_HEIGHT, 0, 0)
        content.layout.setAlignment(Qt.AlignCenter)
        content.layout.addWidget(self.scroll_container)
        content.setStyleSheet("QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}")
        ##########################

        # add both overlapping elements to widget
        self.layout.addWidget(content)

    def _create_search_button(self) -> QPushButton:

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

    def _add_background(self):
        # overwrite function for custom style
        self.background = BackgroundWidget(
            parent=self,
            transparent=False,
            background_color=BACKGR_COLOR_LIGHT_GREY2,
            ignore_close_on_click=True,
        )
        self.background.show()

    def _create_cards_selection_widget(self) -> QWidget:

        # create a container
        scroll_container = self._create_container()

        # create scroll area with this widget
        scroll_area = self._create_scroll_area()

        # add label and scroll area to the container
        scroll_container.layout().addWidget(scroll_area)
        scroll_container.layout().addWidget(self.global_publish_btn)

        return scroll_container

    def _create_container(self):

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

    def _create_widget_label(self, label_text: str):

        label = QLabel(label_text)

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {font-size: 14px;color:rgba(130,130,130,1);"
            + f"{ZERO_MARGIN_PADDING}padding-left:{int(WIDGET_SIDE_BUFFER/6)}; padding-top:{int(WIDGET_SIDE_BUFFER/4)}; text-align:left;"
            + "}"
        )
        return label

    def _create_scroll_area(self):

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setStyleSheet(
            "QScrollArea {"
            + f"{ZERO_MARGIN_PADDING}margin-bottom:{LABEL_HEIGHT};"  # space fot Publish btn
            + "}"
        )
        self.scroll_area.setAlignment(Qt.AlignHCenter)

        # create a widget inside scroll area
        self._create_area_with_cards()
        self.scroll_area.setWidget(self.cards_list_widget)

        return self.scroll_area

    def _create_area_with_cards(self) -> QWidget:

        cards_list_widget = QWidget()
        cards_list_widget.setStyleSheet("QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}")
        _ = QVBoxLayout(cards_list_widget)

        self.cards_list_widget = cards_list_widget

    def _modify_area_with_cards(self, widgets_list: List[Any]) -> QWidget:

        cards_list_widget = QWidget()
        cards_list_widget.setStyleSheet("QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}")
        _ = QVBoxLayout(cards_list_widget)

        self.child_cards.clear()

        # in case the input argument was missing or None, don't create any cards
        if isinstance(widgets_list, list):
            for widget in widgets_list:
                cards_list_widget.layout().addWidget(widget)

                if isinstance(widget, ModelCardWidget):
                    self.child_cards.append(widget)

                    # if widget is not connected yet
                    if widget.connected is False:
                        widget.send_model_signal.connect(self.send_model_signal.emit)
                        widget.cancel_operation_signal.connect(
                            self.cancel_operation_signal.emit
                        )
                        widget.add_selection_filter_signal.connect(
                            self.add_selection_filter_signal.emit
                        )
                        widget.connected = True

        self.cards_list_widget = cards_list_widget
        return self.cards_list_widget

    def add_new_card(self, new_card: ModelCard) -> ModelCardWidget:

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
                    # if not the same model, add the old one and then the new one
                    if widget.card_content.model_id != new_card.model_id:
                        all_widgets.append(widget)

                    if new_card_widget is None:
                        new_card_widget = self._create_model_card_widget(new_card)
                        all_widgets.append(new_card_widget)
                else:
                    all_widgets.append(widget)

            else:  # labels
                all_widgets.append(widget)

        # if the new card widget was not yet created (injcted into a list with existing project cards),
        # create a new project label and a new widget
        if new_card_widget is None:
            project: Project = self.ui_model_card_utils.get_project_by_id_from_client(
                new_card
            )
            label = self._create_widget_label(project.name)
            all_widgets.append(label)
            new_card_widget = self._create_model_card_widget(new_card)
            all_widgets.append(new_card_widget)

        assigned_cards_list_widget = self._modify_area_with_cards(all_widgets)
        self.scroll_area.setWidget(assigned_cards_list_widget)

        # adjust size of new widget:
        self.resizeEvent()
        return new_card_widget

    def _create_model_card_widget(self, new_card: ModelCard) -> ModelCardWidget:

        new_card_widget = ModelCardWidget(self, self.ui_model_card_utils, new_card)
        new_card_widget.remove_self_card_signal.connect(self._remove_card)

        return new_card_widget

    def _remove_card(self, new_card: ModelCard):

        # signal to remove ModelCard info from DocumentStore (handled by main module)
        self.remove_model_signal.emit(new_card)

        project_groups: List[dict] = []

        for i in range(self.cards_list_widget.layout().count()):
            widget = self.cards_list_widget.layout().itemAt(i).widget()

            if not isinstance(widget, ModelCardWidget):
                # labels, will always come first before the card widgets
                # indicates start of a new project group

                # check if the previous group if empty
                self._check_for_empty_group(project_groups)

                # start a new project group, add label and a placeholder for cards
                project_groups.append({"label": widget, "cards": []})
            else:
                # confirm it's NOT the card that needs to be removed
                if not (
                    widget.card_content.server_url == new_card.server_url
                    and widget.card_content.project_id == new_card.project_id
                    and widget.card_content.model_id == new_card.model_id
                ):
                    project_groups[-1]["cards"].append(widget)

        # check if last group if empty
        self._check_for_empty_group(project_groups)

        # if no cards left, remove widget completely
        all_widgets = [
            item for gr in project_groups for item in [gr["label"]] + gr["cards"]
        ]
        if len(all_widgets) == 0:
            self.remove_model_cards_widget_signal.emit()
            return

        assigned_cards_list_widget = self._modify_area_with_cards(all_widgets)
        self.scroll_area.setWidget(assigned_cards_list_widget)

        # adjust size of new widget:
        self.resizeEvent()

    def _find_card_widget(self, model_card_id: str):

        for i in range(self.cards_list_widget.layout().count()):
            widget = self.cards_list_widget.layout().itemAt(i).widget()

            if isinstance(widget, ModelCardWidget):
                if widget.card_content.model_card_id == model_card_id:
                    return widget

        raise ValueError(f"Model Card with id '{model_card_id}' not found")

    def _check_for_empty_group(self, project_groups):

        # check if the last project group only contains a label (no cards), then delete it
        if len(project_groups) > 0 and len(project_groups[-1]["cards"]) == 0:
            project_groups.pop()

    def resizeEvent(self, event=None):
        QtWidgets.QWidget.resizeEvent(self, event)
        try:
            self.background.resize(
                self.parent.frameSize().width(),
                self.parent.frameSize().height(),
            )
            self.cards_list_widget.resize(
                self.parent.frameSize().width() - int(0.5 * WIDGET_SIDE_BUFFER),
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
