from functools import partial
from typing import Any, List
from speckle.host_apps.qgis.connectors.filters import QgisSelectionFilter
from speckle.ui.models import SenderModelCard
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.core.api.models.current import (
    Model,
    Project,
    ResourceCollection,
)
from specklepy.core.api.resources.current.project_resource import ProjectResource
from speckle.ui.utils.utils import (
    # clear_models_cursor,
    # clear_projects_cursor,
    get_accounts,
    get_authenticate_client_for_account,
    get_models_from_client,
    get_projects_from_client,
    time_ago,
)
from PyQt5.QtCore import QObject, pyqtSignal
from specklepy.logging.exceptions import SpeckleException


class UiSearchUtils(QObject):

    cursor_projects: Any = None
    cursor_models: Any = None
    speckle_client: SpeckleClient = None
    add_selection_filter_signal = pyqtSignal(SenderModelCard)
    add_models_search_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        accounts: List[Account] = get_accounts()
        if len(accounts) == 0:  # TODO handle no local accounts
            raise SpeckleException(
                "Add accounts via Speckle Desktop Manager in order to start"
            )

        self.speckle_client: SpeckleClient = get_authenticate_client_for_account(
            accounts[0]
        )

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
                partial(self._emit_function_add_models_signal, project),
                project.name,
                project.role.split(":")[-1],
                f"updated {time_ago(project.updatedAt)}",
            ]
            content_list.append(project_content)
        return content_list

    def _emit_function_add_models_signal(self, project: Project):
        # emitting the signal that will trigger creation of ModelSearch widget,
        # using the ModelCard content generated from the passed function
        self.add_models_search_signal.emit(
            lambda project=project: self.get_new_models_content(project)
        )

    def get_new_models_content(
        self,
        project: Project,
    ) -> List[List]:

        print("____Executing function. Project:")
        print(project.name)

        content_list: List[List] = []
        models_resource_collection: ResourceCollection[Model] = get_models_from_client(
            self.speckle_client, project, self.cursor_models
        )
        models_first: List[Model] = models_resource_collection.items
        self.cursor_models = models_resource_collection.cursor

        print(len(models_first))
        for model in models_first:

            # if a receive workflow: get_version_search_widget_content(...)
            model_content = [
                partial(self.add_selection_filter_widget, project, model),
                model.name,
                f"updated {time_ago(model.updatedAt)}",
                project,
            ]
            content_list.append(model_content)

        return content_list

    def add_selection_filter_widget(self, project: Project, model: Model):

        # leave "search widgets" area and send signal to the main dockwidget
        # dockwidget will kill the search widgets and display a modelCards widget
        server_url = self.speckle_client.account.serverInfo.url

        self.add_selection_filter_signal.emit(
            SenderModelCard(
                model_card_id=f"Send_{server_url}_{project.id}_{model.id}",
                model_id=model.id,
                project_id=project.id,
                workspace_id=None,
                account_id=self.speckle_client.account.id,
                server_url=server_url,
                settings=None,
                send_filter=None,
            )
        )

    def get_version_search_widget_content(self, project: ProjectResource) -> List[List]:
        """Add search cards for models (only valid for Receive workflow)."""

        raise NotImplementedError("Receive workflow is not implemented")
