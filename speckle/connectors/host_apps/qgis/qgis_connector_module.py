# -*- coding: utf-8 -*-

import os.path
from typing import Optional

from plugin_utils.panel_logging import logToUser

from speckle.connectors.common.api import ClientFactory
from speckle.connectors.common.credentials import AccountManager
from speckle.connectors.common.operations import AccountService, SendOperation

from speckle.connectors.host_apps.qgis.connectors.bindings import (
    QgisBasicConnectorBinding,
    QgisSendBinding,
)
from speckle.connectors.host_apps.qgis.connectors.host_app import QgisDocumentStore
from speckle.connectors.host_apps.qgis.connectors.operations import (
    QgisRootObjectBuilder,
)
from speckle.connectors.ui.models import ModelCard
from speckle.connectors.ui.widgets.dockwidget_main import SpeckleQGISv3Dialog

import webbrowser

SPECKLE_COLOR = (59, 130, 246)
SPECKLE_COLOR_LIGHT = (69, 140, 255)


class SpeckleQGISv3:
    """Speckle Connector Plugin for QGIS"""

    basic_binding: QgisBasicConnectorBinding
    send_binding: QgisSendBinding
    document_store: QgisDocumentStore
    root_obj_builder: QgisRootObjectBuilder
    account_service: AccountService

    speckle_version: str
    theads_total: int

    def __init__(self):

        self.speckle_version = "3.0.0"
        self.theads_total = 0
        self.instantiate_module_dependencies()

    def create_dockwidget(self):
        self.dockwidget = SpeckleQGISv3Dialog(
            parent=None, basic_binding=self.basic_binding
        )
        self.dockwidget.runSetup(self)
        self.connect_dockwidget_signals()

    def instantiate_module_dependencies(self):

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
        self.root_obj_builder = QgisRootObjectBuilder(
            root_to_speckle_converter=None,
            send_conversion_cache=None,
            layer_unpacker=None,
            color_unpacker=None,
            converter_settings=None,
            logger=None,
            activity_factory=None,
        )

        account_manager = AccountManager()
        self.account_service = AccountService(account_manager)
        self.client_factory = ClientFactory()

    def connect_dockwidget_signals(self):
        self.dockwidget.send_model_signal.connect(self.send_model)
        self.dockwidget.add_model_signal.connect(self.add_model_card_to_store)
        self.dockwidget.remove_model_signal.connect(self.remove_model_card_from_store)

    def add_model_card_to_store(self, model_card: ModelCard):
        print("dockwidget: to add card to Store")
        self.document_store.add_model(model_card=model_card)

    def remove_model_card_from_store(self, model_card: ModelCard):
        self.document_store.remove_model(model_card=model_card)

    def send_model(self, model_card: ModelCard):
        print(model_card.model_card_id)

        send_operation = SendOperation(
            root_object_builder=self.root_obj_builder,
            send_conversion_cache=None,
            account_service=self.account_service,
            send_progress=None,
            operations=None,
            client_factory=self.client_factory,
            activity_factory=None,
        )

        self.send_binding.send(
            model_card_id=model_card.model_card_id, send_operation=send_operation
        )

    def verify_dependencies(self):

        import urllib3
        import requests

        # if the standard QGIS libraries are used
        if (urllib3.__version__ == "1.25.11" and requests.__version__ == "2.24.0") or (
            urllib3.__version__.startswith("1.24.")
            and requests.__version__.startswith("2.23.")
        ):
            logToUser(
                "Dependencies versioning error.\nClick here for details.",
                url="dependencies_error",
                level=2,
                plugin=self.dockwidget,
            )

    def reloadUI(self):
        return

    def openUrl(self, url: str = ""):

        if url is not None and url != "":
            webbrowser.open(url, new=0, autoraise=True)
