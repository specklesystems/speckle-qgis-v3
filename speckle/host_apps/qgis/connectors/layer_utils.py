from typing import Any, List

from speckle.ui.bindings import SelectionInfo
from speckle.ui.models import ModelCard, SenderModelCard

from qgis.core import QgsProject


class QgisLayerUtils:

    def get_all_layers(self, project) -> List[Any]:
        return []

    def unpack_layers(self, layers_to_unpack) -> List[Any]:
        return []

    def get_layers_in_order(self, project, selected_layers) -> List[Any]:
        #  selected_layers: QgsVectorLayer | QgsRasterLayer
        return []

    def get_selection_filter_summary_from_ids(self, card_content: ModelCard) -> str:

        print("___get_selection_filter_summary_from_ids")
        if isinstance(card_content, SenderModelCard):
            layers = self.get_layers_from_model_card_content(card_content)
            selection_info: SelectionInfo = self.get_selection_info_from_layers(layers)
            return selection_info.summary

        else:
            return "0 layers"

    def get_layers_from_model_card_content(self, card_content: ModelCard):

        print("_____get_layers_from_model_card_content")
        layer_ids: List[str] = card_content.send_filter.refresh_object_ids()
        root = QgsProject.instance().layerTreeRoot()

        # also extract actual .layer() from the found QgsLayerTreeLayer
        layers: List[Any] = [root.findLayer(l_id).layer() for l_id in layer_ids]

        # TODO: unpack nested layers
        # all_nested_layers = ...

        return layers

    def get_currently_selected_layers(self, iface):

        selected_layers = iface.layerTreeView().selectedLayers()
        return self.get_selection_info_from_layers(selected_layers)

    def get_selection_info_from_layers(self, selected_layers):
        # possible inputs are coming from:
        # - QgisSelectionBinding get_selection() = self.iface.layerTreeView().selectedLayers(): returns QgsVectorLayer, QgsRasterLayer
        # - get_layers_from_model_card_content(): List[Any] = [root.findLayer(l_id).layer() for l_id in layer_ids]: returns QgsVectorLayer, QgsRasterLayer

        object_types = list(
            set(
                [
                    str(type(layer)).split(".")[-1].split("'")[0].split(">")[0]
                    for layer in selected_layers
                ]
            )
        )
        return SelectionInfo(
            selected_object_ids=[m.id() for m in selected_layers],
            summary=f"{len(selected_layers)} layers ({", ".join(object_types)})",
        )
