from speckle.ui.utils.search_widget_utils import UiSearchUtils
from speckle.ui.widgets.background_widget import BackgroundWidget
from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR,
    BACKGR_COLOR_LIGHT,
    BACKGR_COLOR_WHITE,
    WIDGET_SIDE_BUFFER,
    ZERO_MARGIN_PADDING,
)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QStackedLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QGraphicsDropShadowEffect,
)


class NewProjectWidget(QWidget):

    ui_search_content: UiSearchUtils = None
    _message_card: QWidget = (
        None  # needs to be here, so it can be called on resize event
    )
    project_name: QLineEdit = None

    def __init__(
        self,
        *,
        parent=None,
        label_text: str = "Create new project",
        ui_search_content: UiSearchUtils = None,
    ):
        super(NewProjectWidget, self).__init__(parent)
        self.parent = parent
        self.ui_search_content = ui_search_content

        # align with the parent widget size
        self.resize(
            parent.frameSize().width(),
            parent.frameSize().height(),
        )

        self._add_background()

        self.layout = QStackedLayout()
        self.layout.addWidget(self.background)

        self._fill_message_card(label_text)

        content = QWidget()
        content.layout = QVBoxLayout(self)
        content.layout.setContentsMargins(0, 0, 0, 0)
        content.layout.setAlignment(Qt.AlignCenter)
        content.layout.addWidget(self._message_card)

        self.layout.addWidget(content)

    def _create_widget_label(self, label_text: str, props: str = ""):

        label = QLabel(label_text)

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {"
            + f"{ZERO_MARGIN_PADDING}padding-left:{int(WIDGET_SIDE_BUFFER/2)};"
            + f"padding-top:{int(WIDGET_SIDE_BUFFER/4)}; margin-bottom:{int(WIDGET_SIDE_BUFFER/4)};"
            + f"text-align:left;{props}"
            + "}"
        )
        return label

    def _create_text_widget(self, label_text: str, props: str = ""):

        label = QLabel(label_text)

        # for some reason, "margin-left" doesn't make any effect here
        label.setStyleSheet(
            "QLabel {"
            + f"{ZERO_MARGIN_PADDING}padding-left:5px;padding-right:5px;padding-bottom:5px;"
            + f"text-align:left;{props}"
            + "}"
        )
        return label

    def _add_background(self):
        self.background = BackgroundWidget(parent=self, transparent=False)
        self.background.show()

    def _add_drop_shadow(self, item=None):
        if not item:
            item = self
        # create drop shadow effect
        self._shadow_effect = QGraphicsDropShadowEffect()
        self._shadow_effect.setOffset(2, 2)
        self._shadow_effect.setBlurRadius(8)
        self._shadow_effect.setColor(QColor.fromRgb(100, 100, 100, 150))

        item.setGraphicsEffect(self._shadow_effect)

    def _fill_message_card(self, label_text: str):

        self._message_card = QWidget()
        self._message_card.setAttribute(Qt.WA_StyledBackground, True)
        self._message_card.setStyleSheet(
            "QWidget {" + "border-radius: 10px;" + f"{BACKGR_COLOR_WHITE}" + "}"
        )
        boxLayout = QVBoxLayout(self._message_card)

        label_main = self._create_widget_label(label_text)
        boxLayout.addWidget(label_main)

        # add text
        label = self._create_text_widget("Project name:")
        boxLayout.addWidget(label)

        # add text input
        self.project_name = QLineEdit()
        self.project_name.setMaxLength(20)
        self.project_name.setStyleSheet(
            """QLineEdit { background-color: white; border-radius: 5px; color: black; height: 30px }"""
        )
        boxLayout.addWidget(self.project_name)

        button_create = self._create_create_button()
        boxLayout.addWidget(button_create)

        self._add_drop_shadow(self._message_card)

    def _create_create_button(self) -> QPushButton:

        button_publish = QPushButton("Create")
        button_publish.clicked.connect(self._create_project_and_exit_widget)
        button_publish.setStyleSheet(
            "QPushButton {"
            + f"color:white;border-radius: 7px;margin:5px;padding: 5px;height: 20px;text-align: center;{BACKGR_COLOR}"
            + "} QPushButton:hover { "
            + f"{BACKGR_COLOR_LIGHT};"
            + " }"
        )
        return button_publish

    def _create_project_and_exit_widget(self):

        self.ui_search_content.create_new_project(self.project_name.text(), None)
        # the next signal will trigger closing the widget and refreshing project list
        self.ui_search_content.change_account_and_projects_signal.emit()

    def resizeEvent(self, event=None):
        QWidget.resizeEvent(self, event)
        try:
            self.background.resize(
                self.parent.frameSize().width(),
                self.parent.frameSize().height(),
            )

            self._message_card.setGeometry(
                int(1.5 * WIDGET_SIDE_BUFFER),
                int(
                    (self.parent.frameSize().height() - self._message_card.height()) / 2
                ),
                self.parent.frameSize().width() - 3 * WIDGET_SIDE_BUFFER,
                self._message_card.height(),
            )
        except RuntimeError as e:
            # e.g. Widget was deleted
            pass
