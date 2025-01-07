from typing import Dict, List, Optional
from speckle.connectors.ui.models import ISendFilter


class QgisSelectionFilter(ISendFilter):

    def __init__(self, selected_object_ids=None):
        self.id: str = "selection"
        self.name: str = "Selection"
        self.is_default: bool = True
        self.selected_object_ids: List[str] = selected_object_ids or []

    def refresh_object_ids(self):
        return self.selected_object_ids
