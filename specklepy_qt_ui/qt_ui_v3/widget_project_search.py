from typing import List
from PyQt5 import QtCore
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QPushButton,
    QGroupBox,
    QHBoxLayout,
    QLabel,
)

from specklepy_qt_ui.qt_ui.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
    FULL_HEIGHT_WIDTH,
    SPECKLE_COLOR,
    BACKGR_COLOR_SEMI_TRANSPARENT,
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_GREY,
    BACKGR_COLOR_TRANSPARENT,
    BACKGR_COLOR_HIGHLIGHT,
    NEW_GREY,
    NEW_GREY_HIGHLIGHT,
    BACKGR_ERROR_COLOR,
    BACKGR_ERROR_COLOR_LIGHT,
)


class ProjectSearchWidget(QWidget):
    context_stack = None
    project_selection_widget: QWidget
    cards_list_widget: QWidget  # needed here to resize child elements
    send_data = pyqtSignal(object)

    def __init__(self, parent=None):
        super(ProjectSearchWidget, self).__init__(parent)
        self.parentWidget = parent

        # enable colored background
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(120,120,120,150);")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 60, 10, 20)
        self.layout.setAlignment(Qt.AlignCenter)

        # align with the parent widget size
        self.setGeometry(
            0,
            0,
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        project_selection_widget = self.create_project_selection_widget()
        self.layout.addWidget(project_selection_widget)

    def create_project_selection_widget(self) -> QWidget:

        # create a container
        scroll_container = self.create_container()

        # create scroll area with this widget
        label = self.create_widget_label()
        scroll_area = self.create_scroll_area()

        # add label and scroll area to the container
        scroll_container.layout().addWidget(label)
        scroll_container.layout().addWidget(scroll_area)

        return scroll_container

    def create_container(self):

        scroll_container = QWidget()
        scroll_container.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        scroll_container.setStyleSheet(
            "QWidget {"
            f"margin:{WIDGET_SIDE_BUFFER};"
            + "border-radius:5px; background-color:rgba(250,250,250,255);"
            + "}"
        )
        scroll_container_layout = QVBoxLayout(scroll_container)
        scroll_container_layout.setAlignment(Qt.AlignHCenter)

        return scroll_container

    def create_widget_label(self):

        label = QLabel("1/3 Select Project:")

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {"
            + f"padding:0px; padding-left:{int(WIDGET_SIDE_BUFFER/2)}; padding-top:{int(WIDGET_SIDE_BUFFER/4)}; margin-bottom:{int(WIDGET_SIDE_BUFFER/4)}; text-align:left;"
            + "}"
        )
        return label

    def create_scroll_area(self):

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setStyleSheet(
            "QScrollArea {"
            + f"margin:{WIDGET_SIDE_BUFFER}; margin-top:0px; padding:0px; padding-left:{int(WIDGET_SIDE_BUFFER/4)}; "
            + "}"
        )
        scroll_area.setAlignment(Qt.AlignHCenter)

        # create a widget inside scroll area
        cards_list_widget = self.create_area_with_cards()
        scroll_area.setWidget(cards_list_widget)

        return scroll_area

    def create_area_with_cards(self) -> QWidget:

        self.cards_list_widget = QWidget()
        self.cards_list_widget.setStyleSheet(
            "QWidget {" + f"{ZERO_MARGIN_PADDING}" + "}"
        )
        _ = QVBoxLayout(self.cards_list_widget)

        for i in range(10):
            project_card = self.create_project_card()
            # project_card.clicked.connect(
            #    lambda: self.parentWidget.open_select_projects_widget()
            # )
            self.cards_list_widget.layout().addWidget(project_card)

        return self.cards_list_widget

    def create_project_card(self):

        # add project card
        project_card = QWidget()
        project_card.setStyleSheet(
            "QWidget {"
            + f"border-radius: 5px;padding: 20px;margin:0px;margin-bottom: 3px;background-color:rgba(240,240,240,255);"
            + "height: 50px;"
            + "} QWidget:hover { "
            + f"background-color:rgba(225,225,225,255);"
            + "}"
        )
        project_card.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        layout = QVBoxLayout(project_card)

        # add text #1 (in a shape of QPushButton for easier styling)
        button_1 = QPushButton("Project X")
        button_1.setStyleSheet(
            "QPushButton {"
            + f"color:black;border-radius: 7px;{ZERO_MARGIN_PADDING} height: 20px;text-align: left;{BACKGR_COLOR_TRANSPARENT}"
            + "} QPushButton:hover { "
            + f"color:rgba{SPECKLE_COLOR};"
            + " }"
        )
        layout.addWidget(button_1)

        # add text #2 (in a shape of QPushButton for easier styling)
        button_role = QPushButton("My role")
        button_role.setStyleSheet(
            "QPushButton {"
            + f"color:grey;border-radius: 7px;{ZERO_MARGIN_PADDING}height: 20px;text-align: left;{BACKGR_COLOR_TRANSPARENT}"
            + " }"
        )
        layout.addWidget(button_role)

        return project_card

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)
        try:
            self.cards_list_widget.resize(
                self.parentWidget.frameSize().width() - 4 * WIDGET_SIDE_BUFFER,
                self.cards_list_widget.height(),
            )
        except RuntimeError as e:
            # e.g. Widget was deleted
            pass
