from typing import Any, Dict, List
from speckle.host_apps.qgis.connectors.extensions import get_speckle_app_id
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.host_apps.qgis.converters.to_speckle.helpers import (
    DisplayValueExtractor,
    PropertiesExtractor,
)
from speckle.sdk.converters_common.converters_common import IRootToSpeckleConverter
from speckle.sdk.converters_common.objects import IToSpeckleTopLevelConverter

from specklepy.objects.base import Base

from specklepy.objects.data_objects import QgisObject

from qgis.core import QgsFeature, QgsRasterLayer


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

    def convert(self, target_dict: Dict[str, Any]) -> "QgisObject":

        target: QgsFeature | QgsRasterLayer = target_dict["target"]
        layer_app_id = target_dict["layer_application_id"]

        object_type: str = type(target)

        # get displayValue
        display: List[Base] = self._display_value_extractor.get_display_value(
            target, layer_app_id
        )

        # get properties
        properties: Dict[str, Any] = self._properties_extractor.get_properties(target)

        # get applicationId
        application_id = ""
        if isinstance(target, QgsFeature):
            application_id = get_speckle_app_id(target, layer_app_id)

        elif isinstance(target, QgsRasterLayer):
            application_id = get_speckle_app_id(target)
        else:
            raise NotImplementedError(
                f"Conversion of objects of type '{object_type}' is not supported"
            )

        result: QgisObject = QgisObject(
            name=object_type,
            type=object_type,
            displayValue=display,
            properties=properties,
            units=self._conversion_settings.speckle_units,
            applicationId=application_id,
        )

        return result
