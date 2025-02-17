# -*- coding: utf-8 -*-

from typing import List
from speckle.sdk.connectors_common.operations import SendOperationResult
from speckle.ui.bindings import IBasicConnectorBinding, SelectionInfo
from speckle.ui.models import ModelCard, SenderModelCard
from speckle.ui.widgets.widget_account_search import AccountSearchWidget
from speckle.ui.widgets.widget_model_card import ModelCardWidget
from speckle.ui.widgets.widget_model_cards_list import ModelCardsWidget
from speckle.ui.widgets.widget_model_search import ModelSearchWidget
from speckle.ui.widgets.widget_new_model import NewModelWidget
from speckle.ui.widgets.widget_new_project import NewProjectWidget
from speckle.ui.widgets.widget_no_document import NoDocumentWidget
from speckle.ui.widgets.widget_no_model_cards import NoModelCardsWidget
from speckle.ui.widgets.widget_project_search import ProjectSearchWidget

from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR_LIGHT_GREY2,
    ICON_LOGO,
    BACKGR_COLOR,
    LABEL_HEIGHT,
    ZERO_MARGIN_PADDING,
)

from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedLayout,
    QWidget,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

from speckle.ui.widgets.widget_selection_filter import SelectionFilterWidget


class SpeckleQGISv3Dialog(QDockWidget):
    """Dockwidget (UI module) handles all Speckle UI events, including
    receiving and responding to the signals from child widgets.
    SpeckleModule is set as .bridge, so we have access to all other Speckle modules."""

    bridge: "QgisConnectorModule"
    basic_binding: IBasicConnectorBinding

    header_widget: QWidget = None
    main_widget: QWidget = None
    widget_no_document: NoDocumentWidget = None
    widget_no_model_cards: NoModelCardsWidget = None
    widget_project_search: ProjectSearchWidget = None
    widget_model_search: ModelSearchWidget = None
    widget_account_search: AccountSearchWidget = None
    widget_new_project: NewProjectWidget = None
    widget_new_model: NewModelWidget = None
    widget_model_cards: ModelCardsWidget = None
    widget_selection_filter: SelectionFilterWidget = None

    close_plugin_signal = pyqtSignal()
    send_model_signal = pyqtSignal(object)
    cancel_operation_signal = pyqtSignal(str)
    add_model_signal = pyqtSignal(ModelCard)
    remove_model_signal = pyqtSignal(ModelCard)

    activity_start_signal = pyqtSignal(str, str)

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
        self.layout = QVBoxLayout(self)

        # create and add header widget
        self.header_widget = self._create_header(plugin)
        self.layout.addWidget(self.header_widget)

        # cerate and add main widget
        return
        self.main_widget = QWidget()
        self.main_widget.layout = QStackedLayout(self.main_widget)
        self.layout.addWidget(self.main_widget)

        # self._add_start_widget(plugin)

    def _create_header(self, plugin):
        try:
            exitIcon = QPixmap(ICON_LOGO)
            exitActIcon = QIcon(exitIcon)

            # create a label
            text_label = QPushButton("Speckle (Beta) for QGIS")
            text_label.setStyleSheet(
                "border: 0px;"
                "color: white;"
                f"{BACKGR_COLOR}"
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

            version_label = QPushButton(version)
            version_label.setStyleSheet(
                "border: 0px;"
                "color: white;"
                f"{BACKGR_COLOR}"
                "padding-left: 0px;"
                "margin-left: 0px;"
                "font-size: 10px;"
                "height: 30px;"
                "text-align: left;"
            )

            header_widget = QWidget()
            header_widget.setStyleSheet(f"{BACKGR_COLOR}")

            boxLayout = QHBoxLayout(header_widget)
            boxLayout.setAlignment(QtCore.Qt.AlignVCenter)
            boxLayout.addWidget(text_label)  # , alignment=Qt.AlignCenter)
            boxLayout.addWidget(version_label)
            boxLayout.setContentsMargins(0, 0, 10, 0)

            self.labelWidget = text_label
            self.labelWidget.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            self.labelWidget.clicked.connect(self._on_click_logo)

            # Add a spacer item to push the next button to the right
            spacer = QSpacerItem(10, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
            boxLayout.addItem(spacer)

            # close button
            close_btn = QPushButton("x")
            close_btn.clicked.connect(self.close_plugin_signal.emit)
            close_btn.setStyleSheet(
                "QPushButton {"
                + f"color:rgba(255,255,255,1); border-radius: 0px;{ZERO_MARGIN_PADDING}font-size: 12px;"
                + "background-color: rgba(240,240,240,0); height:20px;text-align: center; "
                + "} QPushButton:hover { "
                + "color:rgba(155,155,155,1);"
                + " }"
            )

            close_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            boxLayout.addWidget(close_btn)

            self.setWindowTitle("SpeckleQGIS")

            return header_widget

        except Exception as e:
            print(e)

    def _add_start_widget(self, plugin):

        # document in QGIS is opened by default, we don't need as actually saved file to start working with data
        document_open = True

        if not document_open:
            no_document_widget = NoDocumentWidget(parent=self)
            self.main_widget.layout.addWidget(no_document_widget)
            self.widget_no_document = no_document_widget
        else:
            no_model_cards_widget = NoModelCardsWidget(parent=self)
            self.main_widget.layout.addWidget(no_model_cards_widget)
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

        if self.widget_account_search:
            self._remove_widget_account_search()

        if self.widget_new_project:
            self._remove_widget_new_project()

        if self.widget_new_model:
            self._remove_widget_new_model()

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

        elif self.widget_account_search == widget:
            self._remove_widget_account_search()

        elif self.widget_new_project == widget:
            self._remove_widget_new_project()

        elif self.widget_new_model == widget:
            self._remove_widget_new_model()

        elif self.widget_selection_filter == widget:
            self.remove_widget_selection_filter()

    def _remove_process_widgets(self):
        if self.widget_project_search:
            self._remove_widget_project_search()

        if self.widget_model_search:
            self._remove_widget_model_search()

        if self.widget_selection_filter:
            self.remove_widget_selection_filter()

        if self.widget_account_search:
            self._remove_widget_account_search()

        if self.widget_new_project:
            self._remove_widget_new_project()

        if self.widget_new_model:
            self._remove_widget_new_model()

    def _remove_widget_project_search(self):
        self.widget_project_search.setParent(None)
        self.widget_project_search = None

    def _remove_widget_model_search(self):
        self.widget_model_search.setParent(None)
        self.widget_model_search = None

    def _remove_widget_account_search(self):
        self.widget_account_search.setParent(None)
        self.widget_account_search = None

    def _remove_widget_new_project(self):
        self.widget_new_project.setParent(None)
        self.widget_new_project = None

    def _remove_widget_new_model(self):
        self.widget_new_model.setParent(None)
        self.widget_new_model = None

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
            # subscribe to all Cancel events from all future ModelCards
            self.widget_model_cards.cancel_operation_signal.connect(
                self.cancel_operation_signal.emit
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
            self.main_widget.layout.addWidget(self.widget_model_cards)

        # actually add a new widget
        self._add_new_model_card_widget(model_card)

        # send data immediately
        self.send_model_signal.emit(model_card)

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
            self.main_widget.layout.addWidget(self.widget_project_search)

            self.widget_project_search.ui_search_content.add_selection_filter_signal.connect(
                self._create_selection_filter_widget
            )

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_project_search)

            # subscribe to add_models_search_widget signal
            self.widget_project_search.ui_search_content.add_models_search_signal.connect(
                self._open_select_models_widget
            )

            # subscribe to new_project_widget_signal signal
            self.widget_project_search.ui_search_content.new_project_widget_signal.connect(
                self._open_new_project_widget
            )

            # subscribe to select_account_signal signal
            self.widget_project_search.ui_search_content.select_account_signal.connect(
                self._open_select_accounts_widget
            )

            # subscribe to change_account_signal signal
            self.widget_project_search.ui_search_content.change_account_and_projects_signal.connect(
                self._update_project_list
            )

    def _update_project_list(self):

        # can be called from CreateAccount or NewProject widgets
        if self.widget_account_search:
            self._remove_widget_account_search()
        if self.widget_new_project:
            self._remove_widget_new_project()

        self.widget_project_search.refresh_projects()

    def _update_model_list(self):
        # can be called from NewModelWidget
        if self.widget_new_model:
            self._remove_widget_new_model()

        self.widget_model_search.refresh_models()

    def _open_new_project_widget(self):
        if not self.widget_new_project:
            self.widget_new_project = NewProjectWidget(
                parent=self,
                ui_search_content=self.widget_project_search.ui_search_content,
            )
            # add widgets to the layout
            self.main_widget.layout.addWidget(self.widget_new_project)

            # connect clear_project_search_bar_signal. Called when New project is created
            self.widget_new_project.ui_search_content.clear_project_search_bar_signal.connect(
                self.widget_project_search.clear_search_bar
            )

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_new_project)

    def _open_new_model_widget(self, project_id: str):
        if not self.widget_new_model:
            self.widget_new_model = NewModelWidget(
                parent=self,
                project_id=project_id,
                ui_search_content=self.widget_project_search.ui_search_content,
            )
            # add widgets to the layout
            self.main_widget.layout.addWidget(self.widget_new_model)

            # connect clear_model_search_bar_signal. Called when New model is created
            self.widget_new_model.ui_search_content.clear_model_search_bar_signal.connect(
                self.widget_model_search.clear_search_bar
            )

            # subscribe to NewModelCreated event
            self.widget_new_model.ui_search_content.refresh_models_signal.connect(
                self._update_model_list
            )

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_new_model)

    def _open_select_accounts_widget(self):
        if not self.widget_account_search:
            self.widget_account_search = AccountSearchWidget(
                parent=self,
                ui_search_content=self.widget_project_search.ui_search_content,
            )
            # add widgets to the layout
            self.main_widget.layout.addWidget(self.widget_account_search)

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_account_search)

    def _open_select_models_widget(self, project):

        if not self.widget_model_search:
            self.widget_model_search = ModelSearchWidget(
                parent=self,
                project=project,
                ui_search_content=self.widget_project_search.ui_search_content,
            )
            # add widgets to the layout
            self.main_widget.layout.addWidget(self.widget_model_search)

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_model_search)

            # subscribe to new_model_widget_signal signal
            self.widget_model_search.ui_search_content.new_model_widget_signal.connect(
                self._open_new_model_widget
            )

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
            self.main_widget.layout.addWidget(self.widget_selection_filter)

            self.widget_selection_filter.add_model_card_signal.connect(
                self._create_or_add_model_cards_widget
            )

            # subscribe to close-on-background-click event
            self._subscribe_to_close_on_background_click(self.widget_selection_filter)

    def handle_change_selection_info(self, *args):
        if self.widget_selection_filter:
            self.widget_selection_filter.change_selection_info(*args)

    def add_activity_status(self, model_card_id: str, main_text: str):
        model_card_widget = self.widget_model_cards._find_card_widget(model_card_id)
        # enable Dismiss button for occasional situation, when the progress is stuck
        model_card_widget.show_notification_line(main_text, True, False, True)

    def add_send_notification(
        self,
        command: str,
        model_card_id: str,
        version_id: str,
        send_conversion_results: List[SendOperationResult],
    ):
        model_card_widget = self.widget_model_cards._find_card_widget(model_card_id)
        model_card_widget.show_notification_line("Version created!", True, True, False)

    def resizeEvent(self, event):
        QDockWidget.resizeEvent(self, event)

        # handle resize of child elements
        if self.header_widget:
            self.header_widget.resize(
                self.frameSize().width(),
                LABEL_HEIGHT,
            )

        if self.main_widget:
            self.main_widget.resize(
                self.frameSize().width(),
                self.frameSize().height() - LABEL_HEIGHT,
            )

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

        if self.widget_new_project:
            self.widget_new_project.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )

        if self.widget_new_model:
            self.widget_new_model.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )

        if self.widget_account_search:
            self.widget_account_search.resize(
                self.frameSize().width(),
                self.frameSize().height(),
            )

    def closeEvent(self, event):
        self.close_plugin_signal.emit()
        event.accept()

    def _on_click_logo(self):
        import webbrowser

        url = "https://speckle.systems/"
        webbrowser.open(url, new=0, autoraise=True)
