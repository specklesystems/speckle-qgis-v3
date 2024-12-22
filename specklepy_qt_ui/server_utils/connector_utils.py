from typing import List, Tuple
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.core.api.models.current import Model, Project, ProjectWithModels
from specklepy.core.api.resources.current.project_resource import ProjectResource
from specklepy_qt_ui.server_utils.utils import (
    get_accounts,
    get_authenticate_client_for_account,
    get_first_models_from_client,
    get_first_projects_from_client,
    time_ago,
)


def get_project_search_widget_content() -> List[List]:

    content_list: List[List] = []

    accounts: List[Account] = get_accounts()

    if len(accounts) == 0:
        # TODO handle no local accounts
        return

    speckle_client: SpeckleClient = get_authenticate_client_for_account(accounts[0])
    projects_first: List[Project] = get_first_projects_from_client(speckle_client).items

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

    content_list: List[List] = []
    models_first: List[Model] = get_first_models_from_client(
        speckle_client, project
    ).items

    for model in models_first:

        # make sure to pass the actual model, not a reference to a variable
        model_content = [
            lambda model=model: get_version_search_widget_content(
                speckle_client, model
            ),
            model.name,
            f"updated {time_ago(model.updatedAt)}",
        ]
        content_list.append(model_content)

    return content_list


def get_version_search_widget_content(
    speckle_client: SpeckleClient, project: ProjectResource
) -> List[List]:

    return []
