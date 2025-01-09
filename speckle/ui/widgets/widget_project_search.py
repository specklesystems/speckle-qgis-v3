from functools import partial
from typing import List

from speckle.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from speckle.ui.utils.search_widget_utils import UiSearchUtils

from PyQt5.QtCore import pyqtSignal, QObject


class ProjectSearchWidget(CardsListTemporaryWidget):

    ui_search_content: UiSearchUtils = None
    add_models_search_signal = pyqtSignal(object)

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
        # projects_contents_list = [function, proj_name, proj_role, proj_updatedAt]
        self.ui_search_content = UiSearchUtils()
        projects_contents_list = self.ui_search_content.get_new_projects_content(
            clear_cursor=True
        )

        # initialize the inherited widget, passing the card content
        super(ProjectSearchWidget, self).__init__(
            parent=parent,
            label_text=label_text,
            cards_content_list=projects_contents_list,
        )

        # customize load_more function
        self._load_more = lambda: self._add_projects()

    def _send_model_search_signal(self, callback):
        # needs to be a separate function, because the signal is not properly sent
        # from "partial"
        self.add_models_search_signal.emit(callback)

    def _add_projects(self):

        new_project_cards = self.ui_search_content.get_new_projects_content(
            clear_cursor=False
        )

        if len(new_project_cards) == 0:
            self._style_load_btn(active=False, text="No more projects found")
            return

        self._add_more_cards(new_project_cards)

        # adjust size of new widget:
        self.resizeEvent()
