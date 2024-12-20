from typing import List, Tuple
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
    QStackedLayout,
    QLabel,
)

from specklepy_qt_ui.qt_ui.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
    FULL_HEIGHT_WIDTH,
    SPECKLE_COLOR,
    BACKGR_COLOR_LIGHT_GREY,
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
from specklepy_qt_ui.qt_ui_v3.background import BackgroundWidget
from specklepy_qt_ui.qt_ui_v3.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)


class ProjectSearchWidget(CardsListTemporaryWidget):
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
        super(ProjectSearchWidget, self).__init__(
            parent=parent, label_text=label_text, cards_content_list=cards_content_list
        )
