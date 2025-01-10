from abc import ABC, abstractmethod
from typing import Any, Optional

from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.core.api import operations
from specklepy.objects.base import Base
from specklepy.transports.server.server import ServerTransport


class IClientFactory(ABC):
    @abstractmethod
    def create(self, account: Account) -> SpeckleClient:
        raise NotImplementedError()


class IOperations(ABC):
    @abstractmethod
    def send(
        self,
        url: str,
        project_id: str,
        auth_token: Optional[str],
        value: Base,
        on_progress_action: Any = None,
        cancellation_token: Any = None,
    ):
        raise NotImplementedError()


# not in C#
class ClientFactory(IClientFactory):
    def create(slef, account) -> SpeckleClient:
        speckle_client = SpeckleClient(
            account.serverInfo.url, account.serverInfo.url.startswith("https")
        )
        speckle_client.authenticate_with_account(account)
        return speckle_client
