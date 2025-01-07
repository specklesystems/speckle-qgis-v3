from typing import Any, List
from speckle.connectors.common.api import ClientFactory
from speckle.connectors.common.credentials import AccountManager
from speckle.connectors.common.operations import (
    AccountService,
    SendOperation,
    SendOperationResult,
)
from speckle.connectors.host_apps.qgis.connectors.bindings import (
    QgisBasicConnectorBinding,
    QgisSelectionBinding,
    QgisSendBinding,
)
from speckle.connectors.host_apps.qgis.connectors.host_app import (
    QgisColorUnpacker,
    QgisDocumentStore,
    QgisLayerUnpacker,
)
from speckle.connectors.host_apps.qgis.connectors.operations import (
    QgisRootObjectBuilder,
)
from speckle.connectors.host_apps.qgis.connectors.utils import QgisLayerUtils
from speckle.connectors.host_apps.qgis.converters.qgis_converter_module import (
    QgisConverterModule,
)
from speckle.connectors.host_apps.qgis.converters.settings import QgisConversionSettings

from PyQt5.QtCore import pyqtSignal, QObject
from qgis.core import QgsProject
from speckle.connectors.host_apps.qgis.converters.utils import CRSoffsetRotation
from speckle.connectors.ui.models import SendInfo


class QgisConnectorModule(QObject):

    document_store: QgisDocumentStore
    basic_binding: QgisBasicConnectorBinding
    send_binding: QgisSendBinding
    selection_binding: QgisSelectionBinding
    root_obj_builder: QgisRootObjectBuilder
    account_service: AccountService
    send_operation: SendOperation
    layer_unpacker: QgisLayerUnpacker
    color_unpacker: QgisColorUnpacker

    iface = None  # will be assigned on plugin init

    create_conversion_settings_signal = pyqtSignal(QgsProject, CRSoffsetRotation)
    send_operation_execute_signal = pyqtSignal(list, object, object, object)

    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        bridge = None
        self.document_store = QgisDocumentStore()
        self.basic_binding = QgisBasicConnectorBinding(self.document_store, bridge)
        self.send_binding = QgisSendBinding(
            parent=bridge,
            store=self.document_store,
            _service_provider=None,
            _send_filters=[],
            _cancellation_manager=None,
            send_conversion_cache=None,
            _operation_progress_manager=None,
            _logger=None,
            _top_level_exception_handler=None,
            _qgis_conversion_settings=None,
        )
        self.layer_utils = QgisLayerUtils()
        self.selection_binding = QgisSelectionBinding(
            iface=self.iface, parent=None, layer_utils=self.layer_utils
        )
        self.layer_unpacker = QgisLayerUnpacker()
        self.color_unpacker = QgisColorUnpacker()

        self.root_obj_builder = None
        account_manager = AccountManager()
        self.account_service = AccountService(account_manager)
        self.send_operation = None

        # connect to signals from child modules
        self.send_binding.create_conversion_settings_signal.connect(
            self.rethrow_create_conversion_signal
        )
        self.send_binding.send_operation_execute_signal.connect(
            self.rethrow_send_operation_execute_signal
        )

    def execute_send_operation(
        self,
        conversion_settings: QgisConversionSettings,
        layers: list,
        send_info: SendInfo,
        progress: Any,
        ct: Any,
    ):

        self.root_obj_builder = QgisRootObjectBuilder(
            root_to_speckle_converter=None,
            send_conversion_cache=None,
            layer_unpacker=self.layer_unpacker,
            color_unpacker=self.color_unpacker,
            converter_settings=conversion_settings,
            layer_utils=self.layer_utils,
            logger=None,
            activity_factory=None,
        )

        client_factory = ClientFactory()
        send_operation: SendOperation = SendOperation(
            root_object_builder=self.root_obj_builder,
            send_conversion_cache=None,
            account_service=self.account_service,
            send_progress=None,
            operations=None,
            client_factory=client_factory,
            activity_factory=None,
        )

        send_operation_result: SendOperationResult = send_operation.execute(
            objects=layers,
            send_info=send_info,
            on_operation_progressed=progress,
            ct=ct,
        )
        self.send_binding.send_operation_result = send_operation_result

    def rethrow_create_conversion_signal(
        self, project: QgsProject, crs_offsets: CRSoffsetRotation
    ):
        self.create_conversion_settings_signal.emit(project, crs_offsets)

    def rethrow_send_operation_execute_signal(
        self,
        layers: List[Any],
        send_info: SendInfo,
        progress_event_handler: Any,
        ct: Any,
    ):

        self.send_operation_execute_signal.emit(
            layers, send_info, progress_event_handler, ct
        )
