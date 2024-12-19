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
    send_data = pyqtSignal(object)

    def __init__(self, parent=None):
        super(ProjectSearchWidget, self).__init__(parent)
        self.parentWidget = parent

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 60, 10, 20)
        self.layout.setAlignment(Qt.AlignTop)

        # align with the parent widget size
        self.setGeometry(
            0,
            0,
            parent.frameSize().width(),
            parent.frameSize().height(),
        )  # top left corner x, y, width, height

        child_widget = self.create_scroll_area()

        for i in range(10):
            project_card = self.create_project_card()
            # project_card.clicked.connect(
            #    lambda: self.parentWidget.open_select_projects_widget()
            # )
            child_widget.layout().addWidget(project_card)

        scroll = QtWidgets.QScrollArea()
        scroll.setStyleSheet(
            "QScrollArea {"
            + f"max-width:{self.parentWidget.frameSize().width() - 2*WIDGET_SIDE_BUFFER};"
            + "}"
        )
        scroll.setWidget(child_widget)

        self.layout.addWidget(scroll)

    def create_scroll_area(self) -> QWidget:

        child_widget = QWidget()
        boxLayout = QVBoxLayout(child_widget)

        # add text
        label = QLabel("1/3 Select Project:")
        label.setStyleSheet(
            "QLabel {margin-bottom:10px;padding: 5px;height: 20px;text-align: left;}"
        )
        boxLayout.addWidget(label)
        boxLayout.setAlignment(Qt.AlignTop)

        # align with the parent widget size
        # child_widget.setGeometry(
        #    0,
        #    0,
        #    self.parentWidget.frameSize().width() - WIDGET_SIDE_BUFFER,
        #    self.parentWidget.frameSize().height() - WIDGET_SIDE_BUFFER,
        # )  # top left corner x, y, width, height
        return child_widget

    def create_project_card(self):
        project_card = QWidget()
        project_card.setStyleSheet(
            "QWidget {"
            + f"border-radius: 5px;padding: 20px;margin:2px;height: 50px;{BACKGR_COLOR_GREY};"
            + f"width:{self.parentWidget.frameSize().width() - 2*WIDGET_SIDE_BUFFER};"
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
