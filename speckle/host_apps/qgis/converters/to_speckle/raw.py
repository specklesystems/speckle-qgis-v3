import math
from typing import List
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings

from qgis.core import QgsAbstractGeometry, QgsWkbTypes, QgsPoint, QgsCurvePolygon
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
        # WkbTypes: https://qgis.org/pyqgis/master/core/Qgis.html#qgis.core.Qgis.WkbType

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
            or wkb_type == QgsWkbTypes.MultiCurve
            or wkb_type == QgsWkbTypes.MultiCurveZ
            or wkb_type == QgsWkbTypes.MultiCurveM
            or wkb_type == QgsWkbTypes.MultiCurveZM
        ):
            return [self._convert_linestring(part) for part in target.parts()]

        if (
            wkb_type == QgsWkbTypes.CircularString
            or wkb_type == QgsWkbTypes.CircularStringZ
            or wkb_type == QgsWkbTypes.CircularStringM
            or wkb_type == QgsWkbTypes.CircularStringZM
            or wkb_type == QgsWkbTypes.CompoundCurve
            or wkb_type == QgsWkbTypes.CompoundCurveZ
            or wkb_type == QgsWkbTypes.CompoundCurveM
            or wkb_type == QgsWkbTypes.CompoundCurveZM
        ):
            return [self._convert_circularstring(part) for part in target.parts()]

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

    def _convert_circularstring(self, circularstring) -> Polyline:

        new_linestring = circularstring.clone().curveToLine()

        return self._convert_linestring(new_linestring)


class PolygonToSpeckleConverter:
    _conversion_settings: QgisConversionSettings
    _polyline_converter: PolylineToSpeckleConverter

    def __init__(
        self,
        conversion_settings: QgisConversionSettings,
        polyline_converter: PolylineToSpeckleConverter,
    ):
        self._conversion_settings = conversion_settings
        self._polyline_converter = polyline_converter

    def convert(self, target: QgsAbstractGeometry) -> List[Polyline]:

        wkb_type = target.wkbType()

        if (
            wkb_type == QgsWkbTypes.Polygon
            or wkb_type == QgsWkbTypes.PolygonZ
            or wkb_type == QgsWkbTypes.PolygonM
            or wkb_type == QgsWkbTypes.PolygonZM
            or wkb_type == QgsWkbTypes.MultiPolygon
            or wkb_type == QgsWkbTypes.MultiPolygonZ
            or wkb_type == QgsWkbTypes.MultiPolygonM
            or wkb_type == QgsWkbTypes.MultiPolygonZM
            or wkb_type == QgsWkbTypes.CurvePolygon
            or wkb_type == QgsWkbTypes.CurvePolygonZ
            or wkb_type == QgsWkbTypes.CurvePolygonM
            or wkb_type == QgsWkbTypes.CurvePolygonZM
        ):
            all_curves = []
            for part in target.parts():

                all_curves.append(
                    self._polyline_converter.convert(part.exteriorRing())[0]
                )

                for i in range(part.numInteriorRings()):
                    all_curves.append(
                        self._polyline_converter.convert(part.interiorRing(i))[0]
                    )
            return all_curves

        raise ValueError(f"Geometry of type '{type(target)}' cannot be converted")
