from dataclasses import dataclass

from qgis.core import Qgis, QgsProject
from speckle.connectors.host_apps.qgis.converters.utils import (
    CRSoffsetRotation,
    IHostToSpeckleUnitConverter,
)


@dataclass
class QgisConversionSettings:
    project: QgsProject
    activeCrsOffsetRotation: CRSoffsetRotation
    unit_converter: IHostToSpeckleUnitConverter[str]

    def __init__(
        self,
        project: QgsProject,
        activeCrsOffsetRotation: CRSoffsetRotation,
        unit_converter: IHostToSpeckleUnitConverter[Qgis.DistanceUnit],
    ):
        self.project = project
        self.activeCrsOffsetRotation = activeCrsOffsetRotation
        self.unit_converter = unit_converter
