from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, List, Optional

from specklepy_qt_ui.qt_ui_v3.models import (
    DocumentInfo,
    DocumentModelStore,
    ICardSetting,
    ISendFilter,
    ModelCard,
)


class IBinding(ABC):
    name: str
    parent: Any  # IBrowserBridge


class IBasicConnectorBinding(IBinding):
    get_source_app_name: str
    get_source_app_version: str
    get_connector_version: str
    get_document_info: Optional[DocumentInfo]
    get_document_state: DocumentModelStore
    add_model: Callable[[ModelCard], None]
    update_model: Callable[[ModelCard], None]
    remove_model: Callable[[ModelCard], None]
    highlight_model: Callable[[str], None]
    highlight_objects: Callable[[List[str]], None]
    basic_connector_bindings_commands: Any  # TODO


# not a data class, so the variables can be accessed directly
class BasicConnectorBindingEvents:
    DISPLAY_TOAST_NOTIFICATION: str = "DisplayToastNotification"
    DOCUMENT_CHANGED: str = "documentChanged"


class ToastNotificationType(Enum):
    SUCCESS = auto()
    WARNING = auto()
    DANGER = auto()
    INFO = auto()


class BasicConnectorBindingCommands:
    NOTIFY_DOCUMENT_CHANGED_EVENT_NAME: str = "documentChanged"
    SET_MODEL_ERROR_UI_COMMAND_NAME: str = "setModelError"
    SET_GLOBAL_NOTIFICATION: str = "setGlobalNotification"

    bridge: Any

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
