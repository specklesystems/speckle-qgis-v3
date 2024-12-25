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
from speckle.connectors.host_apps.qgis.connectors.operations import (
    QgisRootObjectBuilder,
)
from speckle.connectors.ui.models import ModelCard
from speckle.connectors.ui.widgets.dockwidget_main import SpeckleQGISv3Dialog
from speckle.connectors.host_apps.qgis.connectors.host_app import QgisDocumentStore

# Initialize Qt resources from file resources.py
from resources import *

import webbrowser
from qgis.core import Qgis, QgsProject
from qgis.PyQt.QtCore import QCoreApplication, QSettings, Qt, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget

SPECKLE_COLOR = (59, 130, 246)
SPECKLE_COLOR_LIGHT = (69, 140, 255)


class SpeckleQGISv3:
    """Speckle Connector Plugin for QGIS"""

    basic_binding: QgisBasicConnectorBinding
    send_binding: QgisSendBinding
    document_store: QgisDocumentStore
    root_obj_builder: QgisRootObjectBuilder
    account_service: AccountService

    dockwidget: Optional["QDockWidget"]
    version: str
    gis_version: str
    theads_total: int

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "i18n", "SpeckleQGISv3_{}.qm".format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&SpeckleQGISv3")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.pluginIsActive = False

        # self.lock = threading.Lock()
        self.dockwidget = None
        self.version = "3.0.0"
        self.gis_version = Qgis.QGIS_VERSION.encode(
            "iso-8859-1", errors="ignore"
        ).decode("utf-8")
        self.iface = iface
        self.theads_total = 0

    # noinspection PyMethodMayBeStatic

    def tr(self, message: str):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("SpeckleQGISv3", message)

    def add_action(
        self,
        icon_path: str,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ":/plugins/speckle-qgis-v3/icon.png"
        self.add_action(
            icon_path,
            text=self.tr("SpeckleQGISv3"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        if self.dockwidget:
            self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        self.pluginIsActive = False
        self.dockwidget.close()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(self.tr("&SpeckleQGISv3"), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started

        self.instantiate_module_dependencies()

        if self.pluginIsActive:
            self.reloadUI()
        else:
            print("Plugin inactive, launch")
            self.pluginIsActive = True
            if self.dockwidget is None:
                self.dockwidget = SpeckleQGISv3Dialog(
                    parent=None, basic_binding=self.basic_binding
                )
                self.dockwidget.runSetup(self)
                self.connect_dockwidget_signals()

            # show the dockwidget
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.verify_dependencies()

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
