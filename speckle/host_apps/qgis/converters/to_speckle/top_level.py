from typing import Any, Dict, List
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.sdk.converters_common.converters_common import IRootToSpeckleConverter
from speckle.sdk.converters_common.objects import IToSpeckleTopLevelConverter

from specklepy.objects.data import QgisObject


class CoreObjectsBaseToSpeckleTopLevelConverter(
    IToSpeckleTopLevelConverter, IRootToSpeckleConverter
):

    display_value_extractor: "DisplayValueExtractor"
    properties_extractor: "PropertiesExtractor"
    conversion_settings: QgisConversionSettings

    def __init__(
        self,
        display_value_extractor=None,
        properties_extractor=None,
        conversion_settings=None,
    ):
        self.display_value_extractor = display_value_extractor
        self.properties_extractor = properties_extractor
        self.conversion_settings = conversion_settings

    def convert(self, target: Any) -> "QgisObject":

        object_type: str = type(target)
        r"""
        # get display value
        display: List[Base] = self._display_value_extractor.get_display_value(target)

        # get properties
        properties: Dict[str, Any] = self._properties_extractor.get_properties(target)

        """
        result: QgisObject = QgisObject(
            name=object_type,
            type=object_type,
            displayValue=[],  # display,
            properties={},  # properties,
            units=self.conversion_settings.speckle_units,
            application_id="",
        )
        print(result.name)
        print(result.properties)
        return result
