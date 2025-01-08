# -*- coding: utf-8 -*-

from typing import Any
from plugin_utils.panel_logging import logToUser

from speckle.host_apps.qgis.connectors.qgis_connector_module import (
    QgisConnectorModule,
)
from speckle.host_apps.qgis.converters.qgis_converter_module import (
    QgisConverterModule,
)

from speckle.ui.models import ModelCard, SendInfo
from speckle.ui.widgets.dockwidget_main import SpeckleQGISv3Dialog

import webbrowser

SPECKLE_COLOR = (59, 130, 246)
SPECKLE_COLOR_LIGHT = (69, 140, 255)


class SpeckleQGISv3Module:
    """Speckle Connector Plugin for QGIS"""

    connector_module: QgisConnectorModule
    converter_module: QgisConverterModule
    speckle_version: str
    theads_total: int

    def __init__(self, iface):

        self.speckle_version = "3.0.0"
        self.theads_total = 0
        self.instantiate_module_dependencies(iface)

    def create_dockwidget(self):
        self.dockwidget = SpeckleQGISv3Dialog(
            parent=self, basic_binding=self.connector_module.basic_binding
        )
        self.dockwidget.runSetup(self)
        self.connect_dockwidget_signals()

    def instantiate_module_dependencies(self, iface):

        self.converter_module = QgisConverterModule()
        self.connector_module = QgisConnectorModule(iface)

        self.connect_connector_module_signals()
        self.connect_converter_module_signals()

    def connect_dockwidget_signals(self):
        self.dockwidget.send_model_signal.connect(self.send_model)
        self.dockwidget.add_model_signal.connect(self.add_model_card_to_store)
        self.dockwidget.remove_model_signal.connect(self.remove_model_card_from_store)

        # moved here frpm "connect_connector_module_signals", because it's
        # calling dockwidget and should only be accessed after dockwidget is created
        self.connector_module.selection_binding.selection_changed_signal.connect(
            self.dockwidget.handle_change_selection_info
        )

    def connect_connector_module_signals(self):
        self.connector_module.send_binding.create_conversion_settings_signal.connect(
            self.share_conversion_settings
        )
        self.connector_module.send_binding.send_operation_execute_signal.connect(
            self.connector_module.execute_send_operation
        )

    def share_conversion_settings(self, *args):
        self.connector_module.root_obj_builder.converter_settings = (
            self.converter_module.create_and_save_conversion_settings(*args)
        )

    def connect_converter_module_signals(self):
        return

    def add_model_card_to_store(self, model_card: ModelCard):
        print("dockwidget: to add card to Store")
        self.connector_module.document_store.add_model(model_card=model_card)

    def remove_model_card_from_store(self, model_card: ModelCard):
        self.connector_module.document_store.remove_model(model_card=model_card)

    def send_model(self, model_card: ModelCard):
        # receiving signal from UI and passing it to SendBinding
        print(model_card.model_card_id)
        self.connector_module.send_binding.send(model_card_id=model_card.model_card_id)

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
