import math
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings

from qgis.core import (
    QgsAbstractGeometry,
    QgsCoordinateTransform,
    QgsCoordinateTransformContext,
)
from specklepy.objects.geometry.point import Point


class PointToSpeckleConverter:
    _conversion_settings: QgisConversionSettings

    def __init__(
        self,
        conversion_settings,
    ):
        self._conversion_settings = conversion_settings

    def convert(self, target: QgsAbstractGeometry) -> Point:

        result_geometry = []

        # reproject geometry
        transform_context: QgsCoordinateTransformContext = (
            self._conversion_settings.project.transformContext()
        )
        transformation: QgsCoordinateTransform = QgsCoordinateTransform(
            self._conversion_settings.active_crs_offset_rotation.crs,
            self._conversion_settings.active_crs_offset_rotation.crs,
            transform_context,
        )

        target.transform(transformation)
        for pt in target.parts():
            speckle_point = Point(
                x=pt.x(),
                y=pt.y(),
                z=0 if math.isnan(pt.z()) else pt.z(),
                units=self._conversion_settings.speckle_units,
            )
            result_geometry.append(speckle_point)

        return result_geometry
