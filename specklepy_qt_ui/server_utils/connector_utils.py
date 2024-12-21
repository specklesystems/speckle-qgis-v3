from typing import List, Tuple
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.core.api.models.current import Project
from specklepy_qt_ui.server_utils.utils import (
    get_accounts,
    get_authenticate_client_for_account,
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
    projects_first: List[Project] = get_first_projects_from_client(speckle_client)

    for project in projects_first:

        project_content = [
            lambda: get_model_search_widget_content(project),
            project.name,
            project.role.split(":")[-1],
            f"updated {time_ago(project.updatedAt)}",
        ]
        content_list.append(project_content)

    return content_list


def get_model_search_widget_content(project: Project) -> List[List]:

    content_list: List[List] = [[lambda: print(1), "Label", "Label", "Label"]]

    return content_list
