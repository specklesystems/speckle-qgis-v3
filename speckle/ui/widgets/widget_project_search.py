from typing import Optional
from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
)
from speckle.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from speckle.ui.utils.search_widget_utils import UiSearchUtils

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
)


class ProjectSearchWidget(CardsListTemporaryWidget):

    ui_search_content: UiSearchUtils = None
    account_switch_btn: QPushButton = None

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "1/3 Select project",
    ):
        # initialize QObject to be able to use pyQt signals before initializing parent class
        QObject.__init__(self)
        self.parent = parent

        # get content for project cards
        self.ui_search_content = UiSearchUtils()

        # customize load_more function
        self._load_more = lambda: self._add_projects(clear_cursor=False)

        # initialize the inherited widget, passing the card content
        super(ProjectSearchWidget, self).__init__(
            parent=parent,
            label_text=label_text,
            cards_content_list=[],
        )
        self._add_search_and_account_switch_line()
        self._add_projects(clear_cursor=True)

    def _add_projects(self, clear_cursor=False, name_include: Optional[str] = None):

        if name_include is None:
            # just get the projects in batches
            new_project_cards: list = self.ui_search_content.get_new_projects_content(
                clear_cursor=clear_cursor
            )
        else:
            # get the projects that match the name condition
            new_project_cards: list = (
                self.ui_search_content.get_new_projects_content_with_name_condition(
                    name_include=name_include
                )
            )

        self._add_more_cards(
            new_project_cards, clear_cursor, self.ui_search_content.batch_size
        )

        # adjust size of new widget:
        self.resizeEvent()

    def refresh_projects(self, name_include: Optional[str] = None):
        self._remove_all_cards()
        self._add_projects(clear_cursor=True, name_include=name_include)

    def _add_search_and_account_switch_line(self):

        # create a line widget
        line = QWidget()
        line.setStyleSheet(
            "QWidget {"
            + f"border-radius: 0px;color:white;{ZERO_MARGIN_PADDING}"
            + f"margin-left:{int(WIDGET_SIDE_BUFFER/4)};margin-right:{int(WIDGET_SIDE_BUFFER/4)};text-align: left;"
            + "}"
        )
        layout_line = QHBoxLayout(line)
        layout_line.setAlignment(Qt.AlignLeft)
        layout_line.setContentsMargins(10, 0, 0, 0)

        # project search field
        search_widget = self._create_search_widget()
        layout_line.addWidget(search_widget)

        # Account switch buttom
        self.account_switch_btn = self._create_account_switch_btn()
        layout_line.addWidget(self.account_switch_btn)

        self.scroll_container.layout().insertWidget(1, line)

    def _create_search_widget(self):
        text_box = QLineEdit()
        text_box.setMaxLength(20)
        text_box.setStyleSheet(
            """QLineEdit { background-color: white; border-radius: 5px; color: black; height: 30px }"""
        )

        text_box.textChanged.connect(
            lambda input_text: self.refresh_projects(input_text)
        )
        return text_box

    def _create_account_switch_btn(self):

        # Account switch buttom
        account_switch_btn = QPushButton(" ")
        account_switch_btn.clicked.connect(
            lambda: self.ui_search_content.select_account_signal.emit()
        )
        account_switch_btn.setStyleSheet(
            "QPushButton {"
            + f"color:white; border-radius: 15px;{ZERO_MARGIN_PADDING}"
            + f"{BACKGR_COLOR} height:30px; text-align: center; padding: 0px 10px;font-size:14px"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        account_switch_btn.setFixedHeight(30)
        account_switch_btn.setFixedWidth(30)
        account_switch_btn.setText(self.ui_search_content.get_account_initials())

        account_switch_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        return account_switch_btn
