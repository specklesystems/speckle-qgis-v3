from speckle.connectors.common.api import ClientFactory
from speckle.connectors.common.credentials import AccountManager
from speckle.connectors.common.operations import AccountService, SendOperation
from speckle.connectors.host_apps.qgis.connectors.bindings import (
    QgisBasicConnectorBinding,
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
from speckle.connectors.host_apps.qgis.converters.settings import QgisConversionSettings


class QgisConnectorModule:

    document_store: QgisDocumentStore
    basic_binding: QgisBasicConnectorBinding
    send_binding: QgisSendBinding
    root_obj_builder: QgisRootObjectBuilder
    account_service: AccountService
    send_operation: SendOperation
    layer_unpacker: QgisLayerUnpacker
    color_unpacker: QgisColorUnpacker

    def __init__(self):

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
        self.layer_unpacker = QgisLayerUnpacker()
        self.color_unpacker = QgisColorUnpacker()
        self.layer_utils = QgisLayerUtils()

        self.root_obj_builder = QgisRootObjectBuilder(
            root_to_speckle_converter=None,
            send_conversion_cache=None,
            layer_unpacker=self.layer_unpacker,
            color_unpacker=self.color_unpacker,
            converter_settings=None,
            layer_utils=self.layer_utils,
            logger=None,
            activity_factory=None,
        )

        account_manager = AccountManager()
        self.account_service = AccountService(account_manager)

        client_factory = ClientFactory()

        self.send_operation = SendOperation(
            root_object_builder=self.root_obj_builder,
            send_conversion_cache=None,
            account_service=self.account_service,
            send_progress=None,
            operations=None,
            client_factory=client_factory,
            activity_factory=None,
        )

    def add_conversion_settings(self, conversion_settings: QgisConversionSettings):

        self.root_obj_builder.converter_settings = conversion_settings
