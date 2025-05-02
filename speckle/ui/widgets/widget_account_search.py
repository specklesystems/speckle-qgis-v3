from speckle.ui.utils.search_widget_utils import UiSearchUtils
from speckle.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)

from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
)

from PyQt5.QtWidgets import QPushButton


class AccountSearchWidget(CardsListTemporaryWidget):

    ui_search_content: UiSearchUtils = None

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "Select account",
        ui_search_content: UiSearchUtils = None,
    ):
        self.parent = parent
        self.ui_search_content = ui_search_content

        # customize load_more function
        self._load_more = lambda: self._refresh_accounts(clear_cursor=False)

        # initialize the inherited widget, passing the card content
        super(AccountSearchWidget, self).__init__(
            parent=parent, label_text=label_text, cards_content_list=[]
        )

        self.refresh_accounts_widget()

    def _create_add_button(self) -> QPushButton:

        button_create = QPushButton("Add new account")
        button_create.clicked.connect(
            self.ui_search_content.open_add_new_account_widget_signal.emit
        )
        button_create.setStyleSheet(
            "QPushButton {"
            + f"color:white;border-radius: 7px;margin:5px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR}"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        return button_create

    def _refresh_accounts(self, clear_cursor=False):

        all_accounts = self.ui_search_content.get_accounts_content()

        self._add_more_cards(
            all_accounts, clear_cursor, self.ui_search_content.batch_size
        )

        # adjust size of new widget:
        self.resizeEvent()

    def refresh_accounts_widget(self):

        self._refresh_accounts(clear_cursor=True)
        button_create = self._create_add_button()
        self.cards_list_layout.addWidget(button_create)

        self.scroll_area.setWidget(self.cards_list_widget)
