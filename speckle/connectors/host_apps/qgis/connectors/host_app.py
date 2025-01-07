from typing import Any, Dict, List, Optional
from speckle.connectors.host_apps.qgis.connectors.extensions import get_speckle_app_id
from speckle.connectors.ui.models import DocumentModelStore
from specklepy.objects.models.collections.collection import Collection
from specklepy.objects.proxies import ColorProxy

from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsFeature


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
        qgis_layers: List[Any],
        parent_collection: Collection,
        objects: Optional[List[Any]] = None,
    ):
        if not objects:
            objects = []

        for layer in qgis_layers:
            # TODO: handle group layers
            if layer not in objects:
                collection: Collection = self.create_and_cache_layer_collection(layer)
                parent_collection.elements.append(collection)
                objects.append(layer)

        return objects

    def create_and_cache_layer_collection(
        self, layer: Any, is_layer_group: bool = False
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
            collection["wkbType"] = layer.wkbType()

        # TODO
        # if is_layer_group:
        # self.collection_cache[layer_app_id] = collection

        return collection


class QgisColorUnpacker:
    color_proxy_cache: Dict[int, ColorProxy]
    stored_renderer: Optional[Any]
    stored_renderer_fields: List[str]
    stored_color: Optional[int]

    def __init__(self):
        self.color_proxy_cache = {}

    def store_renderer_and_fields(self, vector_layer: QgsVectorLayer) -> None:
        return

    def process_vector_layer_color(
        self, feature: QgsFeature, feature_app_id: str
    ) -> None:
        return

    def get_feature_color_by_graduate_renderer(
        self, renderer: Any, feature: QgsFeature
    ) -> Any:
        return

    def get_feature_color_by_unique_values_renderer(
        self, renderer: Any, feature: QgsFeature
    ) -> Any:
        return
