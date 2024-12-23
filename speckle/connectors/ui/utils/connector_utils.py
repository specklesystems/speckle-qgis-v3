from typing import Any, List, Tuple
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


class UiSearchContent(QObject):

    cursor_projects: Any = None
    cursor_models: Any = None
    speckle_client: SpeckleClient = None

    def __init__(self):
        super().__init__()

    def get_project_search_widget_content(self) -> List[List]:

        accounts: List[Account] = get_accounts()
        if len(accounts) == 0:  # TODO handle no local accounts
            return

        self.speckle_client: SpeckleClient = get_authenticate_client_for_account(
            accounts[0]
        )
        content_list = self.get_new_projects_content()

        return content_list

    def get_new_projects_content(self):

        content_list: List[List] = []
        projects_resource_collection: ResourceCollection[Project] = (
            get_projects_from_client(self.speckle_client, self.cursor_projects)
        )
        projects_batch: List[Project] = projects_resource_collection.items
        self.cursor_projects = projects_resource_collection.cursor

        for project in projects_batch:

            # make sure to pass the actual project, not a reference to a variable
            project_content = [
                lambda project=project: self.get_new_models_content(project),
                project.name,
                project.role.split(":")[-1],
                f"updated {time_ago(project.updatedAt)}",
            ]
            content_list.append(project_content)
        return content_list

    def get_new_models_content(
        self,
        project: Project,
    ) -> List[List]:

        content_list: List[List] = []
        models_resource_collection: ResourceCollection[Model] = get_models_from_client(
            self.speckle_client, project, self.cursor_models
        )
        models_first: List[Model] = models_resource_collection.items
        self.cursor_models = models_resource_collection.cursor

        for model in models_first:

            # make sure to pass the actual model, not a reference to a variable
            model_content = [
                lambda model=model: self.add_send_model_card(
                    model
                ),  # if a receive workflow: get_version_search_widget_content(...)
                model.name,
                f"updated {time_ago(model.updatedAt)}",
                project,
            ]
            content_list.append(model_content)

        return content_list

    def add_send_model_card(self, *args):
        pass

    def get_version_search_widget_content(self, project: ProjectResource) -> List[List]:
        """Add search cards for models (only valid for Receive workflow)."""

        raise NotImplementedError("Receive workflow is not implemented")
