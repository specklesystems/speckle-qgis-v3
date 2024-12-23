from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


from speckle.connectors.UI_.widgets.background import BackgroundWidget
from speckle.connectors.UI_.widgets.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)


class ProjectSearchWidget(CardsListTemporaryWidget):

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "Label",
        cards_content_list: List[List] = None,
    ):
        super(ProjectSearchWidget, self).__init__(
            parent=parent, label_text=label_text, cards_content_list=cards_content_list
        )
