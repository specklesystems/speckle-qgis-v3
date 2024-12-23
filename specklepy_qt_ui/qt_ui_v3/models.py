from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from PyQt5.QtCore import pyqtSignal
from specklepy_qt_ui.server_utils.exceptions_utils import ModelNotFound


@dataclass
class SendInfo:
    AccountId: str
    ServerUrl: str
    ProjectId: str
    ModelId: str
    hostApplication: str


@dataclass
class SendFilter:
    Id: str
    Name: str
    Summary: Optional[str]
    IsDefault: bool
    SelectedObjectIds: List[str]
    IdMap: Optional[Dict[str, str]]

    def refresh_object_ids(self) -> List[str]:
        return []


@dataclass
class CardSetting:
    Id: str
    Value: dict


@dataclass
class ModelCard:
    ModelCardId: Optional[str] = None
    ModelId: Optional[str] = None
    ProjectId: Optional[str] = None
    WorkspaceId: Optional[str] = None
    AccountId: Optional[str] = None
    ServerUrl: Optional[str] = None
    Settings: Optional[List[CardSetting]] = None


class SenderModelCard(ModelCard):
    ISendFilter: Optional[SendFilter] = None

    def get_send_info(self, hostApplication: str) -> Optional[SendInfo]:
        return SendInfo(
            self.AccountId,
            self.ServerUrl,
            self.ProjectId,
            self.ModelId,
            hostApplication,
        )


class DocumentModelStore:
    Models: List[ModelCard] = None
    IsDocumentInit: bool = None

    def document_changed(self):
        """Placeholder for connector to define."""
        return

    def get_model_by_id(self, id: str) -> ModelCard:
        try:
            return next(x for x in self.Models if x.ModelCardId == id)
        except StopIteration:
            raise ModelNotFound(message="Model card not found.")

    def add_model(self, model_card: ModelCard) -> None:
        self.Models.append(model_card)
        self.save_state()

    def clear_and_save(self) -> None:
        self.Models.clear()
        self.save_state()

    def update_model(self, model_card: ModelCard) -> None:
        try:
            index: int = next(
                i
                for i, x in enumerate(self.Models)
                if x.ModelCardId == model_card.ModelCardId
            )
            self.Models[index] = model_card
            self.save_state()

        except StopIteration:
            raise ModelNotFound(message="Model card not found to update.")

    def remove_model(self, model_card: ModelCard) -> None:
        try:
            index: int = next(
                i
                for i, x in enumerate(self.Models)
                if x.ModelCardId == model_card.ModelCardId
            )
            self.Models.pop(index)
            self.save_state()

        except StopIteration:
            raise ModelNotFound(message="Model card not found to update.")

    def on_document_changed(self) -> None:
        self.document_changed()
        return

    def get_senders(self) -> List[SenderModelCard]:
        return [x for x in self.Models if isinstance(x, SenderModelCard)]

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
        self.Models.clear()
        if not models:
            return
        self.Models.extend(self.deserialize(models))
