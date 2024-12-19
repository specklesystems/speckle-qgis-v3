from typing import List
from PyQt5 import QtCore
from PyQt5 import QtWidgets, uic
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
        self.setStyleSheet(BACKGR_COLOR_GREY)

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

        # create a widget inside scroll area
        cards_list_widget = self.create_area_with_cards()

        # create scroll area with this widget
        scroll_area = self.create_scroll_area()
        scroll_area.setWidget(cards_list_widget)

        # create a container for scroll area
        scroll_container = self.create_container()
        scroll_container.layout().addWidget(scroll_area)

        return scroll_container

    def create_scroll_area(self):

        scroll = QtWidgets.QScrollArea()
        scroll.setStyleSheet(
            "QScrollArea {"
            + f"width:{self.parentWidget.frameSize().width() - 2*WIDGET_SIDE_BUFFER};"
            + "}"
        )
        return scroll

    def create_container(self):

        scroll_container = QWidget()
        scroll_container.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        scroll_container.setStyleSheet(
            "QWidget {"
            f"padding: 20px;margin:{WIDGET_SIDE_BUFFER};"
            + "border-radius: 5px;background-color: rgba(250,250,250,255);"
            + "}"
        )
        scroll_container_layout = QVBoxLayout(scroll_container)
        scroll_container_layout.setAlignment(Qt.AlignHCenter)

        # add label
        label = QLabel("1/3 Select Project:")
        label.setStyleSheet(
            "QLabel {margin-bottom:10px;padding: 5px;height: 20px;text-align: left;}"
        )

        # add label and scroll area to the container
        scroll_container.layout().addWidget(label)

        return scroll_container

    def create_area_with_cards(self) -> QWidget:

        self.cards_list_widget = QWidget()
        boxLayout = QVBoxLayout(self.cards_list_widget)

        for i in range(10):
            project_card = self.create_project_card()
            # project_card.clicked.connect(
            #    lambda: self.parentWidget.open_select_projects_widget()
            # )
            self.cards_list_widget.layout().addWidget(project_card)

        return self.cards_list_widget

    def create_project_card(self):
        project_card = QWidget()
        project_card.setStyleSheet(
            "QWidget {"
            + f"border-radius: 5px;padding: 20px;margin:2px;height: 50px;{BACKGR_COLOR_GREY};"
            + "width:100%;"
            + "}"
        )
        boxLayout = QVBoxLayout(project_card)

        # add project card
        button_1 = QPushButton("Project X")
        button_1.setStyleSheet(
            "QPushButton {"
            + f"color:black;border-radius: 7px;margin-top:0px;padding: 5px;height: 20px;text-align: left;{BACKGR_COLOR_GREY}"
            + "} QPushButton:hover { "
            + f"color:{SPECKLE_COLOR};"
            + " }"
        )
        boxLayout.addWidget(button_1)

        ###
        button_role = QPushButton("My role")
        button_role.setStyleSheet(
            "QPushButton {"
            + f"color:grey;border-radius: 7px;margin-top:0px;padding: 5px;height: 20px;text-align: left;{BACKGR_COLOR_GREY}"
            + "} QPushButton:hover { "
            + f"color:{SPECKLE_COLOR};"
            + " }"
        )
        boxLayout.addWidget(button_role)

        return project_card

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)
        self.cards_list_widget.resize(
            self.parentWidget.frameSize().width() - 4 * WIDGET_SIDE_BUFFER,
            self.cards_list_widget.height(),
        )
