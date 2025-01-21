from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    ZERO_MARGIN_PADDING,
)
from speckle.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from speckle.ui.utils.search_widget_utils import UiSearchUtils

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
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
        self._add_account_switch_btn()
        self._add_projects(clear_cursor=True)

    def _add_projects(self, clear_cursor=False):

        new_project_cards = self.ui_search_content.get_new_projects_content(
            clear_cursor=clear_cursor
        )

        self._add_more_cards(
            new_project_cards, clear_cursor, self.ui_search_content.batch_size
        )

        # adjust size of new widget:
        self.resizeEvent()

    def refresh_projects(self):
        self._remove_all_cards()
        self._add_projects(clear_cursor=True)

    def _add_account_switch_btn(self):

        # create a line widget
        line = QWidget()
        line.setStyleSheet(
            "QWidget {"
            + f"border-radius: 0px;color:white;{ZERO_MARGIN_PADDING}"
            + "text-align: left;"
            + "}"
        )
        layout_line = QHBoxLayout(line)
        layout_line.setAlignment(Qt.AlignLeft)
        layout_line.setContentsMargins(10, 0, 0, 0)

        # Add a spacer item to push the next button to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout_line.addItem(spacer)

        # View in Web buttom
        account_switch_btn = QPushButton(" ")
        account_switch_btn.clicked.connect(
            lambda: self.ui_search_content.select_account_signal.emit()
        )
        account_switch_btn.setStyleSheet(
            "QPushButton {"
            + f"color:white; border-radius: 15px;{ZERO_MARGIN_PADDING}"
            + f"{BACKGR_COLOR} height:15px; text-align: center; padding: 0px 10px;font-size:14px"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        account_switch_btn.setFixedHeight(30)
        account_switch_btn.setFixedWidth(30)
        account_switch_btn.setText(self.ui_search_content.get_account_initials())

        account_switch_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        layout_line.addWidget(account_switch_btn)
        self.scroll_container.layout().insertWidget(1, line)

        self.account_switch_btn = account_switch_btn
