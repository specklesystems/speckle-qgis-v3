from functools import partial
from typing import Any, List, Optional
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
    create_new_project_query,
    create_new_model_query,
    get_accounts,
    get_authenticate_client_for_account,
    get_models_from_client,
    get_projects_from_client,
    time_ago,
    QUERY_BATCH_SIZE,
)
from PyQt5.QtCore import QObject, pyqtSignal
from specklepy.logging.exceptions import SpeckleException


class UiSearchUtils(QObject):

    cursor_projects: Any = None
    cursor_models: Any = None
    speckle_client: SpeckleClient = None
    batch_size: int = None
    add_selection_filter_signal = pyqtSignal(SenderModelCard)
    add_models_search_signal = pyqtSignal(Project)
    select_account_signal = pyqtSignal()
    new_project_widget_signal = pyqtSignal()
    new_model_widget_signal = pyqtSignal(str)
    change_account_and_projects_signal = pyqtSignal()

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
        self.batch_size = QUERY_BATCH_SIZE

    def get_accounts_content(self):
        accounts: List[Account] = get_accounts()
        if len(accounts) == 0:  # TODO handle no local accounts
            raise SpeckleException(
                "Add accounts via Speckle Desktop Manager in order to start"
            )

        content_list = [
            [
                partial(self._replace_projects_list_with_new_account, acc),
                acc.serverInfo.name,
                acc.serverInfo.url,
            ]
            for acc in accounts
        ]
        return content_list

    def _replace_projects_list_with_new_account(self, account: Account):
        self.speckle_client: SpeckleClient = get_authenticate_client_for_account(
            account
        )
        self.change_account_and_projects_signal.emit()

    def get_account_initials(self):
        name = self.speckle_client.account.userInfo.name
        if isinstance(name, str) and len(name) > 0:
            return name[0]

        return "X"

    def create_new_project(self, name: str, workspace_id: Optional[str] = None):
        create_new_project_query(self.speckle_client, name, workspace_id)

    def create_new_model(self, project_id: str, model_name: str):
        create_new_model_query(self.speckle_client, project_id, model_name)

    def get_new_projects_content(self, clear_cursor=False):

        if clear_cursor:
            self.cursor_projects = None

        content_list: List[List] = []
        projects_resource_collection: ResourceCollection[Project] = (
            get_projects_from_client(
                speckle_client=self.speckle_client, cursor=self.cursor_projects
            )
        )
        self.cursor_projects = projects_resource_collection.cursor
        content_list: List[List] = (
            self._create_project_content_list_from_resource_collection(
                projects_resource_collection
            )
        )

        return content_list

    def get_new_projects_content_with_name_condition(self, name_include: str):

        self.cursor_projects = None

        projects_resource_collection: ResourceCollection[Project] = (
            get_projects_from_client(
                speckle_client=self.speckle_client,
                cursor=self.cursor_projects,
                filter_keyword=name_include,
            )
        )
        self.cursor_projects = projects_resource_collection.cursor
        content_list: List[List] = (
            self._create_project_content_list_from_resource_collection(
                projects_resource_collection
            )
        )

        return content_list

    def _create_project_content_list_from_resource_collection(
        self, projects_resource_collection: ResourceCollection[Project]
    ):

        projects_batch: List[Project] = projects_resource_collection.items
        content_list: List[List] = []

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
        self.add_models_search_signal.emit(project)

    def get_new_models_content(
        self, project: Project, clear_cursor=False
    ) -> List[List]:

        if clear_cursor:
            self.cursor_models = None

        models_resource_collection: ResourceCollection[Model] = get_models_from_client(
            self.speckle_client, project, self.cursor_models
        )
        self.cursor_models = models_resource_collection.cursor
        content_list: List[List] = (
            self._create_model_content_list_from_resource_collection(
                models_resource_collection, project
            )
        )

        return content_list

    def get_new_models_content_with_name_condition(
        self, project: Project, name_include: str
    ) -> List[List]:

        self.cursor_models = None

        models_resource_collection: ResourceCollection[Model] = get_models_from_client(
            speckle_client=self.speckle_client,
            project=project,
            cursor=self.cursor_models,
            filter_keyword=name_include,
        )
        self.cursor_models = models_resource_collection.cursor
        content_list: List[List] = (
            self._create_model_content_list_from_resource_collection(
                models_resource_collection, project
            )
        )

        return content_list

    def _create_model_content_list_from_resource_collection(
        self, models_resource_collection: ResourceCollection[Model], project: Project
    ):
        models_first: List[Model] = models_resource_collection.items
        content_list: List[List] = []

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
