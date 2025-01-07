from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

from speckle.connectors.ui.models import (
    DocumentInfo,
    DocumentModelStore,
    ICardSetting,
    ISendFilter,
    ModelCard,
)


class IBinding(ABC):
    name: str
    parent: "IBrowserBridge"  # type not declared yet


class IBrowserBridge(ABC):
    frontend_bound_name: str

    @abstractmethod
    def associate_with_bindings(self, bindings: IBinding) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_bindings_method_names(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def run_methods(self, method_name: str, request_id: str, args: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def run_on_main_thread_async(self, action: Callable) -> None:
        raise NotImplementedError

    @abstractmethod
    def send(event_name: str, cancellation_token: Any, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def top_level_exception_handler(self) -> "ITopLevelExceptionHandler":
        raise NotImplementedError


class BasicConnectorBindingCommands:
    NOTIFY_DOCUMENT_CHANGED_EVENT_NAME: str = "documentChanged"
    SET_MODEL_ERROR_UI_COMMAND_NAME: str = "setModelError"
    SET_GLOBAL_NOTIFICATION: str = "setGlobalNotification"
    bridge: IBrowserBridge

    def __init__(self, bridge: IBrowserBridge = None):
        self.bridge = bridge

    def basic_connector_bindings_commands(self, bridge: IBrowserBridge):
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


class SendBindingUICommands(BasicConnectorBindingCommands):
    REFRESH_SEND_FILTERS_UI_COMMAND_NAME: str = "refreshSendFilters"
    SET_MODELS_EXPIRED_UI_COMMAND_NAME: str = "setModelsExpired"
    SET_MODEL_SEND_RESULT_UI_COMMAND_NAME: str = "setModelSendResult"
    SET_ID_MAP_COMMAND_NAME: str = "setIdMap"

    def __init__(self, bridge: IBrowserBridge):
        super().__init__(bridge=bridge)

    def refresh_send_filter(self) -> None:
        # TODO
        # bridge.send(REFRESH_SEND_FILTERS_UI_COMMAND_NAME)
        raise NotImplementedError

    def set_models_expired(self, expired_models_ids: List[str]) -> None:
        # TODO
        # bridge.send(SET_MODELS_EXPIRED_UI_COMMAND_NAME, expired_models_ids)
        raise NotImplementedError

    def set_filter_object_ids(
        self,
        model_card_id: str,
        id_map: Dict[str, str],
        new_selected_object_ids: List[str],
    ):
        # TODO
        # bridge.send(SET_ID_MAP_COMMAND_NAME, model_card_id, id_map, new_selected_object_ids)
        raise NotImplementedError

    def set_model_send_result(
        self,
        model_card_id: str,
        version_id: str,
        send_conversion_results: List["SendConversionResults"],
    ) -> None:
        # TODO
        # bridge.send(SET_MODEL_SEND_RESULT_UI_COMMAND_NAME, model_card_id, version_id, send_conversion_results)
        # pass results to the UI
        return


class ISendBinding(IBinding, ABC):
    commads: SendBindingUICommands

    @abstractmethod
    def get_send_filters(self) -> List[ISendFilter]:
        raise NotImplementedError

    @abstractmethod
    def get_send_settings() -> List[ICardSetting]:
        raise NotImplementedError

    @abstractmethod
    def send(self, model_card_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def cancel_send(self, model_card_id: str) -> None:
        raise NotImplementedError


@dataclass
class SelectionInfo:
    selected_object_ids: List[str]
    summary: str


class ISelectionBinding(IBinding):
    @abstractmethod
    def get_selection(self) -> SelectionInfo:
        raise NotImplementedError


class SelectionBindingEvents:
    SET_SELECTION = "setSelection"
