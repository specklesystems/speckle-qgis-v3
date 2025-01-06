# -*- coding: utf-8 -*-

from speckle.connectors.ui.bindings import IBasicConnectorBinding
from speckle.connectors.ui.models import ModelCard
from speckle.connectors.ui.widgets.widget_model_cards_list import ModelCardsWidget
from speckle.connectors.ui.widgets.widget_model_search import ModelSearchWidget
from speckle.connectors.ui.widgets.widget_no_document import NoDocumentWidget
from speckle.connectors.ui.widgets.widget_no_model_cards import NoModelCardsWidget
from speckle.connectors.ui.widgets.widget_project_search import ProjectSearchWidget

from plugin_utils.panel_logging import logToUser
from speckle.connectors.ui.widgets.utils.global_resources import (
    COLOR_HIGHLIGHT,
    SPECKLE_COLOR,
    ICON_OPEN_WEB,
    ICON_REPORT,
    ICON_LOGO,
    ICON_SEARCH,
    ICON_DELETE,
    ICON_DELETE_BLUE,
    ICON_SEND,
    ICON_RECEIVE_BLACK,
    ICON_SEND_BLUE,
    COLOR,
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
)

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from speckle.connectors.ui.widgets.widget_selection_filter import SelectionFilterWidget


class SpeckleQGISv3Dialog(QtWidgets.QDockWidget):
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

    def __init__(self, parent=None, basic_binding: IBasicConnectorBinding = None):
        """Constructor."""
        super(SpeckleQGISv3Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        # self.setupUi(self)
        self.basic_binding = basic_binding

    def runSetup(self, plugin):
        self.addLabel(plugin)
        self.add_start_widget(plugin)

    def addLabel(self, plugin):
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
            self.setWindowTitle("SpeckleQGISv3")
            self.setTitleBarWidget(widget)
            self.labelWidget = text_label
            self.labelWidget.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            self.labelWidget.clicked.connect(self.onClickLogo)
        except Exception as e:
            logToUser(e)

    def add_start_widget(self, plugin):

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
                self.open_select_projects_widget
            )

    def remove_all_widgets(self):
        if self.widget_no_document:
            self.widget_no_document.setParent(None)
            self.widget_no_document = None

        if self.widget_no_model_cards:
            self.widget_no_model_cards.setParent(None)
            self.widget_no_model_cards = None

        if self.widget_project_search:
            self.widget_project_search.setParent(None)
            self.widget_project_search = None

    def remove_process_widgets(self):
        if self.widget_project_search:
            self.remove_widget_project_search()
        if self.widget_model_search:
            self.remove_widget_model_search()
        if self.widget_selection_filter:
            self.remove_widget_selection_filter()

    def remove_widget_selection_filter(self):
        self.widget_selection_filter.setParent(None)
        self.widget_selection_filter = None

    def remove_widget_project_search(self):
        self.widget_project_search.setParent(None)
        self.widget_project_search = None

    def remove_widget_model_search(self):
        self.widget_model_search.setParent(None)
        self.widget_model_search = None

    def remove_widget_model_cards(self):
        self.widget_model_cards.setParent(None)
        self.widget_model_cards = None

    def remove_current_widget(self, widget):
        if self.widget_project_search == widget:
            self.remove_widget_project_search()
        elif self.widget_model_search == widget:
            self.remove_widget_model_search()
        elif self.widget_model_cards == widget:
            self.remove_widget_model_cards()
        elif self.widget_selection_filter == widget:
            self.remove_widget_selection_filter()

    def create_or_add_model_cards_widget(self, model_card):
        self.remove_process_widgets()
        if not self.widget_model_cards:

            self.widget_model_cards = ModelCardsWidget(parent=self, cards_list=[])

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
            # subscribe to PUBLISH button to open project search
            self.widget_model_cards.add_projects_search_signal.connect(
                self.open_select_projects_widget
            )

            # emit signal, for the card that was just added (because we subscribed after creating a widget)
            self.widget_model_cards.add_new_card(model_card)
            self.add_model_signal.emit(model_card)

            # add widgets to the layout
            self.layout().addWidget(self.widget_model_cards)

        else:
            self.widget_model_cards.add_new_card(model_card)
            self.add_model_signal.emit(model_card)

    def open_select_projects_widget(self):

        self.widget_project_search = ProjectSearchWidget(parent=self)
        # add widgets to the layout
        self.layout().addWidget(self.widget_project_search)

        self.widget_project_search.ui_search_content.add_selection_filter.connect(
            self.create_selection_filter_widget
        )

    def create_selection_filter_widget(self, model_card: ModelCard):

        self.widget_selection_filter = SelectionFilterWidget(
            parent=self, model_card=model_card, label_text="3/3 Select objects"
        )

        # add widgets to the layout
        self.layout().addWidget(self.widget_selection_filter)

        self.widget_selection_filter.add_model_card_signal.connect(
            self.create_or_add_model_cards_widget
        )

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

    def onClickLogo(self):
        import webbrowser

        url = "https://speckle.systems/"
        webbrowser.open(url, new=0, autoraise=True)
