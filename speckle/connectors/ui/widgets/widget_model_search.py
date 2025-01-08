from typing import List

from speckle.connectors.ui.utils.search_widget_utils import UiSearchUtils
from speckle.connectors.ui.widgets.background import BackgroundWidget
from speckle.connectors.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from specklepy.core.api.models.current import Project


class ModelSearchWidget(CardsListTemporaryWidget):

    project: Project = None

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "2/3 Select model",
        cards_content_list: List[List] = None,
        ui_search_content: UiSearchUtils = None
    ):
        self.parent = parent
        self.ui_search_content = ui_search_content

        super(ModelSearchWidget, self).__init__(
            parent=parent, label_text=label_text, cards_content_list=cards_content_list
        )

        # extract project from the first card
        for item in cards_content_list:
            if isinstance(item[-1], Project):
                self.project = cards_content_list[0][-1]
                break

        self.load_more = lambda: self.add_models()

    def add_background(self):
        # overwrite function to make background transparent
        self.background = BackgroundWidget(parent=self, transparent=True)
        self.background.show()

    def add_models(self):
        new_models_cards = self.ui_search_content.get_new_models_content(self.project)

        if len(new_models_cards) == 0:
            self.style_load_btn(active=False, text="No more models found")
            return

        self.add_more_cards(new_models_cards)

        # adjust size of new widget:
        self.resizeEvent()
