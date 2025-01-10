from typing import Any, List
from speckle.ui.bindings import SelectionInfo
from speckle.ui.models import ModelCard, SenderModelCard

from qgis.core import QgsProject


def get_selection_filter_summary_from_ids(card_content: ModelCard):

    if isinstance(card_content, SenderModelCard):
        layers = get_layers_from_model_card_content(card_content)
        selection_info: SelectionInfo = get_selection_info_from_layers(layers)
        return selection_info.summary

    else:
        return "0 layers"


def get_layers_from_model_card_content(card_content: ModelCard):

    layer_ids: List[str] = card_content.send_filter.refresh_object_ids()
    root = QgsProject.instance().layerTreeRoot()

    # also extract actual .layer() from the found QgsLayerTreeLayer
    layers: List[Any] = [root.findLayer(l_id).layer() for l_id in layer_ids]

    return layers


def get_selection_info_from_layers(selected_layers):

    # TODO: unpack nested layers
    all_nested_layers = selected_layers.copy()

    object_types = list(
        set(
            [
                str(type(layer)).split(".")[-1].split("'")[0].split(">")[0]
                for layer in all_nested_layers
            ]
        )
    )
    return SelectionInfo(
        selected_object_ids=[m.id() for m in all_nested_layers],
        summary=f"{len(all_nested_layers)} layers ({", ".join(object_types)})",
    )
