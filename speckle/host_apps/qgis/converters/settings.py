from dataclasses import dataclass
from typing import Dict, List

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsCoordinateTransform,
    QgsCoordinateTransformContext,
)
from speckle.host_apps.qgis.connectors.extensions import get_speckle_app_id
from speckle.host_apps.qgis.connectors.layer_utils import LayerStorage
from speckle.host_apps.qgis.converters.utils import (
    CRSoffsetRotation,
    IHostToSpeckleUnitConverter,
    QgisToSpeckleUnitConverter,
)


@dataclass
class QgisConversionSettings:
    project: QgsProject
    active_crs_offset_rotation: CRSoffsetRotation
    layers_send_transforms: Dict[str, QgsCoordinateTransformContext]
    unit_converter: IHostToSpeckleUnitConverter[str]
    speckle_units: str

    def __init__(
        self,
        project: QgsProject,
        active_crs_offset_rotation: CRSoffsetRotation,
        layers: List[LayerStorage],
        # unit_converter: IHostToSpeckleUnitConverter[Qgis.DistanceUnit],
    ):
        self.project = project
        self.active_crs_offset_rotation = active_crs_offset_rotation
        self.layers_send_transforms = {}
        self.unit_converter = QgisToSpeckleUnitConverter()
        self.speckle_units = self.unit_converter.convert_or_throw(
            self.project.distanceUnits()
        )

        # create QgsCoordinateTransform for each layer
        transform_context: QgsCoordinateTransformContext = project.transformContext()
        for lyr in layers:
            source_layer = lyr.layer
            if isinstance(source_layer, QgsVectorLayer) or isinstance(
                source_layer, QgsRasterLayer
            ):
                transformation = QgsCoordinateTransform(
                    source_layer.crs(),  # crs_from
                    active_crs_offset_rotation.crs,  # crs_to
                    transform_context,
                )
                self.layers_send_transforms[get_speckle_app_id(source_layer)] = (
                    transformation
                )
