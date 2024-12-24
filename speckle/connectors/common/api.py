from abc import ABC, abstractmethod
from typing import Any, Optional

from specklepy.core.api.client import SpeckleClient
from specklepy.core.api.credentials import Account
from specklepy.objects.base import Base


class IClientFactory(ABC):
    @abstractmethod
    def create(self, account: Account) -> SpeckleClient:
        raise NotImplementedError


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
        raise NotImplementedError
