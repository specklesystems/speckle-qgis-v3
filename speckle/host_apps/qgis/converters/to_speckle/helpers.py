from typing import Any, Dict, List
from qgis.core import QgsFeature, QgsRasterLayer, QgsGeometry, QgsCoordinateTransform
from speckle.host_apps.qgis.converters.settings import QgisConversionSettings
from speckle.host_apps.qgis.converters.to_speckle.raw import (
    PointToSpeckleConverter,
    PolylineToSpeckleConverter,
    PolygonToSpeckleConverter,
)
from specklepy.objects.base import Base


class DisplayValueExtractor:

    _conversion_settings: QgisConversionSettings

    _point_converter: PointToSpeckleConverter
    _polyline_converter: PolylineToSpeckleConverter
    _polygon_converter: PolygonToSpeckleConverter
    _raster_converter: "RasterToSpeckleConverter"

    def __init__(self, conversion_settings):
        self._conversion_settings = conversion_settings
        self._point_converter = PointToSpeckleConverter(conversion_settings)
        self._polyline_converter = PolylineToSpeckleConverter(
            conversion_settings, self._point_converter
        )
        self._polygon_converter = PolygonToSpeckleConverter(
            conversion_settings, self._polyline_converter
        )
        r"""
        self._raster_converter = RasterToSpeckleConverter(conversion_settings)
        """
        pass

    def get_display_value(
        self, core_object: QgsFeature | QgsRasterLayer, layer_app_id: str
    ) -> List[Base]:

        if isinstance(core_object, QgsFeature):
            return self._get_feature_geometries(core_object, layer_app_id)

        elif isinstance(core_object, QgsRasterLayer):
            # return self._raster_converter.convert(core_object)
            return []

        raise NotImplementedError(
            f"Cannot extract displayValue from object of type '{type(core_object)}'"
        )

    def _get_feature_geometries(self, feature: QgsFeature, layer_app_id: str):

        geometry: QgsGeometry = feature.geometry()
        geometry_type = geometry.type().value
        # Point: 0, Line: 1, Polygon: 2, Unknown: 3, Null: 4

        abstract_geometry = geometry.get()

        if geometry_type in [0, 1, 2]:
            # reproject geometry: needs to be done here, while we have a layer reference
            transformation: QgsCoordinateTransform = (
                self._conversion_settings.layers_send_transforms[layer_app_id]
            )
            abstract_geometry.transform(transformation)

            if geometry_type == 0:
                return self._point_converter.convert(abstract_geometry)
            if geometry_type == 1:
                return self._polyline_converter.convert(abstract_geometry)
            if geometry_type == 2:
                return self._polygon_converter.convert(abstract_geometry)

        elif geometry_type == 3:  # no-geometry table feature
            return []

        raise ValueError(f"Unsopported geometry type: '{geometry.type().name}'")


class PropertiesExtractor:

    def get_properties(self, core_object: Any) -> Dict[str, Any]:
        if isinstance(core_object, QgsFeature):
            return core_object.attributeMap()

        return {}
