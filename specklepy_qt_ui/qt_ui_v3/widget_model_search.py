from typing import List, Tuple
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


from specklepy_qt_ui.qt_ui_v3.background import BackgroundWidget
from specklepy_qt_ui.qt_ui_v3.widget_cards_list_temporary import (
    CardsListTemporaryWidget,
)


class ModelSearchWidget(CardsListTemporaryWidget):
    context_stack = None
    background: BackgroundWidget = None
    project_selection_widget: QWidget
    cards_list_widget: QWidget  # needed here to resize child elements
    send_data = pyqtSignal(object)

    def __init__(
        self,
        parent=None,
        label_text: str = "Label",
        cards_content_list: List[Tuple] = None,
    ):
        super(ModelSearchWidget, self).__init__(
            parent=parent, label_text=label_text, cards_content_list=cards_content_list
        )
