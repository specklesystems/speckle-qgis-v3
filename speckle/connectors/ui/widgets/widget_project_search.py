from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


from speckle.connectors.ui.widgets.background import BackgroundWidget
from speckle.connectors.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from speckle.connectors.ui.utils.connector_utils import UiSearchContent
from speckle.connectors.ui.widgets.widget_model_search import ModelSearchWidget


class ProjectSearchWidget(CardsListTemporaryWidget):

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "1/3 Select project",
        cards_content_list: List[List] = None,
    ):
        self.parent = parent
        # get content for project cards
        projects_contents_list = UiSearchContent().get_project_search_widget_content()

        # add a function for generating model card widget
        for i, content in enumerate(projects_contents_list):
            callback = content[0]

            def make_callback(v):
                return lambda: self.overwrite_model_search_callback(v)

            projects_contents_list[i][0] = make_callback(callback)

        super(ProjectSearchWidget, self).__init__(
            parent=parent,
            label_text=label_text,
            cards_content_list=projects_contents_list,
        )

    def overwrite_model_search_callback(self, card_function):
        # current function returns a content list for models
        self.widget_model_search = ModelSearchWidget(
            parent=self.parent,
            cards_content_list=card_function(),
        )

        # add widgets to the layout
        self.parent.layout().addWidget(self.widget_model_search)
        return self.widget_model_search
