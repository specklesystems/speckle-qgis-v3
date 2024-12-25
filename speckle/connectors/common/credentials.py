from abc import ABC, abstractmethod
from typing import List, Optional

from specklepy.core.api.credentials import Account, UserInfo, get_local_accounts


class IAccountManager(ABC):

    @abstractmethod
    def get_server_info(
        self, server: str, cancellation_token: "CancellationToken" = None
    ):
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def get_user_info(
        self, token: str, server: str, cancellation_token: "CancellationToken" = None
    ) -> UserInfo:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def get_default_server_url(self) -> str:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def get_account(self, id: str) -> Account:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def upgrade_account(self, id: str) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def get_accounts(self, server_url: Optional[str] = None) -> List[Account]:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def get_default_account(self) -> Optional[Account]:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def update_accounts(self, ct: "CancellationToken" = None) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def remove_account(self, id: str) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def change_default_account(self, id: str) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def get_local_identifier_for_account(self, account: Account) -> str | None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def validate(self, account: Account) -> UserInfo:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def get_accounts_for_local_identifier(
        self, local_identifier: str
    ) -> Account | None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    @abstractmethod
    def add_account(self, server: str) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError


# not in C#, but needs to be instantiated for use in connector
class AccountManager(IAccountManager):

    def get_server_info(
        self, server: str, cancellation_token: "CancellationToken" = None
    ):
        """Placeholder for connector to define."""
        raise NotImplementedError

    def get_user_info(
        self, token: str, server: str, cancellation_token: "CancellationToken" = None
    ) -> UserInfo:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def get_default_server_url(self) -> str:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def get_account(self, id: str) -> Account:
        accounts: List[Account] = get_local_accounts()
        for acc in accounts:
            if acc.id == id:
                return acc
        raise Exception(f"Account with id '{id}' not found")

    def upgrade_account(self, id: str) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def get_accounts(self, server_url: Optional[str] = None) -> List[Account]:
        accounts: List[Account] = get_local_accounts()
        if len(accounts) == 0:
            # TODO a warning here
            return []

        return accounts

    def get_default_account(self) -> Optional[Account]:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def update_accounts(self, ct: "CancellationToken" = None) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def remove_account(self, id: str) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def change_default_account(self, id: str) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def get_local_identifier_for_account(self, account: Account) -> str | None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def validate(self, account: Account) -> UserInfo:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def get_accounts_for_local_identifier(
        self, local_identifier: str
    ) -> Account | None:
        """Placeholder for connector to define."""
        raise NotImplementedError

    def add_account(self, server: str) -> None:
        """Placeholder for connector to define."""
        raise NotImplementedError
