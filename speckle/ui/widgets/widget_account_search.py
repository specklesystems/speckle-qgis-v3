from speckle.ui.utils.search_widget_utils import UiSearchUtils
from speckle.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)


class AccountSearchWidget(CardsListTemporaryWidget):

    ui_search_content: UiSearchUtils = None

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "Select account",
        ui_search_content: UiSearchUtils = None
    ):
        self.parent = parent
        self.ui_search_content = ui_search_content

        # customize load_more function
        self._load_more = lambda: self._add_accounts(clear_cursor=False)

        # initialize the inherited widget, passing the card content
        super(AccountSearchWidget, self).__init__(
            parent=parent, label_text=label_text, cards_content_list=[]
        )

        self._add_accounts(clear_cursor=True)

    def _add_accounts(self, clear_cursor=False):

        all_accounts = self.ui_search_content.get_accounts_content()

        self._add_more_cards(
            all_accounts, clear_cursor, self.ui_search_content.batch_size
        )

        # adjust size of new widget:
        self.resizeEvent()
