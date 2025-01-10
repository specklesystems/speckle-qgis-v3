from typing import Any, Dict, List
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.host_apps.qgis.converters.to_speckle.helpers import (
    DisplayValueExtractor,
    PropertiesExtractor,
)
from speckle.sdk.converters_common.converters_common import IRootToSpeckleConverter
from speckle.sdk.converters_common.objects import IToSpeckleTopLevelConverter

from specklepy.objects.data import QgisObject


class CoreObjectsBaseToSpeckleTopLevelConverter(
    IToSpeckleTopLevelConverter, IRootToSpeckleConverter
):

    _display_value_extractor: DisplayValueExtractor
    _properties_extractor: PropertiesExtractor
    _conversion_settings: QgisConversionSettings

    def __init__(
        self,
        display_value_extractor,
        properties_extractor,
        conversion_settings,
    ):
        self._display_value_extractor = display_value_extractor
        self._properties_extractor = properties_extractor
        self._conversion_settings = conversion_settings

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
            displayValue=[],
            properties={},
            units=self._conversion_settings.speckle_units,
            application_id="",
        )

        return result
