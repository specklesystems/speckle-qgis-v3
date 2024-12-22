from datetime import datetime, timezone
from typing import List
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import (
    Account,
    get_local_accounts,
)
from specklepy.core.api.models.current import (
    Project,
    ProjectWithModels,
    ResourceCollection,
)

QUERY_LIMIT = 25
QUERY_BATCH_SIZE = 10


def get_accounts() -> List[Account]:
    """Get all local user accounts and return the reordered list,
    where the default account is first."""

    accounts: List[Account] = get_local_accounts()
    if len(accounts) == 0:
        # TODO a warning here
        return []

    sorted_accounts = accounts.copy()
    for account in accounts:
        if account.isDefault:
            sorted_accounts.remove(account)
            sorted_accounts.insert(0, account)
            break

    return sorted_accounts


def get_authenticate_client_for_account(account: Account) -> SpeckleClient:
    speckle_client = SpeckleClient(
        account.serverInfo.url, account.serverInfo.url.startswith("https")
    )
    speckle_client.authenticate_with_account(account)
    return speckle_client


def get_first_projects_from_client(
    speckle_client: SpeckleClient,
) -> ResourceCollection[Project]:

    results = []
    if speckle_client is not None:
        # possible GraphQLException
        results: ResourceCollection[Project] = speckle_client.active_user.get_projects(
            limit=QUERY_LIMIT
        )

        if not isinstance(results, ResourceCollection):
            # TODO: handle
            pass

    else:
        # TODO add a warning
        pass

    return results


def get_first_models_from_client(
    speckle_client: SpeckleClient, project: Project
) -> ResourceCollection[Project]:

    results = []
    if speckle_client is not None:
        # possible GraphQLException
        results: ProjectWithModels = speckle_client.project.get_with_models(
            project_id=project.id, models_limit=QUERY_LIMIT
        ).models

        if not isinstance(results, ResourceCollection):
            # TODO: handle
            pass

    else:
        # TODO add a warning
        pass

    return results


def time_ago(timestamp: datetime) -> str:
    now = datetime.now(timezone.utc)
    diff = now - timestamp

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30
    years = days / 365

    if seconds < 60:
        return f"{int(seconds)} second{'s' if int(seconds) != 1 else ''} ago"
    elif minutes < 60:
        return f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''} ago"
    elif hours < 24:
        return f"{int(hours)} hour{'s' if int(hours) != 1 else ''} ago"
    elif days < 7:
        return f"{int(days)} day{'s' if int(days) != 1 else ''} ago"
    elif weeks < 4:
        return f"{int(weeks)} week{'s' if int(weeks) != 1 else ''} ago"
    elif months < 12:
        return f"{int(months)} month{'s' if int(months) != 1 else ''} ago"
    else:
        return f"{int(years)} year{'s' if int(years) != 1 else ''} ago"
