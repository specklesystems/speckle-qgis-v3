from textwrap import wrap
import webbrowser

from speckle.ui.models import ModelCard

from PyQt5.QtWidgets import QPushButton
from speckle.ui.widgets.utils.global_resources import (
    BACKGR_COLOR_TRANSPARENT,
    ZERO_MARGIN_PADDING,
)


def splitTextIntoLines(text: str = "", number: int = 40) -> str:
    msg = ""
    try:
        if len(text) > number:
            try:
                for i, text_part in enumerate(text.split("\n")):
                    lines = wrap(text_part, number)
                    for k, x in enumerate(lines):
                        msg += x
                        if k != len(lines) - 1:
                            msg += "\n"
                    if i != len(text.split("\n")) - 1:
                        msg += "\n"
            except Exception as e:
                print(e)
        else:
            msg = text
    except Exception as e:
        print(e)
        # print(text)
    return msg


def open_in_web(model_card: ModelCard):
    url = f"{model_card.server_url}/projects/{model_card.project_id}/models/{model_card.model_id}"
    webbrowser.open(url, new=0, autoraise=True)


def create_text_for_widget(content: str, color: str = "black", other_props=""):

    # add label text (in a shape of QPushButton for easier styling)
    text = QPushButton(content)

    # reiterating callback, because QPushButton clicks are not propageted to the parent widget
    text.setStyleSheet(
        "QPushButton {"
        + f"color:{color};border-radius: 7px;{ZERO_MARGIN_PADDING}"
        + f" {BACKGR_COLOR_TRANSPARENT} height: 20px;text-align: left;{other_props}"
        + "}"
    )
    return text
