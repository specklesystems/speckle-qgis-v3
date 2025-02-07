from typing import Optional
from speckle.ui.utils.search_widget_utils import UiSearchUtils
from speckle.ui.widgets.background_widget import BackgroundWidget
from speckle.ui.widgets.utils.global_resources import (
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
)
from speckle.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from specklepy.core.api.models.current import Project

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QLineEdit,
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

    def _add_models(self, clear_cursor=False, name_include: Optional[str] = None):

        new_models_cards = (
            self.ui_search_content.get_new_models_content_with_name_condition(
                project=self._project,
                name_include=name_include,
            )
        )

        self._add_more_cards(
            new_models_cards, clear_cursor, self.ui_search_content.batch_size
        )

        # adjust size of new widget:
        self.resizeEvent()

    def _refresh_models(self, name_include: Optional[str] = None):
        self._remove_all_cards()
        self._add_models(clear_cursor=True, name_include=name_include)

    def _add_search_and_account_switch_line(self):

        # create a line widget
        line = QWidget()
        line.setStyleSheet(
            "QWidget {"
            + f"border-radius: 0px;color:white;{ZERO_MARGIN_PADDING}"
            + f"margin-left:{int(WIDGET_SIDE_BUFFER/4)};margin-right:{int(WIDGET_SIDE_BUFFER/2)};text-align: left;"
            + "}"
        )
        layout_line = QHBoxLayout(line)
        layout_line.setAlignment(Qt.AlignLeft)
        layout_line.setContentsMargins(10, 0, 0, 0)

        # model search field
        search_widget = self._create_search_widget()
        layout_line.addWidget(search_widget)

        self.scroll_container.layout().insertWidget(1, line)

    def _create_search_widget(self):
        text_box = QLineEdit()
        text_box.setMaxLength(20)
        text_box.setStyleSheet(
            """QLineEdit { background-color: white; border-radius: 5px; color: black; height: 30px }"""
        )

        text_box.textChanged.connect(
            lambda input_text: self._refresh_models(input_text)
        )
        return text_box
