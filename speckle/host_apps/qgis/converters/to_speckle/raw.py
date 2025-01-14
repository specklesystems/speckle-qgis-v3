import math
from typing import List
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings

from qgis.core import QgsAbstractGeometry, QgsWkbTypes, QgsPoint
from specklepy.objects.geometry.point import Point
from specklepy.objects.geometry.polyline import Polyline


class PointToSpeckleConverter:
    _conversion_settings: QgisConversionSettings

    def __init__(
        self,
        conversion_settings,
    ):
        self._conversion_settings = conversion_settings

    def convert(self, target: QgsAbstractGeometry) -> List[Point]:

        result_geometry = [self.convert_point_to_speckle(pt) for pt in target.parts()]
        return result_geometry

    def convert_point_to_speckle(self, point: QgsPoint) -> Point:
        speckle_point = Point(
            x=point.x(),
            y=point.y(),
            z=0 if math.isnan(point.z()) else point.z(),
            units=self._conversion_settings.speckle_units,
        )
        return speckle_point


class PolylineToSpeckleConverter:
    _conversion_settings: QgisConversionSettings
    _point_converter: PointToSpeckleConverter

    def __init__(
        self,
        conversion_settings: QgisConversionSettings,
        point_converter: PointToSpeckleConverter,
    ):
        self._conversion_settings = conversion_settings
        self._point_converter = point_converter

    def convert(self, target: QgsAbstractGeometry) -> List[Polyline]:

        wkb_type = target.wkbType()
        print(wkb_type.name)

        if (
            wkb_type == QgsWkbTypes.LineString
            or wkb_type == QgsWkbTypes.LineString25D
            or wkb_type == QgsWkbTypes.LineStringZ
            or wkb_type == QgsWkbTypes.LineStringM
            or wkb_type == QgsWkbTypes.LineStringZM
            or wkb_type == QgsWkbTypes.MultiLineString
            or wkb_type == QgsWkbTypes.MultiLineString25D
            or wkb_type == QgsWkbTypes.MultiLineStringZ
            or wkb_type == QgsWkbTypes.MultiLineStringM
            or wkb_type == QgsWkbTypes.MultiLineStringZM
        ):
            return [self._convert_linestring(part) for part in target.parts()]

        raise ValueError(f"Geometry of type '{wkb_type.name}' cannot be converted")

    def _convert_linestring(self, linestring) -> Polyline:

        speckle_points: List[Point] = [
            self._point_converter.convert_point_to_speckle(pt)
            for pt in linestring.points()
        ]
        coord_list = [item for pt in speckle_points for item in [pt.x, pt.y, pt.z]]

        return Polyline(
            value=coord_list,
            units=self._conversion_settings.speckle_units,
            closed=linestring.isClosed(),
        )
