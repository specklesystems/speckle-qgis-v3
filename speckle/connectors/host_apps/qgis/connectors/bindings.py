from typing import Any, Dict, List, Optional
from speckle.connectors.common.operations import SendOperation
from speckle.connectors.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.connectors.ui.bindings import (
    BasicConnectorBindingCommands,
    IBasicConnectorBinding,
    IBrowserBridge,
    ISendBinding,
    SendBindingUICommands,
)
from speckle.connectors.ui.models import (
    DocumentInfo,
    DocumentModelStore,
    ISendFilter,
    ModelCard,
    SenderModelCard,
)


class QgisBasicConnectorBinding(IBasicConnectorBinding):
    store: DocumentModelStore
    speckle_application: Any  # TODO

    def __init__(self, store, parent):
        self.store = store
        self.name = "baseBinding"
        self.parent = parent
        self.commands = BasicConnectorBindingCommands(parent)

        self.store.document_changed = lambda: self.commands.notify_document_changed()

    def get_source_app_name(self) -> str:
        # TODO self.speckle_application.slug
        return ""

    def get_source_app_version(self) -> str:
        return ""

    def get_connector_version(self) -> str:
        return ""

    def get_document_info(self) -> Optional[DocumentInfo]:
        # TODO
        doc_path = "doc_path"
        doc_name = "doc_name"
        doc_id = "doc_id"
        return DocumentInfo(doc_path, doc_name, doc_id)

    def get_document_state(self) -> DocumentModelStore:
        return self.store

    def add_model(self, model_card: ModelCard) -> None:
        self.store.add_model(model_card=model_card)

    def update_model(self, model_card: ModelCard) -> None:
        self.store.update_model(model_card=model_card)

    def remove_model(self, model_card: ModelCard) -> None:
        self.store.remove_model(model_card=model_card)

    def highlight_model(self, model_card_id: str) -> None:
        return

    def highlight_objects(self, ids: str) -> None:
        return


class QgisSendBinding(ISendBinding):
    name: str = "sendBinding"
    commands: SendBindingUICommands
    parent: IBrowserBridge
    store: DocumentModelStore
    _service_provider: "IServiceProvider"
    _send_filters: List[ISendFilter]
    _cancellation_manager: "CancellationManager"
    _send_conversion_cache: "ISendConversionCache"
    _operation_progress_manager: "IOperationProgressManager"
    _logger: "ILogger[QGISSendBinding]"
    _top_level_exception_handler: "ITopLevelExceptionHandler"
    _qgis_conversion_settings: QgisConversionSettings

    changed_objects_ids: Dict[str, bytes]
    subscribed_layers: List[Any]

    def __init__(
        self,
        parent: IBrowserBridge,
        store: DocumentModelStore,
        _service_provider: "IServiceProvider",
        _send_filters: List[ISendFilter],
        _cancellation_manager: "CancellationManager",
        send_conversion_cache: "ISendConversionCache",
        _operation_progress_manager: "IOperationProgressManager",
        _logger: "ILogger[QGISSendBinding]",
        _top_level_exception_handler: "ITopLevelExceptionHandler",
        _qgis_conversion_settings: QgisConversionSettings,
    ):

        self.store = store
        self._service_provider = _service_provider
        self._send_filters = _send_filters
        self._cancellation_manager = _cancellation_manager
        self.send_conversion_cache = send_conversion_cache
        self._operation_progress_manager = _operation_progress_manager
        self._logger = _logger
        self._top_level_exception_handler = _top_level_exception_handler
        self._qgis_conversion_settings = _qgis_conversion_settings

        self.parent = parent
        self.commads = SendBindingUICommands(parent)
        self.subscribe_to_qgis_events()

        def new_func():
            self.store.document_changed()
            # TODO
            # self.send_conversion_cache.clear_cache()

        self.store.document_changed = new_func

    def subscribe_to_qgis_events(self):
        # TODO
        return

    def get_send_filters(self):
        return self._send_filters

    def get_send_settings(self):
        return []

    def send(self, model_card_id: str, send_operation: SendOperation) -> None:

        # send_operation in C# was resolved with scope.ServiceProvider,
        # and here I don't see another way to get it
        print(self.store.models)
        model_card: SenderModelCard = self.store.get_model_by_id(model_card_id)
        if not isinstance(model_card, SenderModelCard):
            raise Exception("Model card is not a sender model card")

        # TODO initialise cancellation token

        result = send_operation.execute(
            objects=["some_native_qgis_object"],
            send_info=model_card.get_send_info("QGIS"),
            on_operation_progressed=None,
            ct=None,
        )

        return result

        # self.commads.set_model_send_result(
        #    model_card_id=model_card_id, version_id="", send_conversion_results=[]
        # )

    def cancel_send(self, model_card_id):
        return super().cancel_send(model_card_id)
