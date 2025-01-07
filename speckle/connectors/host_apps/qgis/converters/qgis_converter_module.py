from speckle.connectors.host_apps.qgis.converters.settings import QgisConversionSettings

from qgis.core import QgsProject
from speckle.connectors.host_apps.qgis.converters.utils import (
    CRSoffsetRotation,
    QgisToSpeckleUnitConverter,
)


class QgisConverterModule:
    display_value_extractor: "DisplayValueExtractor"
    properties_extractor: "PropertiesExtractor"
    conversion_settings: QgisConversionSettings

    def __init__(
        self,
    ):
        self.display_value_extractor = None
        self.properties_extractor = None

        qgis_project = QgsProject.instance()
        crs_offset_rotation = CRSoffsetRotation(qgis_project.crs(), 0, 0, 0)
        unit_converter = QgisToSpeckleUnitConverter().convert_or_throw(
            qgis_project.distanceUnits()
        )

        self.conversion_settings = QgisConversionSettings(
            project=qgis_project,
            activeCrsOffsetRotation=crs_offset_rotation,
            unit_converter=unit_converter,
        )
