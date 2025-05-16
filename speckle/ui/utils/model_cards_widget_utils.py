from typing import Any, List, Tuple
from speckle.ui.models import ModelCard
from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account

from speckle.ui.utils.utils import (
    # clear_models_cursor,
    # clear_projects_cursor,
    get_model_by_id_from_client,
    get_project_by_id_from_client,
    get_accounts,
    get_authenticate_client_for_account,
)
from PyQt5.QtCore import QObject


class UiModelCardsUtils(QObject):

    def __init__(self):
        super().__init__()

    def get_client_from_model_card(self, model_card: ModelCard) -> SpeckleClient:
        account = None
        accounts: List[Account] = get_accounts()
        for acc in accounts:
            if acc.id == model_card.account_id:
                account = acc
                break
        if account is None:
            # TODO
            return

        speckle_client: SpeckleClient = get_authenticate_client_for_account(account)
        return speckle_client

    def get_project_by_id_from_client(self, model_card: ModelCard) -> List[List]:

        project_id: str = model_card.project_id
        speckle_client: SpeckleClient = self.get_client_from_model_card(model_card)
        if speckle_client is None:
            return

        return get_project_by_id_from_client(
            speckle_client=speckle_client, project_id=project_id
        )

    def get_model_by_id_from_client(self, model_card: ModelCard) -> List[List]:

        project_id: str = model_card.project_id
        speckle_client: SpeckleClient = self.get_client_from_model_card(model_card)
        if speckle_client is None:
            return

        return get_model_by_id_from_client(
            speckle_client=speckle_client,
            project_id=project_id,
            model_id=model_card.model_id,
        )
