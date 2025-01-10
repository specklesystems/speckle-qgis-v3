from speckle.host_apps.qgis.converters.settings import QgisConversionSettings

from qgis.core import QgsProject
from speckle.host_apps.qgis.converters.to_speckle.helpers import (
    DisplayValueExtractor,
    PropertiesExtractor,
)
from speckle.host_apps.qgis.converters.utils import (
    CRSoffsetRotation,
)


class QgisConverterModule:
    display_value_extractor: DisplayValueExtractor
    properties_extractor: PropertiesExtractor
    conversion_settings: QgisConversionSettings

    def __init__(
        self,
    ):
        self.display_value_extractor = DisplayValueExtractor()
        self.properties_extractor = PropertiesExtractor()
        self.conversion_settings = None  # will be assigned on operation

    def create_and_save_conversion_settings(
        self, qgis_project: QgsProject, crs_offset_rotation: CRSoffsetRotation
    ):

        self.conversion_settings = QgisConversionSettings(
            project=qgis_project, activeCrsOffsetRotation=crs_offset_rotation
        )
        return self.conversion_settings
