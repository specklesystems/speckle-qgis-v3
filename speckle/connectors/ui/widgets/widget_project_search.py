from typing import List

from speckle.connectors.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from speckle.connectors.ui.utils.connector_utils import UiSearchContent
from speckle.connectors.ui.widgets.widget_model_search import ModelSearchWidget


class ProjectSearchWidget(CardsListTemporaryWidget):

    ui_search_content: UiSearchContent = None

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "1/3 Select project",
    ):
        self.parent = parent

        # get content for project cards
        self.ui_search_content = UiSearchContent()
        projects_list = self.ui_search_content.get_project_search_widget_content()

        self.modify_card_callback(projects_list)

        super(ProjectSearchWidget, self).__init__(
            parent=parent,
            label_text=label_text,
            cards_content_list=projects_list,
        )

        self.load_more_btn.clicked.connect(lambda: self.add_projects())

    def overwrite_model_search_callback(self, card_function):
        # current function returns a content list for models
        self.parent.widget_model_search = ModelSearchWidget(
            parent=self.parent,
            cards_content_list=card_function(),
        )

        # add widgets to the layout
        self.parent.layout().addWidget(self.parent.widget_model_search)
        return self.parent.widget_model_search

    def modify_card_callback(self, projects_contents_list: List):
        # add a function for generating model card widget
        for i, content in enumerate(projects_contents_list):
            callback = content[0]

            def make_callback(v):
                return lambda: self.overwrite_model_search_callback(v)

            projects_contents_list[i][0] = make_callback(callback)

    def add_projects(self):
        new_project_cards = self.ui_search_content.get_new_projects_content()
        self.modify_card_callback(new_project_cards)
        self.add_more_cards(new_project_cards)
