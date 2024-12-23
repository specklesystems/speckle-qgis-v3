from typing import Any, List, Tuple
from speckle.connectors.ui.models import SenderModelCard
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.core.api.models.current import (
    Model,
    Project,
    ResourceCollection,
)
from specklepy.core.api.resources.current.project_resource import ProjectResource
from speckle.connectors.ui.utils.utils import (
    # clear_models_cursor,
    # clear_projects_cursor,
    get_accounts,
    get_authenticate_client_for_account,
    get_models_from_client,
    get_projects_from_client,
    time_ago,
)
from PyQt5.QtCore import QObject
from specklepy.logging.exceptions import SpeckleException


class UiModelCardsUtils(QObject):

    def __init__(self):
        super().__init__()

    def get_version_search_widget_content(self, project: ProjectResource) -> List[List]:
        """Add search cards for models (only valid for Receive workflow)."""

        raise NotImplementedError("Receive workflow is not implemented")
