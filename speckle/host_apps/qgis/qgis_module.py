# -*- coding: utf-8 -*-

from typing import Any, List
from plugin_utils.panel_logging import display_and_log

from speckle.host_apps.qgis.connectors.qgis_connector_module import (
    QgisConnectorModule,
)
from speckle.host_apps.qgis.converters.qgis_converter_module import (
    QgisConverterModule,
)

from speckle.sdk.connectors_common.operations import SendOperationResult
from speckle.ui.models import ModelCard, SendInfo
from speckle.ui.widgets.dockwidget_main import SpeckleQGISv3Dialog

import webbrowser


class SpeckleQGISv3Module:
    """Speckle Connector Plugin for QGIS"""

    connector_module: QgisConnectorModule
    converter_module: QgisConverterModule

    def __init__(self, iface):

        self.instantiate_module_dependencies(iface)

    def create_dockwidget(self):
        self.dockwidget = SpeckleQGISv3Dialog(
            bridge=self, basic_binding=self.connector_module.basic_binding
        )
        self.dockwidget.header_widget = self.dockwidget.create_header(self)
        self.dockwidget.runSetup()
        self.connect_dockwidget_signals()

    def instantiate_module_dependencies(self, iface):

        self.converter_module = QgisConverterModule()
        self.connector_module = QgisConnectorModule(bridge=self, iface=iface)

        self.connect_connector_module_signals()
        self.connect_converter_module_signals()

    def connect_dockwidget_signals(self):
        self.dockwidget.send_model_signal.connect(self._send_model)
        self.dockwidget.add_model_signal.connect(self.add_model_card_to_store)
        self.dockwidget.remove_model_signal.connect(self.remove_model_card_from_store)
        self.dockwidget.cancel_operation_signal.connect(self._cancel_operation)

        # moved here from "connect_connector_module_signals", because it's
        # calling dockwidget and should only be accessed after dockwidget is created
        self.connector_module.selection_binding.selection_changed_signal.connect(
            self.dockwidget.handle_change_selection_info
        )

        self.connector_module.send_binding.commads.bridge_send_signal.connect(
            self.dockwidget.add_send_notification
        )  # Send a UI notification after Send operation

        # refresh widgets if document change signal received
        self.connector_module.document_store.document_changed_signal.connect(
            self.dockwidget.refresh_ui
        )

        # signal to update UI, needs to be transferred to the main thread
        self.dockwidget.activity_start_signal.connect(
            self.dockwidget.add_activity_status
        )
        # all dockwidget subscribtions to child widget signals are handled in Dockwidget class,
        # because child widget are not persistent

    def connect_connector_module_signals(self):
        # create conversion settings and RootObjectBuilder
        self.connector_module.send_binding.create_send_modules_signal.connect(
            self._create_send_modules
        )

        # move operation to worker thread
        self.connector_module.send_binding.send_operation_execute_signal.connect(
            lambda model_card_id, obj, send_info, progress, ct: self.connector_module.thread_context.run_on_thread_async(
                lambda: self._execute_send_operation(
                    model_card_id, obj, send_info, progress, ct
                ),
                model_card_id,
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

        # first, update UI status
        self.dockwidget.activity_start_signal.emit(
            model_card_id, "Converting and sending.."
        )

        print("_execute_send_operation, send_operation.execute:")
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

    def _cancel_operation(self, model_card_id: str):

        # 1. cancel operations
        # This will mark CalcellationTokenSource as Canceled. The actual operation will only be cancelled
        # whenever "throw_if_cancellation_requested" is called
        self.connector_module.send_binding.cancellation_manager.cancel_operation(
            f"speckle_{model_card_id}"
        )

        # unnecessary, we are using our own CalcellationTokenSource instead of QgsTask
        # might need to be revised later for more "native" implementation
        r"""
        print(QgsApplication.taskManager().tasks())
        for task in QgsApplication.taskManager().tasks():
            if task.description() == f"speckle_{model_card_id}":
                task.cancel()  # this will mark the task as Cancelled
        """

        # 2. hide notification line
        model_card_widget = self.dockwidget.widget_model_cards._find_card_widget(
            model_card_id
        )
        model_card_widget.hide_notification_line()

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

        # first, update UI status through the main thread
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
            display_and_log(
                "Dependencies versioning error.",  # \nClick here for details.",
                url="dependencies_error",
                level=2,
                dockwidget=self.dockwidget,
            )
            raise ImportError(
                f"Incompatible versions of dependencies: 'urllib3=={urllib3.__version__}' and 'requests=={requests.__version__}'"
            )

    def reloadUI(self):
        return

    def openUrl(self, url: str = ""):

        if url is not None and url != "":
            webbrowser.open(url, new=0, autoraise=True)
