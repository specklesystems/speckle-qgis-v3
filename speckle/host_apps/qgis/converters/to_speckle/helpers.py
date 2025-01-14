from typing import Any, Dict, List
from qgis.core import QgsFeature, QgsRasterLayer, QgsGeometry
from speckle.host_apps.qgis.converters.to_speckle.raw import PointToSpeckleConverter
from specklepy.objects.base import Base


class DisplayValueExtractor:

    _point_converter: PointToSpeckleConverter
    _multi_point_converter: "MultiPointToSpeckleConverter"
    _polyline_converter: "PolylineToSpeckleConverter"
    _polygon_converter: "PolygonToSpeckleConverter"
    _raster_converter: "RasterToSpeckleConverter"

    def __init__(self, conversion_settings):
        self._point_converter = PointToSpeckleConverter(conversion_settings)
        r"""
        self._multi_point_converter = MultiPointToSpeckleConverter()
        self._polyline_converter = PolylineToSpeckleConverter()
        self._polygon_converter = PolygonToSpeckleConverter()
        self._raster_converter = RasterToSpeckleConverter()
        """
        pass

    def get_display_value(self, core_object) -> List[Base]:

        if isinstance(core_object, QgsFeature):
            return self._get_feature_geometries(core_object)

        elif isinstance(core_object, QgsRasterLayer):
            # return self._raster_converter.convert(core_object)
            return []

        raise NotImplementedError(
            f"Cannot extract displayValue from object of type '{type(core_object)}'"
        )

    def _get_feature_geometries(self, feature: QgsFeature):

        geometry: QgsGeometry = feature.geometry()
        print(geometry)
        geometry_type = geometry.type().value
        # Point: 0, Line: 1, Polygon: 2, Unknown: 3, Null: 4

        abstract_geometry = geometry.get()

        if geometry_type == 0:
            return self._point_converter.convert(abstract_geometry)
            pass
        if geometry_type == 1:
            # return self._polyline_converter.convert(geometry)
            pass
        if geometry_type == 2:
            # return self._polygon_converter.convert(geometry)
            pass
        if geometry_type == 4:
            return []

        raise ValueError(f"Unsopported geometry type: '{geometry.type().name}'")


class PropertiesExtractor:

    def get_properties(self, core_object: Any) -> Dict[str, Any]:
        if isinstance(core_object, QgsFeature):
            return core_object.attributeMap()

        return {}
