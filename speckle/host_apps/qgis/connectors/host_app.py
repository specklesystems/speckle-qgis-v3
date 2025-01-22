from typing import Any, Dict, List, Optional
from speckle.host_apps.qgis.connectors.extensions import get_speckle_app_id
from speckle.host_apps.qgis.connectors.layer_utils import LayerStorage
from speckle.ui.models import DocumentModelStore
from specklepy.objects.models.collections.collection import Collection
from specklepy.objects.proxies import ColorProxy

from PyQt5.QtGui import QColor
from qgis.core import QgsLayerTreeGroup, QgsVectorLayer, QgsRasterLayer, QgsFeature


class QgisDocumentStore(DocumentModelStore):
    def __init__(self):
        self.models = []
        self.is_document_init = False

    def on_project_closing(self):
        return

    def on_project_saving(self):
        return

    def host_app_save_state(self, state):
        # return super().host_app_save_state(state)
        # TODO: replace model cards written in QGIS project
        return

    def load_state(self):
        # return super().load_state()
        # TODO: get the model cards written into the document
        return


class QgisLayerUnpacker:
    collection_cache: Dict[str, Collection]

    def __init__(self):
        self.collection_cache = {}

    def unpack_selection(
        self,
        qgis_layers: List[LayerStorage],
        parent_collection: Collection,
        objects: Optional[List[Any]] = None,
    ):
        if objects is None:
            objects = []

        for layer_storage in qgis_layers:
            layer = layer_storage.layer

            if isinstance(layer, QgsLayerTreeGroup):
                group_collection: Collection = self.create_and_cache_layer_collection(
                    layer=layer, is_layer_group=True
                )
                parent_collection.elements.append(group_collection)

                # pass all sub-layers through unpacking
                sub_layers = [
                    (
                        LayerStorage(name=lyr.name(), id=None, layer=lyr)
                        if isinstance(lyr, QgsLayerTreeGroup)
                        else LayerStorage(
                            name=lyr.layer().name(),
                            id=lyr.layer().id(),
                            layer=lyr.layer(),
                        )
                    )
                    for lyr in layer.children()
                ]
                self.unpack_selection(sub_layers, group_collection, objects)

            else:  # QgsVectorLayer, QgsRasterLayer
                if layer not in objects:
                    collection: Collection = self.create_and_cache_layer_collection(
                        layer
                    )
                    parent_collection.elements.append(collection)
                    objects.append(layer)

        return objects

    def create_and_cache_layer_collection(
        self,
        layer: QgsLayerTreeGroup | QgsVectorLayer | QgsRasterLayer,
        is_layer_group: bool = False,
    ):

        layer_app_id = get_speckle_app_id(layer)
        collection: Collection = Collection(
            name=layer.name(), applicationId=layer_app_id
        )
        collection["type"] = type(layer)

        if isinstance(layer, QgsVectorLayer):
            layer_fields: Dict[str, Any] = {}
            for field in layer.fields():
                layer_fields[field.name()] = field.type()

            collection["fields"] = layer_fields
            collection["wkbType"] = layer.wkbType().name

        elif isinstance(layer, QgsRasterLayer):
            pass

        if not is_layer_group:
            self.collection_cache[layer_app_id] = collection

        return collection


class QgisColorUnpacker:

    color_proxy_cache: Dict[int, ColorProxy]
    stored_renderer_field: str = None
    stored_renderer: Optional["QgsFeatureRenderer"] = None
    stored_color: Optional[int] = None

    def __init__(self):
        self.color_proxy_cache = {}

    def store_renderer_and_fields(self, vector_layer: QgsVectorLayer) -> None:

        # clear stored values
        self.stored_renderer_field = None
        self.stored_color = None
        self.stored_renderer = None

        renderer = vector_layer.renderer()
        if not renderer:  # e.g. for Tables
            return

        renderer_type = renderer.type()

        if renderer_type == "singleSymbol":
            self.stored_renderer = renderer

        elif renderer_type in ["categorizedSymbol", "graduatedSymbol"]:
            self.stored_renderer = renderer
            # field name or expression string, needs to be double-checked when used to get field value
            self.stored_renderer_field = self.stored_renderer.classAttribute()

    def process_vector_layer_color(
        self, feature: QgsFeature, feature_app_id: str
    ) -> None:
        """Processes a feature color from a vector layer by the stored renderer,
        and stores the feature's id and color proxy to the color_proxy_cache."""

        if not self.stored_renderer:
            return

        if self.stored_color:
            self.add_object_id_to_color_proxy_cache(feature_app_id, self.stored_color)
            return

        color_rgba: int = None
        renderer_type = self.stored_renderer.type()

        if renderer_type == "singleSymbol":
            color_rgba = self.stored_renderer.symbol().color().rgba()

        elif renderer_type == "categorizedSymbol":
            color_rgba = self.get_feature_color_by_categorized_renderer(
                self.stored_renderer, feature
            )

        elif renderer_type == "graduatedSymbol":
            color_rgba = self.get_feature_color_by_graduated_values_renderer(
                self.stored_renderer, feature
            )

        print(color_rgba)

        if not color_rgba:
            return

        # argb: int = self.color_list_to_int(color_rgba)
        self.add_object_id_to_color_proxy_cache(feature_app_id, color_rgba)

        if renderer_type == "singleSymbol":
            self.stored_color = color_rgba

    def get_feature_color_by_categorized_renderer(
        self, renderer: Any, feature: QgsFeature
    ) -> Any:

        feature_value_for_rendering = feature.attribute(self.stored_renderer_field)
        value_symbol = renderer.symbolForValue(
            feature_value_for_rendering
        )  # should be deprecated from 3.40
        if not value_symbol:
            value_symbol = renderer.sourceSymbol()

        color = value_symbol.color().rgba()
        return color

    def get_feature_color_by_graduated_values_renderer(
        self, renderer: Any, feature: QgsFeature
    ) -> Any:

        feature_value_for_rendering = feature.attribute(self.stored_renderer_field)
        value_symbol = renderer.symbolForValue(feature_value_for_rendering)
        if not value_symbol:
            value_symbol = renderer.sourceSymbol()

        color = value_symbol.color().rgba()
        return color

    def add_object_id_to_color_proxy_cache(self, object_id: str, argb: int):

        existing_color_proxy: ColorProxy = self.color_proxy_cache.get(argb)

        if existing_color_proxy:
            existing_color_proxy.objects.append(object_id)
        else:
            new_color_proxy = ColorProxy(
                name=str(argb), value=argb, objects=[object_id], applicationId=str(argb)
            )
            self.color_proxy_cache[argb] = new_color_proxy
