from typing import Any, Dict, List, Optional
from speckle.connectors.common.operations import SendOperation, SendOperationResult
from speckle.connectors.host_apps.qgis.connectors.utils import QgisLayerUtils
from speckle.connectors.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.connectors.host_apps.qgis.converters.utils import CRSoffsetRotation
from speckle.connectors.ui.bindings import (
    BasicConnectorBindingCommands,
    IBasicConnectorBinding,
    IBrowserBridge,
    ISelectionBinding,
    ISendBinding,
    SelectionInfo,
    SendBindingUICommands,
)
from speckle.connectors.ui.models import (
    DocumentInfo,
    DocumentModelStore,
    ISendFilter,
    ModelCard,
    SenderModelCard,
)

from qgis.core import QgsProject
from PyQt5.QtCore import pyqtSignal, QObject, QTimer


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


class MetaQObject(type(QObject), type(ISendBinding)):
    # avoiding TypeError: metaclass conflict: the metaclass of a derived class
    # must be a (non-strict) subclass of the metaclasses of all its bases
    pass


class QgisSendBinding(ISendBinding, QObject, metaclass=MetaQObject):
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

    create_conversion_settings_signal = pyqtSignal(QgsProject, CRSoffsetRotation)
    send_operation_execute_signal = pyqtSignal(list, object, object, object)
    send_operation_result: SendOperationResult = None

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
        QObject.__init__(self)
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

    def send(self, model_card_id: str) -> None:

        # get conversion settings by sending signal to the main module
        qgis_project = QgsProject.instance()
        crs_offset_rotation = CRSoffsetRotation(qgis_project.crs(), 0, 0, 0)
        self.create_conversion_settings_signal.emit(qgis_project, crs_offset_rotation)

        print(self.store.models)
        model_card: SenderModelCard = self.store.get_model_by_id(model_card_id)
        if not isinstance(model_card, SenderModelCard):
            raise Exception("Model card is not a sender model card")

        if model_card.send_filter is None:
            raise ValueError("SendFilter is None")

        # get layers ids and the layers themselves
        layer_ids: List[str] = model_card.send_filter.refresh_object_ids()
        root = qgis_project.layerTreeRoot()
        layers: List[Any] = [root.findLayer(l_id) for l_id in layer_ids]

        self.send_operation_execute_signal.emit(
            layers, model_card.get_send_info("QGIS"), None, None
        )  # should assign self.send_operation_result

        self.commads.set_model_send_result(
            model_card_id=model_card_id,
            version_id=self.send_operation_result.root_obj_id,
            send_conversion_results=self.send_operation_result.converted_references,
        )

    def cancel_send(self, model_card_id):
        return super().cancel_send(model_card_id)


class QgisSelectionBinding(ISelectionBinding, QObject, metaclass=MetaQObject):
    layer_utils: QgisLayerUtils
    name: str
    parent: IBrowserBridge
    iface: Any

    selection_changed_signal = pyqtSignal(SelectionInfo)

    def __init__(self, iface, parent=None, layer_utils=None):
        QObject.__init__(self)
        self.iface = iface
        self.name = "selectionBinding"
        self.parent = parent
        self.layer_utils = layer_utils

        # subscribe to selection change
        # use QTimer to handle the event AFTER the user UI selection event is fully processed
        # otherwise, on event trigger, the UI still has the pre-event layer selection active
        iface.layerTreeView().currentLayerChanged.connect(
            lambda: QTimer.singleShot(0, self.on_selection_changed)
        )

    def on_selection_changed(self) -> None:

        selection_info: SelectionInfo = self.get_selection()
        # instead of parent.send(set_selection event)
        self.selection_changed_signal.emit(selection_info)

    def get_selection(self):

        selected_layers = self.iface.layerTreeView().selectedLayers()

        # TODO: unpack nested layers
        all_nested_layers = selected_layers.copy()

        object_types = list(
            set(
                [
                    str(type(layer)).split(".")[-1].split("'")[0].split(">")[0]
                    for layer in all_nested_layers
                ]
            )
        )
        return SelectionInfo(
            selected_object_ids=[m.id() for m in all_nested_layers],
            summary=f"{len(all_nested_layers)} layers ({", ".join(object_types)})",
        )
