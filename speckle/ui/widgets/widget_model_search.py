from typing import Optional
from speckle.ui.utils.search_widget_utils import UiSearchUtils
from speckle.ui.widgets.background_widget import BackgroundWidget
from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
)
from speckle.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from specklepy.core.api.models.current import Project

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
)


class ModelSearchWidget(CardsListTemporaryWidget):

    ui_search_content: UiSearchUtils = None
    _project: Project = None

    def __init__(
        self,
        *,
        parent=None,
        project=None,
        label_text: str = "2/3 Select model",
        ui_search_content: UiSearchUtils = None,
    ):
        self.parent = parent
        self._project = project
        self.ui_search_content = ui_search_content

        # customize load_more function
        self._load_more = lambda: self._add_models(clear_cursor=False)

        # initialize the inherited widget, passing the card content
        super(ModelSearchWidget, self).__init__(
            parent=parent, label_text=label_text, cards_content_list=[]
        )

        self._add_search_and_account_switch_line()
        self._add_models(clear_cursor=True)

    def _add_background(self):

        # overwrite function to make background transparent
        self.background = BackgroundWidget(parent=self, transparent=True)
        self.background.show()

    def _add_models(self, clear_cursor=False, name_filter: Optional[str] = None):

        new_models_cards = (
            self.ui_search_content.get_new_models_content_with_name_condition(
                project=self._project,
                name_filter=name_filter,
            )
        )

        self._add_more_cards(
            new_models_cards, clear_cursor, self.ui_search_content.batch_size
        )

        # adjust size of new widget:
        self.resizeEvent()

    def refresh_models(self, name_filter: Optional[str] = None):
        self._remove_all_cards()
        self._add_models(clear_cursor=True, name_filter=name_filter)

    def _add_search_and_account_switch_line(self):

        # create a line widget
        line = QWidget()
        line.setStyleSheet(
            "QWidget {"
            + f"border-radius: 0px;color:white;{ZERO_MARGIN_PADDING}"
            + f"margin-left:{int(WIDGET_SIDE_BUFFER/4)};text-align: left;"
            + "}"
        )
        layout_line = QHBoxLayout(line)
        layout_line.setAlignment(Qt.AlignLeft)
        layout_line.setContentsMargins(10, 0, 0, 0)

        # model search field
        search_widget = self._create_search_widget()
        layout_line.addWidget(search_widget)

        # New model buttom
        new_model_btn = self._create_new_model_btn()
        layout_line.addWidget(new_model_btn)

        self.scroll_container.layout().insertWidget(1, line)

    def _create_search_widget(self):
        text_box = QLineEdit()
        text_box.setMaxLength(20)
        text_box.setStyleSheet(
            """QLineEdit { background-color: white; border: 1px solid lightgrey; border-radius: 5px; color: black; height: 30px }"""
        )

        text_box.textChanged.connect(lambda input_text: self.refresh_models(input_text))
        return text_box

    def _create_new_model_btn(self):

        new_item_btn = QPushButton("+")
        new_item_btn.clicked.connect(
            lambda: self.ui_search_content.new_model_widget_signal.emit(
                self._project.id
            )
        )
        new_item_btn.setStyleSheet(
            "QPushButton {"
            + f"color:white; border-radius: 5px;{ZERO_MARGIN_PADDING}"
            + f"{BACKGR_COLOR} height:30px; text-align: center; padding: 0px 10px;font-size:14px"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        new_item_btn.setFixedHeight(30)
        new_item_btn.setFixedWidth(30)

        new_item_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        return new_item_btn
