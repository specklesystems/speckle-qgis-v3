from abc import ABC
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from speckle.connectors.ui.utils.exceptions_utils import ModelNotFound


@dataclass
class SendInfo:
    # TODO
    account_id: str
    server_url: str
    project_id: str
    model_id: str
    host_application: str


class ISendFilter(ABC):
    id: str
    name: str
    summary: Optional[str]
    is_default: bool
    selected_object_ids: List[str]
    id_map: Optional[Dict[str, str]]

    def refresh_object_ids(self) -> List[str]:
        return []


class ICardSetting(ABC):
    id: Optional[str]
    title: Optional[str]
    type: Optional[str]
    value: Any
    enum: Optional[List[str]]


class CardSetting(ICardSetting):
    # TODO
    id: Optional[str]


class ModelCard(ABC):
    model_card_id: Optional[str] = None
    model_id: Optional[str] = None
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    account_id: Optional[str] = None
    server_url: Optional[str] = None
    settings: Optional[List[CardSetting]] = None


class SenderModelCard(ModelCard):
    send_filter: Optional[ISendFilter] = None

    def get_send_info(self, host_application: str) -> Optional[SendInfo]:
        return SendInfo(
            self.account_id,
            self.server_url,
            self.project_id,
            self.model_id,
            host_application,
        )


@dataclass
class DocumentInfo:
    location: str
    name: str
    id: str


class DocumentModelStore:
    models: List[ModelCard]
    is_document_init: bool

    def __init__(self, saved_model_cards: str):
        self.models = []
        self.is_document_init = False

    def document_changed(self):
        """Placeholder for connector to define."""
        return

    def get_model_by_id(self, id: str) -> ModelCard:
        try:
            return next(x for x in self.models if x.model_card_id == id)
        except StopIteration:
            raise ModelNotFound(message="Model card not found.")

    def add_model(self, model_card: ModelCard) -> None:
        self.models.append(model_card)
        self.save_state()

    def clear_and_save(self) -> None:
        self.models.clear()
        self.save_state()

    def update_model(self, model_card: ModelCard) -> None:
        try:
            index: int = next(
                i
                for i, x in enumerate(self.models)
                if x.model_card_id == model_card.model_card_id
            )
            self.models[index] = model_card
            self.save_state()

        except StopIteration:
            raise ModelNotFound(message="Model card not found to update.")

    def remove_model(self, model_card: ModelCard) -> None:
        try:
            index: int = next(
                i
                for i, x in enumerate(self.models)
                if x.model_card_id == model_card.model_card_id
            )
            self.models.pop(index)
            self.save_state()

        except StopIteration:
            raise ModelNotFound(message="Model card not found to update.")

    def on_document_changed(self) -> None:
        self.document_changed()
        return

    def get_senders(self) -> List[SenderModelCard]:
        return [x for x in self.models if isinstance(x, SenderModelCard)]

    def serialize(self) -> str:
        # TODO
        return

    def deserialize(self, models: str) -> List[ModelCard]:
        # TODO
        return

    def save_state(self) -> None:
        state = self.serialize()
        self.host_app_save_state(state)
        return

    def host_app_save_state(self, state: str) -> None:
        return

    def load_state(self) -> None:
        return

    def load_from_string(self, models: Optional[str]) -> None:
        self.models.clear()
        if not models:
            return
        self.models.extend(self.deserialize(models))
