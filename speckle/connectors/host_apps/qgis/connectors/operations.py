from typing import Any, List
from speckle.connectors.common.builders import (
    IRootObjectBuilder,
    RootObjectBuilderResult,
)
from speckle.connectors.host_apps.qgis.connectors.host_app import (
    QgisColorUnpacker,
    QgisLayerUnpacker,
)
from speckle.connectors.ui.models import SendInfo
from specklepy.objects.models.collections.collection import Collection


class QgisRootObjectBuilder(IRootObjectBuilder):
    root_to_speckle_converter: "IRootToSpeckleConverter"
    send_conversion_cache: "ISendConversionCache"
    layer_unpacker: QgisLayerUnpacker
    color_unpacker: QgisColorUnpacker
    converter_settings: "IConverterSettingsStore"
    logger: "ILogger[QgisRootObjectBuilder]"
    activity_factory: "ISdkActivityFactory"

    def __init__(
        self,
        root_to_speckle_converter: "IRootToSpeckleConverter",
        send_conversion_cache: "ISendConversionCache",
        layer_unpacker: QgisLayerUnpacker,
        color_unpacker: QgisColorUnpacker,
        converter_settings: "IConverterSettingsStore",
        logger: "ILogger[QgisRootObjectBuilder]",
        activity_factory: "ISdkActivityFactory",
    ):

        self.root_to_speckle_converter = root_to_speckle_converter
        self.send_conversion_cache = send_conversion_cache
        self.layer_unpacker = layer_unpacker
        self.color_unpacker = color_unpacker
        self.converter_settings = converter_settings
        self.logger = logger
        self.activity_factory = activity_factory

    def build(
        self,
        layers: List[Any],
        send_info: SendInfo,
        on_operation_progressed: Any,
        ct: Any = None,
    ) -> RootObjectBuilderResult:
        # TODO
        return RootObjectBuilderResult(
            root_object=Collection(name="new collection", elements=[]),
            conversion_results=[],
        )
