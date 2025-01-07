# -*- coding: utf-8 -*-

import os.path
from typing import Optional
from speckle.connectors.host_apps.qgis.qgis_module import SpeckleQGISv3Module

# Initialize Qt resources from file resources.py
from resources import *

from qgis.core import Qgis
from qgis.PyQt.QtCore import QCoreApplication, QSettings, Qt, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget

SPECKLE_COLOR = (59, 130, 246)
SPECKLE_COLOR_LIGHT = (69, 140, 255)


class SpeckleQGIS(SpeckleQGISv3Module):
    """Speckle Connector Plugin for QGIS"""

    dockwidget: Optional["QDockWidget"]
    gis_version: str

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        super(SpeckleQGIS, self).__init__(iface)

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "i18n", "SpeckleQGIS_{}.qm".format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&SpeckleQGIS")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.pluginIsActive = False

        self.dockwidget = None
        self.gis_version = Qgis.QGIS_VERSION.encode(
            "iso-8859-1", errors="ignore"
        ).decode("utf-8")
        self.iface = iface

    def tr(self, message: str):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("SpeckleQGIS", message)

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
            text=self.tr("SpeckleQGIS"),
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
            self.iface.removePluginWebMenu(self.tr("&SpeckleQGIS"), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started

        if self.pluginIsActive:
            self.reloadUI()
        else:
            print("Plugin inactive, launch")
            self.pluginIsActive = True
            if self.dockwidget is None:
                self.create_dockwidget()

            # show the dockwidget
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)

        # show the dockwidget
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        self.verify_dependencies()

    def reloadUI(self):
        return
