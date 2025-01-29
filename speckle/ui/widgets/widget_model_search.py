from speckle.ui.utils.search_widget_utils import UiSearchUtils
from speckle.ui.widgets.background_widget import BackgroundWidget
from speckle.ui.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)
from specklepy.core.api.models.current import Project


class ModelSearchWidget(CardsListTemporaryWidget):

    ui_search_content: UiSearchUtils = None
    _project: Project = None

    def __init__(
        self,
        *,
        parent=None,
        project=None,
        label_text: str = "2/3 Select model",
        ui_search_content: UiSearchUtils = None
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

        self._add_models(clear_cursor=True)

    def _add_background(self):

        # overwrite function to make background transparent
        self.background = BackgroundWidget(parent=self, transparent=True)
        self.background.show()

    def _add_models(self, clear_cursor=False):

        new_models_cards = self.ui_search_content.get_new_models_content(
            self._project, clear_cursor=clear_cursor
        )

        self._add_more_cards(
            new_models_cards, clear_cursor, self.ui_search_content.batch_size
        )

        # adjust size of new widget:
        self.resizeEvent()
