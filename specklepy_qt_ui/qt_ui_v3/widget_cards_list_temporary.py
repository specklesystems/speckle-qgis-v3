from typing import List, Tuple
from PyQt5 import QtCore
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QStackedLayout,
    QLabel,
)

from specklepy_qt_ui.qt_ui.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
    FULL_HEIGHT_WIDTH,
    SPECKLE_COLOR,
    BACKGR_COLOR_LIGHT_GREY,
    BACKGR_COLOR_WHITE,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_GREY,
    BACKGR_COLOR_TRANSPARENT,
    BACKGR_COLOR_HIGHLIGHT,
    NEW_GREY,
    NEW_GREY_HIGHLIGHT,
    BACKGR_ERROR_COLOR,
    BACKGR_ERROR_COLOR_LIGHT,
)
from specklepy_qt_ui.qt_ui_v3.background import BackgroundWidget
from specklepy_qt_ui.qt_ui_v3.widget_card_from_list import CardInListWidget


class CardsListTemporaryWidget(QWidget):
    context_stack = None
    background: BackgroundWidget = None
    project_selection_widget: QWidget
    cards_list_widget: QWidget  # needed here to resize child elements
    send_data = pyqtSignal(object)

    def __init__(
        self,
        parent=None,
        label_text: str = "Label",
        cards_content_list: List[Tuple] = None,
    ):
        super(CardsListTemporaryWidget, self).__init__(parent)
        self.parentWidget: "SpeckleQGISv3Dialog" = parent

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        self.background = BackgroundWidget(parent=self)
        self.background.show()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        project_selection_widget = self.create_project_selection_widget(
            label_text, cards_content_list
        )

        content = QWidget()
        content.layout = QVBoxLayout(self)
        content.layout.setContentsMargins(
            WIDGET_SIDE_BUFFER,
            WIDGET_SIDE_BUFFER,
            WIDGET_SIDE_BUFFER,
            WIDGET_SIDE_BUFFER,
        )
        content.layout.setAlignment(Qt.AlignCenter)
        content.layout.addWidget(project_selection_widget)

        self.layout.addWidget(content)

    def create_project_selection_widget(
        self, label_text: str, cards_content_list: List[Tuple]
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

    def create_scroll_area(self, cards_content_list: List[Tuple]):

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setStyleSheet("QScrollArea {" + f"{ZERO_MARGIN_PADDING}" + "}")
        scroll_area.setAlignment(Qt.AlignHCenter)

        # create a widget inside scroll area
        cards_list_widget = self.create_area_with_cards(cards_content_list)
        scroll_area.setWidget(cards_list_widget)

        return scroll_area

    def create_area_with_cards(self, cards_content_list: List[Tuple]) -> QWidget:

        self.cards_list_widget = QWidget()
        self.cards_list_widget.setStyleSheet(
            "QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}"
        )
        _ = QVBoxLayout(self.cards_list_widget)

        for i in range(len(cards_content_list)):
            project_card = CardInListWidget(cards_content_list[i])
            self.cards_list_widget.layout().addWidget(project_card)

        return self.cards_list_widget

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)
        try:
            self.background.resize(
                self.parentWidget.frameSize().width(),
                self.parentWidget.frameSize().height(),
            )
            self.cards_list_widget.resize(
                self.parentWidget.frameSize().width() - 3 * WIDGET_SIDE_BUFFER,
                min(
                    self.cards_list_widget.height(),
                    self.parentWidget.frameSize().height() - 4 * WIDGET_SIDE_BUFFER,
                ),
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
