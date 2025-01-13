from typing import Any, Dict, List
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
from specklepy.objects.data import QgisObject
from specklepy.objects.models.collections.collection import Collection

from qgis.core import QgsProject


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
        layers: List[LayerStorage],
        send_info: SendInfo,
        on_operation_progressed: Any,
        ct: Any = None,
    ) -> RootObjectBuilderResult:
        # TODO

        print("____BUILD")
        print(layers)

        qgis_project = QgsProject.instance()
        rootCollection: Collection = Collection(
            name=qgis_project.fileName(), elements=[]
        )

        qgis_project_crs = qgis_project.crs()
        crs: Dict[str, Any] = {
            "description": qgis_project_crs.description(),
            "unit": qgis_project_crs.mapUnits().name,
            "authid": qgis_project_crs.authid(),
            "wkt": qgis_project_crs.toWkt(),
        }
        rootCollection["units"] = self.converter_settings.speckle_units
        rootCollection["crs"] = crs

        # TODO: wrap into activityFactory
        layers_ordered: List[LayerStorage] = self.layer_utils.get_layers_in_order(
            qgis_project, layers
        )
        unpacked_layers: List[LayerStorage] = self.layer_unpacker.unpack_selection(
            qgis_layers=layers_ordered, parent_collection=rootCollection
        )

        # here will be iteration loop through layers and their features
        results: List[SendConversionResult] = []

        unpacked_layers = layers.copy()
        for lyr in unpacked_layers:
            converted_obj: QgisObject = self.root_to_speckle_converter.convert(lyr)
            result_1 = SendConversionResult(
                status="SUCCESS", source_id="", source_type="type", result=converted_obj
            )
            results.append(result_1)
            rootCollection.elements.append(converted_obj)

        return RootObjectBuilderResult(
            root_object=rootCollection,
            conversion_results=results,
        )
