from typing import Any, Dict, List
from speckle.host_apps.qgis.connectors.extensions import get_speckle_app_id
from speckle.sdk.connectors_common.builders import (
    IRootObjectBuilder,
    RootObjectBuilderResult,
)
from speckle.host_apps.qgis.connectors.host_app import (
    QgisColorUnpacker,
    QgisLayerUnpacker,
)
from speckle.host_apps.qgis.connectors.layer_utils import LayerStorage, QgisLayerUtils
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.sdk.connectors_common.conversion import SendConversionResult
from speckle.sdk.converters_common.converters_common import IRootToSpeckleConverter
from speckle.ui.models import SendInfo

from specklepy.objects.base import Base
from specklepy.objects.data import QgisObject
from specklepy.objects.models.collections.collection import Collection

from qgis.core import QgsProject, QgsLayerTreeGroup, QgsVectorLayer, QgsRasterLayer


class QgisRootObjectBuilder(IRootObjectBuilder):
    root_to_speckle_converter: IRootToSpeckleConverter
    send_conversion_cache: "ISendConversionCache"
    layer_unpacker: QgisLayerUnpacker
    color_unpacker: QgisColorUnpacker
    converter_settings: QgisConversionSettings
    layer_utils: QgisLayerUtils
    logger: "ILogger[QgisRootObjectBuilder]"
    activity_factory: "ISdkActivityFactory"

    def __init__(
        self,
        root_to_speckle_converter: IRootToSpeckleConverter,
        send_conversion_cache: "ISendConversionCache",
        layer_unpacker: QgisLayerUnpacker,
        color_unpacker: QgisColorUnpacker,
        converter_settings: QgisConversionSettings,
        layer_utils: QgisLayerUtils,
        logger: "ILogger[QgisRootObjectBuilder]",
        activity_factory: "ISdkActivityFactory",
    ):

        self.root_to_speckle_converter = root_to_speckle_converter
        self.send_conversion_cache = send_conversion_cache
        self.layer_unpacker = layer_unpacker
        self.color_unpacker = color_unpacker
        self.converter_settings = converter_settings
        self.layer_utils = layer_utils
        self.logger = logger
        self.activity_factory = activity_factory

    def build(
        self,
        layers_flat: List[LayerStorage],
        send_info: SendInfo,
        on_operation_progressed: Any,
        ct: Any = None,
    ) -> RootObjectBuilderResult:
        # TODO

        print("____BUILD")
        print(layers_flat)

        qgis_project = QgsProject.instance()
        root_collection: Collection = Collection(
            name=qgis_project.fileName().split("/")[-1], elements=[]
        )

        qgis_project_crs = qgis_project.crs()
        crs: Dict[str, Any] = {
            "description": qgis_project_crs.description(),
            "unit": qgis_project_crs.mapUnits().name,
            "authid": qgis_project_crs.authid(),
            "wkt": qgis_project_crs.toWkt(),
        }
        root_collection["units"] = self.converter_settings.speckle_units
        root_collection["crs"] = crs

        # TODO: wrap into activityFactory
        layers_ordered: List[LayerStorage] = self.layer_utils.get_layers_in_order(
            qgis_project, layers_flat
        )

        # will modify root_collection and return objects as flat list of Qgs Vector or Raster layers
        unpacked_layers_to_convert: List[Any] = self.layer_unpacker.unpack_selection(
            qgis_layers=layers_ordered, parent_collection=root_collection
        )
        print("____UNPACKED LAYERS TO CONVERT")
        print(unpacked_layers_to_convert)

        # here will be iteration loop through layers and their features
        results: List[SendConversionResult] = []
        for lyr in unpacked_layers_to_convert:
            layer_app_id: str = get_speckle_app_id(lyr)
            layer_collection = self.layer_unpacker.collection_cache[layer_app_id]

            status = "SUCCESS"

            if isinstance(lyr, QgsVectorLayer):
                converted_features: List[Base] = self.convert_vector_features(lyr)
                layer_collection.elements.extend(converted_features)

            result_1 = SendConversionResult(
                status=status,
                source_id=layer_app_id,
                source_type=type(lyr),
                result=layer_collection,
            )
            results.append(result_1)

        return RootObjectBuilderResult(
            root_object=root_collection,
            conversion_results=results,
        )

    def convert_vector_features(self, layer: QgsVectorLayer):
        converted_obj: QgisObject = self.root_to_speckle_converter.convert(layer)
        return [converted_obj]
