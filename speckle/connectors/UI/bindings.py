from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, List, Optional

from speckle.connectors.UI.models import (
    DocumentInfo,
    DocumentModelStore,
    ICardSetting,
    ISendFilter,
    ModelCard,
)


class BasicConnectorBindingCommands:
    NOTIFY_DOCUMENT_CHANGED_EVENT_NAME: str = "documentChanged"
    SET_MODEL_ERROR_UI_COMMAND_NAME: str = "setModelError"
    SET_GLOBAL_NOTIFICATION: str = "setGlobalNotification"
    bridge: Any

    def __init__(self, bridge: "IBrowserBridge" = None):
        self.bridge = bridge

    def basic_connector_bindings_commands(self, bridge: Any):
        self.bridge = bridge

    def notify_document_changed(self):
        # TODO send event to Bridge (IBrowserBridge)
        return

    def set_global_notification(
        self, type: Any, title: str, message: str, autoClose: bool = True
    ):
        # TODO send notification through Bridge
        return

    def set_model_error(self, model_card_id: str, error: Exception):
        # TODO send error through Bridge
        return


class IBinding(ABC):
    name: str
    parent: Any  # IBrowserBridge


class IBasicConnectorBinding(IBinding):
    commands: BasicConnectorBindingCommands

    @abstractmethod
    def get_source_app_name() -> str:
        raise NotImplementedError

    @abstractmethod
    def get_source_app_version() -> str:
        raise NotImplementedError

    @abstractmethod
    def get_connector_version() -> str:
        raise NotImplementedError

    @abstractmethod
    def get_document_info() -> Optional[DocumentInfo]:
        raise NotImplementedError

    @abstractmethod
    def get_document_state() -> DocumentModelStore:
        raise NotImplementedError

    @abstractmethod
    def add_model(model_card: ModelCard) -> None:
        return

    @abstractmethod
    def update_model(model_card: ModelCard) -> None:
        return

    @abstractmethod
    def remove_model(model_card: ModelCard) -> None:
        return

    @abstractmethod
    def highlight_model(model_card_id: str) -> None:
        return

    @abstractmethod
    def highlight_objects(ids: str) -> None:
        return


# not a data class, so the variables can be accessed directly
class BasicConnectorBindingEvents:
    DISPLAY_TOAST_NOTIFICATION: str = "DisplayToastNotification"
    DOCUMENT_CHANGED: str = "documentChanged"


class ToastNotificationType(Enum):
    SUCCESS = auto()
    WARNING = auto()
    DANGER = auto()
    INFO = auto()


class ISendBinding(IBinding):
    get_send_filters: Callable[[], List[ISendFilter]]
    get_send_settings: Callable[[], List[ICardSetting]]
    send: Callable[[str], None]
    cancel_send: Callable[[str], None]
    commads: "SendBindingUICommands"


@dataclass
class SelectionInfo:
    selected_object_ids: List[str]
    summary: str


class ISelectionBinding(IBinding):
    get_selection: Callable[[], SelectionInfo]


class SelectionBindingEvents:
    SET_SELECTION = "setSelection"
