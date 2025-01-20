# -*- coding: utf-8 -*-

from typing import List
from speckle.host_apps.qgis.connectors.filters import QgisSelectionFilter
from speckle.sdk.connectors_common.operations import SendOperationResult
from speckle.ui.bindings import IBasicConnectorBinding, SelectionInfo
from speckle.ui.models import ModelCard, SenderModelCard
from speckle.ui.widgets.widget_model_card import ModelCardWidget
from speckle.ui.widgets.widget_model_cards_list import ModelCardsWidget
from speckle.ui.widgets.widget_model_search import ModelSearchWidget
from speckle.ui.widgets.widget_no_document import NoDocumentWidget
from speckle.ui.widgets.widget_no_model_cards import NoModelCardsWidget
from speckle.ui.widgets.widget_project_search import ProjectSearchWidget

from plugin_utils.panel_logging import logToUser
from speckle.ui.widgets.utils.global_resources import (
    ICON_LOGO,
    BACKGR_COLOR,
)

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from speckle.ui.widgets.widget_selection_filter import SelectionFilterWidget


class SpeckleQGISv3Dialog(QtWidgets.QDockWidget):
    """Dockwidget (UI module) handles all Speckle UI events, including
    receiving and responding to the signals from child widgets.
    SpeckleModule is set as .bridge, so we have access to all other Speckle modules."""

    bridge: "QgisConnectorModule"
    basic_binding: IBasicConnectorBinding
    widget_no_document: NoDocumentWidget = None
    widget_no_model_cards: NoModelCardsWidget = None
    widget_project_search: ProjectSearchWidget = None
    widget_model_search: ModelSearchWidget = None
    widget_model_cards: ModelCardsWidget = None
    widget_selection_filter: SelectionFilterWidget = None

    send_model_signal = pyqtSignal(object)
    add_model_signal = pyqtSignal(ModelCard)
    remove_model_signal = pyqtSignal(ModelCard)

    def __init__(self, bridge=None, basic_binding: IBasicConnectorBinding = None):
        """Constructor."""
        super(SpeckleQGISv3Dialog, self).__init__()
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        # self.setupUi(self)
        self.basic_binding = basic_binding
        self.bridge = bridge

    def runSetup(self, plugin):
        self._add_label(plugin)
        self._add_start_widget(plugin)

    def _add_label(self, plugin):
        try:
            exitIcon = QPixmap(ICON_LOGO)
            exitActIcon = QIcon(exitIcon)

            # create a label
            text_label = QtWidgets.QPushButton("Speckle (Beta) for QGIS")
            text_label.setStyleSheet(
                "border: 0px;"
                "color: white;"
                f"{BACKGR_COLOR}"
                "top-margin: 40 px;"
                "padding: 10px;"
                "padding-left: 20px;"
                "font-size: 15px;"
                "height: 30px;"
                "text-align: left;"
            )
            text_label.setIcon(exitActIcon)
            text_label.setIconSize(QtCore.QSize(300, 93))
            text_label.setMinimumSize(QtCore.QSize(100, 40))
            text_label.setMaximumWidth(200)

            version = ""
            try:
                if isinstance(plugin.version, str):
                    version = str(plugin.version)
            except:
                pass

            version_label = QtWidgets.QPushButton(version)
            version_label.setStyleSheet(
                "border: 0px;"
                "color: white;"
                f"{BACKGR_COLOR}"
                "padding-top: 15px;"
                "padding-left: 0px;"
                "margin-left: 0px;"
                "font-size: 10px;"
                "height: 30px;"
                "text-align: left;"
            )

            widget = QWidget()
            widget.setStyleSheet(f"{BACKGR_COLOR}")
            boxLayout = QHBoxLayout(widget)
            boxLayout.addWidget(text_label)  # , alignment=Qt.AlignCenter)
            boxLayout.addWidget(version_label)
            boxLayout.setContentsMargins(0, 0, 0, 0)
            self.setWindowTitle("SpeckleQGIS")
            self.setTitleBarWidget(widget)
            self.labelWidget = text_label
            self.labelWidget.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            self.labelWidget.clicked.connect(self._on_click_logo)
        except Exception as e:
            logToUser(e)

    def _add_start_widget(self, plugin):

        # document in QGIS is opened by default, we don't need as actually saved file to start working with data
        document_open = True

        if not document_open:
            no_document_widget = NoDocumentWidget(parent=self)
            self.layout().addWidget(no_document_widget)
            self.widget_no_document = no_document_widget
        else:
            no_model_cards_widget = NoModelCardsWidget(parent=self)
            self.layout().addWidget(no_model_cards_widget)
            self.widget_no_model_cards = no_model_cards_widget

            self.widget_no_model_cards.add_projects_search_signal.connect(
                self._open_select_projects_widget
            )

    def _remove_all_widgets(self):
        if self.widget_no_document:
            self.widget_no_document.setParent(None)
            self.widget_no_document = None

        if self.widget_no_model_cards:
            self.widget_no_model_cards.setParent(None)
            self.widget_no_model_cards = None

        if self.widget_project_search:
            self._remove_widget_project_search()

        if self.widget_model_search:
            self._remove_widget_model_search()

        if self.widget_selection_filter:
            self.remove_widget_selection_filter()

        if self.widget_model_cards:
            self._remove_widget_model_cards()

    def _remove_current_widget(self, widget):

        if self.widget_project_search == widget:
            self._remove_widget_project_search()

        elif self.widget_model_search == widget:
            self._remove_widget_model_search()

        elif self.widget_model_cards == widget:
            self._remove_widget_model_cards()

        elif self.widget_selection_filter == widget:
            self.remove_widget_selection_filter()

    def _remove_process_widgets(self):
        if self.widget_project_search:
            self._remove_widget_project_search()

        if self.widget_model_search:
            self._remove_widget_model_search()

        if self.widget_selection_filter:
            self.remove_widget_selection_filter()

    def _remove_widget_project_search(self):
        self.widget_project_search.setParent(None)
        self.widget_project_search = None

    def _remove_widget_model_search(self):
        self.widget_model_search.setParent(None)
        self.widget_model_search = None

    def remove_widget_selection_filter(self):
        self.widget_selection_filter.setParent(None)
        self.widget_selection_filter = None

    def _remove_widget_model_cards(self):
        self.widget_model_cards.setParent(None)
        self.widget_model_cards = None

    def _create_or_add_model_cards_widget(self, model_card: ModelCard):
        self._remove_process_widgets()
        if not self.widget_model_cards:

            self.widget_model_cards = ModelCardsWidget(parent=self)

            # TODO
            # right now the cards are emitting too many signals on single click

            # subscribe to all Remove Card events from all future ModelCards
            self.widget_model_cards.remove_model_signal.connect(
                lambda model_card=model_card: self.remove_model_signal.emit(model_card)
            )
            # subscribe to all Send events from all future ModelCards
            self.widget_model_cards.send_model_signal.connect(
                lambda model_card=model_card: self.send_model_signal.emit(model_card)
            )
            # subscribe to calling SelectionWidget from existing ModelCard
            self.widget_model_cards.add_selection_filter_signal.connect(
                self._create_selection_filter_widget
            )
            # subscribe to PUBLISH button to open project search
            self.widget_model_cards.add_projects_search_signal.connect(
                self._open_select_projects_widget
            )
            # subscribe to signal to remove the entire widget
            self.widget_model_cards.remove_model_cards_widget_signal.connect(
                self._remove_widget_model_cards
            )
            # add widgets to the layout
            self.layout().addWidget(self.widget_model_cards)

        # actually add a new widget
        self._add_new_model_card_widget(model_card)

    def _add_new_model_card_widget(self, model_card: ModelCard):

        model_card_widget = self.widget_model_cards.add_new_card(model_card)
        # emit signal, for the card that was just added (because we subscribed after creating a widget)
        self.add_model_signal.emit(model_card)
        # add correct Selection text
        self._assign_filter_summary_to_model_card_widget(model_card_widget)

    def _assign_filter_summary_to_model_card_widget(
        self, model_card_widget: ModelCardWidget
    ):
        filter_summary: str = (
            self.bridge.connector_module.layer_utils.get_selection_filter_summary_from_ids(
                model_card_widget.card_content
            )
        )
        model_card_widget.change_selection_text(filter_summary)

    def _subscribe_to_close_on_background_click(self, widget):
        """Receive signal from background click, calling to close the widget."""
        widget.background.remove_current_widget_signal.connect(
            self._remove_current_widget
        )

    def _open_select_projects_widget(self):

        if not self.widget_project_search:
            self.widget_project_search = ProjectSearchWidget(parent=self)
            # add widgets to the layout
            self.layout().addWidget(self.widget_project_search)

            self.widget_project_search.ui_search_content.add_selection_filter_signal.connect(
                self._create_selection_filter_widget
            )

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_project_search)

            # subscribe to add_models_search_widget signal
            self.widget_project_search.ui_search_content.add_models_search_signal.connect(
                self._open_select_models_widget
            )

    def _open_select_models_widget(self, project):

        if not self.widget_model_search:
            self.widget_model_search = ModelSearchWidget(
                parent=self,
                project=project,
                ui_search_content=self.widget_project_search.ui_search_content,
            )
            # add widgets to the layout
            self.layout().addWidget(self.widget_model_search)

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_model_search)

    def _create_selection_filter_widget(self, model_card: SenderModelCard):

        # prevent repeated widget initialization
        if not self.widget_selection_filter:
            # get current user selection
            # TODO should be updated on change, without a call
            selection_info: SelectionInfo = (
                self.bridge.connector_module.selection_binding.get_selection()
            )
            self.widget_selection_filter = SelectionFilterWidget(
                parent=self,
                model_card=model_card,
                label_text="3/3 Select objects",
                selection_info=selection_info,
            )

            # add widgets to the layout
            self.layout().addWidget(self.widget_selection_filter)

            self.widget_selection_filter.add_model_card_signal.connect(
                self._create_or_add_model_cards_widget
            )

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_selection_filter)

    def handle_change_selection_info(self, *args):
        if self.widget_selection_filter:
            self.widget_selection_filter.change_selection_info(*args)

    def add_send_notification(
        self,
        command: str,
        model_card_id: str,
        version_id: str,
        send_conversion_results: List[SendOperationResult],
    ):
        model_card_widget = self.widget_model_cards._find_card_widget(model_card_id)
        model_card_widget.show_notification_line()

    def resizeEvent(self, event):
        QtWidgets.QDockWidget.resizeEvent(self, event)

        # handle resize of child elements
        if self.widget_no_document:
            self.widget_no_document.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )
        if self.widget_no_model_cards:
            self.widget_no_model_cards.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )
        if self.widget_project_search:
            self.widget_project_search.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )
        if self.widget_model_search:
            self.widget_model_search.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )

        if self.widget_model_cards:
            self.widget_model_cards.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )

        if self.widget_selection_filter:
            self.widget_selection_filter.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def _on_click_logo(self):
        import webbrowser

        url = "https://speckle.systems/"
        webbrowser.open(url, new=0, autoraise=True)
