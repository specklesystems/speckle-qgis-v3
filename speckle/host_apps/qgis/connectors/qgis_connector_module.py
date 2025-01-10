from typing import Any, Dict, List
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.host_apps.qgis.converters.to_speckle.top_level import (
    CoreObjectsBaseToSpeckleTopLevelConverter,
)
from speckle.sdk.connectors_common.api import ClientFactory
from speckle.sdk.connectors_common.credentials import AccountManager
from speckle.sdk.connectors_common.operations import (
    AccountService,
    SendOperation,
)
from speckle.host_apps.qgis.connectors.bindings import (
    QgisBasicConnectorBinding,
    QgisSelectionBinding,
    QgisSendBinding,
)
from speckle.host_apps.qgis.connectors.host_app import (
    QgisColorUnpacker,
    QgisDocumentStore,
    QgisLayerUnpacker,
)
from speckle.host_apps.qgis.connectors.operations import (
    QgisRootObjectBuilder,
)
from speckle.host_apps.qgis.connectors.utils import QgisLayerUtils

from PyQt5.QtCore import QObject


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

        self.root_obj_builder = None
        self.send_operation = None

    def create_root_builder_send_operation(self, converter_module):

        # create modules for Send operation that require conversion_settings
        self.root_obj_builder = QgisRootObjectBuilder(
            root_to_speckle_converter=CoreObjectsBaseToSpeckleTopLevelConverter(
                display_value_extractor=converter_module.display_value_extractor,
                properties_extractor=converter_module.properties_extractor,
                conversion_settings=converter_module.conversion_settings,
            ),
            send_conversion_cache=None,
            layer_unpacker=self.layer_unpacker,
            color_unpacker=self.color_unpacker,
            converter_settings=converter_module.conversion_settings,
            layer_utils=self.layer_utils,
            logger=None,
            activity_factory=None,
        )
        client_factory = ClientFactory()
        self.send_operation: SendOperation = SendOperation(
            root_object_builder=self.root_obj_builder,
            send_conversion_cache=None,
            account_service=self.account_service,
            send_progress=None,
            operations=None,
            client_factory=client_factory,
            activity_factory=None,
        )
