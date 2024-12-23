from typing import List, Tuple
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.core.api.models.current import (
    Model,
    Project,
    ProjectWithModels,
    ResourceCollection,
)
from specklepy.core.api.resources.current.project_resource import ProjectResource
from speckle.connectors.UI_.utils.utils import (
    clear_models_cursor,
    clear_projects_cursor,
    get_accounts,
    get_authenticate_client_for_account,
    get_models_from_client,
    get_projects_from_client,
    time_ago,
)


def get_project_search_widget_content() -> List[List]:

    # clear cursor to start a new search
    clear_projects_cursor()

    content_list: List[List] = []

    accounts: List[Account] = get_accounts()

    if len(accounts) == 0:
        # TODO handle no local accounts
        return

    speckle_client: SpeckleClient = get_authenticate_client_for_account(accounts[0])
    projects_resource_collection: ResourceCollection[Project] = (
        get_projects_from_client(speckle_client)
    )
    projects_first: List[Project] = projects_resource_collection.items

    for project in projects_first:

        # make sure to pass the actual project, not a reference to a variable
        project_content = [
            lambda project=project: get_model_search_widget_content(
                speckle_client, project
            ),
            project.name,
            project.role.split(":")[-1],
            f"updated {time_ago(project.updatedAt)}",
        ]
        content_list.append(project_content)

    return content_list


def get_model_search_widget_content(
    speckle_client: SpeckleClient, project: Project
) -> List[List]:

    # clear cursor to start a new search
    clear_models_cursor()

    content_list: List[List] = []
    models_resource_collection: ResourceCollection[Model] = get_models_from_client(
        speckle_client, project
    )
    models_first: List[Model] = models_resource_collection.items

    for model in models_first:

        # make sure to pass the actual model, not a reference to a variable
        model_content = [
            lambda model=model: add_send_model_card(
                speckle_client, model
            ),  # if a receive workflow: get_version_search_widget_content(...)
            model.name,
            f"updated {time_ago(model.updatedAt)}",
        ]
        content_list.append(model_content)

    return content_list


def add_send_model_card(*args):
    pass


def get_version_search_widget_content(
    speckle_client: SpeckleClient, project: ProjectResource
) -> List[List]:
    """Add search cards for models (only valid for Receive workflow)."""

    raise NotImplementedError("Receive workflow is not implemented")
