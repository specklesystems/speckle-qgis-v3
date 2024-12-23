from typing import Any, List, Tuple
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.core.api.models.current import (
    Model,
    Project,
    ProjectWithModels,
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
    cursor_projects: Any
    cursor_models: Any

    def __init__(self):
        super().__init__()
        self.cursor_projects = None
        self.cursor_models = None

    def get_project_search_widget_content(self) -> List[List]:

        accounts: List[Account] = get_accounts()
        if len(accounts) == 0:  # TODO handle no local accounts
            return

        speckle_client: SpeckleClient = get_authenticate_client_for_account(accounts[0])
        content_list = self.get_new_projects_content(speckle_client, None)

        return content_list

    def get_new_projects_content(self, speckle_client: SpeckleClient, cursor):

        content_list: List[List] = []
        projects_resource_collection: ResourceCollection[Project] = (
            get_projects_from_client(speckle_client, cursor)
        )
        projects_batch: List[Project] = projects_resource_collection.items
        self.cursor_projects = projects_resource_collection.cursor

        for project in projects_batch:

            # make sure to pass the actual project, not a reference to a variable
            project_content = [
                lambda project=project: self.get_model_search_widget_content(
                    speckle_client, project
                ),
                project.name,
                project.role.split(":")[-1],
                f"updated {time_ago(project.updatedAt)}",
            ]
            content_list.append(project_content)
        return content_list

    def get_model_search_widget_content(
        self, speckle_client: SpeckleClient, project: Project, cursor=None
    ) -> List[List]:

        content_list: List[List] = []
        models_resource_collection: ResourceCollection[Model] = get_models_from_client(
            speckle_client, project, cursor
        )
        models_first: List[Model] = models_resource_collection.items
        self.cursor_models = models_resource_collection.cursor

        for model in models_first:

            # make sure to pass the actual model, not a reference to a variable
            model_content = [
                lambda model=model: self.add_send_model_card(
                    speckle_client, model
                ),  # if a receive workflow: get_version_search_widget_content(...)
                model.name,
                f"updated {time_ago(model.updatedAt)}",
            ]
            content_list.append(model_content)

        return content_list

    def add_send_model_card(self, *args):
        pass

    def get_version_search_widget_content(
        self, speckle_client: SpeckleClient, project: ProjectResource
    ) -> List[List]:
        """Add search cards for models (only valid for Receive workflow)."""

        raise NotImplementedError("Receive workflow is not implemented")
