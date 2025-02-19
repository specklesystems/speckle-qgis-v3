from dataclasses import dataclass
from typing import Any, List, Optional

from speckle.ui.bindings import SelectionInfo
from speckle.ui.models import ModelCard, SenderModelCard

from qgis.core import (
    QgsProject,
    QgsLayerTreeNode,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsVectorLayer,
    QgsRasterLayer,
)


@dataclass
class LayerStorage:
    """This class is implemented to store different types of layers, which, depending
    on the API, might or might not have direct calls to get their ID.
    Name is used as a backup for missing ID.
    """

    name: str
    id: Optional[str]  # None for QgsLayerTreeGroup
    layer: QgsLayerTreeGroup | QgsVectorLayer | QgsRasterLayer


class QgisLayerUtils:
    iface: Any

    def __init__(self, iface: Any):
        self.iface = iface

    def get_all_layers(self, project) -> List[Any]:
        return []

    def unpack_layers(self, layers_to_unpack) -> List[Any]:
        return []

    def get_layers_in_order(
        self, qgis_project, layers_to_search: List[LayerStorage]
    ) -> List[LayerStorage]:

        # get all layer tree
        root_node = qgis_project.layerTreeRoot()

        original_layers_to_search: List[Any] = [lyr.layer for lyr in layers_to_search]
        ordered_top_level_layers: List[LayerStorage] = []

        # get only selected layers, EXCLUDING any child layers (if it's a group)
        # will modify both input lists
        self.traverse_and_select_group(
            root_node, original_layers_to_search, ordered_top_level_layers
        )

        return ordered_top_level_layers

    def get_selection_filter_summary_from_ids(self, card_content: ModelCard) -> str:

        print("___get_selection_filter_summary_from_ids")
        if isinstance(card_content, SenderModelCard):
            layers: List[LayerStorage] = self.get_layers_from_model_card_content(
                card_content
            )
            selection_info: SelectionInfo = self.get_selection_info_from_layers(layers)
            return selection_info.summary

        else:
            return "0 layers"

    def get_layers_from_model_card_content(
        self, card_content: ModelCard
    ) -> List[LayerStorage]:

        layer_ids_and_group_names: List[str] = (
            card_content.send_filter.refresh_object_ids()
        )
        root = QgsProject.instance().layerTreeRoot()

        # get groups
        # for group in root.findGroups() get layer;
        # then extract actual .layer() from the found QgsLayerTreeLayer
        all_groups: List[LayerStorage] = self.traverse_nodes(
            nodes=root.findGroups(), return_layers=False
        )

        groups: List[LayerStorage] = [
            LayerStorage(name=group.name, id=None, layer=group.layer)
            for group in all_groups
            if group.name in layer_ids_and_group_names
        ]

        layers: List[Any] = [
            LayerStorage(
                name=root.findLayer(l_id).layer().name(),
                id=root.findLayer(l_id).layer().id(),
                layer=root.findLayer(l_id).layer(),
            )
            for l_id in layer_ids_and_group_names
            if root.findLayer(l_id) is not None
        ]

        all_layers = groups + layers

        if len(all_layers) != len(layer_ids_and_group_names):
            pass
            # TODO: raise Warning about missing layers. Likely due to document opening/change, or deleted layers

        return self.filter_out_duplicate_layers(all_layers)

    def filter_out_duplicate_layers(
        self, layers: List[LayerStorage]
    ) -> List[LayerStorage]:

        filtered_out_layers = []
        for layer_storage in layers:
            if layer_storage not in filtered_out_layers:
                filtered_out_layers.append(layer_storage)

        return filtered_out_layers

    def traverse_and_select_group(
        self, node: Any, list_to_clear, list_to_add: List[LayerStorage]
    ) -> bool:

        layer_found = False

        if isinstance(node, QgsLayerTreeLayer):
            if node.layer() in list_to_clear:
                list_to_clear.remove(node.layer())
                list_to_add.append(
                    LayerStorage(
                        name=node.layer().name(),
                        id=node.layer().id(),
                        layer=node.layer(),
                    )
                )
                layer_found = True
        elif isinstance(node, QgsLayerTreeGroup):
            if node in list_to_clear:
                list_to_clear.remove(node)
                list_to_add.append(LayerStorage(name=node.name(), id=None, layer=node))
                layer_found = True

        # if the layer was a group, and it wasn't a part of selection: traverse further
        if not layer_found and isinstance(node, QgsLayerTreeGroup):
            children = node.children()
            for child_node in children:
                # will modify both input lists
                self.traverse_and_select_group(child_node, list_to_clear, list_to_add)

    def traverse_nodes(
        self, nodes: QgsLayerTreeNode, return_layers=True, return_groups=True
    ) -> List[LayerStorage]:

        all_layers = []
        for node in nodes:
            if isinstance(node, QgsLayerTreeLayer):
                if return_layers:
                    all_layers.append(
                        LayerStorage(
                            name=node.layer().name(),
                            id=node.layer().id(),
                            layer=node.layer(),
                        )
                    )
            elif isinstance(node, QgsLayerTreeGroup):
                all_layers.extend(
                    self.traverse_group(node, return_layers, return_groups)
                )

        return all_layers

    def traverse_group(
        self, group: QgsLayerTreeGroup, return_layers=True, return_groups=True
    ) -> List[LayerStorage]:
        all_layers = []
        if return_groups:
            all_layers.append(
                LayerStorage(
                    name=group.name(),
                    id=None,
                    layer=group,
                )
            )

        children = group.children()
        for child in children:
            if isinstance(child, QgsLayerTreeLayer):
                if return_layers:
                    all_layers.append(
                        LayerStorage(
                            name=child.layer().name(),
                            id=child.layer().id(),
                            layer=child.layer(),
                        )
                    )
            elif isinstance(child, QgsLayerTreeGroup):
                all_layers.extend(
                    self.traverse_group(child, return_layers, return_groups)
                )

        return all_layers

    def get_currently_selected_layers(self) -> List[LayerStorage]:

        # get groups
        selected_nodes = self.iface.layerTreeView().selectedNodes()  # QgsLayerTreeGroup
        groups_content_layers: List[LayerStorage] = self.traverse_nodes(selected_nodes)

        return self.filter_out_duplicate_layers(groups_content_layers)

    def get_currently_selected_layers_info(self) -> SelectionInfo:

        return self.get_selection_info_from_layers(self.get_currently_selected_layers())

    def get_selection_info_from_layers(
        self, selected_layers: List[LayerStorage]
    ) -> SelectionInfo:
        # possible inputs are coming from:
        # - get_currently_selected_layers() = self.iface.layerTreeView().selectedLayers(): returns QgsVectorLayer, QgsRasterLayer
        # - get_layers_from_model_card_content(): List[Any] = [root.findLayer(l_id).layer() for l_id in layer_ids]: returns QgsVectorLayer, QgsRasterLayer

        object_types = list(
            set(
                [
                    str(type(layer.layer)).split(".")[-1].split("'")[0].split(">")[0]
                    for layer in selected_layers
                ]
            )
        )
        return SelectionInfo(
            selected_object_ids=[layer.id or layer.name for layer in selected_layers],
            summary=f"{len(selected_layers)} layers ({", ".join(object_types)})",
        )
