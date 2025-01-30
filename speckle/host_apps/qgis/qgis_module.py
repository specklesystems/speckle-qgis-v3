# -*- coding: utf-8 -*-

from typing import Any, List
from plugin_utils.panel_logging import logToUser

from speckle.host_apps.qgis.connectors.qgis_connector_module import (
    QgisConnectorModule,
)
from speckle.host_apps.qgis.converters.qgis_converter_module import (
    QgisConverterModule,
)

from speckle.sdk.connectors_common.operations import SendOperationResult
from speckle.ui.models import ModelCard, SendInfo
from speckle.ui.widgets.dockwidget_main import SpeckleQGISv3Dialog

from PyQt5.QtCore import pyqtSignal

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
            bridge=self, basic_binding=self.connector_module.basic_binding
        )
        self.dockwidget.runSetup(self)
        self.connect_dockwidget_signals()
        self.connect_self_signals()

    def instantiate_module_dependencies(self, iface):

        self.converter_module = QgisConverterModule()
        self.connector_module = QgisConnectorModule(bridge=self, iface=iface)

        self.connect_connector_module_signals()
        self.connect_converter_module_signals()

    def connect_dockwidget_signals(self):
        self.dockwidget.send_model_signal.connect(self._send_model)
        self.dockwidget.add_model_signal.connect(self.add_model_card_to_store)
        self.dockwidget.remove_model_signal.connect(self.remove_model_card_from_store)

        # moved here from "connect_connector_module_signals", because it's
        # calling dockwidget and should only be accessed after dockwidget is created
        self.connector_module.selection_binding.selection_changed_signal.connect(
            self.dockwidget.handle_change_selection_info
        )

        self.connector_module.send_binding.commads.bridge_send_signal.connect(
            self.dockwidget.add_send_notification
        )  # Send a UI notification after Send operation

        # all dockwidget subscribtions to child widget signals are handled in Dockwidget class,
        # because child widget are not persistent

    def connect_self_signals(self):
        # signal to update UI, needs t be transferred to the main thread
        self.dockwidget.activity_start_signal.connect(
            self.dockwidget.add_activity_status
        )

    def connect_connector_module_signals(self):
        self.connector_module.send_binding.create_send_modules_signal.connect(
            self._create_send_modules
        )

        # move operation to worker thread
        self.connector_module.send_binding.send_operation_execute_signal.connect(
            lambda model_card_id, obj, send_info, progress, ct: self.connector_module.thread_context.run_on_thread_async(
                lambda: self._execute_send_operation(
                    model_card_id, obj, send_info, progress, ct
                ),
                False,
            )
        )

    def _execute_send_operation(
        self,
        model_card_id: str,
        objects: List[Any],
        send_info: SendInfo,
        on_operation_progressed: "IProgress[CardProgress]",
        ct: "CancellationToken",
    ):
        # execute and return send operation results
        send_operation_result: SendOperationResult = (
            self.connector_module.send_operation.execute(
                objects, send_info, on_operation_progressed, ct
            )
        )

        self.connector_module.send_binding.commads.set_model_send_result(
            model_card_id=model_card_id,
            version_id=send_operation_result.root_obj_id,
            send_conversion_results=send_operation_result.converted_references,
        )

    def _create_send_modules(self, *args):

        # create conversion settings
        self.converter_module.create_and_save_conversion_settings(*args)

        # create root object builder with conversion settings
        self.connector_module.create_root_builder_send_operation(self.converter_module)

    def connect_converter_module_signals(self):
        return

    def add_model_card_to_store(self, model_card: ModelCard):
        self.connector_module.document_store.add_model(model_card=model_card)

    def remove_model_card_from_store(self, model_card: ModelCard):
        self.connector_module.document_store.remove_model(model_card=model_card)

    def _send_model(self, model_card: ModelCard):

        # receiving signal from UI and passing it to SendBinding
        # this part of the operation will only get a model card, layers and conversion settings,
        # and send a signal to execute Build and Send

        # first, update UI status
        self.dockwidget.activity_start_signal.emit(
            model_card.model_card_id, "Preparing to send.."
        )

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
