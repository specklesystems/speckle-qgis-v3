from dataclasses import dataclass

from qgis.core import QgsProject
from speckle.host_apps.qgis.converters.utils import (
    CRSoffsetRotation,
    IHostToSpeckleUnitConverter,
    QgisToSpeckleUnitConverter,
)


@dataclass
class QgisConversionSettings:
    project: QgsProject
    active_crs_offset_rotation: CRSoffsetRotation
    unit_converter: IHostToSpeckleUnitConverter[str]
    speckle_units: str

    def __init__(
        self,
        project: QgsProject,
        active_crs_offset_rotation: CRSoffsetRotation,
        # unit_converter: IHostToSpeckleUnitConverter[Qgis.DistanceUnit],
    ):
        self.project = project
        self.active_crs_offset_rotation = active_crs_offset_rotation
        self.unit_converter = QgisToSpeckleUnitConverter()
        self.speckle_units = self.unit_converter.convert_or_throw(
            self.project.distanceUnits()
        )
